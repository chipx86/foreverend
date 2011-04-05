import pygame

from foreverend.sprites.base import Sprite
from foreverend.sprites.player import Player


class Box(Sprite):
    def __init__(self, width, height, color=(238, 238, 238)):
        super(Box, self).__init__('box')
        self.rect.width = width
        self.rect.height = height
        self.color = color

    def generate_image(self):
        surface = pygame.Surface(self.rect.size).convert_alpha()
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1)
        return surface


class Mountain(Sprite):
    BASE_COLLISION_RECTS = [
        (0, 991, 1565, 11),
        (0, 954, 140, 37),
        (0, 900, 140, 54),
        (1467, 954, 98, 37),
        (1459, 937, 94, 17),
        (1450, 922, 96, 15),
        (1428, 878, 96, 22),
        (443, 219, 93, 40),
        (350, 230, 93, 100),
    ]

    def __init__(self, name):
        super(Mountain, self).__init__(name)
        self.default_name = name
        self.interior_name = name + '_interior'

    def on_moved(self):
        self.collision_rects = [
            pygame.Rect(self.rect.left + x, self.rect.top + y, w, h)
            for x, y, w, h in self.BASE_COLLISION_RECTS
        ]

    def handle_collision(self, obj, matched_rect, dx, dy):
        if (isinstance(obj, Player) and dy > 0 and
            self.rect.contains(matched_rect)):
            self.name = self.interior_name
            self.update_image()

    def handle_stop_colliding(self, obj):
        if (self.name == self.interior_name and isinstance(obj, Player) and
            not self.rect.contains(obj.rect)):
            self.name = self.default_name
            self.update_image()
