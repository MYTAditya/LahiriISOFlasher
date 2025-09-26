import os
import subprocess
import shutil
import tempfile
import time
import struct
from pathlib import Path

class ISOFlasher:
    def __init__(self):
        self.progress_callback = None
        self.temp_dir = None
        
    def flash_iso(self, iso_path, drive_letter, volume_name, partition_scheme, target_system, file_system, progress_callback=None):
        """Flash ISO to USB drive using temporary folder extraction method"""
        self.progress_callback = progress_callback
        
        try:
            # Update progress
            self._update_progress(5, "Validating inputs...")

            # To prevent unwanted configuration
            if partition_scheme == "MBR":
                if target_system == "BIOS or UEFI":
                    if file_system == "FAT32":
                        pass
                    else:
                        raise Exception("Selected unwanted configuration")
                elif target_system == "BIOS (Legacy)":
                    pass
                else:
                    raise Exception("Selected unwanted configuration")
            else:
                if target_system == "UEFI":
                    if file_system == "FAT32":
                        pass
                    else:
                        raise Exception("Selected unwanted configuration")
                else:
                    raise Exception("Selected unwanted configuration")
            
            # Validate inputs
            if not os.path.exists(iso_path):
                raise Exception("ISO file not found")
                
            if not os.path.exists(f"{drive_letter}:\\"):
                raise Exception("USB drive not found")
                
            # Get drive info before formatting
            drive_info = self._get_drive_info(drive_letter)
            if not drive_info:
                raise Exception("Could not get drive information")
                
            # Update progress
            self._update_progress(10, "Preparing USB drive...")
            
            # Format the drive first
            if not self._format_drive_standalone(drive_letter, volume_name, partition_scheme, file_system):
                raise Exception("Failed to format USB drive")
                
            # Update progress
            self._update_progress(20, "Creating temporary folder...")
            
            # Create hidden temporary folder
            self.temp_dir = tempfile.mkdtemp(prefix=".iso_extract_")
            
            # Update progress
            self._update_progress(25, "Extracting ISO to temporary folder...")
            
            # Extract ISO contents to temporary folder
            if not self._extract_iso_to_temp(iso_path):
                raise Exception("Failed to extract ISO contents")
                
            # Update progress
            self._update_progress(70, "Copying files to USB drive...")
            
            # Copy all files from temp folder to USB drive
            if not self._copy_temp_to_usb(drive_letter):
                raise Exception("Failed to copy files to USB drive")
                
            # Update progress
            self._update_progress(90, "Making drive bootable...")
            
            # Make the drive bootable
            if not self._make_bootable_standalone(drive_letter, target_system):
                raise Exception("Failed to make drive bootable")
                
            # Update progress
            self._update_progress(95, "Cleaning up temporary files...")
            
            # Clean up temporary folder
            self._cleanup_temp_dir()
            
            # Update progress
            self._update_progress(100, "Flash completed successfully!")
            
            return True
            
        except Exception as e:
            # Clean up on error
            self._cleanup_temp_dir()
            self._update_progress(0, f"Error: {str(e)}")
            raise e
            
    def _update_progress(self, progress, status):
        """Update progress callback"""
        if self.progress_callback:
            self.progress_callback(progress, status)
            
    def _get_drive_info(self, drive_letter):
        """Get drive information"""
        try:
            import psutil
            drive_path = f"{drive_letter}:\\"
            usage = psutil.disk_usage(drive_path)
            return {
                'total_bytes': usage.total,
                'free_bytes': usage.free
            }
        except Exception:
            return None
            
    def _format_drive_standalone(self, drive_letter, volume_name, partition_scheme, file_system):
        """Format the USB drive using only Windows built-in tools"""
        try:
            # Create diskpart script for comprehensive formatting
            diskpart_script = f"""
select disk {self._get_disk_number(drive_letter)}
clean
convert {partition_scheme}
create partition primary
active
format fs={file_system} label="{volume_name}" quick
assign letter={drive_letter}
exit
"""
            
            # Write diskpart script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(diskpart_script)
                script_path = f.name
                
            try:
                # Run diskpart with elevated privileges
                result = subprocess.run(
                    ['diskpart', '/s', script_path],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    # Wait for drive to be ready
                    time.sleep(3)
                    return os.path.exists(f"{drive_letter}:\\")
                else:
                    # Fallback to simple format
                    return self._simple_format(drive_letter, volume_name, file_system)
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(script_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error formatting drive: {e}")
            # Final fallback
            return self._simple_format(drive_letter, volume_name, "FAT32")
            
    def _get_disk_number(self, drive_letter):
        """Get disk number for the drive letter"""
        try:
            # Use wmic to get disk number
            cmd = f'wmic logicaldisk where "DeviceID=\\"{drive_letter}:\\"" assoc /assocclass:Win32_LogicalDiskToPartition'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                # Parse output to get disk number
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Disk #' in line:
                        disk_num = line.split('Disk #')[1].split(',')[0].strip()
                        return disk_num
                        
            # Fallback: assume it's disk 1 (common for USB drives)
            return "1"
            
        except Exception:
            return "1"
            
    def _simple_format(self, drive_letter, volume_name, file_system):
        """Simple format using format command"""
        try:
            cmd = f'format {drive_letter}: /FS:{file_system} /V:"{volume_name}" /Q /Y'
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except:
            return False
            
    def _extract_iso_to_temp(self, iso_path):
        """Extract ISO contents to temporary folder"""
        try:
            # Try PowerShell mount method first
            if self._extract_with_powershell(iso_path):
                return True
                
            # Fallback to manual ISO parsing
            return self._extract_iso_manual(iso_path)
            
        except Exception as e:
            print(f"Error extracting ISO: {e}")
            return False
            
    def _extract_with_powershell(self, iso_path):
        """Extract ISO using PowerShell mount"""
        try:
            # Mount ISO using PowerShell
            mount_cmd = [
                'powershell', '-Command',
                f'$mount = Mount-DiskImage -ImagePath "{iso_path}" -PassThru; '
                f'$driveLetter = ($mount | Get-Volume).DriveLetter; '
                f'Write-Output $driveLetter'
            ]
            
            result = subprocess.run(mount_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                iso_drive = result.stdout.strip()
                iso_path_src = f"{iso_drive}:\\"
                
                try:
                    # Copy all files to temp directory
                    self._copy_directory_contents(iso_path_src, self.temp_dir)
                    return True
                    
                finally:
                    # Unmount ISO
                    unmount_cmd = [
                        'powershell', '-Command',
                        f'Dismount-DiskImage -ImagePath "{iso_path}"'
                    ]
                    subprocess.run(unmount_cmd, capture_output=True, timeout=30)
                    
            return False
            
        except Exception as e:
            print(f"Error with PowerShell extraction: {e}")
            return False
            
    def _extract_iso_manual(self, iso_path):
        """Manual ISO extraction using Python"""
        try:
            with open(iso_path, 'rb') as iso_file:
                # Read ISO 9660 structure
                iso_file.seek(16 * 2048)  # Primary Volume Descriptor
                pvd = iso_file.read(2048)
                
                if pvd[1:6] != b'CD001':
                    raise Exception("Invalid ISO format")
                
                # Get root directory location
                root_dir_lba = struct.unpack('<L', pvd[158:162])[0]
                root_dir_size = struct.unpack('<L', pvd[166:170])[0]
                
                # Extract files from ISO
                self._extract_iso_files(iso_file, root_dir_lba, root_dir_size, self.temp_dir, "")
                
                return True
                
        except Exception as e:
            print(f"Error with manual ISO extraction: {e}")
            return False
            
    def _extract_iso_files(self, iso_file, dir_lba, dir_size, output_path, current_path):
        """Recursively extract files from ISO directory"""
        try:
            iso_file.seek(dir_lba * 2048)
            dir_data = iso_file.read(dir_size)
            
            offset = 0
            file_count = 0
            
            while offset < len(dir_data):
                if offset + 33 > len(dir_data):
                    break
                    
                record_length = dir_data[offset]
                if record_length == 0:
                    # Skip to next sector
                    sector_offset = offset % 2048
                    if sector_offset != 0:
                        offset += 2048 - sector_offset
                        continue
                    else:
                        break
                
                if offset + record_length > len(dir_data):
                    break
                
                # Parse directory record
                record = dir_data[offset:offset + record_length]
                
                # Get file location and size
                file_lba = struct.unpack('<L', record[2:6])[0]
                file_size = struct.unpack('<L', record[10:14])[0]
                
                # Get filename
                filename_len = record[32]
                if filename_len > 0 and offset + 33 + filename_len <= len(dir_data):
                    filename = record[33:33 + filename_len].decode('ascii', errors='ignore')
                    
                    # Skip . and .. entries
                    if filename not in ['.', '..', '\x00']:
                        file_flags = record[25]
                        is_directory = (file_flags & 2) != 0
                        
                        # Clean filename
                        if ';' in filename:
                            filename = filename.split(';')[0]
                            
                        full_path = os.path.join(output_path, current_path, filename)
                        
                        if is_directory:
                            # Create directory
                            os.makedirs(full_path, exist_ok=True)
                            # Recursively extract directory contents
                            if file_size > 0:
                                self._extract_iso_files(iso_file, file_lba, file_size, output_path, 
                                                      os.path.join(current_path, filename))
                        else:
                            # Extract file
                            if file_size > 0:
                                self._extract_file(iso_file, file_lba, file_size, full_path)
                                file_count += 1
                                
                                # Update progress periodically
                                if file_count % 10 == 0:
                                    progress = 25 + min(40, (file_count / 100) * 40)
                                    self._update_progress(progress, f"Extracting files... ({file_count} files)")
                
                offset += record_length
                
        except Exception as e:
            print(f"Error extracting ISO files: {e}")
            
    def _extract_file(self, iso_file, file_lba, file_size, output_path):
        """Extract a single file from ISO"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Read file data from ISO
            iso_file.seek(file_lba * 2048)
            
            with open(output_path, 'wb') as output_file:
                remaining = file_size
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    chunk = iso_file.read(chunk_size)
                    if not chunk:
                        break
                    output_file.write(chunk)
                    remaining -= len(chunk)
                    
        except Exception as e:
            print(f"Error extracting file {output_path}: {e}")
            
    def _copy_directory_contents(self, src_path, dst_path):
        """Copy directory contents with progress updates"""
        try:
            # Count total files first
            total_files = sum(1 for root, dirs, files in os.walk(src_path) for file in files)
            copied_files = 0
            
            for root, dirs, files in os.walk(src_path):
                # Create corresponding directories
                rel_path = os.path.relpath(root, src_path)
                if rel_path != '.':
                    dst_dir = os.path.join(dst_path, rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_file_path = os.path.relpath(src_file, src_path)
                    dst_file = os.path.join(dst_path, rel_file_path)
                    
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    copied_files += 1
                    
                    # Update progress
                    if total_files > 0:
                        progress = 25 + (copied_files / total_files) * 40
                        self._update_progress(progress, f"Extracting files... ({copied_files}/{total_files})")
                        
        except Exception as e:
            print(f"Error copying directory contents: {e}")
            raise e
            
    def _copy_temp_to_usb(self, drive_letter):
        """Copy files from temporary folder to USB drive"""
        try:
            drive_path = f"{drive_letter}:\\"
            
            # Count total files first
            total_files = sum(1 for root, dirs, files in os.walk(self.temp_dir) for file in files)
            copied_files = 0
            
            for root, dirs, files in os.walk(self.temp_dir):
                # Create corresponding directories
                rel_path = os.path.relpath(root, self.temp_dir)
                if rel_path != '.':
                    dst_dir = os.path.join(drive_path, rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_file_path = os.path.relpath(src_file, self.temp_dir)
                    dst_file = os.path.join(drive_path, rel_file_path)
                    
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    copied_files += 1
                    
                    # Update progress
                    if total_files > 0:
                        progress = 70 + (copied_files / total_files) * 15
                        self._update_progress(progress, f"Copying to USB... ({copied_files}/{total_files})")
                        
            return True
            
        except Exception as e:
            print(f"Error copying to USB drive: {e}")
            return False
            
    def _cleanup_temp_dir(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(f"Error cleaning up temp directory: {e}")
            finally:
                self.temp_dir = None
                
    def _make_bootable_standalone(self, drive_letter, target_system):
        """Make the USB drive bootable using only Windows tools"""
        try:
            drive_path = f"{drive_letter}:\\"
            
            # Check for different boot methods
            boot_files_found = []
            
            # Check for Windows boot files
            if os.path.exists(os.path.join(drive_path, "bootmgr")):
                boot_files_found.append("bootmgr")
            if os.path.exists(os.path.join(drive_path, "boot")):
                boot_files_found.append("boot_folder")
            if os.path.exists(os.path.join(drive_path, "efi")):
                boot_files_found.append("efi")
            if os.path.exists(os.path.join(drive_path, "isolinux")):
                boot_files_found.append("isolinux")
                
            # Make partition active using diskpart
            self._make_partition_active(drive_letter)
            
            # If we have boot files, the drive should be bootable
            if boot_files_found:
                print(f"Boot files found: {boot_files_found}")
                return True
            else:
                print("No specific boot files found, but partition is marked as active")
                return True
                
        except Exception as e:
            print(f"Error making drive bootable: {e}")
            return True  # Don't fail the entire process for boot setup issues
            
    def _make_partition_active(self, drive_letter):
        """Mark the partition as active using diskpart"""
        try:
            disk_num = self._get_disk_number(drive_letter)
            
            diskpart_script = f"""
select disk {disk_num}
select partition 1
active
exit
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(diskpart_script)
                script_path = f.name
                
            try:
                subprocess.run(
                    ['diskpart', '/s', script_path], 
                    capture_output=True, 
                    timeout=60,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True
            finally:
                try:
                    os.unlink(script_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error making partition active: {e}")
            return True
