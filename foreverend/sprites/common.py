import pygame

from foreverend.eventbox import EventBox
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


class Mountain(object):
    LEFT_OFFSETS = [0, 90, 189, 239, 313]
    RIGHT_OFFSETS = [1427, 1236, 1208, 1121, 940]

    def __init__(self):
        self.bg_sprite = Sprite('mountain_bg')

        self.cover_sprite = Sprite('mountain_cover')
        self.cover_sprite.collidable = False

        self.bottom_sprite = Sprite('mountain_bottom')
        self.bottom_sprite.use_pixel_collisions = True
        self.bottom_sprite.update_image()

        self.top_sprite = Sprite('mountain_top')
        self.top_sprite.use_pixel_collisions = True
        self.top_sprite.update_image()

        self.left_sprites = []
        self.right_sprites = []

        for i in range(1, 6):
            sprite = Sprite('mountain_left_%s' % i)
            sprite.use_pixel_collisions = True
            sprite.update_image()
            self.left_sprites.append(sprite)

            sprite = Sprite('mountain_right_%s' % i)
            sprite.use_pixel_collisions = True
            sprite.update_image()
            self.right_sprites.append(sprite)

        self.rect = pygame.Rect(
            0, 0, self.bottom_sprite.rect.width,
            sum([sprite.rect.height for sprite in self.right_sprites]) +
            self.top_sprite.rect.height + self.bottom_sprite.rect.height)

    def add_to(self, time_period):
        time_period.bg_layer.add(self.bg_sprite)
        time_period.main_layer.add(self.bottom_sprite)
        time_period.main_layer.add(self.top_sprite)
        time_period.fg_layer.add(self.cover_sprite)

        for sprite in self.left_sprites:
            time_period.main_layer.add(sprite)

        for sprite in self.right_sprites:
            time_period.main_layer.add(sprite)

        self.cave_eventbox = EventBox(time_period)
        self.cave_eventbox.object_moved.connect(
            self.on_cave_eventbox_moved)
        self.cave_eventbox.watch_object_moves(time_period.engine.player)

        self.floor_eventbox = EventBox(time_period)
        self.floor_eventbox.object_entered.connect(
            lambda x: self.cover_sprite.hide())
        self.floor_eventbox.watch_object_moves(time_period.engine.player)

    def move_to(self, x, y):
        self.rect.left = x
        self.rect.top = y

        self.cover_sprite.move_to(x, y)
        self.bg_sprite.move_to(x, y)
        self.top_sprite.move_to(x + 485, y)
        self.bottom_sprite.move_to(
            x, y + self.rect.height - self.bottom_sprite.rect.height)

        new_y = self.bottom_sprite.rect.top

        for i, sprite in enumerate(self.left_sprites):
            new_y = new_y - sprite.rect.height
            sprite.move_to(x + self.LEFT_OFFSETS[i], new_y)

        new_y = self.bottom_sprite.rect.top

        for i, sprite in enumerate(self.right_sprites):
            new_y = new_y - sprite.rect.height
            sprite.move_to(x + self.RIGHT_OFFSETS[i], new_y)

        self.cave_eventbox.rects.append(
            pygame.Rect(x + 382, y + 110, 157, 110))
        self.floor_eventbox.rects.append(
            pygame.Rect(x + 30, self.bottom_sprite.rect.top - 30,
                        self.rect.width - 60, 30))

    def on_cave_eventbox_moved(self, player):
        if player.rect.centerx <= self.cave_eventbox.rects[0].centerx:
            self.cover_sprite.show()
        else:
            self.cover_sprite.hide()
