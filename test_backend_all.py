import subprocess
import sys

print("1. Running pytest...")
res_pytest = subprocess.run(["uv", "run", "pytest"], cwd="backend", capture_output=True, text=True)
print(res_pytest.stdout)
print(res_pytest.stderr)

print("2. Running ruff check...")
res_ruff = subprocess.run(["uv", "run", "ruff", "check", "."], cwd="backend", capture_output=True, text=True)
print(res_ruff.stdout)
print(res_ruff.stderr)

print("3. Running mypy...")
res_mypy = subprocess.run(["uv", "run", "mypy", "app", "tests", "scripts"], cwd="backend", capture_output=True, text=True)
print(res_mypy.stdout)
print(res_mypy.stderr)

print("4. Testing seed script with SQLite in-memory/file...")
res_seed = subprocess.run(["uv", "run", "python", "scripts/seed_mock_data.py"], cwd="backend", capture_output=True, text=True)
print(res_seed.stdout)
print(res_seed.stderr)

if res_pytest.returncode != 0 or res_ruff.returncode != 0 or res_mypy.returncode != 0 or res_seed.returncode != 0:
    sys.exit(1)
