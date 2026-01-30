# Minecraft Mod Sorter

> A Python tool for automatically sorting Minecraft mods by client-side, server-side, and both using the Modrinth API.

## Features

- **Automatic detection** - Uses the Modrinth API to detect if mods are client-only, server-only, or both
- **Clear organization** - Creates separate folders for each category
- **Hash-based search** - Uses SHA1 and SHA512 hashes for reliable identification
- **Detailed reports** - Shows a summary of all sorted mods
- **GUI version** - Easy-to-use graphical interface (mod_sorter_gui.py)
- **CLI version** - Command-line tool for automation (mod_sorter.py)

## Screenshots

### GUI Version
The graphical interface provides:
- Browse button to select your mods folder
- Real-time progress bar
- Live log showing what's happening
- Cancel button if needed
- Summary popup when finished

### CLI Version
Command-line interface for:
- Automation and scripting
- Server environments
- Quick batch processing

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Version](#gui-version-recommended)
  - [CLI Version](#cli-version)
- [Output Structure](#output-structure)
- [Categories Explained](#what-do-the-categories-mean)
- [Example Output](#example-output)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.6 or higher
- Internet connection (for Modrinth API)
- For GUI version: tkinter (usually included with Python)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/minecraft-mod-sorter.git
   cd minecraft-mod-sorter
   ```

2. No additional dependencies needed! The scripts use only Python standard libraries.

## Usage

### GUI Version (Recommended)

```bash
python mod_sorter_gui.py
```

Then:
1. Click "Browse..." to select your mods folder
2. Click "Start Sorting"
3. Watch the progress in real-time
4. Get a notification when complete

### CLI Version

#### Method 1: With command-line argument

```bash
python mod_sorter.py /path/to/your/mods/folder
```

#### Method 2: Interactive

```bash
python mod_sorter.py
```

The program will then ask you for the path to the mods folder.

## Output Structure

The tool creates a `sorted_mods` folder next to your original mods folder with the following structure:

```
sorted_mods/
├── client-only/     # Only for client
├── server-only/     # Only for server
├── both/            # Client AND server
└── unknown/         # Not found on Modrinth
```

## What do the categories mean?

### CLIENT-ONLY
Mods that should **only** be installed on the client:
- Shader mods
- Minimap mods
- Optifine/Performance mods
- GUI improvements
- etc.

**WARNING:** Do NOT copy these mods to the server!

### SERVER-ONLY
Mods that **only** run on the server:
- Server management tools
- Backup mods
- Anti-cheat mods
- etc.

**WARNING:** Do NOT copy these mods to the client!

### BOTH (Client & Server)
Mods that must be installed on **both sides**:
- Most content mods (new blocks, items, etc.)
- Tech mods
- Magic mods
- etc.

**NOTE:** Copy these mods to client **and** server!

### UNKNOWN
Mods not found on Modrinth:
- Custom/Private mods
- Very old mods
- Mods from other sources (CurseForge, etc.)

**WARNING:** You need to check these **manually**!

## Example Output

```
Found: 50 mod files
============================================================

[1/50] Checking: sodium-fabric-0.5.8.jar
  Client: required, Server: unsupported
  > CLIENT-ONLY

[2/50] Checking: lithium-fabric-0.12.0.jar
  Client: optional, Server: optional
  > BOTH (Client & Server)

...

SUMMARY
============================================================

CLIENT-ONLY: 12 mods
   - sodium-fabric-0.5.8.jar
   - iris-shaders-1.6.10.jar
   ...

SERVER-ONLY: 2 mods
   - server-backup-mod.jar
   ...

BOTH (Client & Server): 32 mods
   - create-fabric-0.5.1.jar
   - applied-energistics-2.jar
   ...

UNKNOWN: 4 mods
   - custom-mod.jar
   ...
```

## Notes

- The script **copies** the files, originals remain unchanged
- The Modrinth API is called with delays to avoid overloading the servers
- For "unknown" mods you should check the mod description or source code

## Troubleshooting

### "No .jar files found"
- Make sure the path to the mods folder is correct
- The folder must contain .jar files

### "Not found on Modrinth"
- The mod may only be on CurseForge or another platform
- Check the mod manually

### API errors
- Check your internet connection
- Modrinth might be temporarily unreachable
- Wait a few minutes and try again

### GUI doesn't start
- Make sure tkinter is installed: `python -m tkinter`
- On Linux, you may need to install: `sudo apt-get install python3-tk`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Uses the [Modrinth API](https://docs.modrinth.com/) for mod information
- Built with Python standard libraries

## Disclaimer

This tool is not affiliated with Minecraft, Mojang, or Modrinth. Use at your own risk.
