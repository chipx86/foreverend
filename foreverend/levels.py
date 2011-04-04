import pygame
from pygame.locals import *

from foreverend.sprites import Box, Elevator, Mountain600AD, Mountain1999AD, \
                               Sprite, TiledSprite, Volcano


class Layer(object):
    def __init__(self, index, level):
        self.level = level
        self.index = index
        self.objs = set()

    def add(self, *objs):
        for obj in objs:
            obj.layer = self
            obj.update_image()
            self.level.group.add(obj, layer=self.index)
            self.objs.add(obj)
            obj.on_added(self)

    def remove(self, *objs):
        for obj in objs:
            obj.update_image()
            self.level.group.remove(obj)
            self.objs.discard(obj)
            obj.on_removed(self)

    def __iter__(self):
        return iter(self.objs)

    def handle_event(self, event):
        pass


class Level(object):
    def __init__(self, engine):
        self.engine = engine
        self.time_periods = []
        self.active_time_period = None
        self.size = None

    def add(self, time_period):
        self.time_periods.append(time_period)

    def switch_time_period(self, time_period_num):
        player = self.engine.player
        time_period = self.time_periods[time_period_num]

        # First, make sure the player can be there.
        if (not self.active_time_period or
            not list(player.get_collisions(group=time_period.group))):
            if self.active_time_period:
                self.active_time_period.main_layer.remove(player)

            self.active_time_period = time_period
            self.active_time_period.main_layer.add(player)

    def draw(self, screen):
        self.active_time_period.draw(screen)

    def tick(self):
        self.active_time_period.tick()


class TimePeriod(object):
    def __init__(self, level):
        assert isinstance(level, Level)
        self.level = level
        self.engine = level.engine
        self.layers = []
        self.group = pygame.sprite.LayeredDirty()
        self.default_layer = self.new_layer()
        self.main_layer = self.new_layer()
        self.bg = pygame.Surface(self.engine.screen.get_size()).convert()

    def new_layer(self):
        layer = Layer(len(self.layers), self)
        layer.time_period = self
        self.layers.append(layer)
        return layer

    def draw(self, screen):
        screen.blit(self.bg, self.engine.camera.rect.topleft)
        self.group.draw(screen)

        if self.engine.debug_collision_rects:
            for sprite in self.group:
                if sprite.visible:
                    rects = sprite.collision_rects or [sprite.rect]

                    for rect in rects:
                        pygame.draw.rect(screen, (0, 0, 255), rect, 1)


    def tick(self):
        self.group.update()

        for sprite in self.group:
            sprite.tick()


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


class Level1(Level):
    def __init__(self, *args, **kwargs):
        super(Level1, self).__init__(*args, **kwargs)
        self.size = (10000, 1600)
        self.start_pos = (10,
                          self.size[1] - 32 - self.engine.player.rect.height)
        self.add(TimePeriod600AD(self))
        self.add(TimePeriod1999AD(self))
        self.add(TimePeriod65000000BC(self))


def get_levels():
    return [Level1]
