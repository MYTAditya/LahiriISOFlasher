import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import subprocess
import time
from pathlib import Path

# Import our modules
from ui.main_window import MainWindow
from core.iso_handler import ISOHandler
from core.usb_handler import USBHandler
from core.flasher import ISOFlasher

def main():
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    # Create and run the application
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()