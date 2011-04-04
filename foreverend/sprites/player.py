import pygame
from pygame.locals import *

from foreverend.sprites.base import Direction, Sprite
from foreverend.sprites.items import Item


class TractorBeam(Sprite):
    ITEM_OFFSET = -5
    VERT_OFFSET_ALLOWANCE = 6

    def __init__(self, player, name='tractor_beam'):
        super(TractorBeam, self).__init__(name, flip_image=True)
        self.player = player
        self.item = None
        self.ungrab()
        self.freeze_item_y = 0
        self.collidable = False
        self.visible = 0

    def _check_for_items(self):
        if self.item:
            return

        for obj, _, _ in self.get_collisions(ignore_collidable_flag=True):
            if isinstance(obj, Item) and obj.grabbable:
                self.grab(obj)
                return

    def grab(self, item):
        assert item
        assert not self.item
        print 'Got item'
        self.item = item
        self.item.stop_falling()
        self.item.obey_gravity = False
        self.item.collidable = False
        self.freeze_item_y = False
        self.name = 'tractor_beam'
        self.update_image()

    def ungrab(self):
        if self.item:
            self.item.obey_gravity = True
            self.item.collidable = True
            self.item.fall()
            self.item = None

        self.name = 'tractor_beam_wide'
        self.update_image()

    def update_position(self, player):
        y = player.rect.top + \
            (player.rect.height - self.rect.height) / 2
        if self.direction == Direction.RIGHT:
            self.move_to(player.rect.right, y)
        elif self.direction == Direction.LEFT:
            self.move_to(player.rect.left - self.rect.width, y)

        self._check_for_items()

    def adjust_item_position(self, collide_rect):
        """Adjusts the position of the held item to not touch the rect."""
        assert self.item

        if (collide_rect.top <= self.item.rect.bottom and
            collide_rect.top - self.item.rect.height >=
            self.item.rect.top - self.VERT_OFFSET_ALLOWANCE):
            self.freeze_item_y = True
            self.item.move_to(self.item.rect.left,
                              collide_rect.top - self.item.rect.height - 1)
            return True

        return False

    def on_moved(self):
        if self.item:
            mid_y = self.rect.top + \
                    (self.rect.height - self.item.rect.height) / 2 - 1
            if self.freeze_item_y:
                y = self.item.rect.top
            else:
                y = mid_y

            if y <= mid_y:
                self.freeze_item_y = False
                y = mid_y

            if self.direction == Direction.RIGHT:
                self.item.move_to(self.rect.right + self.ITEM_OFFSET, y)
            elif self.direction == Direction.LEFT:
                self.item.move_to(self.rect.left - self.item.rect.width -
                                  self.ITEM_OFFSET, y)

        super(TractorBeam, self).on_moved()

    def on_added(self, layer):
        if self.item:
            layer.add(self.item)

    def on_removed(self, layer):
        if self.item:
            layer.remove(self.item)


