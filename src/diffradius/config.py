from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("DIFFRADIUS_MODEL", "gpt-5.6-luna")
    max_turns: int = int(os.getenv("DIFFRADIUS_MAX_TURNS", "12"))
    max_file_chars: int = int(os.getenv("DIFFRADIUS_MAX_FILE_CHARS", "24000"))
    max_search_results: int = int(os.getenv("DIFFRADIUS_MAX_SEARCH_RESULTS", "60"))


def settings() -> Settings:
    return Settings()
