import pygame

from foreverend.levels.base import EventBox, Level, TimePeriod
from foreverend.sprites import Artifact, Box, IceBoulder, Sprite, TiledSprite
from foreverend.timer import Timer


class TimePeriod12000BC(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod12000BC, self).__init__(*args, **kwargs)
        self.bg.fill((219, 228, 252))
        self.name = '12,000 BC'

        level_width, level_height = self.level.size

        ground = TiledSprite('12000bc/ground', 6, 1)
        self.main_layer.add(ground)
        ground.move_to(0, level_height - ground.rect.height)
        x = ground.rect.right + 500

        tiles_x = (self.level.size[0] - x) / 144
        ground = TiledSprite('12000bc/ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(x, level_height - ground.rect.height)

        ice_hill = Sprite('12000bc/ice_hill_left')
        self.main_layer.add(ice_hill)
        ice_hill.use_pixel_collisions = True
        ice_hill.move_to(0, ground.rect.top - ice_hill.rect.height + 18)

        ice_hill = Sprite('12000bc/ice_hill_right')
        self.main_layer.add(ice_hill)
        ice_hill.use_pixel_collisions = True
        ice_hill.move_to(level_width - ice_hill.rect.width,
                         ground.rect.top - ice_hill.rect.height + 18)

        hill_bg = Sprite('12000bc/hill_bg')
        self.bg_layer.add(hill_bg)
        hill_bg.move_to(ice_hill.rect.right,
                        ground.rect.top - hill_bg.rect.height)

        hill_bg = Sprite('12000bc/hill_bg')
        self.bg_layer.add(hill_bg)
        hill_bg.move_to(ground.rect.left + 600,
                        ground.rect.top - hill_bg.rect.height)

        hill_bg = Sprite('12000bc/hill_bg')
        self.bg_layer.add(hill_bg)
        hill_bg.move_to(ground.rect.left + 2000,
                        ground.rect.top - hill_bg.rect.height)

        self.ice_boulder = IceBoulder()
        self.main_layer.add(self.ice_boulder)
        self.ice_boulder.move_to(
            2315, ground.rect.top - self.ice_boulder.rect.height)


class TimePeriod1000AD(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod1000AD, self).__init__(*args, **kwargs)
        self.bg.fill((255, 251, 219))
        self.name = '1000 AD'

        level_width, level_height = self.level.size

        tiles_x = self.level.size[0] / 144
        ground = TiledSprite('1000ad/ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, level_height - ground.rect.height)

        pyramid = Sprite('1000ad/pyramid')
        self.bg_layer.add(pyramid)
        pyramid.move_to(922, ground.rect.top - pyramid.rect.height)

        cactus = Sprite('1000ad/cactus')
        cactus.lethal = True
        self.main_layer.add(cactus)
        cactus.move_to(1050, ground.rect.top - cactus.rect.height)


class TimePeriod2300AD(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod2300AD, self).__init__(*args, **kwargs)
        self.bg.fill((238, 236, 232))
        self.name = '2300 AD'


class Level2(Level):
    def __init__(self, *args, **kwargs):
        super(Level2, self).__init__(*args, **kwargs)
        self.name = 'Level 2'
        self.size = (3956, 1600)
        self.start_pos = (1500,
                          self.size[1] - 64 - self.engine.player.rect.height)
        self.setup()

    def setup(self):
        self.add(TimePeriod12000BC(self))
        self.add(TimePeriod1000AD(self))
        self.add(TimePeriod2300AD(self))
