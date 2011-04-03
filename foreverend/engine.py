import pygame
from pygame.locals import *

from foreverend.sprites import Player, TiledSprite


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
            self.level.group.remove(obj)
            self.objs.discard(obj)

    def __iter__(self):
        return iter(self.objs)

    def handle_event(self, event):
        pass


class Level(object):
    def __init__(self, engine, num):
        self.engine = engine
        self.layers = []
        self.group = pygame.sprite.LayeredDirty()
        self.default_layer = self.new_layer()
        self.main_layer = self.new_layer()

        screen = engine.screen
        ground = TiledSprite('ground', 40, 1)
        self.main_layer.add(ground)
        ground.move_to(0, screen.get_height() - ground.rect.height)

        if num == 2:
            ground = TiledSprite('ground', 40, 1)
            self.main_layer.add(ground)
            ground.move_to(60, screen.get_height() - 2 * ground.rect.height)

    def new_layer(self):
        layer = Layer(len(self.layers), self)
        layer.level = self
        self.layers.append(layer)
        return layer

    def draw(self, screen):
        self.group.draw(screen)

    def tick(self):
        self.group.update()

        for sprite in self.group:
            sprite.tick()


class LevelSet(object):
    def __init__(self, engine):
        self.engine = engine
        self.levels = []
        self.active_level = None

    def add(self, level):
        self.levels.append(level)
        level.levelset = self

        if not self.active_level:
            self.active_level = level

    def switch_level(self, level_num):
        player = self.engine.player
        self.active_level.main_layer.remove(player)
        self.active_level = self.levels[level_num - 1]
        self.active_level.main_layer.add(player)


class ForeverEndEngine(object):
    FPS = 30

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.paused = False

    def run(self):
        self.bg = pygame.Surface(self.screen.get_size()).convert()
        self._setup_game()
        self._mainloop()

    def _setup_game(self):
        self.bg.fill((255, 255, 255))

        self.levelsets = []

        levelset = LevelSet(self)
        level = Level(self, 1)
        levelset.add(level)

        level = Level(self, 2)
        levelset.add(level)

        self.active_levelset = levelset

        self.player = Player(self)
        self.active_levelset.active_level.main_layer.add(self.player)
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
            self.clock.tick(self.FPS)

    def _handle_event(self, event):
        if (event.type == QUIT or
            (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()
            return False
        elif event.type == KEYDOWN and event.key == K_TAB:
            # Switch time periods
            self._show_time_periods()
        elif event.type == KEYDOWN and event.key == K_RETURN:
            if self.paused:
                self._unpause()
            else:
                self._pause()
        # XXX
        elif event.type == KEYDOWN and event.key == K_1:
            self.active_levelset.switch_level(1)
        elif event.type == KEYDOWN and event.key == K_2:
            self.active_levelset.switch_level(2)
        elif event.type == KEYDOWN and event.key == K_3:
            self.active_levelset.switch_level(3)
        else:
            self.player.handle_event(event)

        return True

    def _pause(self):
        self.paused = True

    def _unpause(self):
        self.paused = False

    def _show_time_periods(self):
        self._pause()

    def _paint(self):
        self.screen.blit(self.bg, (0, 0))
        self.active_levelset.active_level.draw(self.screen)
        pygame.display.flip()

    def _tick(self):
        if not self.paused:
            self.active_levelset.active_level.tick()

            for sprite in [self.player]:
                if sprite.velocity != (0, 0):
                    sprite.move_by(*sprite.velocity)
