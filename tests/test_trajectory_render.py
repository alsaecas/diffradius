from diffradius.trajectory_render import render_trajectory_payload


def test_trajectory_markdown_includes_agent_and_tool_evidence():
    payload = {
        "run_id": "demo",
        "events": [
            {"at": "now", "kind": "agent_input", "agent": "Impact Scout", "data": {"input": "inspect"}},
            {"at": "now", "kind": "tool", "agent": "Impact Scout", "data": {"tool": "read_file", "args": {"path": "app/a.py"}, "output": "1: x"}},
        ],
    }
    out = render_trajectory_payload(payload)
    assert "Impact Scout" in out
    assert "read_file" in out
    assert "app/a.py" in out
    assert "private chain-of-thought" in out
