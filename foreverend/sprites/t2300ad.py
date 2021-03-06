from foreverend.effects import FloatEffect
from foreverend.sprites.base import Sprite
from foreverend.sprites.common import FloatingSprite
from foreverend.timer import Timer


class LightningPole(Sprite):
    def __init__(self):
        super(LightningPole, self).__init__('2300ad/lightning_pole')
        self.use_pixel_collisions = True


class TogglePlatform(Sprite):
    OPENING_TIME = 1000
    CLOSING_TIME = 1000

    def __init__(self):
        super(TogglePlatform, self).__init__('2300ad/platform_unpowered')
        self.platform_off_name = '2300ad/platform_off'
        self.platform_on_name = '2300ad/platform_on'
        self.platform_opening_name = '2300ad/platform_opening'
        self.platform_closing_name = '2300ad/platform_closing'
        self.collidable = False

    def power_on(self):
        self.name = self.platform_off_name
        self.update_image()

    def open(self):
        self.name = self.platform_opening_name
        self.update_image()

        timer = Timer(self.OPENING_TIME, self.on_open_timeout, one_shot=True)
        timer.start()

    def close(self):
        self.name = self.platform_closing_name
        self.update_image()

        timer = Timer(self.CLOSING_TIME, self.on_close_timeout, one_shot=True)
        timer.start()

    def on_open_timeout(self):
        self.collidable = True
        self.name = self.platform_on_name
        self.update_image()

    def on_close_timeout(self):
        self.collidable = False
        self.name = self.platform_off_name
        self.update_image()


class QuarantineSign(FloatingSprite):
    def __init__(self):
        super(QuarantineSign, self).__init__('2300ad/quarantine')
