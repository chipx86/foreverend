import pygame

from foreverend.eventbox import EventBox
from foreverend.levels.base import Level, TimePeriod
from foreverend.particles import ExplosionParticleSystem
from foreverend.sprites import Box, Dynamite, Elevator, \
                               Mountain, Sprite, TiledSprite, Volcano
from foreverend.timer import Timer


class TimePeriod600AD(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod600AD, self).__init__(*args, **kwargs)
        self.name = '600 AD'
        self.bg.fill((237, 243, 255))

        tiles_x = self.level.size[0] / 32
        ground = TiledSprite('ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, self.level.size[1] - ground.rect.height)

        hills = Sprite('600ad/hills_1')
        self.bg_layer.add(hills)
        hills.move_to(0, ground.rect.top - hills.rect.height)

        mountain = Mountain()
        mountain.add_to(self)
        mountain.move_to(1300, ground.rect.top - mountain.rect.height)

        # Mountain platforms
        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1740,
                         mountain.rect.bottom - platform.rect.height - 10)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 100)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 180)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 260)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 340)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(1990,
                         mountain.rect.bottom - platform.rect.height - 420)

        platform = Sprite('600ad/platform')
        self.main_layer.add(platform)
        platform.move_to(2240,
                         mountain.rect.bottom - platform.rect.height - 500)


class TimePeriod1999AD(TimePeriod):
    BUILDING_RECT = pygame.Rect(0, 0, 1300, 700)
    WALL_WIDTH = 15
    GROUND_HEIGHT = 32
    WALL_COLOR = (211, 215, 207)
    FLOOR_COLOR = (211, 215, 207)

    def __init__(self, *args, **kwargs):
        super(TimePeriod1999AD, self).__init__(*args, **kwargs)
        self.name = '1999 AD'
        self.bg.fill((199, 214, 251))

        level_width, level_height = self.level.size

        # Ground
        tiles_x = self.level.size[0] / 32
        ground = TiledSprite('ground', tiles_x, 1)
        self.main_layer.add(ground)
        ground.move_to(0, self.level.size[1] - ground.rect.height)

        building_rect = self.BUILDING_RECT.move(
            0, ground.rect.top - self.BUILDING_RECT.height)

        # Building background
        building_bg = Box(*building_rect.size)
        self.bg_layer.add(building_bg)
        building_bg.move_to(*building_rect.topleft)

        # First floor
        floor1 = Box(building_rect.width, self.GROUND_HEIGHT, self.FLOOR_COLOR)
        self.main_layer.add(floor1)
        floor1.move_to(building_rect.left, ground.rect.top)

        # Second floor
        floor2 = Box(building_rect.width, self.GROUND_HEIGHT, self.FLOOR_COLOR)
        self.main_layer.add(floor2)
        floor2.move_to(building_rect.left,
                       building_rect.top +
                       (building_rect.height - floor2.rect.height) / 2)

        # Left wall of building
        box = Box(self.WALL_WIDTH, building_rect.height, self.WALL_COLOR)
        self.main_layer.add(box)
        box.move_to(building_rect.left, building_rect.top)

        # Right wall of the building
        right_wall = Box(self.WALL_WIDTH, building_rect.height, self.WALL_COLOR)
        self.main_layer.add(right_wall)
        right_wall.move_to(building_rect.right - self.WALL_WIDTH,
                           building_rect.top)

        # Ceiling
        box = Box(building_rect.width, self.GROUND_HEIGHT)
        self.main_layer.add(box)
        box.move_to(building_rect.left, building_rect.top)

        # Top elevator
        elevator1 = Elevator()
        self.main_layer.add(elevator1)
        elevator1.move_to(building_rect.left + 100,
                          building_rect.top - elevator1.rect.height)

        # Bottom elevator
        elevator2 = Elevator()
        self.main_layer.add(elevator2)
        elevator2.move_to(elevator1.rect.left,
                          floor2.rect.top - elevator2.rect.height)

        # Link up the elevators
        elevator1.destination = elevator2
        elevator2.destination = elevator1

        # Dynamite
        self.main_layer.add(self.level.dynamite)
        self.level.dynamite.move_to(
            right_wall.rect.left - self.level.dynamite.rect.width - 20,
            floor2.rect.top - self.level.dynamite.rect.height)
        #self.level.dynamite.move_to(
        #    200, ground.rect.top - self.level.dynamite.rect.height)

        # Mountain
        mountain = Mountain()
        mountain.add_to(self)
        mountain.move_to(1300, ground.rect.top - mountain.rect.height)

        platform = Sprite('1999ad/lavamatics_platform')
        self.main_layer.add(platform)
        platform.move_to(1841,
                         mountain.rect.bottom - platform.rect.height - 500)

        platform = Sprite('1999ad/l_tube')
        self.main_layer.add(platform)
        platform.move_to(2140,
                         mountain.rect.bottom - platform.rect.height - 450)


