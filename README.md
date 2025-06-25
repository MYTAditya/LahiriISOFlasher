# LahiriISOFlasher

<img alt="GitHub Created At" src="https://img.shields.io/github/created-at/MYTAditya/LahiriISOFlasher?color=%238a2be2"> <img alt="GitHub Release" src="https://img.shields.io/github/v/release/MYTAditya/LahiriISOFlasher?color=%23a9e43a"> <img alt="GitHub License" src="https://img.shields.io/github/license/MYTAditya/LahiriISOFlasher?color=orange"> <img alt="GitHub top language" src="https://img.shields.io/badge/language-Python-blue">

An user-friendly ISO flashing application for Windows, similar to [balenaEtcher](https://github.com/balena-io/etcher) but with additional [Rufus](https://github.com/pbatard/rufus)-like features.

## Features

- **Modern Dark UI**: Clean, professional interface with lime accent color
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

## Disclaimer

This software can permanently erase data on USB drives. Always ensure you have backups of important data before using this application. Use at your own risk.
