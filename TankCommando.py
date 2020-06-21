import sys, random, pygame 
from pygame.locals import *
from pygame.sprite import Group

GRID_UNIT = 30
GRID_X, GRID_Y = 20, 20 

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = GRID_X * GRID_UNIT, GRID_Y * GRID_UNIT
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
UP, DOWN, LEFT, RIGHT, SHOOT = 'up', 'down', 'left', 'right', 'shoot'
ALLIED_TANK = 0

GRID_STEP = {
    UP: [0, -1], 
    DOWN: [0, 1], 
    LEFT: [-1, 0], 
    RIGHT: [1, 0]
}

TANK_STEP = {
    UP: [0, -GRID_UNIT], 
    DOWN: [0, GRID_UNIT], 
    LEFT: [-GRID_UNIT, 0], 
    RIGHT: [GRID_UNIT, 0]
}

TANK_SPEED = 1
TANK_MOVE = {
    UP: [0, -TANK_SPEED], 
    DOWN: [0, TANK_SPEED], 
    LEFT: [-TANK_SPEED, 0], 
    RIGHT: [TANK_SPEED, 0]
}

BULLET_SPEED = 2
BULLET_MOVE = {}
BULLET_MOVE = {
    UP: [0, -BULLET_SPEED], 
    DOWN: [0, BULLET_SPEED], 
    LEFT: [-BULLET_SPEED, 0], 
    RIGHT: [BULLET_SPEED, 0]
}

pygame.init()

speed = [1, 1]

SCREEN = pygame.display.set_mode(WINDOW_SIZE)        

def is_collided(rect_1, rect_2):
    return False

tank_size = GRID_UNIT, GRID_UNIT
TANK = {}
pro_tank_surface = pygame.Surface((13, 13))
pro_tank_surface.blit(pygame.image.load("sprites.gif"), (0, 0), (0, 0, 13, 13))
TANK[UP] = pygame.transform.scale(pro_tank_surface, tank_size)
TANK[LEFT] = pygame.transform.rotate(TANK[UP], 90)
TANK[DOWN] = pygame.transform.rotate(TANK[UP], 180)
TANK[RIGHT] = pygame.transform.rotate(TANK[UP], -90)


class Tank(pygame.sprite.Sprite):
    def __init__(self, direction, grid_position, tank_id=random.randint(1, 1000000000)):
        pygame.sprite.Sprite.__init__(self)

        self.image = TANK[direction]
        self.direction = direction
        self.rect = self.image.get_rect()
        self.grid_position = grid_position
        self.rect.left, self.rect.top = grid_position[0] * GRID_UNIT, grid_position[1] * GRID_UNIT
        self.tank_id = tank_id
        self.moving = None
        self.next_move_command = None
        self.dead = False

    def is_dead(self):
        return self.dead

    def command_move(self, move_direction):
        if self.next_move_command is None:
            self.next_move_command = move_direction

    def grid_move(self, direction):
        return self.grid_position[0] + GRID_STEP[direction][0], self.grid_position[1] + GRID_STEP[direction][1]

    def set_move(self):
        if self.moving is not None:
            return

        if self.next_move_command is None: 
            return 
        
        self.direction = self.next_move_command
        self.image = TANK[self.next_move_command]
        
        temp_dest_rect = self.rect.move(TANK_STEP[self.next_move_command])

        if temp_dest_rect.left < 0 or temp_dest_rect.right > WINDOW_WIDTH \
            or temp_dest_rect.top < 0 or temp_dest_rect.bottom > WINDOW_HEIGHT:
            self.next_move_command = None
            return

        temp_sprite = Tank(self.direction, self.grid_move(self.direction))
        collide_sprites = pygame.sprite.spritecollide(temp_sprite, OBJECTS, False)
        if len(collide_sprites):
            self.next_move_command = None
            return

        self.moving = {
            'dir': self.next_move_command,
            'dest': temp_dest_rect
        }
        self.next_move_command = None

    def move(self):
        if self.moving is None:
            return
        
        direction = self.moving['dir']
        dest = self.moving['dest']

        temp_tank_rect = self.rect.move(TANK_MOVE[direction])

        if direction == UP and temp_tank_rect.top < dest.top: 
            temp_tank_rect.top = dest.top
        if direction == DOWN and temp_tank_rect.bottom > dest.bottom: 
            temp_tank_rect.bottom = dest.bottom
        if direction == LEFT and temp_tank_rect.left < dest.left: 
            temp_tank_rect.left = dest.left
        if direction == RIGHT and temp_tank_rect.right > dest.right: 
            temp_tank_rect.right = dest.right
            
        self.rect = temp_tank_rect
        if self.rect == dest:
            self.moving = None
            self.grid_position = self.grid_move(direction)

    def fire(self, bullets):
        bullet_position = (0, 0)
        if self.direction == UP:
            bullet_position = self.rect.midtop
        elif self.direction == DOWN:
            bullet_position = self.rect.midbottom
        elif self.direction == LEFT:
            bullet_position = self.rect.midleft
        elif self.direction == RIGHT:
            bullet_position = self.rect.midright
        new_bullet = Bullet(self.direction, bullet_position, self.tank_id)
        bullets.add([new_bullet])

    def terminate(self):
        self.dead = True
        self.kill()

    def update(self, anti_tanks=[]):
        self.set_move()
        self.move()
        SCREEN.blit(self.image, self.rect)
        return
    
    def return_rect(self):
        return self.rect

