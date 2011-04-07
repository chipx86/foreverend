from foreverend.sprites.base import Sprite


class Cactus(Sprite):
    def __init__(self):
        super(Cactus, self).__init__('1000ad/cactus')
        self.lethal = True
        self.use_pixel_collisions = True
