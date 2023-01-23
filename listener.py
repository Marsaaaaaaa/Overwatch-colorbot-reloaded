from pynput import mouse, keyboard


class Listener():

    def __init__():
       dababy = True

    def on_move(x, y):
        print('Pointer moved to {0}'.format(
            (x, y)))

    def on_click(key_code, pressed):
         
        if not pressed:
            return False
        else:
            return True

    def on_scroll(x, y, dx, dy):
        print('Scrolled {0} at {1}'.format(
            'down' if dy < 0 else 'up',
            (x, y)))

    # Collect events until released
    def mouse_listener(self):
        with mouse.Listener(
                on_move = self.on_move,
                on_click = self.on_click,
                on_scroll = self.on_scroll) as listener:
            listener.join()

