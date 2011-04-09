import pygame
from pygame.locals import *

from foreverend import get_engine
from foreverend.resources import load_image
from foreverend.signals import Signal
from foreverend.timer import Timer


class Page(object):
    def __init__(self):
        self.done = Signal()

    def start(self):
        pass

    def stop(self):
        pass

    def draw(self, surface):
        pass


class DelayPage(Page):
    def __init__(self, delay_ms):
        super(DelayPage, self).__init__()
        self.delay_ms = delay_ms
        self.timer = None

    def start(self):
        self.timer = Timer(self.delay_ms, self.stop, one_shot=True)

    def stop(self):
        self.timer.stop()
        self.done.emit()


class TextPage(DelayPage):
    def __init__(self, delay_ms, text):
        super(TextPage, self).__init__(delay_ms)
        self.text = text
        self.widget = None

    def start(self):
        ui_manager = get_engine().ui_manager
        self.widget = ui_manager.show_textbox([
            ({'font': ui_manager.small_font}, line)
            for line in self.text.split('\n')
        ])

        super(TextPage, self).start()

    def stop(self):
        self.widget.close()
        super(TextPage, self).stop()


class Cutscene(object):
    def __init__(self):
        self.pages = []
        self.next_page = 0
        self.current_page = None

        # Signals
        self.done = Signal()

    def start(self):
        self.next_page = 0
        self.show_next_page()

    def stop(self):
        self.next_page = -1
        self.current_page.stop()
        self.current_page = None
        self.done.emit()

    def show_next_page(self):
        if self.next_page == len(self.pages):
            self.done.emit()
        elif self.next_page >= 0:
            self.current_page = self.pages[self.next_page]
            self.next_page += 1
            self.current_page.done.connect(self.show_next_page)
            self.current_page.start()

    def draw(self, surface):
        if self.current_page:
            self.current_page.draw(surface)

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.stop()
            elif event.key in (K_SPACE, K_RETURN, K_RIGHT):
                self.current_page.stop()


class OpeningCutscene(Cutscene):
    def __init__(self):
        super(OpeningCutscene, self).__init__()

        self.pages = [
            TextPage(4000,
                     'The Mayans predicted that 2012 would mark a '
                     'new era, forever changing us all.'),
            TextPage(4000,
                     'History is filled with such predictions. '
                     'Most are dismissed as nonsense.'),
            TextPage(4000,
                     'If only we paid attention...'),
            TextPage(5000,
                     'In December 2012, an object crashed down to Earth in a '
                     'brilliant flash of light.'),
            TextPage(5000,
                     'It came out of nowhere, so it seemed, but we did '
                     'have warning.\nAfterall, history has recorded this very '
                     'crash, time and time again...'),
            TextPage(5000,
                     'We know very little about what it is that hit the '
                     'Earth,\n'
                     'but we do know it shattered time, blending '
                     'pieces of history together.'),
            TextPage(3000,
                     'Scientists refer to the crash as the Omega 13 event.'),
            TextPage(4000,
                     'The object is now believed to exist in fragments, '
                     'scattered throughout history.'),
            TextPage(4000,
                     'No human can safely reach them, or repair the holes '
                     'in time.'),
            TextPage(4000,
                     'But a probe...'),
        ]


class ClosingCutscene(Cutscene):
    def __init__(self):
        super(ClosingCutscene, self).__init__()
        self.earth = load_image('earth.jpg')
        self.probe = load_image('crashing_probe')
        self.fade_effect = None

        self.pages = [
            DelayPage(3000),
            TextPage(3000, 'Irony.'),
            TextPage(5000, 'We sought to prevent the greatest tragedy in '
                           'history, and believed we were capable.'),
            TextPage(5000, 'Yet, with all our arrogance and '
                           'short-sightedness, our very creation was the '
                           'cause of our downfall.'),
            TextPage(5000, 'We thought we could fix the planet. Fix time.'),
            TextPage(5000, 'And now we are all sons of bitches.'),
        ]


    def draw(self, surface):
        if not self.fade_effect:
            from foreverend.effects import ScreenFadeEffect
            self.fade_effect = ScreenFadeEffect(
                None,
                pygame.Rect(0, 0, surface.get_width(), surface.get_height()))
            self.fade_effect.fade_from_alpha = 255
            self.fade_effect.fade_to_alpha = 0
            self.fade_effect.fade_time_ms = 3000
            self.fade_effect.start()
            print 'start'

        surface.fill((0, 0, 0))
        surface.blit(self.earth,
                     (surface.get_width() - self.earth.get_width(), 0))
        surface.blit(self.probe, (150, 60))
        surface.blit(self.fade_effect.sprite.image, (0, 0))
