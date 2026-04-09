import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from vitudoro_cat.pomodoro import DEFAULT_MESSAGES


class SettingsWindow(Gtk.Window):
    def __init__(self, cat_window):
        super().__init__(title="Vitudoro Cat - Configuracoes")
        self.cat = cat_window
        self.set_default_size(400, 520)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        self.add(box)

        scale_label = Gtk.Label(label="Tamanho do gato:")
        scale_label.set_halign(Gtk.Align.START)
        box.pack_start(scale_label, False, False, 0)

        self.scale_adj = Gtk.Adjustment(
            value=cat_window.scale_factor,
            lower=0.3, upper=3.0,
            step_increment=0.1, page_increment=0.5,
        )
        scale_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.scale_adj
        )
        scale_slider.set_digits(1)
        scale_slider.connect("value-changed", self._on_scale_changed)
        box.pack_start(scale_slider, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 4)

        pomo_label = Gtk.Label(label="Pomodoro:")
        pomo_label.set_halign(Gtk.Align.START)
        box.pack_start(pomo_label, False, False, 0)

        pomo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(pomo_box, False, False, 0)

        self.pomo_switch = Gtk.Switch()
        self.pomo_switch.set_active(cat_window.pomodoro.active)
        self.pomo_switch.connect("notify::active", self._on_pomo_toggled)
        pomo_box.pack_start(Gtk.Label(label="Ativar"), False, False, 0)
        pomo_box.pack_start(self.pomo_switch, False, False, 0)

        current_total = cat_window.pomodoro.duration_seconds
        current_min = current_total // 60
        current_sec = current_total % 60

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(time_box, False, False, 0)

        time_box.pack_start(Gtk.Label(label="Min:"), False, False, 0)
        self.min_spin = Gtk.SpinButton.new_with_range(0, 120, 1)
        self.min_spin.set_value(current_min)
        self.min_spin.connect("value-changed", self._on_time_changed)
        time_box.pack_start(self.min_spin, False, False, 0)

        time_box.pack_start(Gtk.Label(label="Seg:"), False, False, 0)
        self.sec_spin = Gtk.SpinButton.new_with_range(0, 59, 5)
        self.sec_spin.set_value(current_sec)
        self.sec_spin.connect("value-changed", self._on_time_changed)
        time_box.pack_start(self.sec_spin, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 4)

        msg_label = Gtk.Label(label="Mensagens de pausa:")
        msg_label.set_halign(Gtk.Align.START)
        box.pack_start(msg_label, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(200)
        box.pack_start(scroll, True, True, 0)

        self.msg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        scroll.add(self.msg_box)

        for msg in cat_window.pomodoro.messages:
            self._add_message_row(msg)

        add_btn = Gtk.Button(label="Adicionar mensagem")
        add_btn.connect("clicked", self._on_add_message)
        box.pack_start(add_btn, False, False, 0)

        quit_btn = Gtk.Button(label="Fechar Vitudoro Cat")
        quit_btn.connect("clicked", self._on_quit)
        box.pack_start(quit_btn, False, False, 8)

    def _get_total_seconds(self):
        return int(self.min_spin.get_value()) * 60 + int(self.sec_spin.get_value())

    def _on_scale_changed(self, scale):
        self.cat.set_scale(scale.get_value())

    def _on_pomo_toggled(self, switch, _param):
        if switch.get_active():
            total = self._get_total_seconds()
            if total < 1:
                total = 60
            self.cat.pomodoro.start(total)
        else:
            self.cat.pomodoro.stop()

    def _on_time_changed(self, _spin):
        total = self._get_total_seconds()
        self.cat.pomodoro.duration_seconds = total
        if self.cat.pomodoro.active:
            self.cat.pomodoro.start(total)

    def _add_message_row(self, text=""):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        entry = Gtk.Entry()
        entry.set_text(text)
        entry.connect("changed", self._on_message_edited)
        row.pack_start(entry, True, True, 0)

        remove_btn = Gtk.Button(label="X")
        remove_btn.connect("clicked", self._on_remove_message, row)
        row.pack_start(remove_btn, False, False, 0)

        self.msg_box.pack_start(row, False, False, 0)
        row.show_all()

    def _on_add_message(self, _btn):
        self._add_message_row("")
        self._sync_messages()

    def _on_remove_message(self, _btn, row):
        self.msg_box.remove(row)
        self._sync_messages()

    def _on_message_edited(self, _entry):
        self._sync_messages()

    def _sync_messages(self):
        messages = []
        for row in self.msg_box.get_children():
            entry = row.get_children()[0]
            text = entry.get_text().strip()
            if text:
                messages.append(text)
        if messages:
            self.cat.pomodoro.messages = messages

    def _on_quit(self, _btn):
        Gtk.main_quit()
