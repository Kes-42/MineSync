import os
from pathlib import Path

def generate_sync_scripts(instance_name: str, instance_path: Path, remote_name: str, cloud_folder: str, local_saves_dir: Path, local_map_dir: Path):
    """
    Generates sync_up.sh and sync_down.sh tailored for the selected instance,
    using the bulletproof bisync flags.
    Returns (sync_down_path, sync_up_path)
    """
    
    # Scripts will be placed in the instance directory
    sync_down_path = instance_path / "sync_down.sh"
    sync_up_path = instance_path / "sync_up.sh"
    
    home_dir = Path.home()
    
    # Path to local saves
    local_saves_dir.mkdir(parents=True, exist_ok=True)
    local_saves_target = f'"{local_saves_dir}/"'
    
    # Path to cloud saves (isolated by instance)
    cloud_saves_target = f"{remote_name}:{cloud_folder}/{instance_name}/saves/"
    
    # Backup directories
    local_backup_dir = home_dir / "minecraft_sync_backups" / "local_overwritten"
    cloud_backup_dir = f"{remote_name}:{cloud_folder}/{instance_name}/safety_backups/cloud_overwritten/"
    
    # Xaero map dirs
    local_map_dir.mkdir(parents=True, exist_ok=True)
    local_map_target = f'"{local_map_dir}/"'
    cloud_map_target = f"{remote_name}:{cloud_folder}/{instance_name}/xaeroworldmap/"
    local_map_backup = home_dir / "minecraft_sync_backups" / "map_local_overwritten"
    cloud_map_backup = f"{remote_name}:{cloud_folder}/{instance_name}/safety_backups/map_cloud_overwritten/"

    # Create the base script content
    down_script = f"""#!/bin/bash
echo "Pulling latest saves from Google Drive..."
mkdir -p "{local_backup_dir}"

rclone bisync "{cloud_saves_target}" {local_saves_target} \\
--verbose \\
--transfers 8 \\
--checkers 16 \\
--drive-chunk-size 64M \\
--conflict-resolve newer \\
--backup-dir2 "{local_backup_dir}/" \\
--resilient

echo "Pulling latest map data..."
mkdir -p "{local_map_backup}"
rclone bisync "{cloud_map_target}" {local_map_target} \\
--verbose --transfers 8 --checkers 16 --conflict-resolve newer \\
--backup-dir2 "{local_map_backup}/" --resilient

echo "Sync Complete! You are ready to play."
"""

    up_script = f"""#!/bin/bash
echo "Updating Google Drive with local saves..."
rclone bisync {local_saves_target} "{cloud_saves_target}" \\
--verbose \\
--transfers 8 \\
--checkers 16 \\
--drive-chunk-size 64M \\
--conflict-resolve newer \\
--backup-dir2 "{cloud_backup_dir}" \\
--resilient

echo "Updating Google Drive with latest map data..."
rclone bisync {local_map_target} "{cloud_map_target}" \\
--verbose --transfers 8 --checkers 16 --conflict-resolve newer \\
--backup-dir2 "{cloud_map_backup}" --resilient

echo "Sync Complete!"
"""

    with open(sync_down_path, 'w', encoding='utf-8') as f:
        f.write(down_script)
    os.chmod(sync_down_path, 0o755)
    
    with open(sync_up_path, 'w', encoding='utf-8') as f:
        f.write(up_script)
    os.chmod(sync_up_path, 0o755)
    
    return sync_down_path, sync_up_path
