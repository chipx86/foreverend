import pygame
from pygame.locals import *

from foreverend.signals import Signal


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
        self.event_handlers = []

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

    def register_for_events(self, obj):
        self.event_handlers.append(obj)

    def unregister_for_events(self, obj):
        self.event_handlers.remove(obj)

    def tick(self):
        self.group.update()

        for sprite in self.group:
            sprite.tick()


class EventBox(object):
    def __init__(self, time_period, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        time_period.register_for_events(self)
        self.event_fired = Signal()

    def handle_event(self, event):
        return self.event_fired.emit(event)