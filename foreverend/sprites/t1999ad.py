from foreverend.sprites.base import Sprite
from foreverend.sprites.common import Mountain


class Elevator(Sprite):
    def __init__(self):
        super(Elevator, self).__init__('1999ad/elevator')
        self.collidable = False
        self.destination = None

    def trigger(self):
        if self.destination:
            player = self.layer.level.engine.player
            dest_rect = self.destination.rect

            player.move_to(
                dest_rect.left + (dest_rect.width - player.rect.width) / 2,
                dest_rect.bottom - player.rect.height)


class Mountain1999AD(Mountain):
    BASE_COLLISION_RECTS = Mountain.BASE_COLLISION_RECTS + [
        (443, 126, 100, 100),
    ]
    def __init__(self):
        super(Mountain1999AD, self).__init__('1999ad/mountain')
