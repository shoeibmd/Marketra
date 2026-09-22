import subprocess
import sys

print("1. Running docker compose config...")
res_cfg = subprocess.run(["docker", "compose", "config"], capture_output=True, text=True)
print(res_cfg.stdout)
print(res_cfg.stderr)

print("2. Running backend pytest...")
res_pytest = subprocess.run(["uv", "run", "pytest"], cwd="backend", capture_output=True, text=True)
print(res_pytest.stdout)
print(res_pytest.stderr)

print("3. Running backend ruff...")
res_ruff = subprocess.run(["uv", "run", "ruff", "check", "."], cwd="backend", capture_output=True, text=True)
print(res_ruff.stdout)

print("4. Running backend mypy...")
res_mypy = subprocess.run(["uv", "run", "mypy", "app", "tests", "scripts"], cwd="backend", capture_output=True, text=True)
print(res_mypy.stdout)

print("5. Running frontend build & lint...")
res_build = subprocess.run(["pnpm", "build"], cwd="frontend", capture_output=True, text=True)
print(res_build.stdout)

if res_cfg.returncode != 0 or res_pytest.returncode != 0 or res_ruff.returncode != 0 or res_mypy.returncode != 0 or res_build.returncode != 0:
    sys.exit(1)
