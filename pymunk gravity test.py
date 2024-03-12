import random, time, math

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

pygame.init()


### Object creation
class Obj:
    all_objs = []
    sun = None
    screen = None
    space = None

    G = 50000
    
    def __init__(self, x, y, mass, radius=20, color=(210, 200, 200)):
        Obj.all_objs.append(self)
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius, Vec2d(0, 0))
        self.shape.color = pygame.Color(color)
        Obj.space.add(self.body, self.shape)


class Sun(Obj):
    def __init__(self):
        screen_size = Obj.screen.get_size()
        Obj.sun = self
        super().__init__(screen_size[0] // 2, screen_size[1] // 2, 60, color=(250, 200, 50))


class Planet(Obj):
    all_planets = []

    def __init__(self, i):
        screen_size = Obj.screen.get_size()
        Planet.all_planets.append(self)
        shift_from_sun = random.randint(0 + 25 * i, 25 + 25 * i)
        super().__init__(screen_size[0] // 2 + 150 + shift_from_sun, screen_size[1] // 2, 0.000001, 2, (155, 205, 215))
        self.body.velocity = Vec2d(0.0, -140.0)


    def calc_gravity(self):
        sun = Obj.sun
        angle = math.atan2(sun.body.position.y - self.body.position.y, self.body.position.x - sun.body.position.x)
        sun_distance_sqrd = sun.body.position.get_dist_sqrd(self.body.position)
        gravity_module = Obj.G * self.body.mass * sun.body.mass / sun_distance_sqrd
        return Vec2d(-gravity_module * math.cos(angle), gravity_module * math.sin(angle))



def main():
    screen = pygame.display.set_mode((1300, 1000))
    Obj.screen = screen
    clock = pygame.time.Clock()
    run = True

    ### Physics stuff
    space = pymunk.Space()
    Obj.space = space
    space.gravity = Vec2d(0.0, 0.0)
    draw_options = pymunk.pygame_util.DrawOptions(screen)


    ### Object istances
    Sun()
    for i in range(3):
        Planet(i)



    ### Mainloop
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False
                pygame.quit()
                return True

        ### Clear screen
        screen.fill((30, 30, 40))

        ### Draw stuff
        space.debug_draw(draw_options)

        ### Do physics
        for planet in Planet.all_planets:
            gravity = planet.calc_gravity()
            planet.body.apply_force_at_local_point(gravity)

        ### Update physics
        dt = 1.0 / 60.0
        for x in range(1):
            space.step(dt)

        ### Flip screen
        pygame.display.update()
        clock.tick(50)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

    pygame.quit()
    return False



while True:
    if main():
        break
