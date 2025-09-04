from __future__ import annotations

from typing import NoReturn


def fail(code: str, impact: str, steps: list[str]) -> NoReturn:
    msg = f"[{code}] {impact}\n" + "\n".join(f"- {s}" for s in steps)
    raise SystemExit(msg)

