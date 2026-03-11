import gi
from pathlib import Path
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

from mc_sync_setup.prism import get_prism_instances, patch_instance_cfg
from mc_sync_setup.scripts_gen import generate_sync_scripts

class SyncSetupWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("MineSync")
        self.set_default_size(550, 500)
        
        # Header Bar
        header = Adw.HeaderBar()
        
        # Main Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Try to find instances
        self.instances = get_prism_instances()
        
        # Preferences Page / Group
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup()
        group.set_title("Sync Configuration")
        group.set_description("Configure rclone bisync for a Prism Launcher instance.")
        page.add(group)
        main_box.append(page)
        
        # Instance Selector
        self.instance_combo = Gtk.DropDown.new_from_strings(list(self.instances.keys()) if self.instances else ["No instances found"])
        if self.instances:
            self.instance_combo.connect("notify::selected", self.on_instance_changed)
        else:
            self.instance_combo.set_sensitive(False)
            
        instance_row = Adw.ActionRow()
        instance_row.set_title("Prism Instance")
        instance_row.add_suffix(self.instance_combo)
        group.add(instance_row)
        
        # Subgroup: Cloud Setup
        cloud_group = Adw.PreferencesGroup()
        cloud_group.set_title("Google Drive Target")
        page.add(cloud_group)
        
        self.remote_entry = Gtk.Entry()
        self.remote_entry.set_text("gdrive")
        remote_row = Adw.ActionRow()
        remote_row.set_title("Rclone Remote Name")
        remote_row.set_subtitle("Usually 'gdrive'")
        remote_row.add_suffix(self.remote_entry)
        cloud_group.add(remote_row)
        
        self.cloud_entry = Gtk.Entry()
        self.cloud_entry.set_text("MinecraftSync")
        cloud_row = Adw.ActionRow()
        cloud_row.set_title("Cloud Directory")
        cloud_row.set_subtitle("Folder inside the remote (Instance name will be appended automatically)")
        cloud_row.add_suffix(self.cloud_entry)
        cloud_group.add(cloud_row)
        
        # Subgroup: Local Folders
        local_group = Adw.PreferencesGroup()
        local_group.set_title("Local Folders")
        page.add(local_group)
        
        # Saves Folder
        self.saves_dir_label = Gtk.Label(label="", xalign=0)
        self.saves_dir_label.set_ellipsize(3) # Pango.EllipsizeMode.MIDDLE (which is enum 3)
        self.saves_dir_label.set_max_width_chars(30)
        
        saves_btn = Gtk.Button(label="Browse...")
        saves_btn.connect("clicked", self.on_browse_saves)
        saves_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        saves_box.append(self.saves_dir_label)
        saves_box.append(saves_btn)
        
        self.saves_row = Adw.ActionRow()
        self.saves_row.set_title("Saves Folder")
        self.saves_row.set_subtitle("World data files path")
        self.saves_row.add_suffix(saves_box)
        local_group.add(self.saves_row)
        
        # Map Folder
        self.map_dir_label = Gtk.Label(label="", xalign=0)
        self.map_dir_label.set_ellipsize(3)
        self.map_dir_label.set_max_width_chars(30)
        
        map_btn = Gtk.Button(label="Browse...")
        map_btn.connect("clicked", self.on_browse_map)
        map_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        map_box.append(self.map_dir_label)
        map_box.append(map_btn)
        
        self.map_row = Adw.ActionRow()
        self.map_row.set_title("Xaero's Map Folder")
        self.map_row.set_subtitle("Map mod data path")
        self.map_row.add_suffix(map_box)
        local_group.add(self.map_row)
        
        # Apply Button
        apply_btn = Gtk.Button(label="Apply Sync Setup")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply_clicked)
        if not self.instances:
            apply_btn.set_sensitive(False)
            
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(12)
        btn_box.append(apply_btn)
        main_box.append(btn_box)

        # Set content
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(main_box)
        
        self.set_content(toolbar_view)
        
        # Init Default Paths
        if self.instances:
            self.on_instance_changed(self.instance_combo, None)
            
    def on_instance_changed(self, dropdown, pspec):
        selected_idx = dropdown.get_selected()
        instance_name = list(self.instances.keys())[selected_idx]
        instance_path = self.instances[instance_name]
        
        default_saves = instance_path / ".minecraft" / "saves"
        default_map = instance_path / ".minecraft" / "xaeroworldmap"
        
        self.current_saves_path = default_saves
        self.current_map_path = default_map
        
        self.saves_dir_label.set_text(str(default_saves))
        self.map_dir_label.set_text(str(default_map))

    def on_browse_saves(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Saves Folder")
        dialog.select_folder(self, None, self._on_saves_folder_selected)

    def _on_saves_folder_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.current_saves_path = Path(folder.get_path())
                self.saves_dir_label.set_text(str(self.current_saves_path))
        except Exception as e:
            print(f"Directory selection cancelled: {e}")

    def on_browse_map(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Map Folder")
        dialog.select_folder(self, None, self._on_map_folder_selected)

    def _on_map_folder_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.current_map_path = Path(folder.get_path())
                self.map_dir_label.set_text(str(self.current_map_path))
        except Exception as e:
            print(f"Directory selection cancelled: {e}")

    def on_apply_clicked(self, button):
        selected_idx = self.instance_combo.get_selected()
        instance_name = list(self.instances.keys())[selected_idx]
        instance_path = self.instances[instance_name]
        
        remote_name = self.remote_entry.get_text().strip()
        cloud_folder = self.cloud_entry.get_text().strip()
        
        if not remote_name or not cloud_folder:
            self.show_error("Please enter a remote name and cloud folder.")
            return
            
        try:
            down_sh, up_sh = generate_sync_scripts(
                instance_name, 
                instance_path, 
                remote_name, 
                cloud_folder, 
                self.current_saves_path, 
                self.current_map_path
            )
            patch_instance_cfg(instance_path, str(down_sh), str(up_sh))
            self.show_success("Successfully configured sync scripts for " + instance_name)
        except Exception as e:
            self.show_error(f"Error configuring sync: {e}")
            
    def show_error(self, message):
        dialog = Adw.MessageDialog(heading="Error", body=message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.choose(None, None)
        
    def show_success(self, message):
        dialog = Adw.MessageDialog(heading="Success", body=message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.choose(None, None)
