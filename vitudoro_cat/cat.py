import os
import random
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from vitudoro_cat.pomodoro import PomodoroTimer

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "kitten")
GRAVITY = 2
WALK_SPEED = 3
JUMP_VELOCITY = -18
UPDATE_INTERVAL = 33

STATE_IDLE = 0
STATE_WALKING = 1
STATE_FALLING = 2
STATE_JUMPING = 3
STATE_DRAGGING = 4


class CatWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.stick()

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.scale_factor = 1.0
        self._load_frames()
        self._update_monitor_info()

        self.state = STATE_FALLING
        self.vx = 0
        self.vy = 0
        self.facing_right = random.choice([True, False])
        self.idle_timer = 0
        self.frame_index = 0
        self.animation_timer = 0

        mon = self.monitors[0] if self.monitors else {"x": 0, "y": 0, "w": 1920, "h": 1080}
        self.cat_x = random.randint(mon["x"], mon["x"] + mon["w"] - self.display_w)
        self.cat_y = mon["y"]

        self.move(self.cat_x, self.cat_y)
        self.set_size_request(self.display_w, self.display_h)

        self.image = Gtk.Image()
        self.add(self.image)
        self._update_frame()

        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.on_right_click = None

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.connect("button-press-event", self._on_button_press)
        self.connect("button-release-event", self._on_button_release)
        self.connect("motion-notify-event", self._on_motion)
        self.connect("draw", self._on_draw)

        self.pomodoro = PomodoroTimer(self)
        self.mouse_chase_active = False
        self.mouse_chase_timer_id = None
        self.mouse_chase_pause_id = None

        GLib.timeout_add(UPDATE_INTERVAL, self._update)

    def _update_monitor_info(self):
        display = Gdk.Display.get_default()
        n_monitors = display.get_n_monitors()
        self.monitors = []
        for i in range(n_monitors):
            mon = display.get_monitor(i)
            geo = mon.get_geometry()
            self.monitors.append({
                "x": geo.x, "y": geo.y,
                "w": geo.width, "h": geo.height,
            })

    def _get_current_monitor(self):
        cx = self.cat_x + self.display_w // 2
        cy = self.cat_y + self.display_h // 2
        for m in self.monitors:
            if m["x"] <= cx < m["x"] + m["w"] and m["y"] <= cy < m["y"] + m["h"]:
                return m
        best = None
        best_dist = float("inf")
        for m in self.monitors:
            mcx = m["x"] + m["w"] // 2
            mcy = m["y"] + m["h"] // 2
            dist = abs(cx - mcx) + abs(cy - mcy)
            if dist < best_dist:
                best_dist = dist
                best = m
        return best or self.monitors[0]

    def _load_frames(self):
        self.original_frames = []
        for i in range(10):
            path = os.path.join(ASSETS_DIR, f"{i}.png")
            if os.path.exists(path):
                self.original_frames.append(GdkPixbuf.Pixbuf.new_from_file(path))
            else:
                self.original_frames.append(None)
        self.frame_w = 161
        self.frame_h = 154
        self._scale_frames()

    def _scale_frames(self):
        self.display_w = int(self.frame_w * self.scale_factor)
        self.display_h = int(self.frame_h * self.scale_factor)
        self.frames = []
        for pb in self.original_frames:
            if pb:
                self.frames.append(
                    pb.scale_simple(self.display_w, self.display_h, GdkPixbuf.InterpType.NEAREST)
                )
            else:
                self.frames.append(None)
        self.frames_flipped = []
        for pb in self.frames:
            if pb:
                self.frames_flipped.append(pb.flip(True))
            else:
                self.frames_flipped.append(None)

    def set_scale(self, factor):
        self.scale_factor = factor
        self._scale_frames()
        self.set_size_request(self.display_w, self.display_h)
        self.resize(self.display_w, self.display_h)
        self._update_frame()

    def _on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(0)
        cr.paint()
        cr.set_operator(2)
        return False

    def _on_button_press(self, widget, event):
        if event.button == 1:
            self.dragging = True
            self.state = STATE_DRAGGING
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
        elif event.button == 3:
            if self.mouse_chase_active:
                self.stop_mouse_chase()
            elif self.on_right_click:
                self.on_right_click()

    def _on_button_release(self, widget, event):
        if event.button == 1 and self.dragging:
            self.dragging = False
            self.state = STATE_FALLING
            self.vy = 0

    def _on_motion(self, widget, event):
        if self.dragging:
            self.cat_x = int(event.x_root - self.drag_offset_x)
            self.cat_y = int(event.y_root - self.drag_offset_y)
            self.move(self.cat_x, self.cat_y)

    def _update(self):
        if self.state == STATE_DRAGGING:
            self._animate()
            return True

        if self.mouse_chase_timer_id:
            return True

        mon = self._get_current_monitor()
        floor_y = mon["y"] + mon["h"] - self.display_h
        on_ground = self.cat_y >= floor_y - 2

        if not on_ground and self.state in (STATE_WALKING, STATE_IDLE):
            self.state = STATE_FALLING

        if self.state in (STATE_FALLING, STATE_JUMPING):
            self.vy += GRAVITY

        if self.state == STATE_IDLE:
            self.vx = 0

        self.cat_x += self.vx
        self.cat_y += self.vy

        mon = self._get_current_monitor()
        floor_y = mon["y"] + mon["h"] - self.display_h

        if self.cat_y >= floor_y:
            self.cat_y = floor_y
            self.vy = 0
            if self.state in (STATE_FALLING, STATE_JUMPING):
                self._pick_action()

        if self.cat_y < mon["y"]:
            self.cat_y = mon["y"]
            self.vy = 0

        cat_center_x = self.cat_x + self.display_w // 2
        in_any_monitor = False
        for m in self.monitors:
            if m["x"] <= cat_center_x < m["x"] + m["w"]:
                in_any_monitor = True
                break

        if not in_any_monitor:
            self.cat_x = random.randint(mon["x"], mon["x"] + mon["w"] - self.display_w)
            self.cat_y = mon["y"]
            self.state = STATE_FALLING
            self.vx = 0
            self.vy = 0

        if self.state == STATE_WALKING:
            self.idle_timer = 0
            if random.random() < 0.01:
                self.state = STATE_IDLE
                self.vx = 0
                self.idle_timer = random.randint(20, 80)
            elif random.random() < 0.005:
                self._jump()
        elif self.state == STATE_IDLE:
            self.idle_timer -= 1
            if self.idle_timer <= 0:
                self._pick_action()

        self._animate()
        self.move(int(self.cat_x), int(self.cat_y))
        return True

    def _pick_action(self):
        if random.random() < 0.6:
            self.state = STATE_WALKING
            direction = 1 if random.random() > 0.5 else -1
            self.vx = direction * WALK_SPEED
            self.facing_right = direction > 0
        else:
            self.state = STATE_IDLE
            self.idle_timer = random.randint(20, 80)

    def _jump(self):
        self.state = STATE_JUMPING
        self.vy = JUMP_VELOCITY
        direction = 1 if self.facing_right else -1
        self.vx = direction * WALK_SPEED * 2

    def _animate(self):
        self.animation_timer += 1
        if self.mouse_chase_timer_id:
            chase_frames = [8, 9]
            idx = (self.animation_timer // 30) % len(chase_frames)
            self.frame_index = chase_frames[idx]
        elif self.state == STATE_WALKING:
            idx = (self.animation_timer // 4) % 4
            self.frame_index = idx
        elif self.state == STATE_IDLE:
            self.frame_index = 4
        elif self.state in (STATE_JUMPING, STATE_FALLING):
            self.frame_index = 5
        elif self.state == STATE_DRAGGING:
            drag_frames = [6, 7] if self.frames[6] and self.frames[7] else [1, 3]
            idx = (self.animation_timer // 8) % len(drag_frames)
            self.frame_index = drag_frames[idx]
        self._update_frame()

    def _update_frame(self):
        if self.facing_right:
            pb = self.frames[self.frame_index] if self.frame_index < len(self.frames) else None
        else:
            pb = self.frames_flipped[self.frame_index] if self.frame_index < len(self.frames_flipped) else None
        if pb:
            self.image.set_from_pixbuf(pb)

    def start_mouse_chase(self):
        self.mouse_chase_active = True
        self._jump_to_mouse()

    def stop_mouse_chase(self):
        self.mouse_chase_active = False
        if self.mouse_chase_timer_id:
            GLib.source_remove(self.mouse_chase_timer_id)
            self.mouse_chase_timer_id = None
        if self.mouse_chase_pause_id:
            GLib.source_remove(self.mouse_chase_pause_id)
            self.mouse_chase_pause_id = None
        self.state = STATE_FALLING
        self.vy = 0
        self.vx = 0

    def _get_mouse_pos(self):
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        screen, mx, my = pointer.get_position()
        return screen, pointer, mx, my

    def _warp_mouse(self, pointer, screen, x, y):
        pointer.warp(screen, x, y)

    def _jump_to_mouse(self):
        if not self.mouse_chase_active:
            return
        screen, pointer, mx, my = self._get_mouse_pos()
        self.cat_x = mx - self.display_w // 2
        mon = self._get_current_monitor()
        floor_y = mon["y"] + mon["h"] - self.display_h
        self.cat_y = floor_y
        self.state = STATE_JUMPING
        self.vy = JUMP_VELOCITY * 1.5
        self.vx = 0
        self.facing_right = mx > self.cat_x + self.display_w // 2
        self.move(int(self.cat_x), int(self.cat_y))
        self._animate()
        GLib.timeout_add(600, self._start_dragging_mouse)

    def _start_dragging_mouse(self):
        if not self.mouse_chase_active:
            return False
        screen, pointer, mx, my = self._get_mouse_pos()
        self.cat_x = mx - self.display_w // 2
        self.cat_y = my + 5
        self.move(int(self.cat_x), int(self.cat_y))
        self.mouse_chase_timer_id = GLib.timeout_add(UPDATE_INTERVAL, self._drag_mouse_tick)
        GLib.timeout_add(10000, self._pause_chase)
        return False

    def _drag_mouse_tick(self):
        if not self.mouse_chase_active:
            return False

        screen, pointer, mx, my = self._get_mouse_pos()
        mon = self._get_current_monitor()

        move_y = 4
        new_my = my + move_y
        floor_limit = mon["y"] + mon["h"] - 30
        if new_my >= floor_limit:
            new_my = floor_limit

        self._warp_mouse(pointer, screen, mx, new_my)

        floor_y = mon["y"] + mon["h"] - self.display_h
        self.cat_x = mx - self.display_w // 2
        self.cat_y = min(new_my + 5, floor_y)
        self.state = STATE_WALKING
        self.animation_timer += 1
        chase_frames = [8, 9]
        idx = (self.animation_timer // 30) % len(chase_frames)
        self.frame_index = chase_frames[idx]
        self._update_frame()
        self.move(int(self.cat_x), int(self.cat_y))
        return True

    def _pause_chase(self):
        if not self.mouse_chase_active:
            return False
        if self.mouse_chase_timer_id:
            GLib.source_remove(self.mouse_chase_timer_id)
            self.mouse_chase_timer_id = None
        mon = self._get_current_monitor()
        floor_y = mon["y"] + mon["h"] - self.display_h
        self.cat_y = floor_y
        self.cat_x = max(mon["x"], min(self.cat_x, mon["x"] + mon["w"] - self.display_w))
        self.vx = 0
        self.vy = 0
        self.state = STATE_IDLE
        self._animate()
        self.move(int(self.cat_x), int(self.cat_y))
        self.mouse_chase_pause_id = GLib.timeout_add(4000, self._resume_chase)
        return False

    def _resume_chase(self):
        if not self.mouse_chase_active:
            return False
        self.mouse_chase_pause_id = None
        self._jump_to_mouse()
        return False
