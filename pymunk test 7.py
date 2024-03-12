import math, random

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d



pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
test = None


### Physics stuff
space = pymunk.Space()
space.gravity = Vec2d(0.0, 10000.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)

collhandler = space.add_collision_handler(0, 0)
collhandler.data["surface"] = screen



### Object definition
class Graph:
    def __init__(self, rect, col, point_distance=1):
        self.values = []
        self.points = []
        self.col = col
        self.rect = rect
        self.surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA, 32)
        self.surf.convert_alpha()
        self.point_distance = point_distance


    def add(self, val):
        self.values = [val] + self.values


    def update(self):
        if self.values:
            self.points = []
            max_val = max(self.values)
            if max_val > 0:
                for i, val in enumerate(self.values):
                    py = self.rect.h - (self.rect.h * val / max_val)
                    px = self.rect.w - (i * self.point_distance)
                    self.points.append((px, py))


    def draw(self):
        self.surf.fill(pygame.Color(0,0,0,0))
        #print()
        for p0, p1 in zip(self.points[:-1], self.points[1:]):
            #print(p0, p1)
            pygame.draw.line(self.surf, self.col, p0, p1)
        screen.blit(self.surf, self.rect)
            



### Object creation
#testgraph = Graph(pygame.Rect(0,0,800,200), pygame.Color((50, 150, 225)), 4)


floor = pymunk.Segment(space.static_body, Vec2d(0, 800), Vec2d(800, 800), 4.0)
floor.friction = 0.4
space.add(floor)

mass, radius = 10, 80
r_moment = pymunk.moment_for_circle(mass, 0, radius)
r_body = pymunk.Body(mass, r_moment)
r_body.position = 400, 400
red = pymunk.Circle(r_body, radius)
red.color = pygame.Color(240, 110, 120)
space.add(r_body, red)

mass, radius = 5, 80
b_moment = pymunk.moment_for_circle(mass, 0, radius)
b_body = pymunk.Body(mass, b_moment)
b_body.position = 200, 600
blue = pymunk.Circle(b_body, radius)
blue.color = pygame.Color(110, 120, 240)
space.add(b_body, blue)

b_body.apply_impulse_at_world_point(Vec2d(1000.0, 0.0), b_body.position)



### Setup
def coll_func(arbiter, space, data):
    global test
    if arbiter.is_first_contact:
        if (arbiter.shapes[0] is red or arbiter.shapes[0] is blue) and (arbiter.shapes[1] is red or arbiter.shapes[1] is blue):
            test = arbiter.contact_point_set
            print(arbiter.total_impulse)

    
collhandler.post_solve = coll_func




### Mainloop
while run:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    ### Update objects

    ### Clear screen
    screen.fill((30, 30, 40))

    ### Draw stuff
    space.debug_draw(draw_options)

    pg_mouse_pos = pygame.mouse.get_pos()
    pm_mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)

    ### Update physics
    dt = 1.0 / 600.0
    for x in range(1):
        space.step(dt)

    ### Flip screen
    pygame.display.update()
    clock.tick(50)
    pygame.display.set_caption("pymunk test 6" + " "*30 + "fps: " + str(clock.get_fps()))

pygame.quit()
