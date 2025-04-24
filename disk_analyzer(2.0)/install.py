# =======================
# Import important modules.
# =======================
import subprocess
import sys
import os

# =======================
# Auto-install required libraries from requirements.txt if they're not already installed.
# =======================
def install_requirements():
    try:
        # Try import necessary packages
        import psutil
        import matplotlib.pyplot as plt
    except ImportError:
        # If any import fails -> install from requirements.txt
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        except subprocess.CalledProcessError as e:
            print("Error installing packages:", e)
            sys.exit(1)

install_requirements()  # Run the installation as soon as this module is imported
