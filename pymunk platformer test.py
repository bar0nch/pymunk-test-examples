import math

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d



pygame.init()
screen = pygame.display.set_mode((800, 800))
pm_surf = pygame.Surface((1000, 1000))
clock = pygame.time.Clock()
camera = (-100, -100)
run = True

### Physics stuff
space = pymunk.Space()
space.gravity = Vec2d(0.0, 10000.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)

collhandler = space.add_collision_handler(0, 0)
collhandler.data["surface"] = screen



### Object definition
class Player:
    limits = {"x":(-1000, 1800), "y":(-1000, 1800)}
    
    def __init__(self, coords, mass, size):
        self.direction = 0
        self.is_touching_ground = True
        self.is_climbing = False
        self.jump = False
        self.ground_shape = None

        self.size = size
        points = [(-size, -size), (-size, size), (size, size), (size, -size)]
        moment = pymunk.moment_for_poly(mass, points)
        self.body = pymunk.Body(mass, moment)
        self.body.position = Vec2d(*coords)
        self.shape = pymunk.Poly(self.body, points, radius=2)
        self.shape.friction = 0.6
        space.add(self.body, self.shape)


    def is_over_limits(self):
        over_x_inf = self.body.position.x < Player.limits["x"][0]
        over_x_sup = self.body.position.x > Player.limits["x"][1]
        over_y_inf = self.body.position.y < Player.limits["y"][0]
        over_y_sup = self.body.position.y > Player.limits["y"][1]
        
        if over_x_inf or over_x_sup or over_y_inf or over_y_sup:
            return True
        else:
            return False


    def apply_topright_force(self, force):
        vertice_pos = Vec2d(self.body.position.x + self.size, self.body.position.y - self.size)
        self.body.apply_force_at_world_point(force, vertice_pos)

    def apply_bottomright_force(self, force):
        vertice_pos = Vec2d(self.body.position.x + self.size, self.body.position.y + self.size)
        self.body.apply_force_at_world_point(force, vertice_pos)


    def process_coll_points(self, arbiter, status):
        if status == "pre solve":
            points = arbiter.contact_point_set.points
            if len(points) == 2:
                point_0a_below = points[0].point_a.y >= self.body.position.y
                point_0b_below = points[1].point_b.y >= self.body.position.y
                point_1a_below = points[1].point_a.y >= self.body.position.y
                point_1b_below = points[1].point_b.y >= self.body.position.y
                if point_0a_below and point_0b_below and point_1a_below and point_1b_below:
                    self.is_touching_ground = True
                    if arbiter.shapes[0] == player:
                        self.ground_shape = arbiter.shapes[1]
                    else:
                        self.ground_shape = arbiter.shapes[0]
        
        elif status == "exit":
            if self.ground_shape in arbiter.shapes:
                self.ground_shape = None
                self.is_touching_ground = False


    def event_update(self, event):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
            self.direction = 0
        elif keys[pygame.K_RIGHT]:
            self.direction = 1
        elif keys[pygame.K_LEFT]:
            self.direction = -1
        else:
            self.direction = 0

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.jump = True


    def update(self):
        if self.jump:
            self.jump = False
            if self.is_touching_ground or self.is_climbing:
                self.body.apply_impulse_at_world_point(Vec2d(0.0, -105000), self.body.position)

        if self.direction != 0:
            if self.is_climbing:
                self.apply_topright_force(Vec2d(900000.0 * self.direction, 0.0))
                self.apply_bottomright_force(Vec2d(900000.0 * self.direction, 0.0))
                self.body.apply_force_at_world_point(Vec2d(0.0, 200000.0), self.body.position)
            else:
                self.body.apply_impulse_at_world_point(Vec2d(3000.0 * self.direction, 0.0), self.body.position)



class Platform:
    all_platforms = []
    radius = 20

    @classmethod
    def all(cls):
        for platform in cls.all_platforms:
            yield platform
    
    def __init__(self, point_a, point_b):
        Platform.all_platforms.append(self)
        self.body = pymunk.Body(10, body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, point_a, point_b, Platform.radius)
        self.shape.friction = 0.5
        space.add(self.body, self.shape)


class ClimbPlatform(Platform):
    all_climb_platforms = []

    @classmethod
    def all(cls):
        for platform in cls.all_climb_platforms:
            yield platform
    
    def __init__(self, point_a, point_b):
        ClimbPlatform.all_climb_platforms.append(self)
        super().__init__(point_a, point_b)
        self.shape.color = pygame.Color(200, 170, 120)
        self.shape.friction = 0.6
            



### Object creation
player = Player((400, 400), 50, 20)

floor = pymunk.Segment(space.static_body, Vec2d(-100, 800), Vec2d(900, 800), 50.0)
floor.friction = 0.5
space.add(floor)


Platform(Vec2d(300, 200), Vec2d(600, 200))
Platform(Vec2d(50, 400), Vec2d(200, 400))
Platform(Vec2d(150, 600), Vec2d(300, 600))
Platform(Vec2d(450, 200), Vec2d(450, 600))
ClimbPlatform(Vec2d(700, 100), Vec2d(700, 600))



### Setup
def enter_coll_func(arbiter, space, data):
    global player

    if player.shape in arbiter.shapes:
        for shape in arbiter.shapes:
            if shape is player:
                continue
            else:
                climb_shapes = [platform.shape for platform in ClimbPlatform.all()]
                if shape in climb_shapes:
                    player.is_climbing = True
                break
        
    return True

def exit_coll_func(arbiter, space, data):
    global player

    if player.shape in arbiter.shapes:
        player.process_coll_points(arbiter, "exit")

    if player.shape in arbiter.shapes:
        for shape in arbiter.shapes:
            if shape is player:
                continue
            else:
                climb_shapes = [platform.shape for platform in ClimbPlatform.all()]
                if shape in climb_shapes:
                    player.is_climbing = False
                break
        
    return True


def pre_coll_func(arbiter, space, data):
    if player.shape in arbiter.shapes:
        player.process_coll_points(arbiter, "pre solve")
    return True

collhandler.begin = enter_coll_func
collhandler.pre_solve = pre_coll_func
collhandler.separate = exit_coll_func


def respawn_player():
    global player
    if player == None:
        player = Player((400, 400), 50, 20)

            
def remove_player_if_out():
    global player
    if player:
        if player.is_over_limits():
            player = None
            respawn_player()
        



### Mainloop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if player:
            player.event_update(event)


    ### Update objects
    remove_player_if_out()
    if player:
        player.update()

    ### Clear screen
    screen.fill((30, 30, 40))

    ### Draw stuff
    space.debug_draw(draw_options)

    pg_mouse_pos = pygame.mouse.get_pos()
    pm_mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)

    ### Update physics
    dt = 1.0 / 60.0
    for x in range(1):
        space.step(dt)

    ### Flip screen
    pygame.display.update()
    clock.tick(50)
    pygame.display.set_caption("pymunk test 6" + " "*30 + "fps: " + str(clock.get_fps()))

pygame.quit()