class Player(Sprite):
    MOVE_SPEED = 6
    JUMP_SPEED = 6
    MAX_JUMP_HEIGHT = 100
    HOVER_TIME_MS = 1000

    PROPULSION_BELOW_OFFSET = 8

    def __init__(self, engine):
        super(Player, self).__init__('player', flip_image=True,
                                     obey_gravity=True)
        self.engine = engine
        self.jumping = False
        self.hovering = False
        self.should_check_collisions = True
        self.hover_time_ms = 0
        self.jump_origin = None
        self.propulsion_below = Sprite("propulsion_below")
        self.propulsion_below.collidable = False
        self.propulsion_below.visible = 0
        self.tractor_beam = TractorBeam(self)

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.move_right()
            elif event.key == K_LEFT:
                self.move_left()
            elif event.key == K_SPACE:
                self.jump()
            elif event.key in (K_LSHIFT, K_RSHIFT):
                self.start_tractor_beam()
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                if self.velocity[0] < 0:
                    self.velocity = (0, self.velocity[1])
            elif event.key == K_RIGHT:
                if self.velocity[0] > 0:
                    self.velocity = (0, self.velocity[1])
            elif event.key == K_SPACE:
                self.fall()
            elif event.key in (K_LSHIFT, K_RSHIFT):
                self.stop_tractor_beam()

    def move_right(self):
        self.velocity = (self.MOVE_SPEED, self.velocity[1])

        if self.direction != Direction.RIGHT:
            self.direction = Direction.RIGHT
            self.tractor_beam.direction = Direction.RIGHT
            self.update_image()

    def move_left(self):
        self.velocity = (-self.MOVE_SPEED, self.velocity[1])

        if self.direction != Direction.LEFT:
            self.direction = Direction.LEFT
            self.tractor_beam.direction = Direction.LEFT
            self.update_image()

    def start_tractor_beam(self):
        self.tractor_beam.show()
        self.tractor_beam.update_position(self)
        self.calculate_collision_rects()

    def stop_tractor_beam(self):
        self.tractor_beam.ungrab()
        self.tractor_beam.hide()
        self.calculate_collision_rects()

    def jump(self):
        if self.falling or self.jumping:
            return

        self.jump_origin = (self.rect.left, self.rect.top)
        self.jumping = True
        self.velocity = (self.velocity[0], -self.JUMP_SPEED)
        self.propulsion_below.show()

    def fall(self):
        if self.falling:
            return

        self.propulsion_below.hide()
        self.jumping = False
        self.hovering = False
        super(Player, self).fall()

    def hover(self):
        if self.hovering:
            return

        self.propulsion_below.show()
        self.jumping = False
        self.hovering = True
        self.hover_time_ms = 0
        self.velocity = (self.velocity[0], 0)

    def calculate_collision_rects(self):
        if self.tractor_beam.item:
            self.collision_rects = [
                self.rect,
                self.tractor_beam.item.rect
            ]
        else:
            self.collision_rects = []

    def check_collisions(self, *args, **kwargs):
        if self.tractor_beam.item:
            self.tractor_beam.update_position(self)

        super(Player, self).check_collisions(*args, **kwargs)

    def tick(self):
        if self.hovering:
            self.hover_time_ms += 1.0 / self.engine.FPS * 1000

            if self.hover_time_ms >= self.HOVER_TIME_MS:
                self.fall()

        super(Player, self).tick()

    def on_added(self, layer):
        for obj in (self.propulsion_below, self.tractor_beam):
            layer.add(obj)

    def on_removed(self, layer):
        for obj in (self.propulsion_below, self.tractor_beam):
            layer.remove(obj)

    def on_moved(self):
        if (self.jumping and
            not self.engine.god_mode and
            self.jump_origin[1] - self.rect.top >= self.MAX_JUMP_HEIGHT):
            self.hover()

        if self.propulsion_below.visible:
            if self.direction == Direction.RIGHT:
                offset = self.PROPULSION_BELOW_OFFSET
            if self.direction == Direction.LEFT:
                offset = self.rect.width - self.propulsion_below.rect.width - \
                         self.PROPULSION_BELOW_OFFSET

            self.propulsion_below.move_to(self.rect.left + offset,
                                          self.rect.bottom)

        if self.tractor_beam.visible:
            self.tractor_beam.update_position(self)

        self.calculate_collision_rects()

        super(Player, self).on_moved()

    def on_collision(self, dx, dy, obj, self_rect, obj_rect):
        if self.tractor_beam.item and self_rect == self.tractor_beam.item.rect:
            move_player = True

            if dy != 0:
                if self.tractor_beam.adjust_item_position(obj_rect):
                    move_player = False

            if move_player:
                if self.direction == Direction.LEFT:
                    self.move_to(obj_rect.right +
                                 (self.rect.left -
                                  self.tractor_beam.item.rect.left),
                                 self.rect.top)
                elif self.direction == Direction.RIGHT:
                    self.move_to(obj_rect.left -
                                 (self.tractor_beam.item.rect.right -
                                  self.rect.left),
                                 self.rect.top)

        if self.jumping and dy < 0:
            self.fall()
        else:
            super(Player, self).on_collision(dx, dy, obj, self_rect, obj_rect)
