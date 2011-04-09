import sys

import pygame
from pygame.locals import *

try:
    import pygame.mixer
    has_mixer = True
except:
    has_mixer = False

from foreverend import set_engine
from foreverend.cutscenes import ClosingCutscene, OpeningCutscene, \
                                 TutorialCutscene
from foreverend.levels import get_levels
from foreverend.resources import get_music_filename, unload_images
from foreverend.signals import Signal
from foreverend.sprites import Player, TiledSprite
from foreverend.timer import Timer
from foreverend.ui import UIManager


class Camera(object):
    SCREEN_PAD = 64

    def __init__(self, engine):
        self.engine = engine
        self.rect = self.engine.screen.get_rect()
        self.rect.height -= self.engine.ui_manager.control_panel.rect.height
        self.old_player_rect = None

    def update(self):
        if self.engine.paused or not self.engine.active_level:
            return

        player_rect = self.engine.player.rect

        if player_rect == self.old_player_rect:
            return

        if player_rect.centerx > self.rect.centerx + self.SCREEN_PAD:
            self.rect.centerx = player_rect.centerx - self.SCREEN_PAD
        elif player_rect.centerx < self.rect.centerx - self.SCREEN_PAD:
            self.rect.centerx = player_rect.centerx + self.SCREEN_PAD

        if player_rect.centery > self.rect.centery + self.SCREEN_PAD:
            self.rect.centery = player_rect.centery - self.SCREEN_PAD
        elif player_rect.centery < self.rect.centery - self.SCREEN_PAD:
            self.rect.centery = player_rect.centery + self.SCREEN_PAD

        self.rect.clamp_ip(
            pygame.Rect(0, 0, *self.engine.active_level.active_area.size))


