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
space.gravity = Vec2d(0.0, 9000.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)

collhandler = space.add_collision_handler(0, 0)
collhandler.data["surface"] = screen



### Object definition
class ChainEstremity:
    #blocks where the chain is attached
    half_side = 40
    mass = 10
    
    def __init__(self, center):
        half_side = ChainEstremity.half_side
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Poly(self.body,
                                 [(-half_side,-half_side), (half_side,-half_side), (half_side,half_side), (-half_side, half_side)]
                                 )
        self.shape.mass = ChainEstremity.mass
        self.body.position = center
        space.add(self.body, self.shape)


    def draw(self):
        topleft = self.body.position - Vec2d(ChainEstremity.half_side, ChainEstremity.half_side)
        pygame.draw.rect(screen, pygame.Color(120, 120, 120), (topleft.x, topleft.y, ChainEstremity.half_side * 2, ChainEstremity.half_side * 2))



    
class Chain:
    estremities = []
    links_offset = 0
    all_links = []


    @classmethod
    def get_links(cls):
        for link in cls.all_links:
            yield link
            
    
    def __init__(self, point_a, point_b, chain_links):
        Chain.estremities.append(ChainEstremity(point_a))
        Chain.estremities.append(ChainEstremity(point_b))

        estremities_dist = Chain.estremities[0].body.position.get_distance(Chain.estremities[1].body.position)
        links_length = estremities_dist // chain_links
        first_link = ChainLink(links_length)
        Chain.all_links.append(first_link)
        first_link.setup(Chain.estremities[0].body.position)
        first_link_constraint = pymunk.constraints.PinJoint(Chain.estremities[0].body, first_link.shape1.body)
        first_link_constraint.collide_bodies = False
        space.add(first_link_constraint)
        
        for i in range(1, chain_links):
            new_link = ChainLink(links_length)
            Chain.all_links.append(new_link)
            new_link.setup(Chain.estremities[0].body.position + Vec2d(links_length * i, 0))
            new_link.link_to(Chain.all_links[i-1])
            
            if i == chain_links - 1:
                last_link_costraint = pymunk.constraints.PinJoint(Chain.estremities[1].body, new_link.shape2.body)
                last_link_costraint.collide_bodies = False
                space.add(last_link_costraint)


    def draw(self):
        for estremity in Chain.estremities:
            estremity.draw()
        for link in self.get_links():
            link.draw()



class ChainLink:
    radius = 30
    mass = 1
    fill_col = pygame.Color(20, 110, 240)
    
    def __init__(self, length):
        self.length = length
        self.shape1 = pymunk.Circle(pymunk.Body(), ChainLink.radius)
        self.shape2 = pymunk.Circle(pymunk.Body(), ChainLink.radius)
        self.shape1.mass = ChainLink.mass
        self.shape2.mass = ChainLink.mass
        self.rotary_limit = pymunk.constraints.RotaryLimitJoint(self.shape1.body, self.shape2.body, 0, 0)
        space.add(self.shape1, self.shape1.body, self.shape2, self.shape2.body, self.rotary_limit)


    def setup(self, pos1):
        self.shape1.body.position = pos1
        self.shape2.body.position = Vec2d(pos1[0] + self.length, pos1[1])
        self.constraint1 = pymunk.constraints.PinJoint(self.shape1.body,
                                                      self.shape2.body,
                                                      Vec2d(0, ChainLink.radius),
                                                      Vec2d(0, ChainLink.radius))
        self.constraint2 = pymunk.constraints.PinJoint(self.shape1.body,
                                                      self.shape2.body,
                                                      Vec2d(0, -ChainLink.radius),
                                                      Vec2d(0, -ChainLink.radius))
        self.constraint3 = pymunk.constraints.PinJoint(self.shape1.body,
                                                      self.shape2.body,
                                                      Vec2d(ChainLink.radius, 0),
                                                      Vec2d(-ChainLink.radius, 0))
        self.constraint1.collide_bodies = False
        self.constraint2.collide_bodies = False
        space.add(self.constraint1, self.constraint2, self.constraint3)


    def get_full_length(self):
        return self.length + ChainLink.radius * 2


    def link_to(self, other):
        #NOTE: in the chain this object links to the previous one added
        slide_constraint = pymunk.constraints.SlideJoint(self.shape1.body, other.shape2.body,
                                                 Vec2d(0, 0), Vec2d(-ChainLink.radius, 0),
                                                 other.get_full_length() // 2, (other.get_full_length() + ChainLink.radius) // 2)
        rotary_constraint = pymunk.constraints.RotaryLimitJoint(self.shape1.body, other.shape2.body, -math.pi // 2, math.pi // 2)
        slide_constraint.collide_bodies = False
        rotary_constraint.collide_bodies = False
        space.add(slide_constraint, rotary_constraint)


    def draw(self):
        pygame.draw.circle(screen, ChainLink.fill_col, self.shape1.body.position, ChainLink.radius)
        pygame.draw.circle(screen, ChainLink.fill_col, self.shape2.body.position, ChainLink.radius)
        pygame.draw.line(screen, ChainLink.fill_col, self.shape1.body.position, self.shape2.body.position, width=ChainLink.radius*2)
            



### Object creation
mychain = Chain(Vec2d(50, 200), Vec2d(750, 200), 10)


#mychain.all_links[4].shape2.body.apply_impulse_at_local_point(Vec2d(0, 100000))



def pre_coll_func(arbiter, space, data):
    link_shapes1 = [link.shape1 for link in mychain.all_links]
    link_shapes2 = [link.shape2 for link in mychain.all_links]
    estremities_shapes = [estremity.shape for estremity in mychain.estremities]

    shape0_is_chainlink = arbiter.shapes[0] in link_shapes1 or arbiter.shapes[0] in link_shapes2
    shape1_is_chainlink = arbiter.shapes[1] in link_shapes1 or arbiter.shapes[1] in link_shapes2
    shape0_is_estremity = arbiter.shapes[0] in estremities_shapes
    shape1_is_estremity = arbiter.shapes[1] in estremities_shapes

    if shape0_is_chainlink and shape1_is_chainlink:
        return False
    
    if (shape0_is_estremity and shape1_is_chainlink) or (shape1_is_estremity and shape0_is_chainlink):
        return False

    print(arbiter.shapes)
    
    return True

collhandler.pre_solve = pre_coll_func




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
    mychain.draw()
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
    pygame.display.set_caption("pymunk test chain" + " "*30 + "fps: " + str(clock.get_fps()))

pygame.quit()
