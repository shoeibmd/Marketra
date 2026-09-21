import subprocess
import sys

res = subprocess.run(["uv", "run", "pytest"], cwd="backend", capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
sys.exit(res.returncode)
