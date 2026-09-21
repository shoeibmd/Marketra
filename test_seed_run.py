import subprocess
import sys

res = subprocess.run(["uv", "run", "python", "scripts/seed_mock_data.py"], cwd="backend", capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
sys.exit(res.returncode)
