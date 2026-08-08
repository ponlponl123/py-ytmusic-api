#!/usr/bin/env python3
"""
Script to apply code quality tools (pylint, black, isort) to all Python source files.
Run from the project root: python scripts/apply_code_quality.py
"""

import subprocess
import sys
from pathlib import Path

# Always resolve paths relative to the project root (one level above this script)
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(command: str, description: str) -> None:
    """Run a shell command and print formatted results."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(PROJECT_ROOT),
            check=False,
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} completed with warnings/errors")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"Errors: {result.stderr.strip()}")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"❌ Error running {description}: {exc}")


def main() -> None:
    """Run all code quality tools over the src/ tree."""
    reconfig_stdout = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfig_stdout):
        reconfig_stdout(encoding="utf-8")
    reconfig_stderr = getattr(sys.stderr, "reconfigure", None)
    if callable(reconfig_stderr):
        reconfig_stderr(encoding="utf-8")

    python_exe = sys.executable

    # Source file patterns (relative to project root)
    source_patterns = [
        "src/main.py",
        "src/routers/*.py",
        "src/utils/*.py",
    ]

    print("🚀 Running code quality tools on YTMusic API project")
    print(f"\n📂 Project root: {PROJECT_ROOT}")

    # ─── Step 1: Format with Black ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎨 FORMATTING CODE WITH BLACK")
    print("=" * 60)

    for pattern in source_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m black "{file_path}" --line-length 100',
                    f"Formatting {file_path.relative_to(PROJECT_ROOT)}",
                )

    # ─── Step 2: Sort imports with isort ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("📚 SORTING IMPORTS WITH ISORT")
    print("=" * 60)

    for pattern in source_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m isort "{file_path}" --profile black',
                    f"Sorting imports in {file_path.relative_to(PROJECT_ROOT)}",
                )

    # ─── Step 3: Pylint analysis ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🔍 RUNNING PYLINT ANALYSIS")
    print("=" * 60)

    for pattern in source_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m pylint "{file_path}"',
                    f"Analysing {file_path.relative_to(PROJECT_ROOT)} with pylint",
                )

    # ─── Step 4: Final combined score ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🏁 FINAL QUALITY SCORE")
    print("=" * 60)

    all_files = []
    for pattern in source_patterns:
        all_files.extend(
            str(f)
            for f in PROJECT_ROOT.glob(pattern)
            if f.name != "__pycache__"
        )

    if all_files:
        files_str = " ".join(f'"{f}"' for f in all_files)
        run_command(
            f"{python_exe} -m pylint {files_str}",
            "Final pylint score for all source files",
        )

    total_files = len(all_files)
    print(f"\n✅ Processed {total_files} Python source files")
    print("\n🎯 Code quality improvements applied:")
    print("   • Consistent formatting with Black")
    print("   • Sorted imports with isort")
    print("   • Code analysis with pylint")


if __name__ == "__main__":
    main()
