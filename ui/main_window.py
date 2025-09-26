import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import tempfile
import shutil
import sys
from pathlib import Path
from PIL import Image

from core.iso_handler import ISOHandler
from core.usb_handler import USBHandler
from core.flasher import ISOFlasher

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Lahiri ISO Flasher")
        self.geometry("800x750")
        self.resizable(False, False)
        self.wm_iconbitmap("ui/icon.ico")
        
        # Set custom colors
        self.primary_color = "#a9e43a"
        self.bg_color = "#1a1a1a"
        self.card_color = "#2b2b2b"
        self.disabled_color = "#404040"
        
        # Initialize handlers
        self.iso_handler = ISOHandler()
        self.usb_handler = USBHandler()
        self.flasher = ISOFlasher()
        
        # Application state
        self.selected_drive = None
        self.selected_iso = None
        self.volume_name = ""
        self.partition_scheme = "MBR"
        self.target_system = "BIOS or UEFI"
        self.file_system = "FAT32"
        self.original_drive_letter = None  # Store original drive letter
        
        # Layer completion status
        self.layer_completed = {
            1: False,  # Drive selection
            2: False,  # ISO selection
            3: False,  # Configuration
            4: False   # Flash
        }
        
        self.setup_ui()
        self.refresh_drives()
        self.update_layer_states()
        
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
        
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with icon and title
        self.setup_header()
        
        # Layer 1: Drive Selection
        self.setup_drive_selection()
        
        # Layer 2: ISO Selection
        self.setup_iso_selection()
        
        # Layer 3: Configuration
        self.setup_configuration()
        
        # Layer 4: Flash Button
        self.setup_flash_section()
        
        # Progress section
        self.setup_progress_section()
        
    def setup_header(self):
        # Header frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Try to load and display the icon
        try:
            # Get the correct path for the icon
            icon_path = self.get_resource_path("ui/icon.png")
            
            # Load and resize the icon
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((48, 48), Image.Resampling.LANCZOS)
            self.icon_photo = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(48, 48))
                
            # Icon label
            icon_label = ctk.CTkLabel(
                header_frame,
                image=self.icon_photo,
                text=""
                )
            icon_label.pack(side="left", padx=(0, 15))

        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Lahiri ISO Flasher",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(side="left")
        
    def setup_drive_selection(self):
        # Drive selection frame
        self.drive_frame = ctk.CTkFrame(self.main_frame, fg_color=self.card_color)
        self.drive_frame.pack(fill="x", pady=(0, 15))
        
        # Title with status indicator
        title_container = ctk.CTkFrame(self.drive_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=20, pady=(15, 10))
        
        self.drive_title = ctk.CTkLabel(
            title_container,
            text="1. Select USB Drive",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.primary_color
        )
        self.drive_title.pack(side="left")
        
        self.drive_status = ctk.CTkLabel(
            title_container,
            text="⚪ Incomplete",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.drive_status.pack(side="right")
        
        # Drive selection container
        drive_container = ctk.CTkFrame(self.drive_frame, fg_color="transparent")
        drive_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Drive dropdown
        self.drive_var = ctk.StringVar(value="Select a USB drive...")
        self.drive_dropdown = ctk.CTkComboBox(
            drive_container,
            variable=self.drive_var,
            values=["No drives found"],
            width=400,
            command=self.on_drive_selected
        )
        self.drive_dropdown.pack(side="left", padx=(0, 10))
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            drive_container,
            text="Refresh",
            width=100,
            command=self.refresh_drives,
            fg_color=self.primary_color,
            text_color="black"
        )
        self.refresh_btn.pack(side="left")
        
    def setup_iso_selection(self):
        # ISO selection frame
        self.iso_frame = ctk.CTkFrame(self.main_frame, fg_color=self.disabled_color)
        self.iso_frame.pack(fill="x", pady=(0, 15))
        
        # Title with status indicator
        title_container = ctk.CTkFrame(self.iso_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=20, pady=(15, 10))
        
        self.iso_title = ctk.CTkLabel(
            title_container,
            text="2. Select ISO File",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="gray"
        )
        self.iso_title.pack(side="left")
        
        self.iso_status = ctk.CTkLabel(
            title_container,
            text="⚪ Incomplete",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.iso_status.pack(side="right")
        
        # ISO selection container
        iso_container = ctk.CTkFrame(self.iso_frame, fg_color="transparent")
        iso_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # ISO path display
        self.iso_path_var = ctk.StringVar(value="No ISO file selected")
        self.iso_path_label = ctk.CTkLabel(
            iso_container,
            textvariable=self.iso_path_var,
            width=400,
            anchor="w",
            text_color="gray"
        )
        self.iso_path_label.pack(side="left", padx=(0, 10))
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            iso_container,
            text="Browse",
            width=100,
            command=self.browse_iso,
            fg_color="gray",
            text_color="white",
            state="disabled"
        )
        self.browse_btn.pack(side="left")
        
    def setup_configuration(self):
        # Configuration frame
        self.config_frame = ctk.CTkFrame(self.main_frame, fg_color=self.disabled_color)
        self.config_frame.pack(fill="x", pady=(0, 15))
        
        # Title with status indicator
        title_container = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=20, pady=(15, 10))
        
        self.config_title = ctk.CTkLabel(
            title_container,
            text="3. Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="gray"
        )
        self.config_title.pack(side="left")
        
        self.config_status = ctk.CTkLabel(
            title_container,
            text="⚪ Incomplete",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.config_status.pack(side="right")
        
        # Configuration container
        config_container = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        config_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Left column
        left_column = ctk.CTkFrame(config_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Volume name
        self.volume_label = ctk.CTkLabel(left_column, text="Volume Name (max 11 chars):", text_color="gray")
        self.volume_label.pack(anchor="w", pady=(0, 5))
        
        self.volume_var = ctk.StringVar()
        self.volume_var.trace("w", self.on_volume_change)
        self.volume_entry = ctk.CTkEntry(
            left_column, 
            textvariable=self.volume_var, 
            width=200,
            state="disabled"
        )
        self.volume_entry.pack(anchor="w", pady=(0, 15))
        
        # Partition scheme
        self.partition_label = ctk.CTkLabel(left_column, text="Partition Scheme:", text_color="gray")
        self.partition_label.pack(anchor="w", pady=(0, 5))
        
        self.partition_var = ctk.StringVar(value="MBR")
        self.partition_var.trace("w", self.on_config_change)
        self.partition_dropdown = ctk.CTkComboBox(
            left_column,
            variable=self.partition_var,
            values=["MBR", "GPT"],
            width=200,
            state="disabled"
        )
        self.partition_dropdown.pack(anchor="w")
        
        # Right column
        right_column = ctk.CTkFrame(config_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Target system
        self.target_label = ctk.CTkLabel(right_column, text="Target System:", text_color="gray")
        self.target_label.pack(anchor="w", pady=(0, 5))
        
        self.target_var = ctk.StringVar(value="BIOS or UEFI")
        self.target_var.trace("w", self.on_config_change)
        self.target_dropdown = ctk.CTkComboBox(
            right_column,
            variable=self.target_var,
            values=["BIOS or UEFI", "UEFI", "BIOS (Legacy)"],
            width=200,
            state="disabled"
        )
        self.target_dropdown.pack(anchor="w", pady=(0, 15))

        # File system
        self.system_label = ctk.CTkLabel(right_column, text="File System:", text_color="gray")
        self.system_label.pack(anchor="w", pady=(0, 5))
        
        self.system_var = ctk.StringVar(value="FAT32")
        self.system_var.trace("w", self.on_config_change)
        self.system_dropdown = ctk.CTkComboBox(
            right_column,
            variable=self.system_var,
            values=["FAT32", "NTFS"],
            width=200,
            state="disabled"
        )
        self.system_dropdown.pack(anchor="w")
        
    def setup_flash_section(self):
        # Flash section frame
        self.flash_frame = ctk.CTkFrame(self.main_frame, fg_color=self.disabled_color)
        self.flash_frame.pack(fill="x", pady=(0, 15))
        
        # Title with status indicator
        title_container = ctk.CTkFrame(self.flash_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=20, pady=(15, 10))
        
        self.flash_title = ctk.CTkLabel(
            title_container,
            text="4. Flash ISO",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="gray"
        )
        self.flash_title.pack(side="left")
        
        self.flash_status = ctk.CTkLabel(
            title_container,
            text="⚪ Ready",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.flash_status.pack(side="right")
        
        # Flash button container
        flash_container = ctk.CTkFrame(self.flash_frame, fg_color="transparent")
        flash_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Flash button
        self.flash_btn = ctk.CTkButton(
            flash_container,
            text="FLASH",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_flash,
            fg_color="gray",
            text_color="white",
            state="disabled"
        )
        self.flash_btn.pack(pady=(0, 10))
        
        # Percentage indicator
        self.percentage_var = ctk.StringVar(value="0%")
        self.percentage_label = ctk.CTkLabel(
            flash_container,
            textvariable=self.percentage_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.primary_color
        )
        self.percentage_label.pack()
        
    def setup_progress_section(self):
        # Progress frame (initially hidden)
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color=self.card_color)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(pady=15)
        self.progress_bar.set(0)
        
        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=(0, 15))
        
    def update_layer_states(self):
        """Update the visual state of all layers based on completion status"""
        
        # Layer 1 - Always enabled
        self.drive_frame.configure(fg_color=self.card_color)
        self.drive_title.configure(text_color=self.primary_color)
        self.drive_status.configure(
            text="✅ Complete" if self.layer_completed[1] else "⚪ Incomplete",
            text_color=self.primary_color if self.layer_completed[1] else "gray"
        )
        
        # Layer 2 - Enabled if Layer 1 is complete
        if self.layer_completed[1]:
            self.iso_frame.configure(fg_color=self.card_color)
            self.iso_title.configure(text_color=self.primary_color)
            self.iso_path_label.configure(text_color="white")
            self.browse_btn.configure(
                state="normal",
                fg_color=self.primary_color,
                text_color="black"
            )
        else:
            self.iso_frame.configure(fg_color=self.disabled_color)
            self.iso_title.configure(text_color="gray")
            self.iso_path_label.configure(text_color="gray")
            self.browse_btn.configure(
                state="disabled",
                fg_color="gray",
                text_color="white"
            )
            
        self.iso_status.configure(
            text="✅ Complete" if self.layer_completed[2] else "⚪ Incomplete",
            text_color=self.primary_color if self.layer_completed[2] else "gray"
        )
        
        # Layer 3 - Enabled if Layer 2 is complete
        if self.layer_completed[2]:
            self.config_frame.configure(fg_color=self.card_color)
            self.config_title.configure(text_color=self.primary_color)
            self.volume_label.configure(text_color="white")
            self.partition_label.configure(text_color="white")
            self.target_label.configure(text_color="white")
            self.system_label.configure(text_color="white")
            self.volume_entry.configure(state="normal")
            self.partition_dropdown.configure(state="normal")
            self.target_dropdown.configure(state="normal")
            self.system_dropdown.configure(state="normal")
        else:
            self.config_frame.configure(fg_color=self.disabled_color)
            self.config_title.configure(text_color="gray")
            self.volume_label.configure(text_color="gray")
            self.partition_label.configure(text_color="gray")
            self.target_label.configure(text_color="gray")
            self.system_label.configure(text_color="gray")
            self.volume_entry.configure(state="disabled")
            self.partition_dropdown.configure(state="disabled")
            self.target_dropdown.configure(state="disabled")
            self.system_dropdown.configure(state="disabled")
            
        self.config_status.configure(
            text="✅ Complete" if self.layer_completed[3] else "⚪ Incomplete",
            text_color=self.primary_color if self.layer_completed[3] else "gray"
        )
        
        # Layer 4 - Enabled if Layer 3 is complete
        if self.layer_completed[3]:
            self.flash_frame.configure(fg_color=self.card_color)
            self.flash_title.configure(text_color=self.primary_color)
            self.flash_btn.configure(
                state="normal",
                fg_color=self.primary_color,
                text_color="black"
            )
            self.flash_status.configure(
                text="🚀 Ready to Flash",
                text_color=self.primary_color
            )
        else:
            self.flash_frame.configure(fg_color=self.disabled_color)
            self.flash_title.configure(text_color="gray")
            self.flash_btn.configure(
                state="disabled",
                fg_color="gray",
                text_color="white"
            )
            self.flash_status.configure(
                text="⚪ Ready",
                text_color="gray"
            )
        
    def refresh_drives(self):
        """Refresh the list of available USB drives"""
        drives = self.usb_handler.get_usb_drives()
        if drives:
            drive_list = [f"{drive['letter']} - {drive['label']} ({drive['size']})" for drive in drives]
            self.drive_dropdown.configure(values=drive_list)
            self.drive_var.set("Select a USB drive...")
        else:
            self.drive_dropdown.configure(values=["No USB drives found"])
            self.drive_var.set("No USB drives found")
            
    def on_drive_selected(self, selection):
        """Handle drive selection"""
        if selection and "No" not in selection and "Select" not in selection:
            drive_letter = selection.split(" - ")[0]
            self.selected_drive = drive_letter
            self.original_drive_letter = drive_letter  # Store original drive letter
            self.layer_completed[1] = True
        else:
            self.selected_drive = None
            self.original_drive_letter = None
            self.layer_completed[1] = False
            
        # Reset subsequent layers if drive changes
        if not self.layer_completed[1]:
            self.layer_completed[2] = False
            self.layer_completed[3] = False
            self.layer_completed[4] = False
            
        self.update_layer_states()
            
    def browse_iso(self):
        """Browse for ISO file"""
        if not self.layer_completed[1]:
            return
            
        file_path = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        
        if file_path:
            # Validate ISO file
            if self.iso_handler.validate_iso(file_path):
                self.selected_iso = file_path
                filename = os.path.basename(file_path)
                self.iso_path_var.set(filename)
                self.layer_completed[2] = True
                
                # Don't auto-set volume name from ISO anymore
                # User must manually enter volume name
                
                # Check if ISO is bootable
                if not self.iso_handler.is_bootable(file_path):
                    messagebox.showwarning(
                        "Warning",
                        "The selected ISO file may not be bootable. "
                        "The flashing process will continue, but the USB drive may not boot properly."
                    )
            else:
                messagebox.showerror("Error", "Invalid ISO file selected.")
                self.selected_iso = None
                self.layer_completed[2] = False
        else:
            self.selected_iso = None
            self.layer_completed[2] = False
            
        # Reset subsequent layers if ISO changes
        if not self.layer_completed[2]:
            self.layer_completed[3] = False
            self.layer_completed[4] = False
            
        self.update_layer_states()
        
    def on_volume_change(self, *args):
        """Handle volume name changes with character limit"""
        current_value = self.volume_var.get()
        
        # Limit to 11 characters
        if len(current_value) > 11:
            self.volume_var.set(current_value[:11])
            
        self.on_config_change()
        
    def on_config_change(self, *args):
        """Handle configuration changes"""
        if not self.layer_completed[2]:
            return
            
        # Check if volume name is provided
        if self.volume_var.get().strip():
            self.layer_completed[3] = True
        else:
            self.layer_completed[3] = False
            
        # Reset flash layer if config changes
        if not self.layer_completed[3]:
            self.layer_completed[4] = False
            
        self.update_layer_states()
        
    def start_flash(self):
        """Start the flashing process"""
        if not self.layer_completed[3]:
            return
            
        # Validate inputs one more time
        if not self.selected_drive:
            messagebox.showerror("Error", "Please select a USB drive.")
            return
            
        if not self.selected_iso:
            messagebox.showerror("Error", "Please select an ISO file.")
            return
            
        if not self.volume_var.get().strip():
            messagebox.showerror("Error", "Please enter a volume name.")
            return
            
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Flash",
            f"This will erase all data on drive {self.selected_drive}.\n"
            f"ISO: {os.path.basename(self.selected_iso)}\n"
            f"Volume: {self.volume_var.get()}\n"
            f"Partition: {self.partition_var.get()}\n"
            f"Target: {self.target_var.get()}\n"
            f"File system: {self.system_var.get()}\n\n"
            "Are you sure you want to continue?"
        )
        
        if result:
            # Show progress frame
            self.progress_frame.pack(fill="x", pady=(0, 15))
            
            # Update flash status
            self.flash_status.configure(
                text="🔄 Flashing...",
                text_color="orange"
            )
            
            # Disable flash button
            self.flash_btn.configure(state="disabled", text="FLASHING...")
            
            # Reset percentage
            self.percentage_var.set("0%")
            
            # Start flashing in separate thread
            flash_thread = threading.Thread(target=self.flash_iso)
            flash_thread.daemon = True
            flash_thread.start()
            
    def flash_iso(self):
        """Flash ISO to USB drive"""
        try:
            # Update status
            self.status_var.set("Preparing to flash...")
            self.progress_bar.set(0.1)
            
            # Use original drive letter to maintain consistency
            drive_letter = self.original_drive_letter if self.original_drive_letter else self.selected_drive
            
            # Flash the ISO
            success = self.flasher.flash_iso(
                iso_path=self.selected_iso,
                drive_letter=drive_letter,
                volume_name=self.volume_var.get(),
                partition_scheme=self.partition_var.get(),
                target_system=self.target_var.get(),
                file_system=self.system_var.get(),
                progress_callback=self.update_progress
            )
            
            if success:
                self.status_var.set("Flash completed successfully!")
                self.progress_bar.set(1.0)
                self.percentage_var.set("100%")
                self.layer_completed[4] = True
                self.flash_status.configure(
                    text="✅ Complete",
                    text_color=self.primary_color
                )
                messagebox.showinfo("Success", f"ISO has been successfully flashed to USB drive {drive_letter}!")
            else:
                self.status_var.set("Flash failed!")
                self.percentage_var.set("0%")
                self.flash_status.configure(
                    text="❌ Failed",
                    text_color="red"
                )
                messagebox.showerror("Error", "Failed to flash ISO to USB drive.")
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            self.percentage_var.set("0%")
            self.flash_status.configure(
                text="❌ Error",
                text_color="red"
            )
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            # Re-enable flash button
            self.flash_btn.configure(state="normal", text="FLASH")
            
    def update_progress(self, progress, status):
        """Update progress bar, status, and percentage"""
        self.progress_bar.set(progress / 100.0)
        self.status_var.set(status)
        self.percentage_var.set(f"{int(progress)}%")
        self.update()
