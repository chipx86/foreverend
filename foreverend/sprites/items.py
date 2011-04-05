import pygame
from pygame.locals import *

from foreverend.signals import Signal
from foreverend.sprites.base import Sprite


class Item(Sprite):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(obey_gravity=True, *args, **kwargs)
        self.should_check_collisions = True
        self.grabbable = True

        # Signals
        self.grab_changed = Signal()


class Artifact(Item):
    def __init__(self, num):
        super(Artifact, self).__init__('artifact%s' % num)


class Dynamite(Item):
    def __init__(self):
        super(Dynamite, self).__init__('1999ad/dynamite')
