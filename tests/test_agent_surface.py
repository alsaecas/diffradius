def test_agent_surface_constructs_with_pinned_sdk():
    from diffradius.agents import (
        adversary_agent,
        baseline_agent,
        impact_scout_agent,
        verifier_agent,
    )
    from diffradius.tools import READ_ONLY_TOOLS

    assert len(READ_ONLY_TOOLS) == 5
    assert baseline_agent().name == "Baseline Reviewer"
    assert impact_scout_agent().name == "Impact Scout"
    assert adversary_agent().name == "Adversarial Reviewer"
    assert verifier_agent().name == "Evidence Verifier"
