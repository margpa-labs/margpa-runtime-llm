"""Execute the repository-local JavaScript Markdown security contract."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
NODE_TEST = PROJECT_ROOT / "tests/unit/web/safe_markdown.test.mjs"


def test_safe_markdown_node_contract() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is unavailable for the static web security contract")

    completed = subprocess.run(
        [node, "--test", str(NODE_TEST)],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
