import pygame
from pygame.locals import *

from foreverend.levels import get_levels
from foreverend.sprites import Player, TiledSprite


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

        self.levels = [level(self) for level in get_levels()]
        self.active_level = self.levels[0]

        self.player = Player(self)
        self.active_level.switch_time_period(0)
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
        self.screen.blit(self.bg, (0, 0))
        self.active_level.draw(self.screen)
        pygame.display.flip()

    def _tick(self):
        if not self.paused:
            self.active_level.tick()

            for sprite in [self.player]:
                if sprite.velocity != (0, 0):
                    sprite.move_by(*sprite.velocity)
