import pygame

from foreverend.effects import FloatEffect
from foreverend.eventbox import EventBox
from foreverend.levels.base import Area, Level, TimePeriod
from foreverend.resources import load_image
from foreverend.sprites import Door, FloatingSprite, Sprite, TiledSprite
from foreverend.timer import Timer


class Monolith1NE(FloatingSprite):
    def __init__(self):
        super(Monolith1NE, self).__init__('1ne/monolith')
        self.collidable = False


class Monolith300NE(Sprite):
    def __init__(self):
        super(Monolith300NE, self).__init__('300ne/monolith')
        self.collidable = False


class FloatingPlatform1NE(FloatingSprite):
    def __init__(self, name='1ne/floating_platform'):
        super(FloatingPlatform1NE, self).__init__(name)


class Teleporter1NE(Door):
    def __init__(self, *args, **kwargs):
        super(Teleporter1NE, self).__init__(*args, **kwargs)
        self.float_effect = FloatEffect(self)

    def on_added(self, layer):
        super(Teleporter1NE, self).on_added(layer)
        self.float_effect.start()


class RedTeleporterNE(Teleporter1NE):
    def __init__(self):
        super(RedTeleporterNE, self).__init__('1ne/red_teleporter')


class BlueTeleporterNE(Teleporter1NE):
    def __init__(self):
        super(BlueTeleporterNE, self).__init__('1ne/blue_teleporter')


class Level3OutsideArea(Area):
    size = (4000, 800)

    def __init__(self, *args, **kwargs):
        super(Level3OutsideArea, self).__init__(*args, **kwargs)
        self.start_pos = (370, 623)


class Outside40000000AD(Level3OutsideArea):
    def setup(self):
        self.bg.fill((209, 186, 151))

        level_width, level_height = self.size

        lava_name = '65000000bc/lava_pool'
        tiles_x = level_width / load_image(lava_name).get_width()
        lava = TiledSprite('65000000bc/lava_pool', tiles_x, 1)
        lava.lethal = True
        self.main_layer.add(lava)
        lava.move_to(0, level_height - lava.rect.height)

        cliff = Sprite('40000000ad/cliff_left')
        cliff.use_pixel_collisions = True
        self.main_layer.add(cliff)
        cliff.move_to(0, level_height - cliff.rect.height)

        cliff = Sprite('40000000ad/cliff_middle')
        cliff.use_pixel_collisions = True
        self.main_layer.add(cliff)
        cliff.move_to(1720, level_height - cliff.rect.height)


class Outside1NE(Level3OutsideArea):
    def setup(self):
        self.bg.fill((50, 50, 50))

        level_width, level_height = self.size

        bottom_platforms_y = self.start_pos[1] + \
                             self.engine.player.rect.height + 3

        platform_x = 233

        monolith = Monolith1NE()
        self.main_layer.add(monolith)
        monolith.move_to(platform_x + 30,
                         bottom_platforms_y - monolith.rect.height)

        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(platform_x, bottom_platforms_y)

        red_teleporter_1 = RedTeleporterNE()
        self.main_layer.add(red_teleporter_1)
        red_teleporter_1.move_to(
            platform.rect.right - red_teleporter_1.rect.width - 30,
            platform.rect.top - red_teleporter_1.rect.height)

        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(934, bottom_platforms_y)

        cage = FloatingSprite('1ne/cage')
        cage.use_pixel_collisions = True
        self.main_layer.add(cage)
        cage.move_to(2000, 53)

        red_teleporter_2 = RedTeleporterNE()
        self.main_layer.add(red_teleporter_2)
        red_teleporter_2.move_to(cage.rect.left + 60, cage.rect.top + 57)

        red_teleporter_1.destination = red_teleporter_2
        red_teleporter_2.destination = red_teleporter_1

        # Middle platform
        platform = FloatingPlatform1NE('1ne/large_floating_platform')
        self.main_layer.add(platform)
        platform.move_to(2000, bottom_platforms_y)

        blue_teleporter_1 = BlueTeleporterNE()
        self.main_layer.add(blue_teleporter_1)
        blue_teleporter_1.move_to(
            platform.rect.left + 60,
            platform.rect.top - blue_teleporter_1.rect.height)

        monolith = Monolith1NE()
        self.main_layer.add(monolith)
        monolith.move_to(platform.rect.right - monolith.rect.width - 60,
                         platform.rect.top - monolith.rect.height)

        # Right platform
        platform = FloatingPlatform1NE('1ne/floating_platform')
        self.main_layer.add(platform)
        platform.move_to(level_width - platform.rect.width - 50,
                         bottom_platforms_y)

        blue_teleporter_2 = BlueTeleporterNE()
        self.main_layer.add(blue_teleporter_2)
        blue_teleporter_2.move_to(
            platform.rect.right - blue_teleporter_2.rect.width - 60,
            platform.rect.top - blue_teleporter_2.rect.height)

        blue_teleporter_1.destination = blue_teleporter_2
        blue_teleporter_2.destination = blue_teleporter_1


