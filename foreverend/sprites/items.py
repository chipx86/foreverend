import pygame
from pygame.locals import *

from foreverend.effects import FloatEffect
from foreverend.signals import Signal
from foreverend.sprites.base import Direction, Sprite
from foreverend.timer import Timer


class Item(Sprite):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(obey_gravity=True, *args, **kwargs)
        self.should_check_collisions = True
        self.grabbable = True
        self.flip_image = True

        # Signals
        self.grab_changed = Signal()


class Artifact(Item):
    def __init__(self, area, num):
        super(Artifact, self).__init__('artifact%s' % num)
        self.float_effect = FloatEffect(self)
        self.grab_changed.connect(self.float_effect.stop)
        self.float_effect.start()

    def should_adjust_position_with(self, obj, dx, dy):
        return False


class Dynamite(Item):
    def __init__(self):
        super(Dynamite, self).__init__('1999ad/dynamite')

    def light(self):
        self.name = '1999ad/dynamite_lit'
        self.update_image()
        self.grabbable = False


class FlameThrower(Item):
    def __init__(self):
        super(FlameThrower, self).__init__('2300ad/flamethrower')


class Vehicle(Item):
    pass


class Hoverboard(Vehicle):
    def __init__(self):
        super(Hoverboard, self).__init__('2300ad/hoverboard')
        self.obey_gravity = False
        self.use_pixel_collisions = True

        self.float_effect = FloatEffect(self)

        self.grab_changed.connect(self.on_grab_changed)
        self.player = None

    def should_adjust_position_with(self, obj, dx, dy):
        return obj != self.player or self.player.vehicle != self

    def on_added(self, layer):
        self.player = layer.area.level.engine.player
        self.float_effect.start()

    def on_removed(self, layer):
        self.float_effect.stop()

    def on_grab_changed(self):
        if self.grabbed:
            self.float_effect.start()
        else:
            self.float_effect.stop()


# Not technically an item, but close enough for now.
class Snake(Item):
    MOVE_SPEED = 3

    def __init__(self):
        super(Snake, self).__init__('1000ad/snake')
        self.lethal = True
        self.velocity = (-self.MOVE_SPEED, 0)
        self.direction = Direction.LEFT

        self.direction_changed.connect(self.update_velocity)
        self.grab_changed.connect(self.update_velocity)

    def update_velocity(self):
        if self.grabbed:
            self.velocity = (0, 0)
        else:
            if self.direction == Direction.RIGHT:
                self.velocity = (self.MOVE_SPEED, self.velocity[1])
            elif self.direction == Direction.LEFT:
                self.velocity = (-self.MOVE_SPEED, self.velocity[1])

    def on_collision(self, dx, dy, obj, self_rect, obj_rect):
        if dx != 0:
            if self.direction == Direction.LEFT:
                self.direction = Direction.RIGHT
            elif self.direction == Direction.RIGHT:
                self.direction = Direction.LEFT

        super(Snake, self).on_collision(dx, dy, obj, self_rect, obj_rect)


class TriangleKey(Item):
    def __init__(self):
        super(TriangleKey, self).__init__('300ne/triangle_key')

        # We want this to always match the keyhole.
        self.flip_image = False
