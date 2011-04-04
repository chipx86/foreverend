import pygame
from pygame.locals import *

from foreverend.resources import load_image


class Direction(object):
    LEFT = 0
    RIGHT = 1


class Sprite(pygame.sprite.DirtySprite):
    FALL_SPEED = 6

    def __init__(self, name, flip_image=False, obey_gravity=False):
        super(Sprite, self).__init__()

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.name = name
        self.image = None
        self.visible = 1
        self.dirty = 2
        self.velocity = (0, 0)
        self.obey_gravity = obey_gravity
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

    def trigger(self):
        pass

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
                if dy < 0:
                    self.rect.top = obj_rect.bottom
                elif dy > 0:
                    self.rect.bottom = obj_rect.top
                elif dx < 0:
                    self.rect.left = obj_rect.right
                elif dx > 0:
                    self.rect.right = obj_rect.left

            obj.handle_collision(self, obj_rect, dx, dy)
            self.on_collision(dx, dy, obj, self_rect)
            self._colliding_objects.add(obj)

        for obj in old_colliding_objects.difference(self._colliding_objects):
            obj.handle_stop_colliding(self)

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
        pass

    def on_collision(self, dx, dy, obj, self_rect):
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


class Item(Sprite):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(obey_gravity=True, *args, **kwargs)
        self.should_check_collisions = True


class Dynamite(Item):
    def __init__(self):
        super(Dynamite, self).__init__('1999ad/dynamite')


class TractorBeam(Sprite):
    ITEM_OFFSET = -5

    def __init__(self, name='tractor_beam'):
        super(TractorBeam, self).__init__(name, flip_image=True)
        self.item = None
        self.ungrab()

    def _check_for_items(self):
        if self.item:
            return

        for obj, _, _ in self.get_collisions(ignore_collidable_flag=True):
            if isinstance(obj, Item):
                self.grab(obj)

    def grab(self, item):
        assert item
        assert not self.item
        print 'Got item'
        self.item = item
        self.item.stop_falling()
        self.item.obey_gravity = False
        self.name = 'tractor_beam'
        self.update_image()

    def ungrab(self):
        if self.item:
            self.item.obey_gravity = True
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

    def on_moved(self):
        if self.item:
            y = self.rect.top + (self.rect.height - self.item.rect.height) / 2

            if self.direction == Direction.RIGHT:
                self.item.move_to(self.rect.right + self.ITEM_OFFSET, y)
            elif self.direction == Direction.LEFT:
                self.item.move_to(self.rect.left - self.item.rect.width -
                                  self.ITEM_OFFSET, y)

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
        self.tractor_beam = TractorBeam()
        self.tractor_beam.collidable = False
        self.tractor_beam.visible = 0

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
            elif event.key == K_UP or event.key == K_DOWN:
                self.trigger_object()
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

    def trigger_object(self):
        old_rect = self.rect.copy()

        for obj, _, _ in self.get_collisions(ignore_collidable_flag=True):
            obj.trigger()

            if self.rect != old_rect:
                break

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

    def on_collision(self, dx, dy, obj, self_rect):
        if self.tractor_beam.item and self_rect == self.tractor_beam.item.rect:
            if self.direction == Direction.LEFT:
                self.move_to(obj.rect.right +
                             (self.rect.left -
                              self.tractor_beam.item.rect.left),
                             self.rect.top)
            elif self.direction == Direction.RIGHT:
                self.move_to(obj.rect.left -
                             (self.tractor_beam.item.rect.right -
                              self.rect.left),
                             self.rect.top)

        if self.jumping and dy < 0:
            self.fall()
        else:
            super(Player, self).on_collision(dx, dy, obj, self_rect)


class Box(Sprite):
    def __init__(self, width, height, color=(238, 238, 238)):
        super(Box, self).__init__('box')
        self.rect.width = width
        self.rect.height = height
        self.color = color

    def generate_image(self):
        surface = pygame.Surface(self.rect.size).convert()
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1)
        return surface


class Elevator(Sprite):
    def __init__(self):
        super(Elevator, self).__init__('1999ad/elevator')
        self.collidable = False
        self.destination = None

    def trigger(self):
        if self.destination:
            player = self.layer.level.engine.player
            dest_rect = self.destination.rect

            player.move_to(
                dest_rect.left + (dest_rect.width - player.rect.width) / 2,
                dest_rect.bottom - player.rect.height)


class Volcano(Sprite):
    BASE_CAVERN_RECT = pygame.Rect(0, 310, 550, 55)

    def __init__(self, name='65000000bc/volcano'):
        super(Volcano, self).__init__(name)
        self.cavern_rect = self.BASE_CAVERN_RECT
        self.default_name = name
        self.interior_name = name + '_inside'

    def on_moved(self):
        self.cavern_rect.left = self.rect.left + self.BASE_CAVERN_RECT.left
        self.cavern_rect.top = self.rect.top + self.BASE_CAVERN_RECT.top
        self.ground_rect = pygame.Rect(self.rect.left, self.cavern_rect.bottom,
                                       self.rect.width, self.rect.width)
        self.collision_rects = [
            pygame.Rect(self.rect.left, self.rect.top, self.rect.width,
                        self.cavern_rect.top - self.rect.top),
            pygame.Rect(self.cavern_rect.right,
                        self.cavern_rect.top,
                        self.rect.width - self.cavern_rect.width,
                        self.cavern_rect.height),
            self.ground_rect,
        ]

    def handle_collision(self, obj, matched_rect, dx, dy):
        if (isinstance(obj, Player) and dy > 0 and
            matched_rect == self.ground_rect):
            self.name = self.interior_name
            self.update_image()

    def handle_stop_colliding(self, obj):
        if (self.name == self.interior_name and isinstance(obj, Player) and
            not obj.rect.colliderect(self.rect)):
            self.name = self.default_name
            self.update_image()


class Mountain(Sprite):
    BASE_COLLISION_RECTS = [
        (0, 991, 1565, 11),
        (0, 954, 140, 37),
        (0, 900, 140, 54),
        (1467, 954, 98, 37),
        (1459, 937, 94, 17),
        (1450, 922, 96, 15),
        (1428, 878, 96, 22),
        (443, 219, 93, 40),
        (350, 230, 93, 100),
    ]

    def __init__(self, name):
        super(Mountain, self).__init__(name)
        self.default_name = name
        self.interior_name = name + '_interior'

    def on_moved(self):
        self.collision_rects = [
            pygame.Rect(self.rect.left + x, self.rect.top + y, w, h)
            for x, y, w, h in self.BASE_COLLISION_RECTS
        ]

    def handle_collision(self, obj, matched_rect, dx, dy):
        if (isinstance(obj, Player) and dy > 0 and
            self.rect.contains(matched_rect)):
            self.name = self.interior_name
            self.update_image()

    def handle_stop_colliding(self, obj):
        if (self.name == self.interior_name and isinstance(obj, Player) and
            not self.rect.contains(obj.rect)):
            self.name = self.default_name
            self.update_image()


class Mountain600AD(Mountain):
    def __init__(self):
        super(Mountain600AD, self).__init__('600ad/mountain')


class Mountain1999AD(Mountain):
    BASE_COLLISION_RECTS = Mountain.BASE_COLLISION_RECTS + [
        (443, 126, 100, 100),
    ]
    def __init__(self):
        super(Mountain1999AD, self).__init__('1999ad/mountain')
