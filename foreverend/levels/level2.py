import pygame

from foreverend.effects import FloatEffect
from foreverend.levels.base import Area, Level, TimePeriod
from foreverend.sprites import Box, Button, Cactus, Door, FlameThrower, \
                               IceBoulder, QuarantineSign, Snake, Sprite, \
                               TiledSprite, TogglePlatform
from foreverend.timer import Timer


class Level2OutsideArea(Area):
    size = (3956, 1600)

    def __init__(self, *args, **kwargs):
        super(Level2OutsideArea, self).__init__(*args, **kwargs)
        self.start_pos = (1500,
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

        cactus = Cactus()
        self.main_layer.add(cactus)
        cactus.move_to(100, ground.rect.top - cactus.rect.height)

        pyramid = Sprite('1000ad/pyramid')
        self.bg_layer.add(pyramid)
        pyramid.move_to(922, ground.rect.top - pyramid.rect.height)

        cactus = Cactus()
        self.main_layer.add(cactus)
        cactus.move_to(pyramid.rect.left + 100,
                       ground.rect.top - cactus.rect.height)

        cactus = Cactus()
        self.main_layer.add(cactus)
        cactus.move_to(2600, ground.rect.top - cactus.rect.height)

        self.pyramid_door.destination = self.time_period.areas['pyramid'].door
        self.main_layer.add(self.pyramid_door)
        self.pyramid_door.move_to(
            pyramid.rect.left + 621,
            pyramid.rect.bottom - self.pyramid_door.rect.height)

        snake = Snake()
        self.main_layer.add(snake)
        snake.move_to(pyramid.rect.left - snake.rect.width,
                      ground.rect.top - snake.rect.height)

        # Artifact
        self.level.add_artifact(self, cactus.rect.right + 100, ground.rect.top)


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

        sign = QuarantineSign()
        self.main_layer.add(sign)
        sign.move_to(bubble.rect.left - sign.rect.width - 200,
                     ground.rect.top - 300)

        sign = QuarantineSign()
        self.main_layer.add(sign)
        sign.move_to(bubble.rect.right + 200, ground.rect.top - 300)


class Level2PyramidArea(Area):
    size = (4000, 800)

    DOOR_X = 230
    PLATFORM_X = DOOR_X + 600
    PLATFORM_Y = 224
    PIT_TILES_X = 65

    def __init__(self, *args, **kwargs):
        super(Level2PyramidArea, self).__init__(*args, **kwargs)
        self.key = 'pyramid'
        self.wall_name = None
        self.spike_name = None
        self.ground_name = None
        self.start_pos = (100,
                          self.size[1] - 64 - self.engine.player.rect.height)

    def setup(self):
        area_width, area_height = self.size

        tiles_y = area_height / 32
        wall = TiledSprite(self.wall_name, 4, tiles_y)
        self.main_layer.add(wall)
        wall.move_to(0, 0)

        ground = TiledSprite(self.ground_name, 10, 1)
        self.main_layer.add(ground)
        ground.move_to(wall.rect.right, area_height - ground.rect.height)
        self.ground_top = ground.rect.top

        self.pit = TiledSprite(self.spike_name, self.PIT_TILES_X, 1)
        self.pit.lethal = True
        self.main_layer.add(self.pit)
        self.pit.move_to(ground.rect.right,
                         ground.rect.bottom - self.pit.rect.height)

        ground = TiledSprite(self.ground_name, 5, 1)
        self.main_layer.add(ground)
        ground.move_to(self.pit.rect.right, area_height - ground.rect.height)

        self.topleft_platform = TiledSprite(self.wall_name, 25, 2)
        self.main_layer.add(self.topleft_platform)
        self.topleft_platform.move_to(self.PLATFORM_X, 200)

        platform = TiledSprite(self.wall_name, 20, 2)
        self.main_layer.add(platform)
        platform.move_to(ground.rect.left, self.PLATFORM_Y)

        tiles_y = (area_height - platform.rect.top) / 32 + 32
        wall = TiledSprite(self.wall_name, 15, tiles_y)
        self.main_layer.add(wall)
        wall.move_to(platform.rect.right, platform.rect.top)

        wall = TiledSprite(self.wall_name, 15, 4)
        self.main_layer.add(wall)
        wall.move_to(platform.rect.right, 0)
        wall_right = wall.rect.right
        wall_bottom = wall.rect.bottom

        self.weapons_entrance_pos = (wall.rect.left, wall.rect.bottom)

        wall = TiledSprite(self.wall_name, 5, 3)
        self.main_layer.add(wall)
        wall.move_to(wall_right - wall.rect.width, wall_bottom)


class Pyramid1000AD(Level2PyramidArea):
    def __init__(self, *args, **kwargs):
        super(Pyramid1000AD, self).__init__(*args, **kwargs)
        self.door = Door('1000ad/pyramid_door')
        self.ground_name = '1000ad/ground'
        self.wall_name = '1000ad/pyramid_wall'
        self.spike_name = '1000ad/spike'

    def setup(self):
        super(Pyramid1000AD, self).setup()

        self.bg.fill((255, 251, 219))

        self.door.destination = self.time_period.areas['default'].pyramid_door
        self.main_layer.add(self.door)
        self.door.move_to(self.DOOR_X, self.ground_top - self.door.rect.height)

        x = self.topleft_platform.rect.left
        y = self.topleft_platform.rect.top

        for i in range(7):
            step = TiledSprite(self.wall_name, 2, 2)
            self.main_layer.add(step)
            x -= step.rect.width
            y += step.rect.height
            step.move_to(x, y)


class Pyramid2300AD(Level2PyramidArea):
    PLATFORM_DELAY_TIME = 2000
    PLATFORM_POS = [
        # To weapons
        (0, 180),
        (218, 218),
        (218, 124),
        (409, 54),
        (611, 0),
        (611, 148),
        (824, 118),
        (930, 45),

        # To exit
        (1079, 373),
        (944, 297),
        (742, 275),
        (521, 326),
        (362, 266),
        (218, 250),
    ]

    def __init__(self, *args, **kwargs):
        super(Pyramid2300AD, self).__init__(*args, **kwargs)
        self.ground_name = '2300ad/ground'
        self.wall_name = '2300ad/pyramid_wall'
        self.spike_name = '2300ad/spike'
        self.platforms_on = False
        self.platforms = []
        self.next_platform_num = 0
        self.last_platform = None

    def setup(self):
        super(Pyramid2300AD, self).setup()
        self.bg.fill((89, 80, 67))

        # Fall to your doom, probes!
        self.pit.remove()

        wall = TiledSprite(self.wall_name, 4, 3)
        self.main_layer.add(wall)
        wall.move_to(*self.weapons_entrance_pos)

        wall = TiledSprite(self.wall_name, 2, 7)
        self.main_layer.add(wall)
        wall.move_to(self.topleft_platform.rect.left,
                     self.topleft_platform.rect.top - wall.rect.height)

        wall = TiledSprite(self.wall_name, 2, 7)
        self.main_layer.add(wall)
        wall.move_to(self.topleft_platform.rect.right - wall.rect.width,
                     self.topleft_platform.rect.top - wall.rect.height)

        button = Button('2300ad/button')
        button.pressed.connect(self.on_platforms_button_pressed)
        self.main_layer.add(button)
        button.move_to(wall.rect.left - button.rect.width,
                       self.topleft_platform.rect.top - button.rect.height - 10)

        wall = TiledSprite(self.wall_name, 15, 6)
        self.main_layer.add(wall)
        wall.move_to(self.topleft_platform.rect.right - wall.rect.width,
                     button.rect.top - wall.rect.height - 10)

        sign = Sprite('2300ad/weapons_sign')
        self.main_layer.add(sign)
        sign.move_to(button.rect.right - sign.rect.width,
                     wall.rect.bottom - sign.rect.height - 20)

        step = TiledSprite(self.wall_name, 2, 6)
        self.main_layer.add(step)
        step.move_to(self.pit.rect.left - step.rect.width,
                     self.ground_top - step.rect.height)
        x = step.rect.left

        step = TiledSprite(self.wall_name, 2, 4)
        self.main_layer.add(step)
        step.move_to(x - step.rect.width, self.ground_top - step.rect.height)
        x = step.rect.left

        step = TiledSprite(self.wall_name, 2, 2)
        self.main_layer.add(step)
        step.move_to(x - step.rect.width, self.ground_top - step.rect.height)

        platform_x = self.pit.rect.left
        platform_y = self.pit.rect.top - 500

        for x, y in self.PLATFORM_POS:
            platform = TogglePlatform()
            self.main_layer.add(platform)
            platform.move_to(platform_x + x, platform_y + y)
            self.platforms.append(platform)

#        self.main_layer.add(self.level.flamethrower)
#        self.level.flamethrower.move_to(
#            wall.rect.right + 100,
#            wall.rect.bottom - self.level.flamethrower.rect.height)

    def on_platforms_button_pressed(self):
        if self.platforms_on:
            return

        self.platforms_on = True
        self.platforms_timer = Timer(self.PLATFORM_DELAY_TIME,
                                     self.next_platform)

    def next_platform(self):
        if self.last_platform:
            self.last_platform.close()

        platform = self.platforms[self.next_platform_num]
        self.last_platform = platform

        if self.next_platform_num == len(self.platforms) - 1:
            self.next_platform_num = 0
        else:
            self.next_platform_num += 1

        platform.open()


class Level2(Level):
    def __init__(self, *args, **kwargs):
        super(Level2, self).__init__(*args, **kwargs)
        self.name = 'Level 2'
        self.setup()

    def setup(self):
        self.flamethrower = FlameThrower()

        self.add(TimePeriod('12,000 BC', [Outside12000BC(self)]))
        self.add(TimePeriod('1000 AD', [
            Outside1000AD(self),
            Pyramid1000AD(self),
        ]))
        self.add(TimePeriod('2300 AD', [
            Outside2300AD(self),
            Pyramid2300AD(self),
        ]))
