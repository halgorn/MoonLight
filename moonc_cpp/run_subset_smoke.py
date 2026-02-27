#!/usr/bin/env python3
"""
Smoke test: run moonc (C++ binary) on subset examples (parse-only with -c).
Expects moonc in build/moonc (Unix) or build/Release/moonc.exe / build/Debug/moonc.exe (Windows),
or in PATH.
"""
import os
import subprocess
import sys

# Subset examples (relative to repo root)
SUBSET_EXAMPLES = [
    "examples/basic/hello_world.gpu",
    "examples/basic/variables.gpu",
    "examples/cuda/vector_add.gpu",
]

def find_moonc(repo_root):
    """Return path to moonc binary or None."""
    candidates = [
        os.path.join(repo_root, "build", "moonc"),
        os.path.join(repo_root, "build", "Release", "moonc.exe"),
        os.path.join(repo_root, "build", "Debug", "moonc.exe"),
        os.path.join(repo_root, "moonc_cpp", "build", "moonc"),
        os.path.join(repo_root, "moonc_cpp", "build", "Release", "moonc.exe"),
        os.path.join(repo_root, "moonc_cpp", "build", "Debug", "moonc.exe"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    # Try PATH
    if sys.platform == "win32":
        for name in ("moonc.exe", "moonc"):
            try:
                subprocess.run([name, "--help"], capture_output=True, check=False)
                return name
            except FileNotFoundError:
                pass
    else:
        try:
            subprocess.run(["moonc", "--help"], capture_output=True, check=False)
            return "moonc"
        except FileNotFoundError:
            pass
    return None

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    moonc = find_moonc(repo_root)
    if not moonc:
        print("moonc binary not found. Build with: mkdir build && cd build && cmake .. && cmake --build .")
        sys.exit(1)

    failed = []
    for rel in SUBSET_EXAMPLES:
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            print(f"SKIP (missing): {rel}")
            continue
        try:
            r = subprocess.run([moonc, "-c", path], capture_output=True, text=True, cwd=repo_root, timeout=10)
            if r.returncode == 0:
                print(f"OK: {rel}")
            else:
                print(f"FAIL: {rel}")
                if r.stderr:
                    print(r.stderr[:500])
                failed.append(rel)
        except Exception as e:
            print(f"ERROR: {rel} - {e}")
            failed.append(rel)

    if failed:
        sys.exit(1)
    print("All subset examples passed (parse-only).")

if __name__ == "__main__":
    main()
