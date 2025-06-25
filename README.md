# LahiriISOFlasher

A modern, user-friendly ISO flashing application for Windows, similar to balenaEtcher but with additional Rufus-like features.

## Features

- **Modern Dark UI**: Clean, professional interface with #a9e43a accent color
- **4-Layer Workflow**: 
  1. Select USB Drive
  2. Select ISO File
  3. Configure Settings (Volume Name, Partition Scheme, Target System)
  4. Flash ISO
- **ISO Validation**: Automatically validates ISO files and checks if they're bootable
- **Auto Volume Detection**: Extracts volume name from ISO files when available
- **Multiple Boot Options**: Support for BIOS, UEFI, and hybrid boot modes
- **Progress Tracking**: Real-time progress updates during flashing
- **Safety Features**: Confirmation dialogs and drive validation

## Requirements

- Windows 10/11
- Python 3.8+ (for development)
- Administrator privileges (for disk operations)

## Installation

### For Users (Standalone Executable)
1. Download the latest release from the releases page
2. Run `LahiriISOFlasher.exe` as administrator
3. Follow the 4-step process to flash your ISO

### For Developers
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Building from Source

To create a standalone executable:

```bash
python build.py
```

This will create a single executable file in the `dist` folder.

## Usage

1. **Select USB Drive**: Choose your target USB drive from the dropdown
2. **Select ISO File**: Browse and select your ISO file
3. **Configure Settings**:
   - Volume Name: Set the name for your USB drive
   - Partition Scheme: Choose MBR or GPT
   - Target System: Select BIOS, UEFI, or hybrid compatibility
4. **Flash**: Click the flash button to start the process

## Safety Features

- **Drive Validation**: Only shows removable USB drives
- **ISO Validation**: Checks for valid ISO format and bootability
- **Confirmation Dialog**: Confirms all settings before flashing
- **Progress Monitoring**: Shows real-time progress and status

## Technical Details

- Built with Python and CustomTkinter for modern UI
- Uses Windows API for drive detection and management
- Supports multiple flashing methods for maximum compatibility
- Implements proper error handling and user feedback

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This software can permanently erase data on USB drives. Always ensure you have backups of important data before using this application. Use at your own risk.