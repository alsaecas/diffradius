from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Iterable

from agents import RunConfig, Runner, set_tracing_disabled

from .agents import (
    adversary_agent,
    baseline_agent,
    impact_scout_agent,
    synthesizer_agent,
    verifier_agent,
)
from .config import settings
from .models import AdversarialReview, ImpactMap, ReviewReport, RunUsage, WorkflowResult
from .pricing import estimate_cost_usd
from .repository import RepositoryView
from .tools import ReviewContext
from .trajectory import TrajectoryRecorder


set_tracing_disabled(True)


def _usage(result, elapsed: float) -> RunUsage:
    u = result.context_wrapper.usage
    return RunUsage(
        requests=u.requests,
        input_tokens=u.input_tokens,
        output_tokens=u.output_tokens,
        total_tokens=u.total_tokens,
        elapsed_seconds=elapsed,
        estimated_cost_usd=estimate_cost_usd(settings().model, u.input_tokens, u.output_tokens),
    )


def _combine_usage(parts: Iterable[RunUsage]) -> RunUsage:
    parts = list(parts)
    input_tokens = sum(p.input_tokens for p in parts)
    output_tokens = sum(p.output_tokens for p in parts)
    known_costs = [p.estimated_cost_usd for p in parts if p.estimated_cost_usd is not None]
    return RunUsage(
        requests=sum(p.requests for p in parts),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=sum(p.total_tokens for p in parts),
        elapsed_seconds=sum(p.elapsed_seconds for p in parts),
        estimated_cost_usd=round(sum(known_costs), 6) if len(known_costs) == len(parts) else None,
    )


def _run_agent(agent, prompt: str, context: ReviewContext):
    context.current_agent = agent.name
    context.trajectory.add("agent_input", agent.name, input=prompt)
    started = time.perf_counter()
    result = Runner.run_sync(
        agent,
        prompt,
        context=context,
        max_turns=settings().max_turns,
        run_config=RunConfig(tracing_disabled=True, trace_include_sensitive_data=False),
    )
    elapsed = time.perf_counter() - started
    output = result.final_output
    serializable = output.model_dump(mode="json") if hasattr(output, "model_dump") else str(output)
    usage = _usage(result, elapsed)
    context.trajectory.add("agent_output", agent.name, output=serializable, usage=usage.model_dump())
    return result, usage


def _finish(
    recorder: TrajectoryRecorder,
    report: ReviewReport,
    usages: list[RunUsage],
    trajectory_dir: Path | None,
) -> WorkflowResult:
    usage = _combine_usage(usages)
    recorder.add("workflow_result", "workflow", report=report.model_dump(mode="json"), usage=usage.model_dump())
    path = recorder.save(trajectory_dir) if trajectory_dir else None
    return WorkflowResult(report=report, usage=usage, trajectory_path=str(path) if path else None)


def run_baseline(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"baseline-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    result, usage = _run_agent(
        baseline_agent(),
        "Review the supplied ticket and diff for release risk. Use repository tools as needed.",
        context,
    )
    return _finish(recorder, result.final_output, [usage], trajectory_dir)


def _run_scout(view: RepositoryView, recorder: TrajectoryRecorder, context: ReviewContext):
    scout_result, usage = _run_agent(
        impact_scout_agent(),
        "Build an impact map for the supplied ticket and diff. Trace behavior beyond changed lines.",
        context,
    )
    return scout_result.final_output, usage


def _run_adversary(impact: ImpactMap, context: ReviewContext):
    prompt = (
        "Here is the Impact Scout output. Attack it and inspect the repository for missed or weak "
        "failure modes.\n\n" + json.dumps(impact.model_dump(mode="json"), indent=2)
    )
    result, usage = _run_agent(adversary_agent(), prompt, context)
    return result.final_output, usage


def _run_synthesizer(candidates: object, context: ReviewContext):
    prompt = (
        "Turn these upstream candidates into the final review report.\n\n"
        + json.dumps(candidates.model_dump(mode="json"), indent=2)
    )
    result, usage = _run_agent(synthesizer_agent(), prompt, context)
    return result.final_output, usage


def run_impact(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    """Ablation: explicit impact map followed by ordinary synthesis."""
    recorder = TrajectoryRecorder(f"impact-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    impact, scout_usage = _run_scout(view, recorder, context)
    report, synth_usage = _run_synthesizer(impact, context)
    return _finish(recorder, report, [scout_usage, synth_usage], trajectory_dir)


def run_adversarial(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    """Ablation: impact map + adversarial pass, without independent verification."""
    recorder = TrajectoryRecorder(f"adversarial-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    impact, scout_usage = _run_scout(view, recorder, context)
    adversarial, adversary_usage = _run_adversary(impact, context)
    report, synth_usage = _run_synthesizer(adversarial, context)
    return _finish(recorder, report, [scout_usage, adversary_usage, synth_usage], trajectory_dir)


def run_final(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"final-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    impact, scout_usage = _run_scout(view, recorder, context)
    adversarial, adversary_usage = _run_adversary(impact, context)
    verifier_prompt = (
        "Independently verify these candidate risks. Keep only concrete regressions caused by the "
        "diff. Reject unsupported claims.\n\n"
        + json.dumps(adversarial.model_dump(mode="json"), indent=2)
    )
    verifier_result, verifier_usage = _run_agent(verifier_agent(), verifier_prompt, context)
    return _finish(
        recorder,
        verifier_result.final_output,
        [scout_usage, adversary_usage, verifier_usage],
        trajectory_dir,
    )
