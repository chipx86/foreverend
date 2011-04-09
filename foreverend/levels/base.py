import random

import pygame
from pygame.locals import *

from foreverend.eventbox import EventBox
from foreverend.signals import Signal
from foreverend.sprites.common import Crossover
from foreverend.sprites.items import Artifact
from foreverend.timer import Timer


class QuadTree(object):
    def __init__(self, rect, depth=4, parent=None):
        depth -= 1

        self.rect = rect
        self.sprites = []
        self.parent = parent
        self.depth = depth
        self.cx = self.rect.centerx
        self.cy = self.rect.centery
        self.moved_cnxs = {}

        if depth == 0:
            self.nw_tree = None
            self.ne_tree = None
            self.sw_tree = None
            self.se_tree = None
        else:
            quad_size = (rect.width / 2, rect.height / 2)

            self.nw_tree = QuadTree(pygame.Rect(rect.x, rect.y, *quad_size),
                                    depth, self)
            self.ne_tree = QuadTree(pygame.Rect(self.cx, rect.y, *quad_size),
                                    depth, self)
            self.sw_tree = QuadTree(pygame.Rect(rect.x, self.cy, *quad_size),
                                    depth, self)
            self.se_tree = QuadTree(pygame.Rect(self.cx, self.cy, *quad_size),
                                    depth, self)

    def __repr__(self):
        return 'Quad Tree (%s, %s, %s, %s)' % (self.rect.left, self.rect.top,
                                               self.rect.width,
                                               self.rect.height)

    def add(self, sprite):
        if not self.parent:
            assert sprite not in self.moved_cnxs
            self.moved_cnxs[sprite] = sprite.moved.connect(
                lambda dx, dy: self._recompute_sprite(sprite))

        # If it's overlapping all regions, or we're a leaf, it
        # belongs in items. Otherwise, stick it in as many regions as
        # necessary.
        if self.depth > 0:
            trees = list(self._get_trees(sprite.rect))
            assert len(trees) > 0

            if len(trees) < 4:
                for tree in trees:
                    tree.add(sprite)

                return

        assert sprite not in self.sprites
        self.sprites.append(sprite)
        sprite.quad_trees.add(self)

    def remove(self, sprite):
        if self.parent:
            self.parent.remove(sprite)
            return

        assert sprite.quad_trees

        for tree in sprite.quad_trees:
            tree.sprites.remove(sprite)

        sprite.quad_trees.clear()
        cnx = self.moved_cnxs.pop(sprite)
        cnx.disconnect()

    def get_sprites(self, rect=None):
        """Returns any sprites stored in quadrants intersecting with rect.

        This does not necessarily mean that the sprites themselves intersect
        with rect.
        """
        for sprite in self.sprites:
            yield sprite

        for tree in self._get_trees(rect):
            for sprite in tree.get_sprites(rect):
                yield sprite

    def __iter__(self):
        return self.get_sprites()

    def _get_trees(self, rect):
        if self.depth > 0:
            if not rect or (rect.left <= self.cx and rect.top <= self.cy):
                yield self.nw_tree

            if not rect or (rect.right >= self.cx and rect.top <= self.cy):
                yield self.ne_tree

            if not rect or (rect.left <= self.cx and rect.bottom >= self.cy):
                yield self.sw_tree

            if not rect or (rect.right >= self.cx and rect.bottom >= self.cy):
                yield self.se_tree

    def _get_leaf_trees(self, rect):
        trees = list(self._get_trees(rect))

        if not trees or len(trees) == 4:
            yield self
        else:
            for tree in trees:
                for leaf in tree._get_leaf_trees(rect):
                    yield leaf

    def _recompute_sprite(self, sprite):
        assert sprite.quad_trees


        if sprite.quad_trees != set(self._get_leaf_trees(sprite.rect)):
            self.remove(sprite)
            self.add(sprite)


class Layer(object):
    def __init__(self, index, area):
        self.area = area
        self.index = index
        self.quad_tree = QuadTree(pygame.Rect(0, 0, *self.area.size))

    def __repr__(self):
        return 'Layer %s on time period %s' % (self.index, self.area)

    def add(self, *objs):
        for obj in objs:
            obj.layer = self
            self.update_sprite(obj)
            self.quad_tree.add(obj)
            obj.on_added(self)

    def remove(self, *objs):
        for obj in objs:
            self.update_sprite(obj, True)
            self.quad_tree.remove(obj)
            obj.on_removed(self)

    def update_sprite(self, sprite, force_remove=False):
        assert sprite.layer == self

        sprite.update_image()

        if sprite.visible and not force_remove:
            self.area.group.add(sprite, layer=self.index)
        else:
            self.area.group.remove(sprite)

    def __iter__(self):
        return iter(self.quad_tree)

    def handle_event(self, event):
        pass


