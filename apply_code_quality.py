#!/usr/bin/env python3
"""
Script to apply code quality tools (pylint, black, isort) to all Python files in the project
"""
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and report results"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} completed with warnings/errors")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"Errors: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Error running {description}: {e}")


def main():
    """Main function to run all code quality tools"""
    print("🚀 Running code quality tools on YTMusic API project")
    
    # Get Python executable path
    python_exe = "D:/github/py-ytmusic-api/venv/Scripts/python.exe"
    
    # Define file patterns to check
    python_files = [
        "src/main.py",
        "src/routers/*.py",
        "src/utils/*.py"
    ]
    
    print(f"\n📂 Working directory: {Path.cwd()}")
    
    # Step 1: Format code with black
    print("\n" + "="*60)
    print("🎨 FORMATTING CODE WITH BLACK")
    print("="*60)
    
    for pattern in python_files:
        files = list(Path(".").glob(pattern))
        for file_path in files:
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m black "{file_path}" --line-length 100',
                    f"Formatting {file_path}"
                )
    
    # Step 2: Sort imports with isort
    print("\n" + "="*60)
    print("📚 SORTING IMPORTS WITH ISORT")
    print("="*60)
    
    for pattern in python_files:
        files = list(Path(".").glob(pattern))
        for file_path in files:
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m isort "{file_path}" --profile black',
                    f"Sorting imports in {file_path}"
                )
    
    # Step 3: Run pylint analysis
    print("\n" + "="*60)
    print("🔍 RUNNING PYLINT ANALYSIS")
    print("="*60)
    
    for pattern in python_files:
        files = list(Path(".").glob(pattern))
        for file_path in files:
            if file_path.name != "__pycache__":
                run_command(
                    f'{python_exe} -m pylint "{file_path}" --rcfile=.pylintrc',
                    f"Analyzing {file_path} with pylint"
                )
    
    # Step 4: Generate summary report
    print("\n" + "="*60)
    print("📊 GENERATING SUMMARY REPORT")
    print("="*60)
    
    # Count Python files
    total_files = 0
    for pattern in python_files:
        files = list(Path(".").glob(pattern))
        total_files += len([f for f in files if f.name != "__pycache__"])
    
    print(f"✅ Processed {total_files} Python files")
    print("\n🎯 Code quality improvements applied:")
    print("   • Consistent formatting with Black")
    print("   • Sorted imports with isort")
    print("   • Code analysis with pylint")
    
    print("\n📝 Next steps:")
    print("   • Review pylint warnings and fix any critical issues")
    print("   • Consider adding pre-commit hooks for automatic formatting")
    print("   • Add these tools to your CI/CD pipeline")
    
    # Optional: Run a final pylint check on all files
    print("\n" + "="*60)
    print("🏁 FINAL QUALITY SCORE")
    print("="*60)
    
    all_python_files = []
    for pattern in python_files:
        files = list(Path(".").glob(pattern))
        all_python_files.extend([str(f) for f in files if f.name != "__pycache__"])
    
    if all_python_files:
        files_str = " ".join(f'"{f}"' for f in all_python_files)
        run_command(
            f'{python_exe} -m pylint {files_str} --rcfile=.pylintrc',
            "Final pylint score for all files"
        )


if __name__ == "__main__":
    main()