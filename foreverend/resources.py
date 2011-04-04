import os
import pygame


image_cache = {}


def get_cached_image(name, create_func):
    assert name

    if name not in image_cache:
        image_cache[name] = create_func().convert_alpha()

    return image_cache[name]


def load_image(name):
    def _load_image_file():
        filename = name + '.png'

        path = os.path.join(os.path.dirname(__file__), 'data',
                            *filename.split('/'))

        try:
            return pygame.image.load(path)
        except pygame.error, message:
            print 'Unable to load image %s' % path
            assert False

    return get_cached_image(name, _load_image_file)
