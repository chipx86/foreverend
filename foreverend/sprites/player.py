import pygame
from pygame.locals import *

from foreverend import get_engine
from foreverend.signals import Signal
from foreverend.sprites.base import Direction, Sprite
from foreverend.sprites.items import Item, Vehicle


class TractorBeam(Sprite):
    ITEM_OFFSET = -5
    HORIZ_OFFSET_ALLOWANCE = -32
    VERT_OFFSET_ALLOWANCE = 6

    def __init__(self, player, name='tractor_beam'):
        super(TractorBeam, self).__init__(name, flip_image=True)
        self.player = player
        self.item = None
        self.ungrab()
        self.freeze_item_y = 0
        self.collidable = False
        self.visible = 0
        self.item_offset = 0

    def _check_for_items(self):
        if self.item:
            return

        for obj, _, _ in self.get_collisions(ignore_collidable_flag=True):
            if obj.grabbable and obj != self.player.vehicle:
                self.grab(obj)
                return

    def grab(self, item):
        assert item
        assert not self.item
        self.old_item_obey_gravity = item.obey_gravity
        self.item = item
        self.item.stop_falling()
        self.item.obey_gravity = False
        self.item.collidable = False
        self.item.grabbed = True
        self.freeze_item_y = False
        self.item_offset = self.ITEM_OFFSET
        self.name = 'tractor_beam'
        self.update_image()
        self.item.grab_changed.emit()

    def ungrab(self):
        if self.item:
            self.item.obey_gravity = self.old_item_obey_gravity
            self.item.collidable = True
            self.item.grabbed = False
            self.item.fall()
            self.item.grab_changed.emit()
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

        new_x = self.item.rect.left
        new_y = self.item.rect.top

        adjusted = False

        if (collide_rect.top <= self.item.rect.bottom and
            collide_rect.top - self.item.rect.height >=
            self.item.rect.top - self.VERT_OFFSET_ALLOWANCE):
            self.freeze_item_y = True
            adjusted = True
            new_y = collide_rect.top - self.item.rect.height

        old_item_offset = self.item_offset

        if (self.direction == Direction.RIGHT and
            collide_rect.left <= self.item.rect.right):
            self.item_offset = \
                max(self.HORIZ_OFFSET_ALLOWANCE,
                    collide_rect.left - self.rect.right - self.item.rect.width)
            new_x = self.rect.right + self.item_offset
        elif (self.direction == Direction.LEFT and
              collide_rect.right >= self.item.rect.left):
            self.item_offset = \
                max(self.HORIZ_OFFSET_ALLOWANCE,
                    self.rect.left - collide_rect.right - self.item.rect.width)
            new_x = self.rect.left - self.item.rect.width + self.item_offset

        if old_item_offset != self.item_offset:
            adjusted = True

        if adjusted:
            self.item.move_to(new_x, new_y)

        return adjusted

    def on_moved(self, dx, dy):
        if self.item:
            mid_y = self.rect.top + \
                    (self.rect.height - self.item.rect.height) / 2

            if self.freeze_item_y:
                y = self.item.rect.top
            else:
                y = mid_y

            if y > mid_y:
                self.freeze_item_y = False
                y = mid_y

            self.item.direction = self.direction
            self.item.update_image()

            if self.direction == Direction.RIGHT:
                self.item.move_to(self.rect.right + self.item_offset, y)
            elif self.direction == Direction.LEFT:
                self.item.move_to(self.rect.left - self.item.rect.width -
                                  self.item_offset, y)

        super(TractorBeam, self).on_moved(dx, dy)

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

    MAX_HEALTH = 3
    MAX_LIVES = 3

    PROPULSION_BELOW_OFFSET = 8

    def __init__(self):
        super(Player, self).__init__('player', flip_image=True,
                                     obey_gravity=True)
        self.engine = get_engine()
        self.should_check_collisions = True

        # Sprites
        self.propulsion_below = Sprite("propulsion_below")
        self.propulsion_below.collidable = False
        self.propulsion_below.visible = 0
        self.tractor_beam = TractorBeam(self)

        # State
        self.jumping = False
        self.hovering = False
        self.block_events = False
        self.jump_origin = None
        self.hover_time_ms = 0
        self.health = self.MAX_HEALTH
        self.lives = self.MAX_LIVES
        self.last_safe_spot = None
        self.vehicle = None
        self.vehicle_move_cnx = None

        # Signals
        self.health_changed = Signal()
        self.lives_changed = Signal()

        self.direction_changed.connect(self.on_direction_changed)

    def handle_event(self, event):
        if self.block_events:
            return

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

    def ride(self, vehicle):
        self.vehicle = vehicle
        self.velocity = (self.velocity[0], 0)
        self.vehicle_moved_cnx = \
            self.vehicle.moved.connect(self.on_vehicle_moved)
        self.calculate_collision_rects()

    def jump(self):
        if (self.falling and not self.engine.god_mode) or self.jumping:
            return

        self.jump_origin = (self.rect.left, self.rect.top)
        self.jumping = True
        self.falling = False
        self.velocity = (self.velocity[0], -self.JUMP_SPEED)
        self.propulsion_below.show()

        if self.vehicle:
            self.vehicle_moved_cnx.disconnect()
            self.vehicle = None
            self.calculate_collision_rects()

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
        self.collision_masks = []
        self.collision_rects = [self.rect]

        if self.tractor_beam.item:
            self.collision_rects.append(self.tractor_beam.item.rect)

        if self.vehicle:
            self.collision_rects.append(self.vehicle.rect)

    def check_collisions(self, *args, **kwargs):
        if self.tractor_beam.item:
            self.tractor_beam.update_position(self)

        super(Player, self).check_collisions(*args, **kwargs)

    def should_adjust_position_with(self, obj, dx, dy):
        return obj != self.vehicle

    def tick(self):
        if self.hovering:
            self.hover_time_ms += 1.0 / self.engine.FPS * 1000

            if self.hover_time_ms >= self.HOVER_TIME_MS:
                self.fall()

        super(Player, self).tick()

    def on_added(self, layer):
        for obj in (self.propulsion_below, self.tractor_beam, self.vehicle):
            if obj:
                layer.add(obj)

    def on_removed(self, layer):
        for obj in (self.propulsion_below, self.tractor_beam, self.vehicle):
            if obj:
                layer.remove(obj)

    def on_moved(self, dx, dy):
        if not self.last_safe_spot:
            self.last_safe_spot = self.rect.topleft

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

        if self.vehicle and dx != 0:
            self.vehicle.move_to(
                self.rect.left -
                (self.vehicle.rect.width - self.rect.width) / 2,
                self.vehicle.rect.top)

        self.calculate_collision_rects()

        super(Player, self).on_moved(dx, dy)

    def on_collision(self, dx, dy, obj, self_rect, obj_rect):
        if obj.lethal and not self.engine.god_mode and self_rect == self.rect:
            self.on_hit()
            return

        self.last_safe_spot = self.rect.topleft

        if self.tractor_beam.item and self_rect == self.tractor_beam.item.rect:
            move_player = True

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

        if dy > 0 and not self.vehicle and isinstance(obj, Vehicle):
            self.ride(obj)

        if self.jumping and dy < 0:
            self.fall()
        else:
            super(Player, self).on_collision(dx, dy, obj, self_rect, obj_rect)

    def on_direction_changed(self):
        if self.vehicle:
            self.vehicle.direction = self.direction

    def on_vehicle_moved(self, dx, dy):
        if dy != 0:
            self.move_by(0, dy)

    def on_hit(self):
        self.health -= 1
        self.health_changed.emit()

        if self.health == 0:
            self.on_dead()
        else:
            self.move_to(*self.last_safe_spot)
            self.velocity = (0, 0)
            self.falling = False
            self.fall()

    def on_dead(self):
        self.lives -= 1
        self.lives_changed.emit()
        self.velocity = (0, 0)

        if self.lives == 0:
            self.engine.game_over()
        else:
            self.health = self.MAX_HEALTH
            self.health_changed.emit()
            self.engine.dead()
