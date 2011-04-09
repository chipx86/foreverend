#!/usr/bin/env python

import pygame
from pygame.locals import *

from foreverend.engine import ForeverEndEngine


def main():
    pygame.init()

    version = pygame.__version__.split('.')

    if int(version[0]) <= 1 and int(version[1]) < 9:
        print 'This game requires pygame 1.9 or higher.'
        return

    screen = pygame.display.set_mode((960, 720))
    pygame.display.set_caption("Forever End")

    engine = ForeverEndEngine(screen)
    engine.run()

    pygame.quit()
