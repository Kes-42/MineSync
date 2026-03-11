import os
from pathlib import Path

def get_prism_instances():
    """Returns a dictionary of instance_name -> Path object for the instance folder."""
    instances = {}
    paths_to_check = [
        Path.home() / ".local" / "share" / "PrismLauncher" / "instances",
        Path.home() / ".var" / "app" / "org.prismlauncher.PrismLauncher" / "data" / "PrismLauncher" / "instances",
        Path.home() / "Library" / "Application Support" / "PrismLauncher" / "instances" # macOS
    ]
    
    for base_path in paths_to_check:
        if base_path.exists() and base_path.is_dir():
            for child in base_path.iterdir():
                if child.is_dir() and (child / "instance.cfg").exists():
                    instances[child.name] = child
    
    return instances

def patch_instance_cfg(instance_path, pre_cmd, post_cmd):
    """Parses instance.cfg, updates Pre/Post commands, and saves."""
    cfg_file = instance_path / "instance.cfg"
    if not cfg_file.exists():
        raise FileNotFoundError(f"Missing instance.cfg at {cfg_file}")
        
    lines = []
    with open(cfg_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    found_pre = False
    found_post = False
    
    # Wrap in quotes and prepend bash to ensure Prism Launcher executes it correctly
    pre_cmd = f'bash "{pre_cmd}"'
    post_cmd = f'bash "{post_cmd}"'
    
    for line in lines:
        if line.startswith("PreLaunchCommand="):
            new_lines.append(f"PreLaunchCommand={pre_cmd}\n")
            found_pre = True
        elif line.startswith("PostExitCommand="):
            new_lines.append(f"PostExitCommand={post_cmd}\n")
            found_post = True
        else:
            new_lines.append(line)
            
    # If not found, add them to the [General] section
    if not found_pre or not found_post:
        general_idx = -1
        for i, line in enumerate(new_lines):
            if line.strip() == "[General]":
                general_idx = i
                break
                
        if general_idx != -1:
            if not found_pre:
                new_lines.insert(general_idx + 1, f"PreLaunchCommand={pre_cmd}\n")
            if not found_post:
                new_lines.insert(general_idx + 2, f"PostExitCommand={post_cmd}\n")
        else:
            # If no [General] section, fallback to end
            if not found_pre:
                new_lines.append(f"PreLaunchCommand={pre_cmd}\n")
            if not found_post:
                new_lines.append(f"PostExitCommand={post_cmd}\n")
                
    with open(cfg_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
