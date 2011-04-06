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

        # Signals
        self.time_period_changed = Signal()

    def add(self, time_period):
        self.time_periods.append(time_period)

    def reset(self):
        self.active_time_period = None
        self.time_periods = []
        self.setup()

    def setup(self):
        pass

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
            self.time_period_changed.emit()

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
        self.bg_layer = self.new_layer()
        self.main_layer = self.new_layer()
        self.fg_layer = self.new_layer()
        self.bg = pygame.Surface(self.engine.screen.get_size()).convert()
        self.event_handlers = []
        self.timers = []
        self.particle_systems = []

    def new_layer(self):
        layer = Layer(len(self.layers), self)
        layer.time_period = self
        self.layers.append(layer)
        return layer

    def draw(self, screen):
        screen.blit(self.bg, self.engine.camera.rect.topleft)
        self.group.draw(screen)

        if self.engine.debug_rects:
            for sprite in self.group:
                if sprite.visible:
                    rects = sprite.collision_rects or [sprite.rect]

                    for rect in rects:
                        pygame.draw.rect(screen, (0, 0, 255), rect, 1)

            for eventbox in self.event_handlers:
                if isinstance(eventbox, EventBox):
                    for rect in eventbox.rects:
                        pygame.draw.rect(screen, (255, 0, 0), rect, 1)

        for particle_system in self.particle_systems:
            particle_system.draw(screen)

    def register_for_events(self, obj):
        self.event_handlers.append(obj)

    def unregister_for_events(self, obj):
        self.event_handlers.remove(obj)

    def tick(self):
        self.group.update()

        for sprite in self.group:
            sprite.tick()

        for timer in self.timers:
            timer.tick()


class EventBox(object):
    def __init__(self, time_period):
        self.rects = []
        time_period.register_for_events(self)
        self.entered_objects = set()

        # Signals
        self.event_fired = Signal()
        self.object_moved = Signal()
        self.object_entered = Signal()
        self.object_exited = Signal()

    def watch_object_moves(self, obj):
        obj.moved.connect(lambda: self.handle_object_move(obj))

    def handle_event(self, event):
        return self.event_fired.emit(event)

    def handle_object_move(self, obj):
        if obj.rect.collidelist(self.rects) != -1:
            if obj not in self.entered_objects:
                self.entered_objects.add(obj)
                self.object_entered.emit(obj)

            self.object_moved.emit(obj)
        elif obj in self.entered_objects:
            self.entered_objects.remove(obj)
            self.object_exited.emit(obj)
