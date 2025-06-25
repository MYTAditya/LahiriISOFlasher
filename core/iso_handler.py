import os
import struct
import subprocess
from pathlib import Path

class ISOHandler:
    def __init__(self):
        pass
        
    def validate_iso(self, iso_path):
        """Validate if the file is a valid ISO"""
        try:
            if not os.path.exists(iso_path):
                return False
                
            # Check file extension
            if not iso_path.lower().endswith('.iso'):
                return False
                
            # Check ISO signature
            with open(iso_path, 'rb') as f:
                # Skip to sector 16 (ISO 9660 primary volume descriptor)
                f.seek(16 * 2048)
                data = f.read(6)
                
                # Check for ISO 9660 signature
                if data[1:6] == b'CD001':
                    return True
                    
            return False
            
        except Exception:
            return False
            
    def is_bootable(self, iso_path):
        """Check if ISO is bootable"""
        try:
            with open(iso_path, 'rb') as f:
                # Check for El Torito boot record
                f.seek(17 * 2048)  # Boot record volume descriptor
                data = f.read(2048)
                
                # Look for El Torito signature
                if b'EL TORITO SPECIFICATION' in data:
                    return True
                    
                # Alternative check for boot signature
                f.seek(0x8000)  # Common boot sector location
                boot_data = f.read(512)
                
                # Check for boot signature (0x55AA at end of boot sector)
                if len(boot_data) >= 512 and boot_data[510:512] == b'\x55\xAA':
                    return True
                    
            return False
            
        except Exception:
            return False
            
    def get_volume_name(self, iso_path):
        """Extract volume name from ISO"""
        try:
            with open(iso_path, 'rb') as f:
                # Go to primary volume descriptor
                f.seek(16 * 2048)
                data = f.read(2048)
                
                # Volume identifier is at offset 40, 32 bytes long
                if len(data) >= 72:
                    volume_name = data[40:72].decode('ascii', errors='ignore').strip()
                    if volume_name:
                        return volume_name
                        
            return None
            
        except Exception:
            return None
            
    def get_iso_info(self, iso_path):
        """Get comprehensive ISO information"""
        info = {
            'valid': False,
            'bootable': False,
            'volume_name': None,
            'size': 0,
            'creation_date': None
        }
        
        try:
            if not os.path.exists(iso_path):
                return info
                
            # Basic file info
            stat = os.stat(iso_path)
            info['size'] = stat.st_size
            
            # Validate ISO
            info['valid'] = self.validate_iso(iso_path)
            if not info['valid']:
                return info
                
            # Check if bootable
            info['bootable'] = self.is_bootable(iso_path)
            
            # Get volume name
            info['volume_name'] = self.get_volume_name(iso_path)
            
            # Get creation date from ISO
            with open(iso_path, 'rb') as f:
                f.seek(16 * 2048)
                data = f.read(2048)
                
                # Creation date is at offset 813, 17 bytes
                if len(data) >= 830:
                    date_str = data[813:830].decode('ascii', errors='ignore')
                    info['creation_date'] = date_str
                    
        except Exception as e:
            print(f"Error getting ISO info: {e}")
            
        return info