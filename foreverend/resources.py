import os
import pygame


image_cache = {}

DATA_PY = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.normpath(os.path.join(DATA_PY, '..', 'data'))

# Try to find it in the exe.
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.normpath(os.path.join(DATA_PY, '..', '..', 'data'))


def get_cached_image(name, create_func):
    assert name

    if name not in image_cache:
        image_cache[name] = create_func().convert_alpha()

    return image_cache[name]


def load_image(name):
    def _load_image_file():
        if not name.endswith('.png') and not name.endswith('.jpg'):
            filename = name + '.png'
        else:
            filename = name

        path = os.path.join(DATA_DIR, *filename.split('/'))

        try:
            return pygame.image.load(path)
        except pygame.error, message:
            print 'Unable to load image %s' % path
            assert False

    return get_cached_image(name, _load_image_file)


def unload_image(name):
    print 'unloading %s' % name
    if name in image_cache:
        del image_cache[name]


def unload_images():
    image_cache.clear()


def get_font_filename():
    return os.path.join(DATA_DIR, 'DejaVuSans.ttf')


def get_music_filename(name):
    return os.path.join(DATA_DIR, 'sound', name)
