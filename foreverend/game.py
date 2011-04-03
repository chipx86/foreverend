#!/usr/bin/env python

import pygame
from pygame.locals import *

from foreverend.resources import load_image


FPS = 30


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

    def remove(self, *objs):
        for obj in objs:
            obj.update_image()
            self.map.group.remove(obj)
            self.objs.discard(obj)

    def __iter__(self):
        return iter(self.objs)

    def handle_event(self, event):
        pass


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, name):
        super(Sprite, self).__init__()

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.name = name
        self.image = None
        self.visible = 1
        self.dirty = 2
        self.velocity = (0, 0)

    def show(self):
        if not self.visible:
            self.visible = 1
            self.dirty = 1
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

    def move_to(self, x, y):
        self.rect.move_ip(x - self.rect.x, y - self.rect.y)
        self.on_moved()

    def move_by(self, dx, dy):
        self.rect.move_ip(dx, dy)
        self.on_moved()

    def on_moved(self):
        pass

    def on_collided(self, obj):
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
    MOVE_SPEED = 2
    JUMP_SPEED = 4
    FALL_SPEED = 4
    MAX_JUMP_HEIGHT = 64

    def __init__(self):
        super(Player, self).__init__('player')
        self.jumping = False
        self.falling = False
        self.jump_origin = None

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

    def fall(self):
        if self.falling:
            return

        self.jumping = False
        self.falling = True
        self.velocity = (self.velocity[0], self.FALL_SPEED)

    def on_moved(self):
        if (self.jumping and
            self.jump_origin[1] - self.rect.top >= self.MAX_JUMP_HEIGHT):
            self.fall()

    def on_collided(self, obj):
        if self.velocity[1] == 0:
            if self.jumping:
                self.fall()
            elif self.falling:
                self.falling = False


class Level(object):
    def __init__(self, engine):
        self.engine = engine
        self.layers = []
        self.group = pygame.sprite.LayeredDirty()
        self.default_layer = self.new_layer()
        self.main_layer = self.new_layer()
        self.collision_rects = []

        screen = engine.screen
        self.ground = TiledSprite('ground', 40, 1)
        self.main_layer.add(self.ground)
        self.ground.move_to(0, screen.get_height() - self.ground.rect.height)
        self.collision_rects.append(self.ground.rect)

    def new_layer(self):
        layer = Layer(len(self.layers), self)
        layer.level = self
        self.layers.append(layer)
        return layer

    def draw(self, screen):
        self.group.draw(screen)

    def tick(self):
        self.group.update()
        self.check_collisions()

    def check_collisions(self):
        player = self.engine.player

        for obj in pygame.sprite.spritecollide(player, self.group, False):
            if obj == player or obj.layer != player.layer:
                continue

            print 'collide - %s -- %s' % (obj.rect, player.rect)
            if (player.rect.left >= obj.rect.left and
                player.rect.right <= obj.rect.right):
                if obj.rect.top <= player.rect.bottom:
                    player.velocity = (player.velocity[0], 0)
                    player.move_to(player.rect.left,
                                   obj.rect.top - player.rect.height)
                elif obj.rect.bottom >= player.rect.top:
                    player.velocity = (player.velocity[0], 0)
                    player.move_to(player.rect.left, obj.rect.bottom)

            if (player.rect.top >= obj.rect.top and
                player.rect.bottom <= obj.rect.bottom):
                if obj.rect.left <= player.rect.right:
                    player.velocity = (0, player.velocity[1])
                    player.move_to(obj.rect.left - player.rect.width,
                                   player.rect.top)
                elif obj.rect.right >= player.rect.left:
                    player.velocity = (0, player.velocity[1])
                    player.move_to(obj.rect.right, player.rect.top)

            player.on_collided(obj)


class ForeverEndEngine(object):
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

    def run(self):
        self.bg = pygame.Surface(self.screen.get_size()).convert()
        self._setup_game()
        self._mainloop()

    def _setup_game(self):
        self.bg.fill((255, 255, 255))
        self.level = Level(self)

        self.player = Player()
        self.level.main_layer.add(self.player)
        self.player.move_to(10, self.screen.get_height() - 32 -
                            self.player.rect.height)
        self.player.show()

    def _mainloop(self):
        while 1:
            for event in pygame.event.get():
                if not self._handle_event(event):
                    return

            self._tick()
            self._paint()
            self.clock.tick(FPS)

    def _handle_event(self, event):
        if (event.type == QUIT or
            (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()
            return False
        else:
            self.player.handle_event(event)

        return True

    def _paint(self):
        self.screen.blit(self.bg, (0, 0))
        self.level.draw(self.screen)
        pygame.display.flip()

    def _tick(self):
        for sprite in [self.player]:
            if sprite.velocity != (0, 0):
                sprite.move_by(*sprite.velocity)

        self.level.tick()


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Forever End")

    engine = ForeverEndEngine(screen)
    engine.run()

    pygame.quit()
