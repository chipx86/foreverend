from foreverend.signals import Signal
from foreverend.sprites.base import Direction
from foreverend.timer import Timer


class TransitionEffect(object):
    def __init__(self, obj):
        self.obj = obj
        self.timer = None
        self.timer_ms = 150

        # Signals
        self.started = Signal()
        self.stopped = Signal()

    def start(self):
        assert not self.timer
        self.timer = Timer(self.timer_ms, self._on_tick)
        self.timer.start()
        self.started.emit()

    def stop(self):
        assert self.timer
        self.timer.stop()
        self.timer = None
        self.stopped.emit()

    def _on_tick(self):
        pass


class MoveEffect(TransitionEffect):
    def __init__(self, obj):
        super(MoveEffect, self).__init__(obj)
        self.destination = None
        self.old_collidable = False
        self.old_obey_gravity = False
        self.start_x = 0
        self.start_y = 0
        self.total_time_ms = 3000

    def start(self):
        assert self.destination

        self.old_collidable = self.obj.collidable
        self.old_obey_gravity = self.obj.obey_gravity
        self.obj.collidable = False
        self.obj.obey_gravity = False
        self.obj.velocity = (0, 0)

        self.start_x = self.obj.rect.left
        self.start_y = self.obj.rect.top
        self.gradient = (float(self.destination[1] - self.start_y) /
                         float(self.destination[0] - self.start_x))

        self.step = 0
        self.num_steps = self.total_time_ms / self.timer_ms
        assert self.num_steps > 0

        diff_x = self.destination[0] - self.start_x
        self.dx = float(diff_x) / self.num_steps
        self.dy = (diff_x * self.gradient) / self.num_steps

        super(MoveEffect, self).start()

    def stop(self):
        super(MoveEffect, self).stop()
        self.obj.collidable = self.old_collidable
        self.obj.obey_gravity = self.old_obey_gravity

    def _on_tick(self):
        if self.step == self.num_steps:
            self.stop()
            return

        self.obj.move_to(int(self.start_x + self.dx * self.step),
                         int(self.start_y + self.dy * self.step))

        self.step += 1


class FloatEffect(TransitionEffect):
    def __init__(self, obj):
        super(FloatEffect, self).__init__(obj)
        self.up_count = 0
        self.down_count = 0
        self.pause_count = 0
        self.float_paused = False
        self.max_movement = 2
        self.max_pause_count = 6
        self.float_distance = 1
        self.direction = Direction.UP

    def _on_tick(self):
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