class EnemyTank(Tank):
    def __init__(self, direction, grid_position, tank_id=random.randint(1, 1000000000)):
        Tank.__init__(self, direction, grid_position, tank_id)

    def set_action(self):
        if self.moving is None and random.randint(1, 100000000) % 30 == 0:
            possible_action = [UP, DOWN, LEFT, RIGHT, SHOOT]
            action = possible_action[random.randint(0,4)]

            if action == SHOOT:
                self.fire(enemy_bullets)
            else:
                self.command_move(action)

    def update(self, anti_tanks=[]):
        self.set_action()
        self.set_move()
        self.move()
        SCREEN.blit(self.image, self.rect)
        return

bullet_size = 10, 10
BULLET = {}
BULLET[UP] =  pygame.transform.scale(pygame.image.load("bullet.png"), bullet_size)
BULLET[LEFT] = pygame.transform.rotate(BULLET[UP], 90)
BULLET[DOWN] = pygame.transform.rotate(BULLET[UP], 180)
BULLET[RIGHT] = pygame.transform.rotate(BULLET[UP], -90)

class Bullet(pygame.sprite.Sprite):

    def __init__(self, direction, position, tank_id):
        pygame.sprite.Sprite.__init__(self)

        self.image = BULLET[direction]
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.tank_id = tank_id

    def is_out(self):
        if self.rect.top < 0 or self.rect.bottom > WINDOW_HEIGHT \
            or self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
            return True

        return False

    def update(self, anti_tanks=[]):
        self.rect = self.rect.move(BULLET_MOVE[self.direction])
        SCREEN.blit(self.image, self.rect)
        for tank in anti_tanks:
            if pygame.sprite.collide_rect(self, tank):
                tank.terminate()
                self.kill()
        
        if self.is_out():
            self.kill()

    



clock = pygame.time.Clock()

OBJECTS = Group()
bullets = Group()
enemy_bullets = Group()
enemy_tanks = Group()

tank = Tank(UP, (0, 0), ALLIED_TANK)
OBJECTS.add(tank)

enemy_tank = EnemyTank(UP, (8, 9))
enemy_tanks.add(enemy_tank)
OBJECTS.add(enemy_tank)


while 1:
    dt = clock.tick(80)
    SCREEN.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            pressing = pygame.key.get_pressed()
            if pressing[pygame.K_DOWN]:
                tank.command_move(DOWN)
            elif pressing[pygame.K_UP]:
                tank.command_move(UP)
            elif pressing[pygame.K_LEFT]:
                tank.command_move(LEFT)
            elif pressing[pygame.K_RIGHT]:
                tank.command_move(RIGHT)
            if pressing[pygame.K_SPACE]:
                tank.fire(bullets)
        
    bullets.update(enemy_tanks)
    enemy_bullets.update([tank])

    if not tank.is_dead():
        tank.update(enemy_tanks)

    enemy_tanks.update([tank])
    
    
    pygame.display.flip()


