from foreverend.sprites.base import Direction
from foreverend.timer import Timer


class FloatEffect(object):
    def __init__(self, obj):
        self.obj = obj
        self.float_timer = None
        self.up_count = 0
        self.down_count = 0
        self.pause_count = 0
        self.float_paused = False
        self.max_movement = 2
        self.max_pause_count = 6
        self.float_distance = 1
        self.direction = Direction.UP

    def start(self):
        self.float_timer = Timer(150, self.on_float)
        self.float_timer.start()

    def stop(self):
        self.float_timer.stop()
        self.float_timer = None

    def on_float(self):
        dy = 0

        if self.float_paused:
            self.pause_count += 1

            if self.pause_count == self.max_pause_count:
                self.float_paused = False
                self.pause_count = 0
        elif self.direction == Direction.UP:
            dy = -self.float_distance
            self.up_count += 1

            if self.up_count == self.max_movement:
                self.direction = Direction.DOWN
                self.float_paused = True
                self.up_count = 0
        elif self.direction == Direction.DOWN:
            dy = self.float_distance
            self.down_count += 1

            if self.down_count == self.max_movement:
                self.direction = Direction.UP
                self.down_count = 0

        if self.obj.reverse_gravity:
            dy = -dy

        if dy != 0:
            self.obj.move_by(0, dy)
