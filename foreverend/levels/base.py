import pygame
from pygame.locals import *

from foreverend.signals import Signal


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
            self.moved_cnxs[sprite] = \
                sprite.moved.connect(lambda: self._recompute_sprite(sprite))

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
    def __init__(self, index, time_period):
        self.time_period = time_period
        self.index = index
        self.quad_tree = QuadTree(
            pygame.Rect(0, 0, *self.time_period.level.size))

    def __repr__(self):
        return 'Layer %s on time period %s' % (self.index, self.time_period)

    def add(self, *objs):
        for obj in objs:
            obj.layer = self
            self.update_sprite(obj)
            self.quad_tree.add(obj)
            obj.on_added(self)

    def remove(self, *objs):
        for obj in objs:
            self.update_sprite(obj)
            self.quad_tree.remove(obj)
            obj.on_removed(self)

    def update_sprite(self, sprite):
        assert sprite.layer == self

        sprite.update_image()

        if sprite.visible:
            self.time_period.group.add(sprite, layer=self.index)
        else:
            self.time_period.group.remove(sprite)

    def __iter__(self):
        return iter(self.quad_tree)

    def handle_event(self, event):
        pass


class Level(object):
    def __init__(self, engine):
        self.engine = engine
        self.time_periods = []
        self.active_time_period = None
        self.size = None

        self.engine.tick.connect(self.on_tick)

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
            not list(player.get_collisions(
                tree=time_period.main_layer.quad_tree))):
            if self.active_time_period:
                self.active_time_period.main_layer.remove(player)

            self.active_time_period = time_period
            self.active_time_period.main_layer.add(player)
            self.time_period_changed.emit()

    def draw(self, screen):
        self.active_time_period.draw(screen)

    def on_tick(self):
        if not self.engine.paused and self.engine.active_level == self:
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
