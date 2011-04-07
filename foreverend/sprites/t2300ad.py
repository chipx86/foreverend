from foreverend.effects import FloatEffect
from foreverend.sprites.base import Sprite


class QuarantineSign(Sprite):
    def __init__(self):
        super(QuarantineSign, self).__init__('2300ad/quarantine')
        self.float_effect = FloatEffect(self)

    def on_added(self, layer):
        self.float_effect.start()
