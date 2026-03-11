# MineSync

MineSync is a native Linux GUI tool written in Python, GTK4, and libadwaita. It automates the process of synchronizing Minecraft saves between computers using `rclone bisync`. 

It is designed specifically for modded setups matching the configuration outlined in the author's prior research, targeting setups using massive mods such as Voxy, Chunky, and Xaero's World Map on instances managed by Prism Launcher.

## Features
- **Auto-Detection**: Scans your system (`~/.local/share/PrismLauncher` and Flatpak directories) to find installed Prism Launcher instances.
- **Rclone Integration**: Generates highly optimized, robust scripts (`sync_up.sh` and `sync_down.sh`) tailored to avoid Google Drive API rate limits and "182-year wait times."
- **Prism Launcher Patching**: Automatically edits the `instance.cfg` of your chosen instance to run the sync scripts on Pre-Launch and Post-Exit.
- **Conflict Resolution**: Ensures "newer-wins" logic, preventing overwrites of recent work.
- **Safety Backups**: If a conflict occurs and files are overwritten, the old version is safeguarded in a `safety_backups` folder.

## Requirements
- `rclone` must be installed and authenticated with your cloud remote (default: `gdrive`).
- Prism Launcher must be installed on your Linux system.
- Python 3 and PyGObject are required to run directly.

## Running via Flatpak
This project uses Flatpak for simple distribution across any Linux distribution.
```bash
flatpak-builder build-dir com.github.lilz.MCSyncSetup.json --force-clean --user --install
flatpak run com.github.lilz.MCSyncSetup
```

## Running directly (for development)
```bash
export PYTHONPATH=.
python3 -m mc_sync_setup.main
```

## How It Works
1. When launched, the application searches for Prism instances and displays them in a dropdown.
2. Select your instance and confirm your Rclone remote name (e.g., `gdrive`) and folder name.
3. Click "Apply Sync Setup".
4. The application generates scripts inside your instance directory and injects `PreLaunchCommand` and `PostExitCommand` hooks into `instance.cfg`. 
5. Start Prism Launcher and play! `bisync` logic will make sure everything stays up-to-date.

## Roadmap
- [ ] Automatic configuration of `rclone` during installation
- [ ] Support for other cloud services besides Google Drive
- [ ] Native macOS support
