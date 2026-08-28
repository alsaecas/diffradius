from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TrajectoryEvent:
    at: str
    kind: str
    agent: str
    data: dict[str, Any]


@dataclass
class TrajectoryRecorder:
    run_id: str
    events: list[TrajectoryEvent] = field(default_factory=list)

    def add(self, kind: str, agent: str, **data: Any) -> None:
        self.events.append(TrajectoryEvent(_utc_now(), kind, agent, data))

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.run_id}.json"
        payload = {
            "run_id": self.run_id,
            "events": [asdict(event) for event in self.events],
        }
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path
