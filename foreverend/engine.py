import pygame
from pygame.locals import *

from foreverend.levels import get_levels
from foreverend.sprites import Player, TiledSprite


class Camera(object):
    SCREEN_PAD = 64

    def __init__(self, engine):
        self.engine = engine
        self.rect = self.engine.screen.get_rect()
        self.old_player_rect = None

    def update(self):
        player_rect = self.engine.player.rect

        if player_rect == self.old_player_rect:
            return

        self.old_player_rect = player_rect.copy()
        old_rect = self.rect.copy()

        if player_rect.centerx > self.rect.centerx + self.SCREEN_PAD:
            self.rect.centerx = player_rect.centerx - self.SCREEN_PAD
        elif player_rect.centerx < self.rect.centerx - self.SCREEN_PAD:
            self.rect.centerx = player_rect.centerx + self.SCREEN_PAD

        if player_rect.centery > self.rect.centery + self.SCREEN_PAD:
            self.rect.centery = player_rect.centery - self.SCREEN_PAD
        elif player_rect.centery < self.rect.centery - self.SCREEN_PAD:
            self.rect.centery = player_rect.centery + self.SCREEN_PAD

        if old_rect != self.rect:
            self.rect.clamp_ip(
                pygame.Rect(0, 0, *self.engine.active_level.get_size()))


class ForeverEndEngine(object):
    FPS = 30

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.paused = False
        self.camera = Camera(self)

    def run(self):
        self._setup_game()
        self._mainloop()

    def _setup_game(self):
        self.player = Player(self)

        self.levels = [level(self) for level in get_levels()]
        self.switch_level(0)

        self.active_level.switch_time_period(0)
        self.player.move_to(10, self.screen.get_height() - 32 -
                            self.player.rect.height)
        self.player.show()

    def switch_level(self, num):
        assert num < len(self.levels)
        self.active_level = self.levels[num]
        self.active_level.switch_time_period(0)
        self.surface = pygame.Surface(self.active_level.get_size())

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
        elif event.type == KEYDOWN and event.key == K_RETURN:
            if self.paused:
                self._unpause()
            else:
                self._pause()
        elif not self.paused:
            if event.type == KEYDOWN and event.key == K_TAB:
                # Switch time periods
                self._show_time_periods()
            # XXX
            elif event.type == KEYDOWN and event.key == K_1:
                self.active_level.switch_time_period(0)
            elif event.type == KEYDOWN and event.key == K_2:
                self.active_level.switch_time_period(1)
            elif event.type == KEYDOWN and event.key == K_3:
                self.active_level.switch_time_period(2)
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
        self.active_level.draw(self.surface)
        self.screen.blit(self.surface.subsurface(
            pygame.Rect(self.camera.rect.left, self.camera.rect.top,
                        self.screen.get_width(), self.screen.get_height())),
            (0, 0))
        pygame.display.flip()

    def _tick(self):
        if not self.paused:
            self.active_level.tick()

            for sprite in [self.player]:
                if sprite.velocity != (0, 0):
                    sprite.move_by(*sprite.velocity)

            self.camera.update()