import pygame
from pygame.locals import *

from foreverend.resources import load_image
from foreverend.signals import Signal


class Direction(object):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Sprite(pygame.sprite.DirtySprite):
    FALL_SPEED = 6

    def __init__(self, name, flip_image=False, obey_gravity=False):
        super(Sprite, self).__init__()

        # Signals
        self.moved = Signal()
        self.direction_changed = Signal()
        self.reverse_gravity_changed = Signal()

        # State
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.quad_trees = set()
        self.layer = None
        self.name = name
        self.image = None
        self.visible = 1
        self.dirty = 2
        self.velocity = (0, 0)
        self.obey_gravity = obey_gravity
        self.reverse_gravity = False
        self.lethal = False
        self.falling = False
        self.collidable = True
        self.grabbed = False
        self.grabbable = False
        self.should_check_collisions = False
        self.use_pixel_collisions = False
        self.flip_image = flip_image
        self.collision_rects = []
        self.collision_masks = []
        self._colliding_objects = set()
        self._direction = Direction.RIGHT
        self._flipped_images = {}

    def __repr__(self):
        return 'Sprite %s (%s, %s, %s, %s)' % \
               (self.name, self.rect.left, self.rect.top,
                self.rect.width, self.rect.height)

    def set_reverse_gravity(self, reverse_gravity):
        if self.reverse_gravity != reverse_gravity:
            self.reverse_gravity = reverse_gravity
            self.velocity = (self.velocity[0], -self.velocity[1])
            self.update_image()
            self.reverse_gravity_changed.emit()

    def _set_direction(self, direction):
        if self.direction != direction:
            self._direction = direction
            self.direction_changed.emit()
            self.update_image()
    direction = property(lambda self: self._direction, _set_direction)

    def show(self):
        if not self.visible:
            self.visible = 1
            self.dirty = 2
            self.layer.update_sprite(self)

    def hide(self):
        if self.visible:
            self.visible = 0
            self.dirty = 1
            self.layer.update_sprite(self)

    def remove(self):
        self.hide()
        self.layer.remove(self)

    def fall(self):
        if self.falling or not self.obey_gravity:
            return

        self.falling = True

        if self.reverse_gravity:
            self.velocity = (self.velocity[0], -self.FALL_SPEED)
        else:
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
        if not self.name:
            # Must be a custom sprite.
            return self.image

        image = load_image(self.name)

        if (self.flip_image and
            (self._direction == Direction.LEFT or self.reverse_gravity)):
            flip_h = (self.direction == Direction.LEFT)
            flip_v = self.reverse_gravity

            key = (self.name, flip_h, flip_v)

            if key not in self._flipped_images:
                self._flipped_images[key] = \
                    pygame.transform.flip(image, flip_h, flip_v)

            image = self._flipped_images[key]

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

        self.on_moved(dx, dy)

    def _move(self, dx=0, dy=0):
        self.rect.move_ip(dx, dy)
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.layer.area.size[0])
        self.rect.top = max(self.rect.top, 0)
        self.check_collisions(dx, dy)

    def check_collisions(self, dx=0, dy=0):
        old_colliding_objects = set(self._colliding_objects)
        self._colliding_objects = set()

        for obj, self_rect, obj_rect in self.get_collisions():
            if (self_rect == self.rect and
                self.should_adjust_position_with(obj, dx, dy)):
                self.position_beside(obj_rect, dx, dy)

            obj.handle_collision(self, obj_rect, dx, dy)
            self.on_collision(dx, dy, obj, self_rect, obj_rect)
            self._colliding_objects.add(obj)

        for obj in old_colliding_objects.difference(self._colliding_objects):
            obj.handle_stop_colliding(self)

    def should_adjust_position_with(self, obj, dx, dy):
        return True

    def position_beside(self, rect, dx, dy):
        if dy < 0:
            self.rect.top = rect.bottom
        elif dy > 0:
            self.rect.bottom = rect.top
        elif dx < 0:
            self.rect.left = rect.right
        elif dx > 0:
            self.rect.right = rect.left

    def get_collisions(self, tree=None, ignore_collidable_flag=False):
        if not self.should_check_collisions and not ignore_collidable_flag:
            raise StopIteration

        if tree is None:
            tree = self.layer.quad_tree

        num_checks = 0

        if self.collision_rects:
            self_rect = self.collision_rects[0].unionall(
                self.collision_rects[1:])
        else:
            self_rect = self.rect

        # We want more detailed collision info, so we use our own logic
        # instead of calling spritecollide.
        for obj in tree.get_sprites(self_rect):
            num_checks += 1
            self_rect, obj_rect = \
                self._check_collision(self, obj, ignore_collidable_flag)

            if self_rect and obj_rect:
                yield obj, self_rect, obj_rect

        #print 'Performing %s checks' % num_checks

    def _check_collision(self, left, right, ignore_collidable_flag):
        if (left == right or
            left.layer.index != right.layer.index or
            (not ignore_collidable_flag and
             ((not left.collidable or not right.collidable) or
              (not left.should_check_collisions and
               not right.should_check_collisions)))):
            return None, None

        left_rects = left.collision_rects or [left.rect]
        right_rects = right.collision_rects or [right.rect]

        for left_index, left_rect in enumerate(left_rects):
            right_index = left_rect.collidelist(right_rects)

            if right_index == -1:
                continue

            right_rect = right_rects[right_index]

            if left.use_pixel_collisions or right.use_pixel_collisions:
                left_mask = left._build_mask(left_rect, left_index)
                right_mask = right._build_mask(right_rect, right_index)

                offset = (left_rect.left - right_rect.left,
                          left_rect.top - right_rect.top)
                pos = right_mask.overlap(left_mask, offset)

                if not pos:
                    continue

                mask = right_mask.overlap_mask(left_mask, offset)
                collision_rect = mask.get_bounding_rects()[0]
                right_rect = pygame.Rect(right_rect.left + collision_rect.left,
                                         right_rect.top + collision_rect.top,
                                         *collision_rect.size)

            return left_rect, right_rect

        return None, None

    def _build_mask(self, rect, collision_index):
        mask = None
        image = None

        if self.use_pixel_collisions:
            if collision_index < len(self.collision_masks):
                mask = self.collision_masks[collision_index]

            if not mask:
                mask = getattr(self, 'mask', None)

            if not mask:
                if rect == self.rect:
                    image = self.image
                else:
                    try:
                        image = self.image.subsurface(rect)
                    except ValueError, e:
                        image = None

                if image:
                    mask = pygame.sprite.from_surface(image)

        if not mask:
            mask = pygame.Mask(rect.size)
            mask.fill()

        if self.collision_rects:
            if not self.collision_masks:
                self.collision_masks = [None] * len(self.collision_rects)

            self.collision_masks[collision_index] = mask
        else:
            self.mask = mask

        return mask

    def handle_collision(self, obj, rect, dx, dy):
        pass

    def handle_stop_colliding(self, obj):
        pass

    def tick(self):
        if self.velocity != (0, 0):
            self.move_by(*self.velocity)

    def on_moved(self, dx, dy):
        self.moved.emit(dx, dy)

    def on_collision(self, dx, dy, obj, self_rect, obj_rect):
        if dy != 0 and self.obey_gravity and self.falling:
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
        new_image.fill((0, 0, 0, 0))

        for y in range(0, self.tiles_y):
            for x in range(0, self.tiles_x):
                new_image.blit(self.image,
                               (self.rect.x + x * tile_width,
                                self.rect.y + y * tile_height))

        self.image = new_image
