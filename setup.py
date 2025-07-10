import os
import subprocess
import sys

venv_dir = ".venv"

# Create virtual environment if it doesn't exist
if not os.path.isdir(venv_dir):
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    print(f"Created virtual environment in {venv_dir}")
else:
    print(f"Virtual environment already exists in {venv_dir}")

# Path to pip inside the venv
pip_path = os.path.join(venv_dir, "bin", "pip")

# Upgrade pip
subprocess.check_call([pip_path, "install", "--upgrade", "pip"])

# Install requirements
if os.path.isfile("requirements.txt"):
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
    print("Dependencies installed from requirements.txt.")
else:
    print("requirements.txt not found. Skipping dependency installation.")

print(f"Setup complete. To activate the environment, run: source {venv_dir}/bin/activate")
