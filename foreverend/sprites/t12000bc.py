import pygame

from foreverend.particles import FlameThrowerParticleSystem
from foreverend.sprites.base import Sprite
from foreverend.sprites.items import FlameThrower
from foreverend.sprites.player import Player
from foreverend.timer import Timer


class IceBoulder(Sprite):
    MELT_AMOUNT = 5

    def __init__(self, *args, **kwargs):
        super(IceBoulder, self).__init__('12000bc/ice_boulder',
                                         *args, **kwargs)
        #self.use_pixel_collisions = True
        self.melting = False

    def melt(self, x, y):
        self.explosion = FlameThrowerParticleSystem(self.layer.area)
        self.explosion.start(x, y)
        self.explosion.repeat = True

        self.timer = Timer(60, self.on_melt_timer)
        self.melting = True

    def on_melt_timer(self):
        new_height = self.image.get_height() - self.MELT_AMOUNT

        if new_height <= 0:
            self.timer.stop()
            self.explosion.stop()
            self.remove()
        else:
            self.image = self.image.subsurface(
                pygame.Rect(0, 0, self.image.get_width(), new_height))
            self.move_to(self.rect.left, self.rect.top + self.MELT_AMOUNT)

    def handle_collision(self, obj, *args, **kwargs):
        if (not self.melting and
            isinstance(obj, Player) and
            obj.tractor_beam.item and
            isinstance(obj.tractor_beam.item, FlameThrower)):
            flamethrower = obj.tractor_beam.item
            self.melt(flamethrower.rect.right, flamethrower.rect.centery)
