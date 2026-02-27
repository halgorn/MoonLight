#!/usr/bin/env python3
"""
CI benchmark subset: run a few fast benchmarks to detect regressions.
Exits 0 if all complete successfully, 1 otherwise.
Run from repository root: python benchmarks/ci_benchmarks.py
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_moonlight_script(rel_path):
    """Run a .gpu file with executor_main.py; return True if exit 0."""
    path = REPO_ROOT / rel_path
    if not path.exists():
        print(f"SKIP (missing): {rel_path}")
        return True
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "executor_main.py"), str(path)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO_ROOT),
    )
    if r.returncode != 0:
        print(f"FAIL: {rel_path}")
        if r.stderr:
            print(r.stderr[:500])
        return False
    print(f"OK: {rel_path}")
    return True

def main():
    # Subset rápido: exemplos que devem executar em poucos segundos
    subset = [
        "examples/basic/hello_world.gpu",
        "examples/basic/variables.gpu",
    ]
    ok = all(run_moonlight_script(p) for p in subset)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
