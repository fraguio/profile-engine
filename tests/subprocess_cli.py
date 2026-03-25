from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


def run_profilecli_subprocess(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"

    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{current_pythonpath}"
        if current_pythonpath
        else str(src_path)
    )

    return subprocess.run(
        [sys.executable, "-m", "profilecli", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
