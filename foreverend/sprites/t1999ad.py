from pygame.locals import *

from foreverend.sprites.base import Sprite
from foreverend.sprites.common import Mountain


class Elevator(Sprite):
    def __init__(self):
        super(Elevator, self).__init__('1999ad/elevator')
        self.collidable = False
        self.destination = None

    def on_added(self, layer):
        layer.time_period.register_for_events(self)

    def on_removed(self, layer):
        layer.time_period.unregister_for_events(self)

    def handle_event(self, event):
        if (event.type == KEYDOWN and
            event.key in (K_UP, K_DOWN) and
            self.destination):
            player = self.layer.time_period.engine.player
            dest_rect = self.destination.rect

            player.move_to(
                dest_rect.left + (dest_rect.width - player.rect.width) / 2,
                dest_rect.bottom - player.rect.height)

            return True

        return False
