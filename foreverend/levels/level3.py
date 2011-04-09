import math

import pygame

from foreverend.effects import FloatEffect, MoveEffect, ScreenFadeEffect, \
                               ScreenFlashEffect, ShakeEffect, \
                               SlideHideEffect, SlideShowEffect
from foreverend.eventbox import EventBox
from foreverend.levels.base import Area, Level, TimePeriod
from foreverend.particles import ExplosionParticleSystem
from foreverend.resources import load_image
from foreverend.sprites import Box, Direction, Door, FloatingSprite, Sprite, \
                               TiledSprite, TriangleKey
from foreverend.timer import Timer


class Monolith1NE(FloatingSprite):
    def __init__(self):
        super(Monolith1NE, self).__init__('1ne/monolith')
        self.collidable = False


class Monolith300NE(Sprite):
    def __init__(self):
        super(Monolith300NE, self).__init__('300ne/monolith')
        self.collidable = False


class BlueBoxTeleporter(Door):
    def __init__(self):
        super(BlueBoxTeleporter, self).__init__('1ne/blue_teleporter')
        self.flip_image = True


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


class RedTeleporter1NE(Teleporter1NE):
    def __init__(self):
        super(RedTeleporter1NE, self).__init__('1ne/red_teleporter')


class BlueTeleporter1NE(Teleporter1NE):
    def __init__(self):
        super(BlueTeleporter1NE, self).__init__('1ne/blue_teleporter')


class Level3OutsideArea(Area):
    size = (4000, 800)

    def __init__(self, *args, **kwargs):
        super(Level3OutsideArea, self).__init__(*args, **kwargs)
        self.start_pos = (370, 623)


