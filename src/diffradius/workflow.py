from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Iterable

from agents import RunConfig, Runner, set_tracing_disabled

from .agents import (
    adversary_agent,
    contract_agent,
    impact_scout_agent,
    prompt_baseline_agent,
    proof_reviewer_agent,
    synthesizer_agent,
    tool_reviewer_agent,
)
from .config import settings
from .models import ChangeContract, ImpactMap, ReviewReport, RunUsage, WorkflowResult
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


def run_prompt_baseline(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    """Fair direct-prompt baseline: same model, ticket + diff only, no repository tools."""
    recorder = TrajectoryRecorder(f"prompt-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    prompt = (
        "Review this software change for concrete release risk using only the supplied evidence.\n\n"
        "TICKET\n"
        + view.ticket
        + "\n\nDIFF\n"
        + view.diff_text
    )
    result, usage = _run_agent(prompt_baseline_agent(), prompt, context)
    return _finish(recorder, result.final_output, [usage], trajectory_dir)


def run_tool_agent(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    """Strong comparator: one general agent with basic current-repository tools."""
    recorder = TrajectoryRecorder(f"tool-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    result, usage = _run_agent(
        tool_reviewer_agent(),
        "Review the supplied ticket and diff for release risk. Use repository tools as needed.",
        context,
    )
    return _finish(recorder, result.final_output, [usage], trajectory_dir)


def run_final(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    """Selected architecture: one evidence-seeking agent with current + before-version tools."""
    recorder = TrajectoryRecorder(f"final-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    result, usage = _run_agent(
        proof_reviewer_agent(),
        "Investigate this change end-to-end. Prove change-induced counterexamples and return the concise release-risk report.",
        context,
    )
    return _finish(recorder, result.final_output, [usage], trajectory_dir)


# Historical multi-agent experiments retained for reproducibility and changelog evidence.
def _run_contract(context: ReviewContext):
    result, usage = _run_agent(contract_agent(), "Reconstruct the change contract before evaluating release risk.", context)
    return result.final_output, usage


def _run_scout(contract: ChangeContract, context: ReviewContext):
    prompt = (
        "Investigate the repository using this change contract. Find concrete counterexamples beyond the diff.\n\n"
        + json.dumps(contract.model_dump(mode="json"), indent=2)
    )
    result, usage = _run_agent(impact_scout_agent(), prompt, context)
    return result.final_output, usage


def run_contract_experiment(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"contract-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    contract, contract_usage = _run_contract(context)
    impact, scout_usage = _run_scout(contract, context)
    prompt = "Turn these supported candidates into a concise release-risk report.\n\n" + json.dumps(impact.model_dump(mode="json"), indent=2)
    result, synth_usage = _run_agent(synthesizer_agent(), prompt, context)
    return _finish(recorder, result.final_output, [contract_usage, scout_usage, synth_usage], trajectory_dir)


def run_adversarial_experiment(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"adversarial-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    contract, contract_usage = _run_contract(context)
    impact, scout_usage = _run_scout(contract, context)
    prompt = (
        "Falsify these candidates first, then look for at most one independently testable missed regression.\n\n"
        + json.dumps(impact.model_dump(mode="json"), indent=2)
    )
    adversarial, adversary_usage = _run_agent(adversary_agent(), prompt, context)
    synth_prompt = "Turn these supported candidates into a concise release-risk report.\n\n" + json.dumps(adversarial.final_output.model_dump(mode="json"), indent=2)
    result, synth_usage = _run_agent(synthesizer_agent(), synth_prompt, context)
    return _finish(recorder, result.final_output, [contract_usage, scout_usage, adversary_usage, synth_usage], trajectory_dir)
