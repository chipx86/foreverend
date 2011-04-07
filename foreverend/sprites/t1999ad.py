from pygame.locals import *

from foreverend.sprites.base import Sprite
from foreverend.sprites.common import Door, Mountain


class Elevator(Door):
    def __init__(self):
        super(Elevator, self).__init__('1999ad/elevator')
        self.destination = None
