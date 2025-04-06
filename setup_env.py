import os
import subprocess
import sys

# Check for Python 3.12
REQUIRED_VERSION = (3, 12)

if sys.version_info < REQUIRED_VERSION:
    print(f"❌ Python 3.12 or higher is required. You are using Python {sys.version.split()[0]}")
    sys.exit(1)

VENV_DIR = "venv"

def create_virtual_env():
    print("📦 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR])

def install_dependencies():
    print("📥 Installing allowed libraries (pandas, numpy)...")
    pip_path = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "pip")
    
    # Install pip first without printing anything
    subprocess.run([pip_path, "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Install dependencies silently and capture the result
    result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # If the return code is non-zero, it means there was an error
    if result.returncode != 0:
        print("❌ Error installing libraries.")
        print(result.stderr.decode())  # Print the error details
        sys.exit(1)  # Exit the script if there's an error
    
    print("✅ Libraries installed successfully.")

def print_activation_instructions():
    print("\n✅ Setup complete!")
    print("👉 To activate your virtual environment:")

    if os.name == "nt":
        print(r"   venv\Scripts\activate")
    else:
        print("   source venv/bin/activate")

def main():
    if not os.path.exists(VENV_DIR):
        create_virtual_env()
    else:
        print("✅ Virtual environment already exists.")
    
    install_dependencies()
    print_activation_instructions()

if __name__ == "__main__":
    main()
