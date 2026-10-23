"""Optional wireless-gamepad reader. Safe to import without pygame."""
import threading, time

class Gamepad:
    def __init__(self):
        self.axes, self.buttons, self._ok = [], [], False
        try:
            import pygame
            pygame.init(); pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                return
            self._pg = pygame
            self._js = pygame.joystick.Joystick(0); self._js.init()
            self._ok = True
            threading.Thread(target=self._loop, daemon=True).start()
        except Exception:
            pass

    def _loop(self):
        while True:
            self._pg.event.pump()
            self.axes = [round(self._js.get_axis(i), 3) for i in range(self._js.get_numaxes())]
            self.buttons = [self._js.get_button(i) for i in range(self._js.get_numbuttons())]
            time.sleep(0.01)

    def state(self):
        return {"axes": self.axes, "buttons": self.buttons} if self._ok else None
