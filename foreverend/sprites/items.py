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

        # Signals
        self.grab_changed = Signal()


class Artifact(Item):
    def __init__(self, area, num):
        super(Artifact, self).__init__('artifact%s' % num)
        self.float_effect = FloatEffect(self)
        self.grab_changed.connect(self.float_effect.stop)
        self.float_effect.start()


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
        self.flip_image = True


# Not technically an item, but close enough for now.
class Snake(Item):
    MOVE_SPEED = 3

    def __init__(self):
        super(Snake, self).__init__('1000ad/snake')
        self.flip_image = True
        self.lethal = True
        self.velocity = (-self.MOVE_SPEED, 0)
        self.direction = Direction.LEFT

        self.direction_changed.connect(self.on_direction_changed)

    def on_direction_changed(self):
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
