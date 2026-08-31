from __future__ import annotations

import py_compile
from pathlib import Path


def test_agent_examples_compile() -> None:
    root = Path(__file__).resolve().parents[3]
    examples = sorted((root / "examples" / "python" / "agent_runtime").glob("*.py"))
    assert len(examples) == 6
    for example in examples:
        py_compile.compile(str(example), doraise=True)
