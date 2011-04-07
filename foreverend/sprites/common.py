import pygame
from pygame.locals import *

from foreverend.eventbox import EventBox
from foreverend.signals import Signal
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


class Button(Sprite):
    def __init__(self, name):
        super(Button, self).__init__(name)
        self.pressed = Signal()

    def handle_collision(self, *args, **kwargs):
        self.pressed.emit()


class Door(Sprite):
    def __init__(self, name):
        super(Door, self).__init__(name)
        self.collidable = False
        self.destination = None

    def on_added(self, layer):
        layer.area.register_for_events(self)

    def on_removed(self, layer):
        layer.area.unregister_for_events(self)

    def handle_event(self, event):
        if (event.type == KEYDOWN and event.key in (K_UP, K_DOWN) and
            self.destination):
            assert isinstance(self.destination, Door)

            player = self.layer.area.engine.player
            dest_rect = self.destination.rect

            dest_area = self.destination.layer.area
            assert dest_area.level == self.layer.area.level

            if self.layer.area != dest_area:
                dest_area.level.switch_area(dest_area)

            player.move_to(
                dest_rect.left + (dest_rect.width - player.rect.width) / 2,
                dest_rect.bottom - player.rect.height)

            return True

        return False


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

    def add_to(self, area):
        area.bg_layer.add(self.bg_sprite)
        area.main_layer.add(self.bottom_sprite)
        area.main_layer.add(self.top_sprite)
        area.fg_layer.add(self.cover_sprite)

        for sprite in self.left_sprites:
            area.main_layer.add(sprite)

        for sprite in self.right_sprites:
            area.main_layer.add(sprite)

        self.cave_eventbox = EventBox(area)
        self.cave_eventbox.object_moved.connect(
            self.on_cave_eventbox_moved)
        self.cave_eventbox.watch_object_moves(area.engine.player)

        self.floor_eventbox = EventBox(area)
        self.floor_eventbox.object_entered.connect(
            lambda x: self.cover_sprite.hide())
        self.floor_eventbox.watch_object_moves(area.engine.player)

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
