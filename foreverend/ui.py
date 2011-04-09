import pygame

from foreverend.resources import get_font_filename, load_image
from foreverend.signals import Signal
from foreverend.sprites.player import Player
from foreverend.timer import Timer


class Widget(object):
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.ui_manager.widgets.append(self)
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.closed = Signal()

    def move_to(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def resize(self, w, h):
        self.rect.width = w
        self.rect.height = h

    def close(self):
        self.ui_manager.close(self)

    def draw(self, surface):
        raise NotImplemented


class TextBox(Widget):
    BG_COLOR = (0, 0, 0, 190)
    BORDER_COLOR = (255, 255, 255, 120)
    BORDER_WIDTH = 1

    def __init__(self, ui_manager, text, line_spacing=10):
        super(TextBox, self).__init__(ui_manager)
        self.text = text
        self.surface = None
        self.line_spacing = line_spacing

    def _render_text(self):
        if isinstance(self.text, list):
            lines = self.text
        else:
            lines = [self.text]

        surfaces = []
        total_height = 0

        for line in lines:
            if isinstance(line, list):
                columns = line
            else:
                columns = [line]

            column_surfaces = []
            line_height = 0

            for column in columns:
                attrs = None

                if not isinstance(column, tuple):
                    column = {}, column

                attrs, text = column
                font = attrs.get('font', self.ui_manager.font)

                text_surface = font.render(text, True, (255, 255, 255))
                column_surfaces.append((attrs, text_surface))
                column_height = text_surface.get_height()

                if 'padding_top' in attrs:
                    column_height += attrs['padding_top']

                column_height += self.line_spacing

                line_height = max(line_height, column_height)

            if column_surfaces:
                surfaces.append((line_height, column_surfaces))
                total_height += line_height

        # Get rid of that last spacing.
        total_height -= self.line_spacing

        y = (self.rect.height - total_height) / 2

        for line_height, column_surfaces in surfaces:
            column_width = self.rect.width / len(column_surfaces)
            x = 0

            for attrs, column_surface in column_surfaces:
                self.surface.blit(
                    column_surface,
                    (x + (column_width - column_surface.get_width()) / 2,
                     y + attrs.get('padding_top', 0)))
                x += column_width

            y += line_height

    def draw(self, surface):
        if not self.surface:
            self.surface = pygame.Surface(self.rect.size).convert_alpha()
            self.surface.fill(self.BG_COLOR)
            pygame.draw.rect(self.surface, self.BORDER_COLOR,
                             (0, 0, self.rect.width, self.rect.height),
                             self.BORDER_WIDTH)
            self._render_text()

        surface.blit(self.surface, self.rect.topleft)


class ControlPanel(Widget):
    SIDE_SPACING = 10
    IMAGE_SPACING = 5

    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self._level = None
        self.resize(self.ui_manager.size[0], 40)
        self.surface = pygame.Surface(self.rect.size)
        self.heart_image = load_image('heart')
        self.heart_lost_image = load_image('heart_lost')
        self.life_image = load_image('life')
        self.life_lost_image = load_image('life_lost')

        player = self.ui_manager.engine.player
        player.lives_changed.connect(self.render)
        player.health_changed.connect(self.render)

        self.area_changed_cnx = None

    def _set_level(self, level):
        if self.area_changed_cnx:
            self.area_changed_cnx.disconnect()

        self._level = level
        self.render()

        if self._level:
            self.area_changed_cnx = \
                level.area_changed.connect(self.render)

    level = property(lambda self: self._level, _set_level)

    def render(self):
        self.surface.fill((0, 0, 0))

        text_surface = self.ui_manager.font.render(
            self.level.active_time_period.name, True, (255, 255, 255))
        self.surface.blit(text_surface,
                          ((self.rect.width - text_surface.get_width()) / 2,
                           (self.rect.height - text_surface.get_height()) / 2))

        x = self.SIDE_SPACING
        y = (self.rect.height - self.heart_image.get_height()) / 2
        heart_width = self.heart_image.get_width()

        player = self.ui_manager.engine.player

        for i in range(Player.MAX_HEALTH):
            if player.health > i:
                self.surface.blit(self.heart_image, (x, y))
            else:
                self.surface.blit(self.heart_lost_image, (x, y))

            x += heart_width + self.IMAGE_SPACING

        life_width = self.life_image.get_width()
        x = self.rect.width - self.SIDE_SPACING - \
            (Player.MAX_LIVES * (life_width + self.IMAGE_SPACING)) + \
            self.IMAGE_SPACING
        y = (self.rect.height - self.life_image.get_height()) / 2

        for i in range(Player.MAX_LIVES):
            if player.lives > i:
                self.surface.blit(self.life_image, (x, y))
            else:
                self.surface.blit(self.life_lost_image, (x, y))

            x += life_width + self.IMAGE_SPACING

    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)


class UIManager(object):
    SCREEN_PADDING = 100
    TEXTBOX_HEIGHT = 100
    CONTROL_PANEL_HEIGHT = 40

    def __init__(self, engine):
        pygame.font.init()

        self.ready = Signal()

        self.engine = engine
        self.size = engine.screen.get_size()
        self.surface = pygame.Surface(self.size).convert_alpha()
        self.widgets = []
        self.timers = []

        self.default_font = get_font_filename()
        #self.default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(self.default_font, 20)
        self.small_font = pygame.font.Font(self.default_font, 16)

        self.control_panel = ControlPanel(self)
        self.control_panel.move_to(
            0, self.size[1] - self.control_panel.rect.height)

        self.engine.level_changed.connect(self.on_level_changed)

    def show_level(self, level):
        timeline_attrs = {
            'font': self.small_font,
            'padding_top': 20,
        }

        widget = self.show_textbox([
            ({'padding_top': 10}, level.name),
            [(timeline_attrs, time_period.name)
             for time_period in level.time_periods]
        ], line_spacing=0)

        timer = Timer(2000, lambda: self.close(widget), one_shot=True)
        timer.start()

        return widget

    def show_textbox(self, text, **kwargs):
        textbox = TextBox(self, text, **kwargs)
        textbox.resize(self.size[0] - 2 * self.SCREEN_PADDING,
                       self.TEXTBOX_HEIGHT)
        textbox.move_to(self.SCREEN_PADDING,
                        self.size[1] - textbox.rect.height -
                        self.SCREEN_PADDING)
        return textbox

    def close(self, widget):
        try:
            self.widgets.remove(widget)
        except ValueError:
            # It was already closed
            pass

    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))
        for element in self.widgets:
            element.draw(self.surface)

        surface.blit(self.surface, (0, 0))

    def on_level_changed(self):
        level = self.engine.active_level
        self.show_level(level)
        self.control_panel.level = level