class Outside40000000AD(Level3OutsideArea):
    def __init__(self, *args, **kwargs):
        super(Outside40000000AD, self).__init__(*args, **kwargs)
        self.bluebox = Door('40000000ad/bluebox')

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

        self.main_layer.add(self.bluebox)
        self.bluebox.move_to(60, cliff.rect.top - self.bluebox.rect.height)
        self.bluebox.destination = self.time_period.areas['bluebox'].door

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

        red_teleporter_1 = RedTeleporter1NE()
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

        red_teleporter_2 = RedTeleporter1NE()
        self.main_layer.add(red_teleporter_2)
        red_teleporter_2.move_to(cage.rect.left + 60, cage.rect.top + 57)

        red_teleporter_1.destination = red_teleporter_2
        red_teleporter_2.destination = red_teleporter_1

        # Middle platform
        platform = FloatingPlatform1NE('1ne/large_floating_platform')
        self.main_layer.add(platform)
        platform.move_to(2000, bottom_platforms_y)

        blue_teleporter_1 = BlueTeleporter1NE()
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

        blue_teleporter_2 = BlueTeleporter1NE()
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
        self.in_end_sequence = False
        self.bg.fill((200, 200, 200))

        level_width, level_height = self.size

        base_platforms_y = \
            self.start_pos[1] + self.engine.player.rect.height + 3

        # Left platforms
        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(233, base_platforms_y)

        platform = FloatingPlatform1NE()
        self.main_layer.add(platform)
        platform.move_to(0, 255)

        # Ceiling
        ceiling = Sprite('300ne/ceiling')
        self.main_layer.add(ceiling)
        ceiling.move_to(platform.rect.right + 80, 0)

        # Spikes
        spikes = Sprite('300ne/ceiling_spikes')
        spikes.lethal = True
        self.main_layer.add(spikes)
        spikes.move_to(ceiling.rect.left, ceiling.rect.bottom)

        # Reverse-gravity platforms
        for x, y in self.PLATFORM_POS:
            platform = FloatingSprite('300ne/small_platform')
            platform.set_reverse_gravity(True)
            self.main_layer.add(platform)
            platform.move_to(ceiling.rect.left + x,
                             ceiling.rect.top + y)

        # Reverse gravity background
        reverse_grav_bg = Sprite('300ne/reverse_gravity_bg')
        self.bg_layer.add(reverse_grav_bg)
        reverse_grav_bg.move_to(ceiling.rect.left, ceiling.rect.bottom)

        # Reverse gravity area
        gravity_eventbox = EventBox(self)
        gravity_eventbox.rects.append(reverse_grav_bg.rect)
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

        step = FloatingSprite('300ne/step')
        self.main_layer.add(step)
        step.move_to(floor.rect.left + 20,
                     floor.rect.top - step.rect.height - 40)

        monolith = Monolith300NE()
        self.main_layer.add(monolith)
        monolith.move_to(floor.rect.left + 200,
                         floor.rect.top - monolith.rect.height)

        # Container
        self.container_base = Sprite('300ne/container_base')
        self.main_layer.add(self.container_base)
        self.container_base.move_to(
            floor.rect.right - self.container_base.rect.width - 400,
            floor.rect.top - self.container_base.rect.height)

        self.container_bg = Sprite('300ne/container_bg')
        self.bg_layer.add(self.container_bg)
        self.container_bg.move_to(
            self.container_base.rect.left +
            (self.container_base.rect.width - self.container_bg.rect.width) / 2,
            self.container_base.rect.top - self.container_bg.rect.height)

        self.level.add_artifact(self, self.container_base.rect.centerx,
                                self.container_base.rect.top)

        self.container = Sprite('300ne/container')
        self.main_layer.add(self.container)
        self.container.move_to(self.container_bg.rect.left,
                               self.container_bg.rect.top)

        self.keyhole = Sprite('300ne/keyhole')
        self.main_layer.add(self.keyhole)
        self.keyhole.move_to(
            self.container.rect.right - self.keyhole.rect.width - 10,
            self.container.rect.bottom - self.keyhole.rect.height - 10)

        keyhole_eventbox = EventBox(self)
        keyhole_eventbox.rects.append(
            pygame.Rect(self.container.rect.right,
                        self.keyhole.rect.top,
                        40,
                        self.keyhole.rect.height))
        keyhole_eventbox.watch_object_moves(self.level.triangle_key)
        keyhole_eventbox.object_entered.connect(self.start_end_sequence)


    def start_end_sequence(self, *args, **kwargs):
        if self.in_end_sequence:
            return

        self.in_end_sequence = True
        player = self.level.engine.player
        player.stop_tractor_beam()
        player.block_events = True
        player.velocity = (0, 0)
        player.fall()

        move_effect = MoveEffect(self.level.triangle_key)
        move_effect.total_time_ms = 1500
        move_effect.timer_ms = 30
        move_effect.destination = self.keyhole.rect.topleft
        move_effect.stopped.connect(self.on_key_inserted)
        move_effect.start()

    def on_key_inserted(self):
        self.level.triangle_key.remove()
        self.keyhole.remove()

        hide_effect = SlideHideEffect(self.container)
        hide_effect.direction = Direction.DOWN
        hide_effect.timer_ms = 30
        hide_effect.total_time_ms = 500
        hide_effect.stopped.connect(self.on_container_removed)
        hide_effect.start()

        hide_effect = SlideHideEffect(self.container_bg)
        hide_effect.direction = Direction.DOWN
        hide_effect.timer_ms = 30
        hide_effect.total_time_ms = 500
        hide_effect.start()

    def on_container_removed(self):
        self.container.collidable = False

        # Go collect the artifact!
        player = self.level.engine.player
        player.jump()

        timer = Timer(200, self.hop_onto_platform, one_shot=True)
        timer.start()

    def hop_onto_platform(self):
        player = self.level.engine.player
        player.velocity = (-player.MOVE_SPEED, player.velocity[1])
        timer = Timer(700, self.stop_moving, one_shot=True)
        timer.start()

    def stop_moving(self):
        timer = Timer(300, self.show_container, one_shot=True)
        timer.start()

    def show_container(self):
        player = self.level.engine.player
        player.velocity = (0, player.velocity[1])
        player.fall()

        show_effect = SlideShowEffect(self.container)
        show_effect.direction = Direction.UP
        show_effect.timer_ms = 30
        show_effect.total_time_ms = 500
        show_effect.stopped.connect(self.on_container_added)
        timer = Timer(700, show_effect.start, one_shot=True)
        timer.start()

    def on_container_added(self):
        player = self.level.engine.player
        self.questionmark = Sprite('questionmark')
        self.questionmark.collidable = False
        self.main_layer.add(self.questionmark)
        self.questionmark.move_to(
            player.rect.left +
            (player.rect.width - self.questionmark.rect.width) / 2,
            player.rect.top - self.questionmark.rect.height - 10)

        timer = Timer(300, self.hide_questionmark, one_shot=True)
        timer.start()

    def hide_questionmark(self):
        self.questionmark.remove()
        self.level.engine.player.direction = Direction.RIGHT

        timer = Timer(500, self.absorb_artifact, one_shot=True)
        timer.start()

    def absorb_artifact(self):
        player = self.level.engine.player
        player.direction = Direction.LEFT

        self.level.artifact.collidable = False

        move_effect = MoveEffect(self.level.artifact)
        move_effect.collidable = False
        move_effect.total_time_ms = 1500
        move_effect.timer_ms = 30
        move_effect.destination = player.rect.center
        move_effect.start()

        screen_flash_effect = ScreenFlashEffect(self.fg_layer,
                                                self.level.engine.camera.rect)
        screen_flash_effect.flash_peaked.connect(self.grow_probe)
        screen_flash_effect.stopped.connect(self.prepare_launch)
        screen_flash_effect.start()

    def grow_probe(self):
        bottom = self.container_bg.rect.bottom
        self.container_bg.name = '300ne/broken_container_bg'
        self.container_bg.update_image()
        self.container_bg.rect.bottom = bottom

        bottom = self.container.rect.bottom
        self.container.name = '300ne/broken_container'
        self.container.update_image()
        self.container.rect.bottom = bottom

        self.level.artifact.remove()
        self.level.engine.player.remove()

        self.large_probe = Sprite('probe_large')
        self.main_layer.add(self.large_probe)
        self.large_probe.collidable = False
        self.large_probe.obey_gravity = False
        self.large_probe.move_to(
            self.container.rect.left +
            (self.container.rect.width - self.large_probe.rect.width) / 2,
            self.container.rect.bottom - 2 * self.large_probe.rect.height)

        # We're going to force updates to get things in the right order.
        self.container.hide()
        self.container.show()
        self.container_base.hide()
        self.container_base.show()

    def prepare_launch(self):
        player = self.level.engine.player
        self.explosion = ExplosionParticleSystem(self)
        self.explosion.max_lifetime = 1
        self.explosion.min_lifetime = 0.5
        self.explosion.min_particles = 30
        self.explosion.max_particles = 40
        self.explosion.max_scale = 0.4
        self.explosion.min_angle = -(4 * math.pi) / 3
        self.explosion.max_angle = -(5 * math.pi) / 3
        self.explosion.repeat = True
        self.explosion.start(self.container.rect.centerx,
                             self.large_probe.rect.bottom)

        shake_effect = ShakeEffect(self.large_probe)
        shake_effect.start()

        timer = Timer(3000, self.launch_probe, one_shot=True)
        timer.start()

    def launch_probe(self):
        self.large_probe.velocity = (0, -15)
        self.large_probe.moved.connect(self.move_explosion)

        timer = Timer(4000, self.probe_launched, one_shot=True)
        timer.start()

    def move_explosion(self, dx, dy):
        self.explosion.pos = (self.container.rect.centerx,
                              self.large_probe.rect.bottom)

    def probe_launched(self):
        self.explosion.stop()
        screen_flash_effect = ScreenFadeEffect(self.fg_layer,
                                               self.level.engine.camera.rect)
        screen_flash_effect.fade_time_ms = 3000
        screen_flash_effect.stopped.connect(
            self.level.engine.show_end_scene)
        screen_flash_effect.start()