class Level(object):
    CROSSOVER_TIME_INTERVAL = (4000, 10000)
    MAX_CROSSOVERS = 3

    def __init__(self, engine):
        self.engine = engine
        self.time_periods = []
        self.active_area = None
        self.music = None
        self.crossover_timer = None
        self.crossovers = []
        self.pending_crossovers = {}
        self.next_crossover_id = 0

        self.engine.tick.connect(self.on_tick)

        # Signals
        self.area_changed = Signal()
        self.time_period_changed = Signal()

    def add(self, time_period):
        self.time_periods.append(time_period)

    def add_artifact(self, area, x, y):
        # Artifact
        self.artifact = Artifact(area, 1)
        area.main_layer.add(self.artifact)
        self.artifact.move_to(x - self.artifact.rect.width / 2,
                              y - self.artifact.rect.height - 50)
        self.artifact.grab_changed.connect(self.on_artifact_grabbed)

    def reset(self):
        self.active_area = None
        self.active_time_period = None
        self.time_periods = []
        self._setup()

    def setup(self):
        pass

    def _setup(self):
        self.setup()

        for time_period in self.time_periods:
            time_period.setup()

    def switch_area(self, area):
        if area == self.active_area:
            return

        player = self.engine.player

        if self.active_area:
            self.active_area.main_layer.remove(player)

        self.active_area = area
        self.active_area.main_layer.add(player)
        self.area_changed.emit()
        player.reset_gravity()

        for crossover, timer in self.crossovers:
            timer.stop()
            crossover.remove()

        for pending_timer in self.pending_crossovers.itervalues():
            pending_timer.stop()

        self.crossovers = []
        self.pending_crossovers = {}

    def switch_time_period(self, num):
        time_period = self.time_periods[num]

        if self.active_area:
            key = self.active_area.key
            area = time_period.areas.get(key, None)
        else:
            area = time_period.default_area

        player = self.engine.player

        if (area and
            (not self.active_area or
             not list(player.get_collisions(tree=area.main_layer.quad_tree)))):
            self.active_time_period = time_period
            self.time_period_changed.emit()
            self.switch_area(area)

    def draw(self, screen):
        self.active_area.draw(screen)

    def on_artifact_grabbed(self):
        if self.artifact.grabbed:
            player = self.engine.player
            player.block_events = True
            player.velocity = (0, 0)
            player.fall()

            timer = Timer(1000, self.engine.next_level, one_shot=True)
            timer.start()

    def on_tick(self):
        if not self.engine.paused and self.engine.active_level == self:
            self.active_area.tick()

            if (len(self.time_periods) > 1 and
                len(self.crossovers) + len(self.pending_crossovers) <
                self.MAX_CROSSOVERS):
                crossover_id = self.next_crossover_id
                self.next_crossover_id += 1
                timer = Timer(
                    random.randint(*self.CROSSOVER_TIME_INTERVAL),
                    lambda: self.show_crossover(crossover_id),
                    one_shot=True)
                self.pending_crossovers[crossover_id] = timer

    def show_crossover(self, crossover_id):
        def hide_crossover():
            crossover_sprite.remove()
            self.crossovers.remove((crossover_sprite, timer))

        self.pending_crossovers[crossover_id].stop()
        del self.pending_crossovers[crossover_id]

        key = self.active_area.key

        time_periods = [
            time_period.areas[key]
            for time_period in self.time_periods
            if (time_period != self.active_time_period and
                key in time_period.areas)
        ]

        if len(time_periods) - 1 <= 0:
            return

        i = random.randint(0, len(time_periods) - 1)


        crossover_sprite = Crossover(time_periods[i])
        crossover_sprite.rect = self.engine.camera.rect

        if random.randint(0, 5) <= 3:
            layer = self.active_area.bg_layer
        else:
            layer = self.active_area.main_layer

        layer.add(crossover_sprite)

        timer = Timer(500, hide_crossover, one_shot=True)
        timer.start()
        self.crossovers.append((crossover_sprite, timer))


class TimePeriod(object):
    def __init__(self, name, areas=[]):
        self.name = name
        self.default_area = None
        self.active_area = None
        self.areas = {}

        for area in areas:
            self.add_area(area)

    def add_area(self, area):
        if not self.default_area:
            self.default_area = area

        self.areas[area.key] = area
        area.time_period = self

    def draw(self, screen):
        self.active_area.draw(screen)

    def setup(self):
        for area in self.areas.itervalues():
            area.setup()


class Area(object):
    def __init__(self, level):
        assert isinstance(level, Level)
        self.key = 'default'
        self.level = level
        self.engine = level.engine
        self.layers = []
        self.group = pygame.sprite.LayeredDirty()
        self.default_layer = self.new_layer()
        self.bg_layer = self.new_layer()
        self.main_layer = self.new_layer()
        self.fg_layer = self.new_layer()
        self.layers = [self.bg_layer, self.main_layer, self.fg_layer]
        self.event_handlers = []
        self.timers = []
        self.particle_systems = []

    def new_layer(self):
        layer = Layer(len(self.layers), self)
        layer.area = self
        self.layers.append(layer)
        return layer

    def draw_bg(self, surface):
        pass

    def draw(self, screen):
        self.draw_bg(screen)
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
