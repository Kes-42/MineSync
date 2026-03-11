import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from mc_sync_setup.window import SyncSetupWindow

class SyncSetupApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.github.lilz.MCSyncSetup')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = self.props.active_window
        if not win:
            win = SyncSetupWindow(application=app)
        win.present()

if __name__ == '__main__':
    app = SyncSetupApplication()
    app.run(sys.argv)