class ForeverEndEngine(object):
    FPS = 30

    def __init__(self, screen):
        set_engine(self)

        # Signals
        self.level_changed = Signal()
        self.tick = Signal()

        # State and objects
        self.active_level = None
        self.active_cutscene = None
        self.paused = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.ui_manager = UIManager(self)
        self.camera = None

        # Debug flags
        self.debug_rects = False
        self.god_mode = False
        self.show_debug_info = False

        self.area_changed_cnx = None
        self.ui_ready_cnx = None

    def run(self):
        self.active_cutscene = OpeningCutscene()
        self.active_cutscene.done.connect(self._setup_game)
        self.active_cutscene.start()

        self._mainloop()

    def quit(self):
        pygame.quit()
        sys.exit(0)

    def dead(self):
        def on_timeout():
            widget.close()
            self.restart_level()

        widget = self.ui_manager.show_textbox([
            "It's okay! You had another guy!",
            "%s lives left." % self.player.lives
        ])
        self.paused = True

        timer = Timer(2000, on_timeout, one_shot=True)

    def restart_level(self):
        self.switch_level(self.levels.index(self.active_level))

    def game_over(self):
        def on_timeout():
            widget.close()
            self._setup_game()
            sys.exit(0)

        widget = self.ui_manager.show_textbox('Game Over')
        self.paused = True

        timer = Timer(2000, on_timeout, one_shot=True)

    def show_end_scene(self):
        self.ui_manager.control_panel.close()
        self.active_level = None
        self.active_cutscene = ClosingCutscene()
        self.active_cutscene.start()

    def _setup_game(self):
        self.ui_manager.add_control_panel()
        self.camera = Camera(self)
        self.tick.clear()

        self.active_cutscene = None

        self.player.lives = self.player.MAX_LIVES
        self.player.health = self.player.MAX_HEALTH
        self.player.update_image()
        self.levels = [level(self) for level in get_levels()]
        self.switch_level(0)

        if self.ui_ready_cnx:
            self.ui_ready_cnx.disconnect()

        self.paused = True
        self.ui_ready_cnx = self.ui_manager.ready.connect(self.show_tutorial)

    def show_tutorial(self):
        def on_done():
            self.active_cutscene = False
            self.paused = False

        self.ui_ready_cnx.disconnect()
        self.ui_ready_cnx = None

        self.active_cutscene = TutorialCutscene()
        self.active_cutscene.start()
        self.active_cutscene.done.connect(on_done)

    def switch_level(self, num):
        assert num < len(self.levels)
        self.paused = False
        self.player.stop_tractor_beam()
        self.player.stop_riding()
        self.player.block_events = False
        self.player.reverse_gravity = False
        self.player.jumping = False
        self.player.falling = False
        self.player.fall()
        self.active_level = self.levels[num]
        self.active_level.reset()

        if self.area_changed_cnx:
            self.area_changed_cnx.disconnect()

        self.area_changed_cnx = \
            self.active_level.area_changed.connect(self._on_area_changed)

        self.active_level.switch_time_period(0)
        self.player.move_to(*self.active_level.active_area.start_pos)
        self.camera.update()
        self.player.show()

        if False and has_mixer:
            pygame.mixer.music.stop()

            if self.active_level.music:
                pygame.mixer.music.load(
                    get_music_filename(self.active_level.music))
                pygame.mixer.music.play(-1)

        self.level_changed.emit()

    def next_level(self):
        def on_timeout():
            widget.close()
            unload_images()
            self.switch_level(next_level)

        next_level = self.levels.index(self.active_level) + 1
        widget = self.ui_manager.show_textbox([
            'You got the artifact! %s left to go.'
            % (len(self.levels) - next_level),
        ])

        timer = Timer(2000, on_timeout, one_shot=True)
        timer.start()

    def _on_area_changed(self):
        area = self.active_level.active_area
        self.surface = pygame.Surface(area.size)

        if self.camera:
            self.camera.update()

    def _mainloop(self):
        while 1:
            for event in pygame.event.get():
                if not self._handle_event(event):
                    return

            self.tick.emit()
            self._paint()
            self.clock.tick(self.FPS)

    def _handle_event(self, event):
        if event.type == QUIT:
            self.quit()
            return False

        if (self.ui_manager and not self.active_cutscene and
            self.ui_manager.handle_event(event)):
            return True

        if event.type == KEYDOWN and event.key == K_F2:
            self.show_debug_info = not self.show_debug_info
        elif event.type == KEYDOWN and event.key == K_F3:
            self.debug_rects = not self.debug_rects
        elif event.type == KEYDOWN and event.key == K_F4:
            self.god_mode = not self.god_mode
        elif self.active_cutscene:
            self.active_cutscene.handle_event(event)
        elif self.active_level:
            if event.type == KEYDOWN and event.key == K_TAB:
                # Switch time periods
                self._show_time_periods()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                if self.paused:
                    self._unpause()
                else:
                    self._pause()
            elif not self.paused:
                if event.type == KEYDOWN and event.key in (K_1, K_a):
                    self.active_level.switch_time_period(0)
                elif event.type == KEYDOWN and event.key in (K_2, K_s):
                    self.active_level.switch_time_period(1)
                elif event.type == KEYDOWN and event.key in (K_3, K_d):
                    self.active_level.switch_time_period(2)
                elif event.type == KEYDOWN and event.key == K_F5:
                    # XXX For debugging only.
                    i = self.levels.index(self.active_level)

                    if i + 1 == len(self.levels):
                        self.switch_level(0)
                    else:
                        self.switch_level(i + 1)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.ui_manager.confirm_quit()
                elif not self.player.handle_event(event):
                    area = self.active_level.active_area

                    for box in area.event_handlers:
                        if hasattr(box, 'rects'):
                            rects = box.rects
                        else:
                            rects = [box.rect]

                        if (self.player.rect.collidelist(rects) != -1 and
                            box.handle_event(event)):
                            break

        return True

    def _pause(self):
        self.paused = True
        self.ui_manager.pause()

    def _unpause(self):
        self.paused = False
        self.ui_manager.unpause()

    def _show_time_periods(self):
        self._pause()

    def _paint(self):
        if self.camera:
            self.camera.update()

        if self.active_cutscene:
            self.screen.set_clip(None)
            self.active_cutscene.draw(self.screen)

        if self.active_level:
            self.surface.set_clip(self.camera.rect)
            self.active_level.draw(self.surface)
            self.screen.blit(self.surface.subsurface(self.camera.rect), (0, 0))

        self.ui_manager.draw(self.screen)

        if self.show_debug_info:
            debug_str = '%0.f FPS     X: %s     Y: %s' % (
                self.clock.get_fps(),
                self.player.rect.left, self.player.rect.top)

            self.screen.blit(
                self.ui_manager.small_font.render(debug_str, True, (255, 0, 0)),
                (30, 10))

        pygame.display.flip()
