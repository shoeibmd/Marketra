import subprocess
import sys

print("1. Running backend pytest...")
res_pytest = subprocess.run(["uv", "run", "pytest"], cwd="backend", capture_output=True, text=True)
print(res_pytest.stdout)
print(res_pytest.stderr)

print("2. Running backend ruff check...")
res_ruff = subprocess.run(["uv", "run", "ruff", "check", "."], cwd="backend", capture_output=True, text=True)
print(res_ruff.stdout)
print(res_ruff.stderr)

print("3. Running backend mypy...")
res_mypy = subprocess.run(["uv", "run", "mypy", "app", "tests", "scripts"], cwd="backend", capture_output=True, text=True)
print(res_mypy.stdout)
print(res_mypy.stderr)

print("4. Running frontend build...")
res_build = subprocess.run(["pnpm", "build"], cwd="frontend", capture_output=True, text=True)
print(res_build.stdout)
print(res_build.stderr)

print("5. Running frontend lint...")
res_lint = subprocess.run(["pnpm", "lint"], cwd="frontend", capture_output=True, text=True)
print(res_lint.stdout)
print(res_lint.stderr)

if (
    res_pytest.returncode != 0
    or res_ruff.returncode != 0
    or res_mypy.returncode != 0
    or res_build.returncode != 0
    or res_lint.returncode != 0
):
    sys.exit(1)
