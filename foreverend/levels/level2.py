import pygame

from foreverend.effects import FloatEffect
from foreverend.levels.base import Area, Level, TimePeriod
from foreverend.sprites import Box, Door, IceBoulder, Sprite, TiledSprite
from foreverend.timer import Timer


class Level2OutsideArea(Area):
    size = (3956, 1600)

    def __init__(self, *args, **kwargs):
        super(Level2OutsideArea, self).__init__(*args, **kwargs)
        self.start_pos = (1500,
                          self.size[1] - 64 - self.engine.player.rect.height)


class Level2PyramidArea(Area):
    size = (4000, 800)

    DOOR_X = 230
    PLATFORM_X = DOOR_X + 600
    PLATFORM_Y = 200
    PIT_TILES_X = 65

    def __init__(self, *args, **kwargs):
        super(Level2PyramidArea, self).__init__(*args, **kwargs)
        self.key = 'pyramid'
        self.start_pos = (100,
                          self.size[1] - 64 - self.engine.player.rect.height)


class Outside12000BC(Level2OutsideArea):
    def setup(self):
        self.bg.fill((219, 228, 252))

        level_width, level_height = self.size

        ground = TiledSprite('12000bc/ground', 6, 1)
        self.main_layer.add(ground)
        ground.move_to(0, level_height - ground.rect.height)
        x = ground.rect.right + 500

        tiles_x = (self.size[0] - x) / 144
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


class Outside1000AD(Level2OutsideArea):
    def __init__(self, *args, **kwargs):
        super(Outside1000AD, self).__init__(*args, **kwargs)
        self.pyramid_door = Door('1000ad/pyramid_door')

    def setup(self):
        self.bg.fill((255, 251, 219))

        level_width, level_height = self.size

        tiles_x = self.size[0] / 144
        ground = TiledSprite('1000ad/ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, level_height - ground.rect.height)

        cactus = Sprite('1000ad/cactus')
        cactus.lethal = True
        self.main_layer.add(cactus)
        cactus.move_to(100, ground.rect.top - cactus.rect.height)

        pyramid = Sprite('1000ad/pyramid')
        self.bg_layer.add(pyramid)
        pyramid.move_to(922, ground.rect.top - pyramid.rect.height)

        cactus = Sprite('1000ad/cactus')
        cactus.lethal = True
        self.main_layer.add(cactus)
        cactus.move_to(pyramid.rect.left + 100,
                       ground.rect.top - cactus.rect.height)

        cactus = Sprite('1000ad/cactus')
        cactus.lethal = True
        self.main_layer.add(cactus)
        cactus.move_to(2600, ground.rect.top - cactus.rect.height)

        self.pyramid_door.destination = self.time_period.areas['pyramid'].door
        self.main_layer.add(self.pyramid_door)
        self.pyramid_door.move_to(
            pyramid.rect.left + 621,
            pyramid.rect.bottom - self.pyramid_door.rect.height)

        # Artifact
        self.level.add_artifact(self, cactus.rect.right + 100, ground.rect.top)


class Pyramid1000AD(Level2PyramidArea):
    def __init__(self, *args, **kwargs):
        super(Pyramid1000AD, self).__init__(*args, **kwargs)
        self.door = Door('1000ad/pyramid_door')

    def setup(self):
        self.bg.fill((255, 251, 219))

        area_width, area_height = self.size

        tiles_y = area_height / 32
        wall = TiledSprite('1000ad/pyramid_wall', 4, tiles_y)
        self.main_layer.add(wall)
        wall.move_to(0, 0)

        ground = TiledSprite('1000ad/ground', 10, 1)
        self.main_layer.add(ground)
        ground.move_to(wall.rect.right, area_height - ground.rect.height)

        pit = TiledSprite('1000ad/spike', self.PIT_TILES_X, 1)
        pit.lethal = True
        self.main_layer.add(pit)
        pit.move_to(ground.rect.right, ground.rect.bottom - pit.rect.height)

        self.door.destination = self.time_period.areas['default'].pyramid_door
        self.main_layer.add(self.door)
        self.door.move_to(self.DOOR_X, ground.rect.top - self.door.rect.height)

        ground = TiledSprite('1000ad/ground', 5, 1)
        self.main_layer.add(ground)
        ground.move_to(pit.rect.right, area_height - ground.rect.height)

        tiles_y = area_height / 32
        wall = TiledSprite('1000ad/pyramid_wall', 8, tiles_y)
        self.main_layer.add(wall)
        wall.move_to(ground.rect.right, 0)

        platform = TiledSprite('1000ad/pyramid_wall', 15, 2)
        self.main_layer.add(platform)
        platform.move_to(self.PLATFORM_X, 200)
        x = platform.rect.left
        y = platform.rect.top

        for i in range(7):
            step = TiledSprite('1000ad/pyramid_wall', 2, 2)
            self.main_layer.add(step)
            x -= step.rect.width
            y += step.rect.height
            step.move_to(x, y)


class Outside2300AD(Level2OutsideArea):
    def setup(self):
        self.bg.fill((89, 80, 67))

        level_width, level_height = self.size

        toxicwaste = TiledSprite('2300ad/toxicwaste', 5, 1)
        toxicwaste.lethal = True
        self.main_layer.add(toxicwaste)
        toxicwaste.move_to(0, level_height - toxicwaste.rect.height)

        ground = TiledSprite('2300ad/ground', 15, 1)
        self.main_layer.add(ground)
        ground.move_to(toxicwaste.rect.right, level_height - ground.rect.height)

        toxicwaste = TiledSprite('2300ad/toxicwaste', 8, 1)
        toxicwaste.lethal = True
        self.main_layer.add(toxicwaste)
        toxicwaste.move_to(ground.rect.right,
                           level_height - toxicwaste.rect.height)

        pyramid = Sprite('2300ad/pyramid')
        self.bg_layer.add(pyramid)
        pyramid.move_to(922, ground.rect.top - pyramid.rect.height)

        bubble = Sprite('2300ad/pyramid_bubble')
        self.bg_layer.add(bubble)
        bubble.move_to(
            pyramid.rect.left + (pyramid.rect.width - bubble.rect.width) / 2,
            ground.rect.top - bubble.rect.height)

        sign = Sprite('2300ad/quarantine')
        self.main_layer.add(sign)
        sign.move_to(bubble.rect.left - sign.rect.width - 200,
                     ground.rect.top - 300)
        float_effect = FloatEffect(sign)
        float_effect.start()

        sign = Sprite('2300ad/quarantine')
        self.main_layer.add(sign)
        sign.move_to(bubble.rect.right + 200, ground.rect.top - 300)
        float_effect = FloatEffect(sign)
        float_effect.start()


class Pyramid2300AD(Level2PyramidArea):
    def setup(self):
        self.bg.fill((89, 80, 67))


class Level2(Level):
    def __init__(self, *args, **kwargs):
        super(Level2, self).__init__(*args, **kwargs)
        self.name = 'Level 2'
        self.setup()

    def setup(self):
        self.add(TimePeriod('12,000 BC', [Outside12000BC(self)]))
        self.add(TimePeriod('1000 AD', [
            Outside1000AD(self),
            Pyramid1000AD(self),
        ]))
        self.add(TimePeriod('2300 AD', [
            Outside2300AD(self),
            Pyramid2300AD(self),
        ]))
