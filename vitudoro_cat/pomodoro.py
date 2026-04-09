import random
import math
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

UPDATE_INTERVAL = 33

DEFAULT_MESSAGES = [
    "Para e descansa, humano!",
    "Ei! Hora de dar uma pausa!",
    "Miau! Voce precisa descansar!",
    "Seus olhos precisam de uma folga!",
    "Levanta e estica as pernas!",
    "Hora do break! Vai beber agua!",
    "Descansa um pouco, vai...",
    "Pausa obrigatoria! Ordem do gato!",
    "Tira os olhos da tela agora!",
    "Respira fundo e relaxa!",
    "Voce ta trabalhando demais!",
]


class PomodoroTimer:
    def __init__(self, cat_window):
        self.cat = cat_window
        self.duration_seconds = 25 * 60
        self.remaining_seconds = 0
        self.messages = list(DEFAULT_MESSAGES)
        self.active = False
        self.tick_id = None
        self.on_tick = None

    def start(self, seconds=None):
        if seconds:
            self.duration_seconds = seconds
        self.stop()
        self.active = True
        self.remaining_seconds = self.duration_seconds
        self.tick_id = GLib.timeout_add_seconds(1, self._tick)

    def stop(self):
        self.active = False
        if self.tick_id:
            GLib.source_remove(self.tick_id)
            self.tick_id = None
        self.remaining_seconds = 0
        if self.on_tick:
            self.on_tick()
        self.cat.stop_mouse_chase()

    def get_remaining_str(self):
        if not self.active or self.remaining_seconds <= 0:
            return ""
        m = self.remaining_seconds // 60
        s = self.remaining_seconds % 60
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        if not self.active:
            return False
        self.remaining_seconds -= 1
        if self.on_tick:
            self.on_tick()
        if self.remaining_seconds <= 0:
            self._on_timer_done()
            return False
        return True

    def _on_timer_done(self):
        if not self.active:
            return
        self._show_bubble()
        self.cat.start_mouse_chase()
        self.remaining_seconds = self.duration_seconds
        self.tick_id = GLib.timeout_add_seconds(1, self._tick)

    def _show_bubble(self):
        msg = random.choice(self.messages)
        bubble = BubbleWindow(self.cat, msg)
        bubble.show_all()
        GLib.timeout_add_seconds(6, self._destroy_bubble, bubble)

    def _destroy_bubble(self, bubble):
        try:
            bubble.destroy()
        except Exception:
            pass
        return False


class BubbleWindow(Gtk.Window):
    def __init__(self, cat_window, message):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        self.stick()

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.cat_window = cat_window
        self.message = message
        self.bubble_w = 200
        self.bubble_h = 75

        self.set_size_request(self.bubble_w, self.bubble_h)

        da = Gtk.DrawingArea()
        da.set_size_request(self.bubble_w, self.bubble_h)
        da.connect("draw", self._on_draw)
        self.add(da)

        self._reposition()
        self._follow_id = GLib.timeout_add(UPDATE_INTERVAL, self._follow_cat)

    def _reposition(self):
        cat_x = self.cat_window.cat_x
        cat_y = self.cat_window.cat_y
        bubble_x = cat_x + self.cat_window.display_w - 10
        bubble_y = cat_y - self.bubble_h + 10

        mon = self.cat_window._get_current_monitor()
        if bubble_y < mon["y"]:
            bubble_y = mon["y"]
        if bubble_x + self.bubble_w > mon["x"] + mon["w"]:
            bubble_x = cat_x - self.bubble_w + 10

        self.move(int(bubble_x), int(bubble_y))

    def _follow_cat(self):
        try:
            self._reposition()
        except Exception:
            return False
        return True

    def destroy(self):
        if hasattr(self, "_follow_id") and self._follow_id:
            GLib.source_remove(self._follow_id)
            self._follow_id = None
        super().destroy()

    def _on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(0)
        cr.paint()
        cr.set_operator(2)

        w = self.bubble_w
        h = self.bubble_h
        tail_h = 10
        body_h = h - tail_h
        r = 10

        cr.move_to(r, 0)
        cr.line_to(w - r, 0)
        cr.arc(w - r, r, r, -math.pi / 2, 0)
        cr.line_to(w, body_h - r)
        cr.arc(w - r, body_h - r, r, 0, math.pi / 2)
        cr.line_to(18, body_h)
        cr.line_to(5, h)
        cr.line_to(5, body_h)
        cr.line_to(r, body_h)
        cr.arc(r, body_h - r, r, math.pi / 2, math.pi)
        cr.line_to(0, r)
        cr.arc(r, r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()

        cr.set_source_rgba(1, 1, 1, 0.95)
        cr.fill_preserve()
        cr.set_source_rgba(0.9, 0.55, 0.1, 1)
        cr.set_line_width(2.5)
        cr.stroke()

        cr.set_source_rgba(0.15, 0.15, 0.15, 1)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(12)

        lines = []
        words = self.message.split()
        current_line = ""
        for word in words:
            test = current_line + " " + word if current_line else word
            extents = cr.text_extents(test)
            if extents.width > w - 24:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test
        if current_line:
            lines.append(current_line)

        line_h = 16
        total_text_h = len(lines) * line_h
        start_y = (body_h - total_text_h) // 2 + 12
        for i, line in enumerate(lines):
            extents = cr.text_extents(line)
            x = (w - extents.width) // 2
            cr.move_to(x, start_y + i * line_h)
            cr.show_text(line)

        return True
