import sys
import os
import signal
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from vitudoro_cat.cat import CatWindow
from vitudoro_cat.settings import SettingsWindow
from vitudoro_cat.tray import TrayIcon

PID_FILE = os.path.join(GLib.get_user_runtime_dir(), "vitudoro-cat.pid")


class VitudoroCat:
    def __init__(self):
        self._write_pid()
        self.cat_window = CatWindow()
        self.settings_window = None
        self.cat_window.on_right_click = self.open_settings
        self.cat_window.show_all()
        self.tray = TrayIcon(self.cat_window, self.open_settings)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self._on_signal)

    def _write_pid(self):
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

    def _on_signal(self):
        self.open_settings()
        return True

    def open_settings(self):
        if self.settings_window and self.settings_window.get_visible():
            self.settings_window.present()
            return
        self.settings_window = SettingsWindow(self.cat_window)
        self.settings_window.show_all()

    def run(self):
        try:
            Gtk.main()
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)


def open_settings_remote():
    if not os.path.exists(PID_FILE):
        print("Vitudoro Cat nao esta rodando.")
        sys.exit(1)
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
    try:
        os.kill(pid, signal.SIGUSR1)
        print("Configuracoes abertas.")
    except ProcessLookupError:
        print("Vitudoro Cat nao esta rodando (processo nao encontrado).")
        os.remove(PID_FILE)
        sys.exit(1)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--settings":
        open_settings_remote()
        return
    app = VitudoroCat()
    app.run()


if __name__ == "__main__":
    main()
