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
