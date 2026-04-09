import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "kitten", "4.png")


class TrayIcon:
    def __init__(self, cat_window, open_settings_fn):
        self.cat = cat_window
        self.open_settings = open_settings_fn

        self.status_icon = Gtk.StatusIcon()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 24, 24, True)
        self.status_icon.set_from_pixbuf(pixbuf)
        self.status_icon.set_tooltip_text("Vitudoro Cat")
        self.status_icon.set_visible(True)
        self.status_icon.connect("popup-menu", self._on_popup)
        self.status_icon.connect("activate", self._on_activate)

        self.cat.pomodoro.on_tick = self._update_tooltip

    def _update_tooltip(self):
        remaining = self.cat.pomodoro.get_remaining_str()
        if remaining:
            self.status_icon.set_tooltip_text(f"Vitudoro Cat - {remaining}")
        else:
            self.status_icon.set_tooltip_text("Vitudoro Cat")

    def _on_activate(self, _icon):
        self.open_settings()

    def _on_popup(self, icon, button, time):
        menu = Gtk.Menu()

        item_settings = Gtk.MenuItem(label="Configuracoes")
        item_settings.connect("activate", lambda _: self.open_settings())
        menu.append(item_settings)

        menu.append(Gtk.SeparatorMenuItem())

        remaining = self.cat.pomodoro.get_remaining_str()
        if self.cat.pomodoro.active and remaining:
            item_time = Gtk.MenuItem(label=f"Restante: {remaining}")
            item_time.set_sensitive(False)
            menu.append(item_time)

        pomo_label = "Parar Pomodoro" if self.cat.pomodoro.active else "Iniciar Pomodoro"
        item_pomo = Gtk.MenuItem(label=pomo_label)
        item_pomo.connect("activate", self._toggle_pomodoro)
        menu.append(item_pomo)

        if self.cat.mouse_chase_active:
            item_stop_chase = Gtk.MenuItem(label="Parar perseguicao")
            item_stop_chase.connect("activate", lambda _: self.cat.stop_mouse_chase())
            menu.append(item_stop_chase)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Sair")
        item_quit.connect("activate", lambda _: Gtk.main_quit())
        menu.append(item_quit)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def _toggle_pomodoro(self, _item):
        if self.cat.pomodoro.active:
            self.cat.pomodoro.stop()
        else:
            self.cat.pomodoro.start()
