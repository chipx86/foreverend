import pygame
from pygame.locals import *

from foreverend.resources import load_image


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, name):
        super(Sprite, self).__init__()

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.name = name
        self.image = None
        self.visible = 1
        self.dirty = 2
        self.velocity = (0, 0)
        self.collidable = True
        self.check_collisions = False
        self.collision_rects = []
        self._colliding_objects = set()

    def __repr__(self):
        return 'Sprite %s (%s, %s, %s, %s)' % \
               (self.name, self.rect.left, self.rect.top,
                self.rect.width, self.rect.height)

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

    def update_image(self):
        self.image = self.generate_image()
        assert self.image
        self.rect.size = self.image.get_rect().size

    def generate_image(self):
        return load_image(self.name)

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

        old_colliding_objects = set(self._colliding_objects)
        self._colliding_objects = set()

        for obj, self_rect, obj_rect in self.get_collisions():
            if dy < 0:
                self.rect.top = obj_rect.bottom
            elif dy > 0:
                self.rect.bottom = obj_rect.top
            elif dx < 0:
                self.rect.left = obj_rect.right
            elif dx > 0:
                self.rect.right = obj_rect.left

            obj.handle_collision(self, obj_rect, dx, dy)
            self.on_collision(dx, dy, obj)
            self._colliding_objects.add(obj)

        for obj in old_colliding_objects.difference(self._colliding_objects):
            obj.handle_stop_colliding(self)

    def get_collisions(self, group=None, ignore_collidable_flag=False):
        if not self.check_collisions:
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
             (not left.collidable or not right.collidable)) or
            (not left.check_collisions and not right.check_collisions)):
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
        pass

    def on_moved(self):
        pass

    def on_collision(self, dx, dy, obj):
        pass

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


class Player(Sprite):
    MOVE_SPEED = 6
    JUMP_SPEED = 6
    FALL_SPEED = 6
    MAX_JUMP_HEIGHT = 100
    HOVER_TIME_MS = 1000

    PROPULSION_BELOW_OFFSET = 8

    # Directions
    LEFT = 0
    RIGHT = 1

    def __init__(self, engine):
        super(Player, self).__init__('player')
        self.engine = engine
        self.jumping = False
        self.falling = False
        self.hovering = False
        self.check_collisions = True
        self.hover_time_ms = 0
        self.jump_origin = None
        self.propulsion_below = Sprite("propulsion_below")
        self.propulsion_below.collidable = False
        self.direction = self.RIGHT

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.move_right()
            elif event.key == K_LEFT:
                self.move_left()
            elif event.key == K_SPACE:
                self.jump()
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

    def generate_image(self):
        if self.direction == self.LEFT:
            name = self.name + '-left'
        elif self.direction == self.RIGHT:
            name = self.name + '-right'
        else:
            assert False

        return load_image(name)

    def move_right(self):
        self.velocity = (self.MOVE_SPEED, self.velocity[1])

        if self.direction != self.RIGHT:
            self.direction = self.RIGHT
            self.update_image()

    def move_left(self):
        self.velocity = (-self.MOVE_SPEED, self.velocity[1])

        if self.direction != self.LEFT:
            self.direction = self.LEFT
            self.update_image()

    def trigger_object(self):
        old_rect = self.rect.copy()

        for obj, _, _ in self.get_collisions(ignore_collidable_flag=True):
            obj.trigger()

            if self.rect != old_rect:
                break

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
        self.falling = True
        self.velocity = (self.velocity[0], self.FALL_SPEED)

    def hover(self):
        if self.hovering:
            return

        self.propulsion_below.show()
        self.jumping = False
        self.hovering = True
        self.hover_time_ms = 0
        self.velocity = (self.velocity[0], 0)

    def tick(self):
        if self.hovering:
            self.hover_time_ms += 1.0 / self.engine.FPS * 1000

            if self.hover_time_ms >= self.HOVER_TIME_MS:
                self.fall()

    def on_added(self, layer):
        layer.add(self.propulsion_below)
        self.propulsion_below.hide()

    def on_removed(self, layer):
        layer.remove(self.propulsion_below)

    def on_moved(self):
        if (self.jumping and
            not self.engine.god_mode and
            self.jump_origin[1] - self.rect.top >= self.MAX_JUMP_HEIGHT):
            self.hover()

        if self.propulsion_below.visible:
            if self.direction == self.RIGHT:
                offset = self.PROPULSION_BELOW_OFFSET
            if self.direction == self.LEFT:
                offset = self.rect.width - self.propulsion_below.rect.width - \
                         self.PROPULSION_BELOW_OFFSET

            self.propulsion_below.move_to(self.rect.left + offset,
                                          self.rect.bottom)

    def on_collision(self, dx, dy, obj):
        if self.jumping and dy < 0:
            self.fall()
        elif self.falling:
            self.falling = False


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
