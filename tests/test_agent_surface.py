def test_agent_surface_constructs_with_pinned_sdk():
    from diffradius.agents import prompt_baseline_agent, proof_reviewer_agent, tool_reviewer_agent
    from diffradius.tools import CHANGE_AWARE_TOOLS, READ_ONLY_TOOLS

    assert len(READ_ONLY_TOOLS) == 5
    assert len(CHANGE_AWARE_TOOLS) == 6
    assert prompt_baseline_agent().name == "Direct Prompt Baseline"
    assert tool_reviewer_agent().name == "General Tool Reviewer"
    assert proof_reviewer_agent().name == "DiffRadius Evidence Investigator"
    assert len(prompt_baseline_agent().tools) == 0
