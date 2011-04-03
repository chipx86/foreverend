import pygame
from pygame.locals import *

from foreverend.sprites import TiledSprite


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
        time_period.time_periodset = self

        if not self.active_time_period:
            self.active_time_period = time_period

    def switch_time_period(self, time_period_num):
        player = self.engine.player

        if self.active_time_period:
            self.active_time_period.main_layer.remove(player)

        self.active_time_period = self.time_periods[time_period_num]
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
        layer.level = self
        self.layers.append(layer)
        return layer

    def draw(self, screen):
        screen.blit(self.bg, self.engine.camera.rect.topleft)
        self.group.draw(screen)

    def tick(self):
        self.group.update()

        for sprite in self.group:
            sprite.tick()


class TimePeriod1999AD(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod1999AD, self).__init__(*args, **kwargs)
        self.bg.fill((255, 255, 255))

        tiles_x = self.level.size[0] / 32
        screen = self.engine.screen
        ground = TiledSprite('ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, screen.get_height() - ground.rect.height)

        ground = TiledSprite('ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(60, screen.get_height() - 2 * ground.rect.height)


class TimePeriod65000000BC(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod65000000BC, self).__init__(*args, **kwargs)

        screen = self.engine.screen
        ground = TiledSprite('ground', self.level.size[0] / 32, 1)
        self.main_layer.add(ground)
        ground.move_to(0, screen.get_height() - ground.rect.height)


class Level1(Level):
    def __init__(self, *args, **kwargs):
        super(Level1, self).__init__(*args, **kwargs)
        self.size = (10000, 600)
        self.start_pos = (10,
                          self.size[1] - 32 - self.engine.player.rect.height)
        self.add(TimePeriod1999AD(self))
        self.add(TimePeriod65000000BC(self))


def get_levels():
    return [Level1]