class TimePeriod65000000BC(TimePeriod):
    def __init__(self, *args, **kwargs):
        super(TimePeriod65000000BC, self).__init__(*args, **kwargs)
        self.name = '65,000,000 BC'
        self.exploding = False
        self.exploded = False

        ground = TiledSprite('ground', self.level.size[0] / 32, 1)
        self.main_layer.add(ground)
        ground.move_to(0, self.level.size[1] - ground.rect.height)

        hills = Sprite('65000000bc/hills_1')
        self.bg_layer.add(hills)
        hills.move_to(0, ground.rect.top - hills.rect.height)

        # Volcano
        self.volcano = Volcano()
        self.volcano.add_to(self)
        self.volcano.move_to(1400, ground.rect.top - self.volcano.rect.height)

        blocker = Box(150, self.level.size[1] - self.volcano.rect.height - 20,
                      (0, 0, 0, 0))
        self.main_layer.add(blocker)
        blocker.move_to(self.volcano.lava_pool.rect.right - 100, 0)

        # Left-side lava pool
        lava_pool = TiledSprite('65000000bc/lava_pool', 5, 1)
        lava_pool.lethal = True
        self.main_layer.add(lava_pool)
        lava_pool.move_to(self.volcano.rect.left - lava_pool.rect.width - 100,
                          ground.rect.top - 18)

        # Platforms
        platform = Sprite('65000000bc/platform')
        self.main_layer.add(platform)
        platform.move_to(lava_pool.rect.left + 250, lava_pool.rect.top - 10)

        platform = Sprite('65000000bc/platform')
        self.main_layer.add(platform)
        platform.move_to(lava_pool.rect.left + 500, lava_pool.rect.top - 8)

        platform = Sprite('65000000bc/platform')
        self.main_layer.add(platform)
        platform.move_to(lava_pool.rect.left + 750, lava_pool.rect.top - 12)

        # Right-side lava pool
        lava_pool = TiledSprite('65000000bc/lava_pool', 3, 1)
        lava_pool.lethal = True
        self.main_layer.add(lava_pool)
        lava_pool.move_to(self.volcano.rect.right + 200,
                          ground.rect.top - 18)

        # Dynamite explosion trigger
        explosion_box = EventBox(self)
        explosion_box.rects.append(
            pygame.Rect(self.volcano.lava_puddle.rect.x,
                        self.volcano.lava_puddle.rect.bottom - 5,
                        self.volcano.lava_puddle.rect.width,
                        5))
        explosion_box.watch_object_moves(self.level.dynamite)
        explosion_box.object_entered.connect(self.on_dynamite_placed)

        # Artifact
        self.level.add_artifact(self, lava_pool.rect.right + 200,
                                ground.rect.top)

    def on_dynamite_placed(self, obj):
        assert obj == self.level.dynamite

        if self.exploding or self.exploded:
            return

        self.level.dynamite.light()
        self.exploding = True

        self.detonate_timer = Timer(1000, self.start_explosion)

    def start_explosion(self):
        self.detonate_timer.stop()
        self.detonate_timer = None

        self.level.dynamite.remove()
        self.level.dynamite = None

        self.explosion = ExplosionParticleSystem(self)
        self.explosion.start(2040, 1500)

        self.explosion_timer = Timer(350, self.on_explosion_done)
        self.explosion_timer.start()

    def on_explosion_done(self):
        self.explosion_timer.stop()
        self.explosion_timer = None
        self.exploding = False
        self.exploded = True
        self.volcano.clear_passage()


class Level1(Level):
    def __init__(self, *args, **kwargs):
        super(Level1, self).__init__(*args, **kwargs)
        self.name = 'Level 1'
        self.size = (4200, 1600)
        self.start_pos = (10,
                          self.size[1] - 32 - self.engine.player.rect.height)
        self.setup()

    def setup(self):
        # Items that we'll make use of.
        self.dynamite = Dynamite()

        self.add(TimePeriod600AD(self))
        self.add(TimePeriod1999AD(self))
        self.add(TimePeriod65000000BC(self))
