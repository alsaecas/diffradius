def test_agent_surface_constructs_with_pinned_sdk():
    from diffradius.agents import (
        adversary_agent,
        baseline_agent,
        contract_agent,
        impact_scout_agent,
        verifier_agent,
    )
    from diffradius.tools import CHANGE_AWARE_TOOLS, READ_ONLY_TOOLS

    assert len(READ_ONLY_TOOLS) == 5
    assert len(CHANGE_AWARE_TOOLS) == 6
    assert baseline_agent().name == "Baseline Reviewer"
    assert contract_agent().name == "Change Contract Analyst"
    assert impact_scout_agent().name == "Impact Investigator"
    assert adversary_agent().name == "Adversarial Reviewer"
    assert verifier_agent().name == "Counterexample Verifier"
