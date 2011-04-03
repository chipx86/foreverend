#!/usr/bin/env python

import pygame
from pygame.locals import *

from foreverend.engine import ForeverEndEngine


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Forever End")

    engine = ForeverEndEngine(screen)
    engine.run()

    pygame.quit()
