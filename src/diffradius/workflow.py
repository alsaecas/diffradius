from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from agents import RunConfig, Runner, set_tracing_disabled

from .agents import adversary_agent, baseline_agent, impact_scout_agent, verifier_agent
from .config import settings
from .models import AdversarialReview, ImpactMap, ReviewReport, RunUsage, WorkflowResult
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
    serializable = output.model_dump() if hasattr(output, "model_dump") else str(output)
    context.trajectory.add("agent_output", agent.name, output=serializable)
    return result, elapsed


def run_baseline(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"baseline-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)
    prompt = (
        "Review this change for release risk. Read the ticket and diff first, then inspect any "
        "repository code needed to verify concrete regressions."
    )
    result, elapsed = _run_agent(baseline_agent(), prompt, context)
    report: ReviewReport = result.final_output
    path = recorder.save(trajectory_dir) if trajectory_dir else None
    return WorkflowResult(report=report, usage=_usage(result, elapsed), trajectory_path=str(path) if path else None)


def run_final(view: RepositoryView, trajectory_dir: Path | None = None) -> WorkflowResult:
    recorder = TrajectoryRecorder(f"final-{uuid.uuid4().hex[:12]}")
    context = ReviewContext(view, recorder)

    scout_result, scout_elapsed = _run_agent(
        impact_scout_agent(),
        "Build an impact map for the supplied ticket and diff. Trace behavior beyond changed lines.",
        context,
    )
    impact: ImpactMap = scout_result.final_output

    adversary_prompt = (
        "Here is the Impact Scout output. Attack it and inspect the repository for missed or weak "
        "failure modes.\n\n" + json.dumps(impact.model_dump(mode="json"), indent=2)
    )
    adversary_result, adversary_elapsed = _run_agent(adversary_agent(), adversary_prompt, context)
    adversarial: AdversarialReview = adversary_result.final_output

    verifier_prompt = (
        "Independently verify these candidate risks. Keep only concrete regressions caused by the "
        "diff. Reject unsupported claims.\n\n"
        + json.dumps(adversarial.model_dump(mode="json"), indent=2)
    )
    verifier_result, verifier_elapsed = _run_agent(verifier_agent(), verifier_prompt, context)
    report: ReviewReport = verifier_result.final_output

    usage = RunUsage(
        requests=(scout_result.context_wrapper.usage.requests + adversary_result.context_wrapper.usage.requests + verifier_result.context_wrapper.usage.requests),
        input_tokens=(scout_result.context_wrapper.usage.input_tokens + adversary_result.context_wrapper.usage.input_tokens + verifier_result.context_wrapper.usage.input_tokens),
        output_tokens=(scout_result.context_wrapper.usage.output_tokens + adversary_result.context_wrapper.usage.output_tokens + verifier_result.context_wrapper.usage.output_tokens),
        total_tokens=(scout_result.context_wrapper.usage.total_tokens + adversary_result.context_wrapper.usage.total_tokens + verifier_result.context_wrapper.usage.total_tokens),
        elapsed_seconds=scout_elapsed + adversary_elapsed + verifier_elapsed,
    )
    path = recorder.save(trajectory_dir) if trajectory_dir else None
    return WorkflowResult(report=report, usage=usage, trajectory_path=str(path) if path else None)
