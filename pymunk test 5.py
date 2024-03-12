import random, math

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d



pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True

### Physics stuff
space = pymunk.Space()
space.gravity = Vec2d(0.0, 0.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)


### Object creation
class CollFilter:
    cur_index = "0b1"
    all_filters = {}
    
    def __init__(self, name):
        self.name = name
        if name in CollFilter.all_filters.keys():
            raise Exception(f"{name} is already a filter.")
        CollFilter.all_filters[name] = self
        self.filter = pymunk.ShapeFilter(categories=eval(CollFilter.cur_index))
        CollFilter.cur_index += "0"

    @classmethod
    def get(cls, name):
        return cls.all_filters[name]


class Obj:
    mass = 10
    all_objs = []

    @staticmethod
    def find_by_shape(shape):
        for obj in Obj.all_objs:
            if obj.shape == shape:
                return obj
    
    def __init__(self, x, y, radius=100, color=(210, 200, 200)):
        Obj.all_objs.append(self)
        inertia = pymunk.moment_for_circle(Obj.mass, 0, radius, (0, 0))
        self.body = pymunk.Body(Obj.mass, inertia)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius, Vec2d(0, 0))
        self.shape.color = pygame.Color(color)
        space.add(self.body, self.shape)

    def add_mask(self, mask):
        self.shape.filter = pymunk.ShapeFilter(categories=self.shape.filter.categories, mask=mask)

    def calc_imp_components_from_point(self, point):
        pos = self.body.position
        impulse = pos.get_dist_sqrd(point) * 0.1
        angle = math.atan2(point[1] - pos.y, point[0] - pos.x)
        return impulse * math.cos(angle), impulse * math.sin(angle)


class Timmy(Obj):
    def __init__(self, x, y):
        super().__init__(x, y, 90, (200, 110, 100))
        self.shape.filter = CollFilter("timmy").filter

    def __str__(self):
        return "Timmy"


class Johnny(Obj):
    def __init__(self, x, y):
        super().__init__(x, y, 90, (100, 200, 110))
        self.shape.filter = CollFilter("johnny").filter

    def __str__(self):
        return "Johnny"


class Carlos(Obj):
    def __init__(self, x, y):
        super().__init__(x, y, 90, (110, 100, 200))
        self.shape.filter = CollFilter("carlos").filter

    def __str__(self):
        return "Carlos"


class CollFilterMask:
    def __new__(cls, whitelist, *params):
        obj = object.__new__(cls)
        if whitelist:
            obj.__whitelist_init(params)
        else:
            obj.__blacklist_init(params)
        return obj
    
    def __whitelist_init(self, filter_objs):
        self.mask = 0
        for obj in filter_objs:
            self.mask += obj.shape.filter.categories

    def __blacklist_init(self, filter_objs):
        self.mask = pymunk.ShapeFilter.ALL_MASKS()
        for obj in filter_objs:
            self.mask -= obj.shape.filter.categories



timmy = Timmy(200, 550) #red
johnny = Johnny(600, 550) #green
carlos = Carlos(400, 550 - 347) #blue
test1 = CollFilterMask(True, timmy, johnny)
test2 = CollFilterMask(True, carlos)
timmy.add_mask(test2.mask)
johnny.add_mask(test2.mask)
carlos.add_mask(test1.mask)


aim_size = 50

### Mainloop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

    ### Clear screen
    screen.fill((30, 30, 40))

    ### Draw stuff
    space.debug_draw(draw_options)

    pg_mouse_pos = pygame.mouse.get_pos()
    pm_mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)

    aim_rect = pygame.Rect(pg_mouse_pos[0] - aim_size // 2, pg_mouse_pos[1] - aim_size // 2, aim_size, aim_size)
    shapes = space.bb_query(pymunk.BB(pm_mouse_pos[0] - aim_size // 2, pm_mouse_pos[1] - aim_size // 2, pm_mouse_pos[0] + aim_size // 2, pm_mouse_pos[1] + aim_size // 2),
                            pymunk.ShapeFilter())
    for shape in shapes:
        p = pymunk.pygame_util.to_pygame(shape.body.position, screen)
        r = shape.radius + 4
        pygame.draw.circle(screen, pygame.Color("white"), p, int(r), 2)

    pygame.draw.rect(screen, pygame.Color("white"), aim_rect, 2)

    ### Update physics
    dt = 1.0 / 60.0
    for x in range(1):
        space.step(dt)

    ### Flip screen
    pygame.display.update()
    clock.tick(50)
    pygame.display.set_caption("fps: " + str(clock.get_fps()))

pygame.quit()


