import pygame

from foreverend.levels.base import EventBox
from foreverend.sprites.base import Sprite, TiledSprite
from foreverend.sprites.common import Box
from foreverend.sprites.player import Player


class Volcano(object):
    BASE_CAVERN_RECT = pygame.Rect(0, 310, 600, 57)

    def __init__(self):
        self.lava_pool = TiledSprite('65000000bc/lava_pool', 4, 1)
        self.lava_pool.lethal = True

        self.lava_puddle = Sprite('65000000bc/volcano_lava_puddle')
        self.lava_puddle.collidable = False

        self.lava_puddle_blocker = Box(10, self.BASE_CAVERN_RECT.height,
                                       (0, 0, 0))

        self.top_sprite = Sprite('65000000bc/volcano_top')
        self.top_sprite.use_pixel_collisions = True
        self.top_sprite.update_image()

        self.bottom_sprite = Sprite('65000000bc/volcano_bottom')
        self.bottom_sprite.update_image()

        self.cavern_blocker = Box(self.bottom_sprite.rect.width / 2,
                                  self.BASE_CAVERN_RECT.height, (0, 0, 0))

        self.column_sprite = Sprite('65000000bc/volcano_column')
        self.column_sprite.use_pixel_collisions = True
        self.column_sprite.update_image()

        self.cover_sprite = Sprite('65000000bc/volcano_cover')
        self.cover_sprite.collidable = False

        self.rect = pygame.Rect(0, 0, self.bottom_sprite.rect.width,
                                self.top_sprite.rect.height +
                                self.BASE_CAVERN_RECT.height +
                                self.bottom_sprite.rect.height)

    def add_to(self, area):
        self.eventbox = EventBox(area)
        self.eventbox.object_entered.connect(
            lambda x: self.cover_sprite.hide())
        self.eventbox.object_exited.connect(
            lambda x: self.cover_sprite.show())
        self.eventbox.watch_object_moves(area.engine.player)

        area.main_layer.add(self.lava_puddle_blocker)
        area.main_layer.add(self.cavern_blocker)
        area.main_layer.add(self.lava_puddle)
        area.main_layer.add(self.lava_pool)
        area.main_layer.add(self.top_sprite)
        area.main_layer.add(self.bottom_sprite)
        area.main_layer.add(self.column_sprite)
        area.fg_layer.add(self.cover_sprite)

    def move_to(self, x, y):
        self.rect.left = x
        self.rect.top = y

        self.lava_pool.move_to(x + 360, y + 10)
        self.top_sprite.move_to(x, y)
        self.column_sprite.move_to(
            x + 578, y + self.rect.height - self.column_sprite.rect.height)
        self.bottom_sprite.move_to(
            x, y + self.rect.height - self.bottom_sprite.rect.height)
        self.lava_puddle.move_to(
            x + 574,
            self.bottom_sprite.rect.top - self.lava_puddle.rect.height + 4)
        self.lava_puddle_blocker.move_to(
            self.lava_puddle.rect.right - 10,
            self.lava_puddle.rect.bottom - self.lava_puddle_blocker.rect.height)
        self.cavern_blocker.move_to(
            self.column_sprite.rect.right,
            self.bottom_sprite.rect.top - self.cavern_blocker.rect.height)
        self.cover_sprite.move_to(
            x, y + self.rect.height - self.cover_sprite.rect.height)

        self.eventbox.rects.append(
            pygame.Rect(x, y + self.BASE_CAVERN_RECT.top,
                        self.rect.width, self.BASE_CAVERN_RECT.height))
        self.eventbox.rects.append(self.column_sprite.rect)

    def clear_passage(self):
        self.column_sprite.remove()
        self.lava_puddle.remove()
        self.lava_puddle_blocker.remove()
        self.cavern_blocker.remove()
