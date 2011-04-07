import pygame

from foreverend.particles import ExplosionParticleSystem
from foreverend.sprites.base import Sprite
from foreverend.timer import Timer


class IceBoulder(Sprite):
    MELT_AMOUNT = 5

    def __init__(self, *args, **kwargs):
        super(IceBoulder, self).__init__('12000bc/ice_boulder',
                                         *args, **kwargs)
        self.use_pixel_collisions = True

    def melt(self):
        self.explosion = ExplosionParticleSystem(self.layer.time_period)
        self.explosion.start(self.rect.centerx, self.rect.bottom - 80)

        self.timer = Timer(60, self.on_melt_timer)

    def on_melt_timer(self):
        new_height = self.image.get_height() - self.MELT_AMOUNT

        if new_height <= 0:
            self.timer.stop()
            self.hide()
        else:
            self.image = self.image.subsurface(
                pygame.Rect(0, 0, self.image.get_width(), new_height))
            self.move_to(self.rect.left, self.rect.top + self.MELT_AMOUNT)

    def handle_collision(self, *args, **kwargs):
        # Temporary
        self.melt()
