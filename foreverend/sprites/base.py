import pygame
from pygame.locals import *

from foreverend.resources import load_image
from foreverend.signals import Signal


class Direction(object):
    LEFT = 0
    RIGHT = 1


class Sprite(pygame.sprite.DirtySprite):
    FALL_SPEED = 6

    def __init__(self, name, flip_image=False, obey_gravity=False):
        super(Sprite, self).__init__()

        # Signals
        self.moved = Signal()

        # State
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.name = name
        self.image = None
        self.visible = 1
        self.dirty = 2
        self.velocity = (0, 0)
        self.obey_gravity = obey_gravity
        self.lethal = False
        self.falling = False
        self.collidable = True
        self.should_check_collisions = False
        self.flip_image = flip_image
        self.collision_rects = []
        self._colliding_objects = set()
        self._direction = Direction.RIGHT
        self._flipped_images = {}

    def __repr__(self):
        return 'Sprite %s (%s, %s, %s, %s)' % \
               (self.name, self.rect.left, self.rect.top,
                self.rect.width, self.rect.height)

    def _set_direction(self, direction):
        if self.direction != direction:
            self._direction = direction
            self.update_image()

    direction = property(lambda self: self._direction, _set_direction)

    def show(self):
        if not self.visible:
            self.visible = 1
            self.dirty = 2
            self.layer.add(self)

    def hide(self):
        if self.visible:
            self.visible = 0
            self.dirty = 1
            self.layer.remove(self)

    def fall(self):
        if self.falling or not self.obey_gravity:
            return

        self.falling = True
        self.velocity = (self.velocity[0], self.FALL_SPEED)

    def stop_falling(self):
        if self.obey_gravity:
            self.falling = False
            self.velocity = (self.velocity[0], 0)

    def update_image(self):
        self.image = self.generate_image()
        assert self.image
        self.rect.size = self.image.get_rect().size

    def generate_image(self):
        image = load_image(self.name)

        if self.flip_image and self._direction == Direction.LEFT:
            if self.name not in self._flipped_images:
                self._flipped_images[self.name] = \
                    pygame.transform.flip(image, True, False)

            image = self._flipped_images[self.name]

        return image

    def move_to(self, x, y, check_collisions=False):
        self.move_by(x - self.rect.x, y - self.rect.y, check_collisions)

    def move_by(self, dx, dy, check_collisions=True):
        if check_collisions:
            if dx:
                self._move(dx=dx)

            if dy:
                self._move(dy=dy)
        else:
            self.rect.move_ip(dx, dy)

        self.on_moved()

    def _move(self, dx=0, dy=0):
        self.rect.move_ip(dx, dy)
        self.check_collisions(dx, dy)

    def check_collisions(self, dx=0, dy=0):
        old_colliding_objects = set(self._colliding_objects)
        self._colliding_objects = set()

        for obj, self_rect, obj_rect in self.get_collisions():
            if self_rect == self.rect:
                self.position_beside(obj_rect, dx, dy)

            obj.handle_collision(self, obj_rect, dx, dy)
            self.on_collision(dx, dy, obj, self_rect, obj_rect)
            self._colliding_objects.add(obj)

        for obj in old_colliding_objects.difference(self._colliding_objects):
            obj.handle_stop_colliding(self)

    def position_beside(self, rect, dx, dy):
        if dy < 0:
            self.rect.top = rect.bottom
        elif dy > 0:
            self.rect.bottom = rect.top
        elif dx < 0:
            self.rect.left = rect.right
        elif dx > 0:
            self.rect.right = rect.left

    def get_collisions(self, group=None, ignore_collidable_flag=False):
        if not self.should_check_collisions and not ignore_collidable_flag:
            raise StopIteration

        if group is None:
            group = self.layer.level.group
            compare_layers = True
        else:
            compare_layers = False

        # We want more detailed collision info, so we use our own logic
        # instead of calling spritecollide.
        for obj in group:
            self_rect, obj_rect = \
                self._check_collision(self, obj, compare_layers,
                                      ignore_collidable_flag)

            if self_rect and obj_rect:
                yield obj, self_rect, obj_rect

    def _check_collision(self, left, right, compare_layers,
                         ignore_collidable_flag):
        if (left == right or
            (compare_layers and left.layer != right.layer) or
            (not ignore_collidable_flag and
             ((not left.collidable or not right.collidable) or
              (not left.should_check_collisions and
               not right.should_check_collisions)))):
            return None, None

        left_rects = left.collision_rects or [left.rect]
        right_rects = right.collision_rects or [right.rect]

        for left_rect in left_rects:
            index = left_rect.collidelist(right_rects)

            if index != -1:
                return left_rect, right_rects[index]

        return None, None

    def handle_collision(self, obj, rect, dx, dy):
        pass

    def handle_stop_colliding(self, obj):
        pass

    def tick(self):
        if self.velocity != (0, 0):
            self.move_by(*self.velocity)

    def on_moved(self):
        self.moved.emit()

    def on_collision(self, dx, dy, obj, self_rect, obj_rect):
        if self.obey_gravity and self.falling:
            self.falling = False

    def on_added(self, layer):
        pass

    def on_removed(self, layer):
        pass


class TiledSprite(Sprite):
    def __init__(self, name, tiles_x=1, tiles_y=1):
        super(TiledSprite, self).__init__(name)

        self.tiles_x = tiles_x
        self.tiles_y = tiles_y

    def update_image(self):
        super(TiledSprite, self).update_image()

        tile_width = self.rect.width
        tile_height = self.rect.height

        self.rect.width = self.tiles_x * self.rect.width
        self.rect.height = self.tiles_y * self.rect.height

        new_image = pygame.Surface(self.rect.size).convert_alpha()

        for y in range(0, self.tiles_y):
            for x in range(0, self.tiles_x):
                new_image.blit(self.image,
                               (self.rect.x + x * tile_width,
                                self.rect.y + y * tile_height))

        self.image = new_image
