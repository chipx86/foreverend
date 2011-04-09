import pygame

from foreverend.signals import Signal
from foreverend.sprites.base import Direction, Sprite
from foreverend.timer import Timer


class Effect(object):
    def __init__(self):
        self.timer = None
        self.timer_ms = 150

        # Signals
        self.started = Signal()
        self.stopped = Signal()

    def pre_start(self):
        pass

    def pre_stop(self):
        pass

    def start(self):
        assert not self.timer
        self.pre_start()
        self.timer = Timer(self.timer_ms, self.on_tick)
        self.timer.start()
        self.started.emit()

    def stop(self):
        assert self.timer
        self.pre_stop()
        self.timer.stop()
        self.timer = None
        self.stopped.emit()

    def on_tick(self):
        pass


class ScreenEffect(Effect):
    def __init__(self, layer, rect):
        super(ScreenEffect, self).__init__()
        self.rect = rect

        self.sprite = Sprite(None)
        self.sprite.image = pygame.Surface(rect.size).convert_alpha()
        self.sprite.move_to(*rect.topleft)

        if layer:
            layer.add(self.sprite)


class ScreenFadeEffect(ScreenEffect):
    def __init__(self, *args, **kwargs):
        super(ScreenFadeEffect, self).__init__(*args, **kwargs)
        self.color = (0, 0, 0)
        self.fade_from_alpha = 0
        self.fade_to_alpha = 255
        self.fade_time_ms = 500
        self.timer_ms = 30

    def pre_start(self):
        self.sprite.show()
        self.alpha = self.fade_from_alpha
        self.alpha_delta = ((self.fade_to_alpha - self.fade_from_alpha) /
                            (self.fade_time_ms / self.timer_ms))
        self.sprite.image.fill(
            (self.color[0], self.color[1], self.color[2], self.alpha))

    def on_tick(self):
        self.sprite.image.fill(
            (self.color[0], self.color[1], self.color[2], self.alpha))

        self.alpha += self.alpha_delta

        if ((self.fade_from_alpha > self.fade_to_alpha and
             self.alpha <= self.fade_to_alpha) or
            (self.fade_from_alpha < self.fade_to_alpha and
             self.alpha >= self.fade_to_alpha)):
            self.stop()


class ScreenFlashEffect(ScreenEffect):
    def __init__(self, *args, **kwargs):
        super(ScreenFlashEffect, self).__init__(*args, **kwargs)
        self.fade_out = True
        self.color = (255, 255, 255)

        self.flash_peaked = Signal()

    def pre_start(self):
        self.hit_peak = False
        self.alpha = 100
        self.sprite.show()

        self._fill(0)

    def _fill(self, alpha):
        self.sprite.image.fill((self.color[0], self.color[1], self.color[2],
                                alpha))

    def on_tick(self):
        self._fill(self.alpha)

        if self.hit_peak:
            self.alpha = max(self.alpha - 20, 0)
        else:
            self.alpha = min(self.alpha + 20, 255)

        if self.alpha == 255:
            self.hit_peak = True
            self.flash_peaked.emit()

            if not self.fade_out:
                self.stop()
        elif self.alpha <= 0:
            self.stop()



class TransitionEffect(Effect):
    def __init__(self, obj):
        super(TransitionEffect, self).__init__()
        self.obj = obj


class MoveEffect(TransitionEffect):
    def __init__(self, obj):
        super(MoveEffect, self).__init__(obj)
        self.destination = None
        self.old_collidable = False
        self.old_obey_gravity = False
        self.start_x = 0
        self.start_y = 0
        self.total_time_ms = 3000

    def pre_start(self):
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

    def pre_stop(self):
        self.obj.collidable = self.old_collidable
        self.obj.obey_gravity = self.old_obey_gravity

    def on_tick(self):
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

    def on_tick(self):
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


class SlideHideEffect(TransitionEffect):
    def __init__(self, obj):
        super(SlideHideEffect, self).__init__(obj)
        self.direction = Direction.UP

    def pre_start(self):
        self.orig_x = self.obj.rect.left
        self.orig_y = self.obj.rect.top

        num_steps = self.total_time_ms / self.timer_ms

        if self.direction in (Direction.UP, Direction.DOWN):
            self.dx = 0
            self.dy = self.obj.image.get_height() / num_steps
        else:
            self.dx = self.obj.image.get_width() / num_steps
            self.dy = 0

    def pre_stop(self):
        self.obj.move_to(self.orig_x, self.orig_y)

    def on_tick(self):
        rect = pygame.Rect(0, 0,
                           self.obj.image.get_width() - self.dx,
                           self.obj.image.get_height() - self.dy)

        if rect.width <= 0 or rect.height <= 0:
            self.obj.hide()
            self.stop()
            return

        if self.direction == Direction.RIGHT:
            rect.left = self.dx
        elif self.direction == Direction.DOWN:
            rect.top = self.dy

        self.obj.image = self.obj.image.subsurface(rect)
        self.obj.move_to(self.obj.rect.left + rect.left,
                         self.obj.rect.top + rect.top)


class SlideShowEffect(TransitionEffect):
    def __init__(self, obj):
        super(SlideShowEffect, self).__init__(obj)
        self.direction = Direction.UP
        self.orig_image = None

    def pre_start(self):
        self.obj.update_image()
        self.orig_image = self.obj.image
        self.orig_x = self.obj.rect.left
        self.orig_y = self.obj.rect.top
        num_steps = self.total_time_ms / self.timer_ms

        self.dx = self.orig_image.get_width() / num_steps
        self.dy = self.orig_image.get_height()
        self.last_width = 0
        self.last_height = 0

        if self.direction in (Direction.UP, Direction.DOWN):
            self.dy /= num_steps
            self.last_width = self.orig_image.get_width()
        else:
            self.dx /= num_steps
            self.last_height = self.orig_image.get_height()

    def on_tick(self):
        rect = pygame.Rect(0, 0,
                           min(self.last_width + self.dx,
                               self.orig_image.get_width()),
                           min(self.last_height + self.dy,
                               self.orig_image.get_height()))

        if not self.obj.visible:
            self.obj.show()

        if self.direction == Direction.LEFT:
            rect.left = self.orig_image.get_width() - rect.width
        elif self.direction == Direction.UP:
            rect.top = self.orig_image.get_height() - rect.height

        self.obj.image = self.orig_image.subsurface(rect)
        self.obj.move_to(self.orig_x + rect.left,
                         self.orig_y + rect.top)

        self.last_width = self.obj.image.get_width()
        self.last_height = self.obj.image.get_height()

        if (rect.width == self.orig_image.get_width() and
            rect.height == self.orig_image.get_height()):
            self.stop()
            return


class ShakeEffect(TransitionEffect):
    def __init__(self, *args, **kwargs):
        super(ShakeEffect, self).__init__(*args, **kwargs)
        self.shake_distance = 2
        self.timer_ms = 60

    def pre_start(self):
        self.dx = self.shake_distance
        self.obj.move_by(self.dx, 0)

    def on_tick(self):
        self.dx = -self.dx
        self.obj.move_by(self.dx, 0)
