import pygame

from foreverend.sprites.base import Sprite
from foreverend.sprites.player import Player


class Volcano(Sprite):
    BASE_CAVERN_RECT = pygame.Rect(0, 310, 550, 55)

    def __init__(self, name='65000000bc/volcano'):
        super(Volcano, self).__init__(name)
        self.cavern_rect = self.BASE_CAVERN_RECT
        self.default_name = name
        self.interior_name = name + '_inside'

    def on_moved(self):
        self.cavern_rect.left = self.rect.left + self.BASE_CAVERN_RECT.left
        self.cavern_rect.top = self.rect.top + self.BASE_CAVERN_RECT.top
        self.ground_rect = pygame.Rect(self.rect.left, self.cavern_rect.bottom,
                                       self.rect.width, self.rect.width)
        self.collision_rects = [
            pygame.Rect(self.rect.left, self.rect.top, self.rect.width,
                        self.cavern_rect.top - self.rect.top),
            pygame.Rect(self.cavern_rect.right,
                        self.cavern_rect.top,
                        self.rect.width - self.cavern_rect.width,
                        self.cavern_rect.height),
            self.ground_rect,
        ]

    def handle_collision(self, obj, matched_rect, dx, dy):
        if (isinstance(obj, Player) and dy > 0 and
            matched_rect == self.ground_rect):
            self.name = self.interior_name
            self.update_image()

    def handle_stop_colliding(self, obj):
        if (self.name == self.interior_name and isinstance(obj, Player) and
            not obj.rect.colliderect(self.rect)):
            self.name = self.default_name
            self.update_image()