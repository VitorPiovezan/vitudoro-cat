import sys
import os
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from vitudoro_cat.cat import CatWindow
from vitudoro_cat.settings import SettingsWindow
from vitudoro_cat.tray import TrayIcon


class VitudoroCat:
    def __init__(self):
        self.cat_window = CatWindow()
        self.settings_window = None
        self.cat_window.on_right_click = self.open_settings
        self.cat_window.show_all()
        self.tray = TrayIcon(self.cat_window, self.open_settings)

    def open_settings(self):
        if self.settings_window and self.settings_window.get_visible():
            self.settings_window.present()
            return
        self.settings_window = SettingsWindow(self.cat_window)
        self.settings_window.show_all()

    def run(self):
        Gtk.main()


def main():
    app = VitudoroCat()
    app.run()


if __name__ == "__main__":
    main()
