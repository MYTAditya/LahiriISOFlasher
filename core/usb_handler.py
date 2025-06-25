import os
import subprocess
import psutil
import win32api
import win32file

class USBHandler:
    def __init__(self):
        pass
        
    def get_usb_drives(self):
        """Get list of USB drives"""
        usb_drives = []
        
        try:
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Check if it's a removable drive
                    drive_type = win32file.GetDriveType(partition.mountpoint)
                    
                    # DRIVE_REMOVABLE = 2
                    if drive_type == 2:
                        # Get drive info
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        # Get volume label
                        try:
                            volume_info = win32api.GetVolumeInformation(partition.mountpoint)
                            label = volume_info[0] if volume_info[0] else "Removable Drive"
                        except:
                            label = "Removable Drive"
                            
                        # Format size
                        size_gb = usage.total / (1024**3)
                        size_str = f"{size_gb:.1f} GB"
                        
                        usb_drives.append({
                            'letter': partition.mountpoint[0],
                            'label': label,
                            'size': size_str,
                            'total_bytes': usage.total,
                            'free_bytes': usage.free,
                            'device': partition.device
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error getting USB drives: {e}")
            
        return usb_drives
        
    def format_drive(self, drive_letter, volume_name, file_system="FAT32"):
        """Format USB drive"""
        try:
            # Use Windows format command
            cmd = f'format {drive_letter}: /FS:{file_system} /V:"{volume_name}" /Q /Y'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error formatting drive: {e}")
            return False
            
    def is_drive_mounted(self, drive_letter):
        """Check if drive is mounted"""
        try:
            return os.path.exists(f"{drive_letter}:\\")
        except:
            return False
            
    def get_drive_info(self, drive_letter):
        """Get detailed drive information"""
        try:
            drive_path = f"{drive_letter}:\\"
            
            if not os.path.exists(drive_path):
                return None
                
            usage = psutil.disk_usage(drive_path)
            
            # Get volume label
            try:
                volume_info = win32api.GetVolumeInformation(drive_path)
                label = volume_info[0] if volume_info[0] else "Removable Drive"
                file_system = volume_info[4]
            except:
                label = "Removable Drive"
                file_system = "Unknown"
                
            return {
                'letter': drive_letter,
                'label': label,
                'file_system': file_system,
                'total_bytes': usage.total,
                'free_bytes': usage.free,
                'used_bytes': usage.used
            }
            
        except Exception as e:
            print(f"Error getting drive info: {e}")
            return None