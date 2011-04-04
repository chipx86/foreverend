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
        self.collision_rects = []

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
        matched = {}

        def _check_collision(left, right):
            if left == right:
                return False

            left_rects = left.collision_rects or [left.rect]
            right_rects = right.collision_rects or [right.rect]

            for left_rect in left_rects:
                index = left_rect.collidelist(right_rects)

                if index != -1:
                    matched['left_rect'] = left_rect
                    matched['right_rect'] = right_rects[index]
                    matched['left_obj'] = left
                    matched['right_obj'] = right
                    return True

            return False

        self.rect.move_ip(dx, dy)

        for obj in pygame.sprite.spritecollide(self, self.layer.level.group,
                                               False,
                                               _check_collision):
            if obj == self or obj.layer != self.layer or not obj.collidable:
                matched = {}
                continue

            if matched['left_obj'] == obj:
                matched_rect = matched['left_rect']
            else:
                matched_rect = matched['right_rect']
                assert matched['right_obj'] == obj

            if dy < 0:
                self.rect.top = matched_rect.bottom
            elif dy > 0:
                self.rect.bottom = matched_rect.top
            elif dx < 0:
                self.rect.left = matched_rect.right
            elif dx > 0:
                self.rect.right = matched_rect.left

            matched = {}

            self.on_collision(dx, dy, obj)

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
    MOVE_SPEED = 4
    JUMP_SPEED = 6
    FALL_SPEED = 6
    MAX_JUMP_HEIGHT = 64
    HOVER_TIME_MS = 1000

    def __init__(self, engine):
        super(Player, self).__init__('player')
        self.engine = engine
        self.jumping = False
        self.falling = False
        self.hovering = False
        self.hover_time_ms = 0
        self.jump_origin = None
        self.propulsion_below = Sprite("propulsion_below")
        self.propulsion_below.collidable = False

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.velocity = (self.MOVE_SPEED, self.velocity[1])
            elif event.key == K_LEFT:
                self.velocity = (-self.MOVE_SPEED, self.velocity[1])
            elif event.key == K_SPACE:
                self.jump()
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                if self.velocity[0] < 0:
                    self.velocity = (0, self.velocity[1])
            elif event.key == K_RIGHT:
                if self.velocity[0] > 0:
                    self.velocity = (0, self.velocity[1])
            elif event.key == K_SPACE:
                self.fall()

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
            self.jump_origin[1] - self.rect.top >= self.MAX_JUMP_HEIGHT):
            self.hover()

        if self.propulsion_below.visible:
            self.propulsion_below.move_to(self.rect.left, self.rect.bottom)

    def on_collision(self, dx, dy, obj):
        if self.jumping and dy < 0:
            self.fall()
        elif self.falling:
            self.falling = False