class BlueBoxArea(Area):
    size = (1024, 768)
    def __init__(self, *args, **kwargs):
        super(BlueBoxArea, self).__init__(*args, **kwargs)
        self.key = 'bluebox'
        self.door = Door('40000000ad/bluebox_door')

    def setup(self):
        self.bg.fill((193, 198, 251))

        area_width, area_height = self.size

        ground = Box(area_width, 60, (83, 107, 143))
        self.main_layer.add(ground)
        ground.move_to(0, area_height - ground.rect.height)

        ceiling = Box(area_width, 60, (83, 107, 143))
        self.main_layer.add(ceiling)
        ceiling.move_to(0, 0)

        wall_height = area_height - ground.rect.height - ceiling.rect.height + 2
        wall_y = ceiling.rect.bottom - 1

        left_wall = Box(60, wall_height, (83, 107, 143))
        self.main_layer.add(left_wall)
        left_wall.move_to(0, wall_y)

        right_wall = Box(60, wall_height, (83, 107, 143))
        self.main_layer.add(right_wall)
        right_wall.move_to(area_width - right_wall.rect.width, wall_y)

        self.main_layer.add(self.door)
        self.door.move_to(left_wall.rect.right + 100,
                          ground.rect.top - self.door.rect.height)
        self.door.destination = self.time_period.areas['default'].bluebox

        # Reverse gravity background
        reverse_grav_bg = Sprite('300ne/bluebox_reverse_gravity_bg')
        self.bg_layer.add(reverse_grav_bg)
        reverse_grav_bg.move_to(left_wall.rect.right, ceiling.rect.bottom)

        # Reverse gravity area
        gravity_eventbox = EventBox(self)
        gravity_eventbox.rects.append(reverse_grav_bg.rect)
        gravity_eventbox.watch_object_moves(self.level.engine.player)
        gravity_eventbox.object_entered.connect(
            lambda obj: obj.set_reverse_gravity(True))
        gravity_eventbox.object_exited.connect(
            lambda obj: obj.set_reverse_gravity(False))

        teleporter1 = BlueBoxTeleporter()
        self.main_layer.add(teleporter1)
        teleporter1.move_to(right_wall.rect.left - teleporter1.rect.width - 20,
                            ground.rect.top - teleporter1.rect.height)

        teleporter2 = BlueBoxTeleporter()
        teleporter2.reverse_gravity = True
        self.main_layer.add(teleporter2)
        teleporter2.move_to(left_wall.rect.right + 20, ceiling.rect.bottom)

        teleporter1.destination = teleporter2
        teleporter2.destination = teleporter1

        self.main_layer.add(self.level.triangle_key)
        self.level.triangle_key.move_to(
            right_wall.rect.left - self.level.triangle_key.rect.width - 40,
            ceiling.rect.bottom)
        self.level.triangle_key.set_reverse_gravity(True)


class Level3(Level):
    def __init__(self, *args, **kwargs):
        super(Level3, self).__init__(*args, **kwargs)
        self.name = 'Level 3'
        self.setup()

    def setup(self):
        self.triangle_key = TriangleKey()

        self.add(TimePeriod('40,000,000 AD', [
            Outside40000000AD(self),
            BlueBoxArea(self),
        ]))
        self.add(TimePeriod('1 NE', [Outside1NE(self)]))
        self.add(TimePeriod('300 NE', [Outside300NE(self)]))
