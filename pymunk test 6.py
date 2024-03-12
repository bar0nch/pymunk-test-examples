import math

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


### Object definition
class TargetPoint:
    '''
    All the target points will form the target shape in which the shape query will be executed.
    They are moveable with the mouse so the shape can be customized.
    New points can be created and each point except the first one can be deleted.
    '''
    
    all_points = []
    p0 = None
    r = 20
    p_font = pygame.font.SysFont('Arial', 28)

    point_lock = False
    cur_id = 0

    @classmethod
    def all(cls):
        for p in cls.all_points:
            yield p


    @classmethod
    def get_shape(cls):
        return pymunk.Poly(pymunk.Body(body_type=pymunk.Body.KINEMATIC), [point.pm_coords for point in cls.all()])
        

    def __init__(self, pm_coords : tuple):
        TargetPoint.cur_id += 1
        TargetPoint.all_points.append(self)
        if TargetPoint.p0 == None:
            TargetPoint.p0 = self
            
        self.selected = False
        self.id = TargetPoint.cur_id
        self.pm_coords = Vec2d(*pm_coords)
        self.pg_coords = pymunk.pygame_util.to_pygame(pm_coords, screen)
        self.txt_obj = TargetPoint.p_font.render(str(self.id), False, pygame.Color("white"))
        self.txt_rect = self.txt_obj.get_rect()
        self.txt_rect.topleft = self.pg_coords[0] - 40, self.pg_coords[1] - 40

        if TargetPoint.p0 is self:
            self.next = self
        else:
            self.next = TargetPoint.p0.next
            TargetPoint.p0.next = self


    def delete(self):
        if TargetPoint.p0 is not self:
            TargetPoint.all_points.remove(self)
            for p in TargetPoint.all():
                if p.next is self:
                    p.next = self.next


    def event_update(self, event):
        mouse_point_distance = Vec2d(*pymunk.pygame_util.get_mouse_pos(screen)).get_distance(self.pm_coords)

        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if event.button == 3:
                if mouse_point_distance <= TargetPoint.r:
                    self.delete()
                
            if not TargetPoint.point_lock:
                if event.button == 1:
                    if mouse_point_distance <= TargetPoint.r:
                        self.selected = True
                        TargetPoint.point_lock = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected = False
            TargetPoint.point_lock = False


    def update(self):
        if self.selected:
            self.pm_coords = pymunk.pygame_util.get_mouse_pos(screen)
            self.pg_coords = pymunk.pygame_util.to_pygame(self.pm_coords, screen)
            self.txt_rect.topleft = self.pg_coords[0] - 40, self.pg_coords[1] - 40


    def draw(self):
        center = (self.pg_coords[0], self.pg_coords[1])
        
        if self.selected:
            pygame.draw.circle(screen, pygame.Color("white"), center, TargetPoint.r)
        else:
            pygame.draw.circle(screen, pygame.Color("white"), center, TargetPoint.r, width=4)

        pygame.draw.line(screen, pygame.Color("white"), center, (self.next.pg_coords[0], self.next.pg_coords[1]))
        screen.blit(self.txt_obj, self.txt_rect)



class QueryDisplay:
    '''
    Displays the colors of the shapes found in the query.
    '''

    txt_obj = pygame.font.SysFont('Arial', 32).render("Query Shapes:   ", False, pygame.Color(240, 240, 240)).convert_alpha()
    txt_rect = txt_obj.get_rect()
    txt_rect.topleft = 20, 20
    query_res = []
    rect_side = 50
    
    @classmethod
    def update(cls):
        if len(TargetPoint.all_points) >= 3:
            cls.query_res = space.shape_query(TargetPoint.get_shape())


    @classmethod
    def draw(cls):
        screen.blit(cls.txt_obj, cls.txt_rect)
        for i, res in enumerate(cls.query_res):
            col = res.shape.color
            rect = pygame.Rect(0, 0, cls.rect_side, cls.rect_side)
            rect.midleft = cls.txt_rect.x + cls.txt_rect.w + (20 + cls.rect_side) * i, cls.txt_rect.y + cls.txt_rect.h // 2
            pygame.draw.rect(screen, col, rect)



### Object creation
TargetPoint((200, 200))

mass, radius = 10, 80
r_moment = pymunk.moment_for_circle(mass, 0, radius)
r_body = pymunk.Body(mass, r_moment)
r_body.position = 400, 400
red = pymunk.Circle(r_body, radius)
red.color = pygame.Color(240, 110, 120)
space.add(r_body, red)

mass, radius = 20, 80
b_moment = pymunk.moment_for_circle(mass, 0, radius)
b_body = pymunk.Body(mass, b_moment)
b_body.position = 200, 600
blue = pymunk.Circle(b_body, radius)
blue.color = pygame.Color(110, 120, 240)
space.add(b_body, blue)


### Mainloop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_SPACE:
                TargetPoint((400, 400))

        for p in TargetPoint.all():
            p.event_update(event)


    ### Update objects
    for p in TargetPoint.all():
        p.update()

    QueryDisplay.update()

    ### Clear screen
    screen.fill((30, 30, 40))

    ### Draw stuff
    space.debug_draw(draw_options)

    pg_mouse_pos = pygame.mouse.get_pos()
    pm_mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)

    for p in TargetPoint.all():
        p.draw()

    QueryDisplay.draw()

    ### Update physics
    dt = 1.0 / 60.0
    for x in range(1):
        space.step(dt)

    ### Flip screen
    pygame.display.update()
    clock.tick(50)
    pygame.display.set_caption("pymunk test 6" + " "*30 + "fps: " + str(clock.get_fps()))

pygame.quit()


