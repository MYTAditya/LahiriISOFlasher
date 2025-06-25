import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller command with icon and version info
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=LahiriISOFlasher",
        "--add-data=ui;ui",
        "--add-data=core;core",
	"--add-data=icon;icon",
	"--add-data=icon.ico;.",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=psutil",
        "--hidden-import=win32api",
        "--hidden-import=win32file",
        "main.py"
    ]
    
    # Add icon if it exists
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
        print("Using custom icon for executable")
    else:
        print("No icon file found, building without icon")
    
    # Add version info if it exists
    if os.path.exists("ver_info.txt"):
        cmd.insert(-1, "--version-file=ver_info.txt")
        print("Using version info file")
    else:
        print("No version info file found, building without version info")
    
    print("Building executable...")
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print("Executable created in 'dist' folder")
                
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()
