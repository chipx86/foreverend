import pygame

from foreverend.timer import Timer


class Widget(object):
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.ui_manager.widgets.append(self)
        self.rect = pygame.Rect(0, 0, 0, 0)

    def move_to(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def resize(self, w, h):
        self.rect.width = w
        self.rect.height = h

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

                line_height = max(line_height, column_height)

            surfaces.append((line_height, column_surfaces))
            total_height += line_height + self.line_spacing

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
    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self._level = None
        self._health = 0
        self._lives = 0
        self.resize(self.ui_manager.size[0], 40)
        self.surface = pygame.Surface(self.rect.size)

        self.time_period_changed_cnx = None

    def _set_level(self, level):
        if self.time_period_changed_cnx:
            self.time_period_changed_cnx.disconnect()

        self._level = level
        self.render()

        if self._level:
            self.time_period_changed_cnx = \
                level.time_period_changed.connect(self.render)

    level = property(lambda self: self._level, _set_level)

    def _set_health(self, health):
        self._health = health
        self.render()
    health = property(lambda self: self._health, _set_health)

    def _set_lives(self, lives):
        self._lives = lives
        self.render()
    lives = property(lambda self: self._lives, _set_lives)

    def render(self):
        self.surface.fill((0, 0, 0))

        text_surface = self.ui_manager.font.render(
            self.level.active_time_period.name, True, (255, 255, 255))
        self.surface.blit(text_surface,
                          ((self.rect.width - text_surface.get_width()) / 2,
                           (self.rect.height - text_surface.get_height()) / 2))


    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)


class UIManager(object):
    SCREEN_PADDING = 100
    TEXTBOX_HEIGHT = 100
    CONTROL_PANEL_HEIGHT = 40

    def __init__(self, engine):
        pygame.font.init()

        self.engine = engine
        self.size = engine.screen.get_size()
        self.surface = pygame.Surface(self.size).convert_alpha()
        self.widgets = []
        self.timers = []

        self.default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(self.default_font, 20)
        self.small_font = pygame.font.Font(self.default_font, 14)

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

        timer = Timer(self.engine, self, 2000, lambda: self.close(widget),
                      one_shot=True)
        timer.start()

    def show_textbox(self, text, **kwargs):
        textbox = TextBox(self, text, **kwargs)
        textbox.resize(self.size[0] - 2 * self.SCREEN_PADDING,
                       self.TEXTBOX_HEIGHT)
        textbox.move_to(self.SCREEN_PADDING,
                        self.size[1] - textbox.rect.height -
                        self.SCREEN_PADDING)
        return textbox

    def close(self, widget):
        self.widgets.remove(widget)

    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))
        for element in self.widgets:
            element.draw(self.surface)

        surface.blit(self.surface, (0, 0))

    def tick(self):
        for timer in self.timers:
            timer.tick()

    def on_level_changed(self):
        level = self.engine.active_level
        self.show_level(level)
        self.control_panel.level = level