class Outside300NE(Level3OutsideArea):
    PLATFORM_POS = [
        (2, 83),
        (83, 180),
        (277, 238),
        (445, 163),
        (608, 186),
        (912, 272),
    ]

    def setup(self):
        self.bg.fill((200, 200, 200))

        level_width, level_height = self.size

        base_platforms_y = \
            self.start_pos[1] + self.engine.player.rect.height + 3

        # Left platforms
        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(233, base_platforms_y)
        bottom_ceiling_y = platform.rect.top - 150

        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(0, 255)

        # Ceiling
        top_ceiling = Sprite('300ne/ceiling')
        self.main_layer.add(top_ceiling)
        top_ceiling.move_to(platform.rect.right + 100, 50)

        # Reverse-gravity platforms
        for x, y in self.PLATFORM_POS:
            platform = FloatingSprite('300ne/small_platform')
            platform.reverse_gravity = True
            self.main_layer.add(platform)
            platform.move_to(top_ceiling.rect.left + x,
                             top_ceiling.rect.top + y)

        # Ceiling
        bottom_ceiling = Sprite('300ne/ceiling')
        self.main_layer.add(bottom_ceiling)
        bottom_ceiling.move_to(top_ceiling.rect.x, bottom_ceiling_y)

        # Reverse gravity area
        gravity_eventbox = EventBox(self)
        gravity_eventbox.rects.append(
            pygame.Rect(top_ceiling.rect.left,
                        top_ceiling.rect.bottom,
                        top_ceiling.rect.width,
                        bottom_ceiling.rect.top - top_ceiling.rect.bottom))
        gravity_eventbox.watch_object_moves(self.level.engine.player)
        gravity_eventbox.object_entered.connect(
            lambda obj: obj.set_reverse_gravity(True))
        gravity_eventbox.object_exited.connect(
            lambda obj: obj.set_reverse_gravity(False))

        # Right-side floor
        floor = Sprite('300ne/floor')
        self.main_layer.add(floor)
        floor.move_to(level_width - floor.rect.width,
                      level_height - floor.rect.height)

        monolith = Monolith300NE()
        self.main_layer.add(monolith)
        monolith.move_to(floor.rect.left + 200,
                         floor.rect.top - monolith.rect.height)

        # Container
        container_base = Sprite('300ne/container_base')
        self.main_layer.add(container_base)
        container_base.move_to(
            floor.rect.right - container_base.rect.width - 400,
            floor.rect.top - container_base.rect.height)

        container = Sprite('300ne/container')
        self.main_layer.add(container)
        container.move_to(
            container_base.rect.left +
            (container_base.rect.width - container.rect.width) / 2,
            container_base.rect.top - container.rect.height)

        self.level.add_artifact(self, container_base.rect.centerx,
                                container_base.rect.top)



class Level3(Level):
    def __init__(self, *args, **kwargs):
        super(Level3, self).__init__(*args, **kwargs)
        self.name = 'Level 3'
        self.setup()

    def setup(self):
        self.add(TimePeriod('40,000,000 AD', [Outside40000000AD(self)]))
        self.add(TimePeriod('1NE AD', [Outside1NE(self)]))
        self.add(TimePeriod('300NE AD', [Outside300NE(self)]))
