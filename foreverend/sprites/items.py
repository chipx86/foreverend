import pygame
from pygame.locals import *

from foreverend.signals import Signal
from foreverend.sprites.base import Direction, Sprite
from foreverend.timer import Timer


class Item(Sprite):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(obey_gravity=True, *args, **kwargs)
        self.should_check_collisions = True
        self.grabbable = True

        # Signals
        self.grab_changed = Signal()


class Artifact(Item):
    def __init__(self, time_period, num):
        super(Artifact, self).__init__('artifact%s' % num)
        self.float_timer = None
        self.time_period = None
        self.up_count = 0
        self.down_count = 0
        self.pause_count = 0
        self.float_paused = False
        self.max_movement = 6
        self.max_pause_count = 1
        self.float_distance = 1
        self.direction = Direction.UP

        self.grab_changed.connect(self.stop_floating)

        self.float_timer = Timer(time_period.engine, time_period, 100,
                                 self.on_float)
        self.float_timer.start()

    def stop_floating(self):
        self.float_timer.stop()
        self.float_timer = None

    def on_float(self):
        if self.float_paused:
            self.pause_count += 1

            if self.pause_count == self.max_pause_count:
                self.float_paused = False
                self.pause_count = 0
        elif self.direction == Direction.UP:
            self.move_by(0, -self.float_distance)
            self.up_count += 1

            if self.up_count == self.max_movement:
                self.direction = Direction.DOWN
                self.float_paused = True
                self.up_count = 0
        elif self.direction == Direction.DOWN:
            self.move_by(0, self.float_distance)
            self.down_count += 1

            if self.down_count == self.max_movement:
                self.direction = Direction.UP
                self.float_paused = True
                self.down_count = 0


class Dynamite(Item):
    def __init__(self):
        super(Dynamite, self).__init__('1999ad/dynamite')

    def light(self):
        self.name = '1999ad/dynamite_lit'
        self.update_image()
        self.grabbable = False
