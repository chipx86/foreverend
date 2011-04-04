import pygame

from foreverend.levels.base import EventBox, Level, TimePeriod
from foreverend.sprites import Box, Dynamite, Elevator, Mountain600AD, \
                               Mountain1999AD, Sprite, TiledSprite, Volcano


class TimePeriod600AD(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod600AD, self).__init__(*args, **kwargs)
        self.bg.fill((255, 255, 255))

        tiles_x = self.level.size[0] / 32
        ground = TiledSprite('ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, self.level.size[1] - ground.rect.height)

        mountain = Mountain600AD()
        self.main_layer.add(mountain)
        mountain.move_to(1345, ground.rect.top - mountain.rect.height)

        # Mountain platforms
        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1740,
                         mountain.rect.bottom - platform.rect.height - 10)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 100)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 180)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 260)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 340)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 420)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 500)


class TimePeriod1999AD(TimePeriod):
    BUILDING_RECT = pygame.Rect(0, 0, 1300, 700)
    WALL_WIDTH = 15
    GROUND_HEIGHT = 32
    WALL_COLOR = (211, 215, 207)
    FLOOR_COLOR = (211, 215, 207)

    def __init__(self, *args, **kwargs):
        super(TimePeriod1999AD, self).__init__(*args, **kwargs)
        self.bg.fill((255, 255, 255))

        level_width, level_height = self.level.size

        # Ground
        ground = Box(level_width, self.GROUND_HEIGHT)
        self.main_layer.add(ground)
        ground.move_to(0, level_height - ground.rect.height)

        building_rect = self.BUILDING_RECT.move(
            0, ground.rect.top - self.BUILDING_RECT.height)

        # Second floor
        floor2 = Box(building_rect.width, self.GROUND_HEIGHT)
        self.main_layer.add(floor2)
        floor2.move_to(building_rect.left,
                       building_rect.top +
                       (building_rect.height - floor2.rect.height) / 2)

        # Left wall of building
        box = Box(self.WALL_WIDTH, building_rect.height, self.WALL_COLOR)
        self.main_layer.add(box)
        box.move_to(building_rect.left, building_rect.top)

        # Right wall of the building
        box = Box(self.WALL_WIDTH, building_rect.height, self.WALL_COLOR)
        self.main_layer.add(box)
        box.move_to(building_rect.right - self.WALL_WIDTH, building_rect.top)

        # Ceiling
        box = Box(building_rect.width, self.GROUND_HEIGHT)
        self.main_layer.add(box)
        box.move_to(building_rect.left, building_rect.top)

        # Top elevator
        elevator1 = Elevator()
        self.main_layer.add(elevator1)
        elevator1.move_to(building_rect.left + 100,
                          building_rect.top - elevator1.rect.height)

        # Bottom elevator
        elevator2 = Elevator()
        self.main_layer.add(elevator2)
        elevator2.move_to(elevator1.rect.left,
                          floor2.rect.top - elevator2.rect.height)

        # Link up the elevators
        elevator1.destination = elevator2
        elevator2.destination = elevator1

        # Dynamite box
        box = Box(20, 10)
        self.main_layer.add(box)
        box.move_to(200, ground.rect.top - box.rect.height)

        # Dynamite
        dynamite = Dynamite()
        self.main_layer.add(dynamite)
        dynamite.move_to(200, ground.rect.top - dynamite.rect.height)

        # Mountain
        mountain = Mountain1999AD()
        self.main_layer.add(mountain)
        mountain.move_to(1345, ground.rect.top - mountain.rect.height)

        platform = Sprite('1999ad/lavamatics_platform')
        self.main_layer.add(platform)
        platform.move_to(1841,
                         mountain.rect.bottom - platform.rect.height - 500)

        platform = Sprite('1999ad/l_tube')
        self.main_layer.add(platform)
        platform.move_to(2140,
                         mountain.rect.bottom - platform.rect.height - 450)


class TimePeriod65000000BC(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod65000000BC, self).__init__(*args, **kwargs)

        ground = TiledSprite('ground', self.level.size[0] / 32, 1)
        self.main_layer.add(ground)
        ground.move_to(0, self.level.size[1] - ground.rect.height)

        volcano = Volcano()
        self.main_layer.add(volcano)
        volcano.move_to(1400, ground.rect.top - volcano.rect.height)

        # Dynamite explosion trigger
        explosion_box = EventBox(self, 1934, 1540, 16, 16)


class Level1(Level):
    def __init__(self, *args, **kwargs):
        super(Level1, self).__init__(*args, **kwargs)
        self.size = (10000, 1600)
        self.start_pos = (10,
                          self.size[1] - 32 - self.engine.player.rect.height)
        self.add(TimePeriod600AD(self))
        self.add(TimePeriod1999AD(self))
        self.add(TimePeriod65000000BC(self))