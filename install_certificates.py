#!/usr/bin/env python3
"""
This script installs the SSL certificates for Python on macOS.
Run this script with: python install_certificates.py
"""

import os
import sys
import subprocess
import platform

def main():
    # Only run on macOS
    if platform.system() != 'Darwin':
        print("This script is only for macOS systems.")
        sys.exit(1)
    
    print("Installing SSL certificates for Python on macOS...")
    
    # Get path to the certifi package
    try:
        import certifi
        print(f"Found certifi package at: {certifi.where()}")
    except ImportError:
        print("Installing certifi package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "certifi"])
        import certifi
    
    # Run the certificate installation command
    cmd = [
        "/Applications/Python 3.11/Install Certificates.command"
    ]
    
    if not os.path.exists(cmd[0]):
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"Certificate installation command not found at default location.")
        print(f"Please install certificates manually by running:")
        print(f"/Applications/Python {python_version}/Install Certificates.command")
        print("")
        print("Alternatively, keep using the SSL verification bypass in main.py")
        return
    
    print(f"Running: {cmd[0]}")
    subprocess.run(cmd)
    print("Certificates installation complete.")
    print("You can now comment out the SSL workaround in main.py if desired.")

if __name__ == "__main__":
    main() 