import pygame
from pygame.locals import *

from foreverend.sprites.base import Sprite


class Item(Sprite):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(obey_gravity=True, *args, **kwargs)
        self.should_check_collisions = True


class Dynamite(Item):
    def __init__(self):
        super(Dynamite, self).__init__('1999ad/dynamite')
