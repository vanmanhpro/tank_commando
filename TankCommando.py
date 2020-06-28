import sys, random, pygame
from pygame.locals import *
from pygame.sprite import Group
import pickle

GRID_UNIT = 30

MAP = []
with open('map', 'r') as map_file:
    for line in map_file:
        temp_line = []
        for character in line:
            if character != '\n':
                temp_line.append(character)
        MAP.append(temp_line)

GRID_X, GRID_Y = len(MAP[0]), len(MAP)

SURFACE_LIB = pygame.image.load("sprites.gif")
sprites = pygame.image.load("sprites.gif")

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
pygame.display.set_caption('Battle Field')

speed = [1, 1]

SCREEN = pygame.display.set_mode(WINDOW_SIZE)


def is_collided(rect_1, rect_2):
    return False


tank_size = GRID_UNIT, GRID_UNIT
PRO = 'pro'
ANTA = 'anta'
TANK_SUR = {
    PRO: {},
    ANTA: {}
}
pro_tank_surface = pygame.Surface((13, 13))
pro_tank_surface.blit(pygame.image.load("sprites.gif"), (0, 0), (0, 0, 13, 13))
temp_tank = {}
TANK_SUR[PRO][UP] = pygame.transform.scale(pro_tank_surface, tank_size)
TANK_SUR[PRO][LEFT] = pygame.transform.rotate(TANK_SUR[PRO][UP], 90)
TANK_SUR[PRO][DOWN] = pygame.transform.rotate(TANK_SUR[PRO][UP], 180)
TANK_SUR[PRO][RIGHT] = pygame.transform.rotate(TANK_SUR[PRO][UP], -90)

anta_tank_surface = pygame.Surface((13, 13))
anta_tank_surface.blit(pygame.image.load("sprites.gif"), (0, 0), (31, 0, 18, 16))
temp_tank = {}
TANK_SUR[ANTA][UP] = pygame.transform.scale(anta_tank_surface, tank_size)
TANK_SUR[ANTA][LEFT] = pygame.transform.rotate(TANK_SUR[ANTA][UP], 90)
TANK_SUR[ANTA][DOWN] = pygame.transform.rotate(TANK_SUR[ANTA][UP], 180)
TANK_SUR[ANTA][RIGHT] = pygame.transform.rotate(TANK_SUR[ANTA][UP], -90)


class Tank(pygame.sprite.Sprite):
    def __init__(self, direction, grid_position, type, tank_id=random.randint(1, 1000000000)):
        pygame.sprite.Sprite.__init__(self)

        self.image = TANK_SUR[type][direction]
        self.image.set_colorkey(BLACK)
        self.direction = direction
        self.type = type
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
        self.image = TANK_SUR[self.type][self.next_move_command]

        temp_dest_rect = self.rect.move(TANK_STEP[self.next_move_command])

        if temp_dest_rect.left < 0 or temp_dest_rect.right > WINDOW_WIDTH \
                or temp_dest_rect.top < 0 or temp_dest_rect.bottom > WINDOW_HEIGHT:
            self.next_move_command = None
            return

        temp_sprite = Tank(self.direction, self.grid_move(self.direction), self.type)

        if len(pygame.sprite.spritecollide(temp_sprite, OBJECTS, False)) \
                or len(pygame.sprite.spritecollide(temp_sprite, STEEL_OBJS, False)) \
                or len(pygame.sprite.spritecollide(temp_sprite, WATER_OBJS, False)) \
                or len(pygame.sprite.spritecollide(temp_sprite, BRICK_OBJS, False)):
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
    def __init__(self, direction, grid_position, type, tank_id=random.randint(1, 1000000000)):
        Tank.__init__(self, direction, grid_position, type, tank_id)

    def set_action(self):
        if self.moving is None and random.randint(1, 100000000) % 30 == 0:
            possible_action = [UP, DOWN, LEFT, RIGHT]
            action = possible_action[random.randint(0, 3)]

            self.fire(ENEMY_BULLETS)
            self.command_move(action)

    def update(self, anti_tanks=[]):
        self.set_action()
        self.set_move()
        self.move()
        SCREEN.blit(self.image, self.rect)
        return


bullet_size = 10, 10
BULLET = {}
BULLET[UP] = pygame.transform.scale(pygame.image.load("bullet.png"), bullet_size)
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

        collision_bricks = pygame.sprite.spritecollide(self, BRICK_OBJS, False)
        for brick in collision_bricks:
            brick.kill()
            self.kill()

        if len(pygame.sprite.spritecollide(self, STEEL_OBJS, False)):
            self.kill()

        if self.is_out():
            self.kill()

GROUND, BRIDGE, BRICK, STEEL, WATER, GRASS, ALLIED_TANK_SYM, ENEMY_TANK_SYM = '-', 'R', 'B', 'S', 'W', 'G', 'A', 'E'

object_size = (GRID_UNIT, GRID_UNIT)

OBJ_SUR = {}

ground_surface = pygame.Surface((8, 8))
ground_surface.blit(SURFACE_LIB, (0, 0), (64, 72, 8, 8))

brick_surface = pygame.Surface((8, 8))
brick_surface.blit(SURFACE_LIB, (0, 0), (56, 64, 8, 8))

steel_surface = pygame.Surface((8, 8))
steel_surface.blit(SURFACE_LIB, (0, 0), (48, 72, 8, 8))

water_surface = pygame.Surface((8, 8))
water_surface.blit(SURFACE_LIB, (0, 0), (64, 64, 8, 8))

grass_surface = pygame.Surface((8, 8))
grass_surface.blit(SURFACE_LIB, (0, 0), (56, 72, 8, 8))

OBJ_SUR = {
    BRIDGE: pygame.transform.scale(ground_surface, object_size),
    BRICK: pygame.transform.scale(brick_surface, object_size),
    STEEL: pygame.transform.scale(steel_surface, object_size),
    WATER: pygame.transform.scale(water_surface, object_size),
    GRASS: pygame.transform.scale(grass_surface, object_size),
}


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, obs_type, grid_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = OBJ_SUR[obs_type]
        self.image.set_colorkey(BLACK)

        self.obs_type = obs_type

        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = grid_position[0] * GRID_UNIT, grid_position[1] * GRID_UNIT

    def update(self):
        SCREEN.blit(self.image, self.rect)

class Game():
    MENU, PLAY, GAMEOVER = 0, 1, 2
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0, 0, 0))
        self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416 + 40
        self.player_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13, 13), 270)

        self.game_stage = self.MENU

    def gameCycle(self):
        game_loop = True
        while game_loop:
            if self.game_stage == self.MENU:
                self.showMenu()
            elif self.game_stage == self.PLAY:
                self.play()
            elif self.game_stage == self.GAMEOVER:
                self.gameOver()

    def gameOver(self):
        """ End game and return to menu """

        print("Game Over")

        self.game_over_y = 416 + 40

        self.gameOverScreen()


    def gameOverScreen(self):
        """ Show game over screen """

        SCREEN.fill([0, 0, 0])

        self.writeInBricks("game", [125, 140])
        self.writeInBricks("over", [125, 220])
        pygame.display.flip()

        while self.game_stage == self.GAMEOVER:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.game_stage = self.MENU


    def showMenu(self):
        """ Show game menu
        Redraw screen only when up or down key is pressed. When enter is pressed,
        exit from this screen and start the game with selected number of players
        """


        self.animateIntroScreen()

        while self.game_stage == self.MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_UP:
                        if self.nr_of_players == 2:
                            self.nr_of_players = 1
                            self.drawIntroScreen()
                    elif event.key == pygame.K_DOWN:
                        if self.nr_of_players == 1:
                            self.nr_of_players = 2
                            self.drawIntroScreen()
                    elif event.key == pygame.K_RETURN:
                        self.game_stage = self.PLAY

    def play(self):
        
        global OBJECTS, BULLETS, ENEMY_BULLETS, ENEMY_TANKS, TANK, ENEMY_TANK, ENEMY_TANKS, BRIDGE_OBJS, BRICK_OBJS, STEEL_OBJS, WATER_OBJS, GRASS_OBJS

        OBJECTS = Group()
        BULLETS = Group()
        ENEMY_BULLETS = Group()
        ENEMY_TANKS = Group()

        BRIDGE_OBJS, BRICK_OBJS, STEEL_OBJS, WATER_OBJS, GRASS_OBJS = Group(), Group(), Group(), Group(), Group()

        for i in range(0, GRID_X):
            for j in range(0, GRID_Y):
                if MAP[j][i] == GROUND:
                    continue

                if MAP[j][i] == BRIDGE:
                    new_obs = Obstacles(MAP[j][i], (i, j))
                    BRIDGE_OBJS.add(new_obs)
                elif MAP[j][i] == BRICK:
                    new_obs = Obstacles(MAP[j][i], (i, j))
                    BRICK_OBJS.add(new_obs)
                elif MAP[j][i] == STEEL:
                    new_obs = Obstacles(MAP[j][i], (i, j))
                    STEEL_OBJS.add(new_obs)
                elif MAP[j][i] == WATER:
                    new_obs = Obstacles(MAP[j][i], (i, j))
                    WATER_OBJS.add(new_obs)
                elif MAP[j][i] == GRASS:
                    new_obs = Obstacles(MAP[j][i], (i, j))
                    GRASS_OBJS.add(new_obs)
                elif MAP[j][i] == ALLIED_TANK_SYM:
                    TANK = Tank(UP, (i, j), PRO, ALLIED_TANK)
                elif MAP[j][i] == ENEMY_TANK_SYM:
                    ENEMY_TANK = EnemyTank(UP, (i, j), ANTA)
                    ENEMY_TANKS.add(ENEMY_TANK)
                    OBJECTS.add(ENEMY_TANK)
        
        OBJECTS.add(TANK)

        period_sum = 0

        commands = []
        with open("commands", "wb") as file:
            pickle.dump(commands, file)

        while self.game_stage == self.PLAY:

            dt = clock.tick(60)

            period_sum += dt
            if period_sum > 250:
                period_sum = 0
                with open("commands", "rb") as file:
                    commands = pickle.load(file)

                for command in commands:
                    if command == DOWN:
                        TANK.command_move(DOWN)
                    elif command == UP:
                        TANK.command_move(UP)
                    elif command == LEFT:
                        TANK.command_move(LEFT)
                    elif command == RIGHT:
                        TANK.command_move(RIGHT)
                    elif command == SHOOT:
                        TANK.fire(BULLETS)

                commands = []
                with open("commands", "wb") as file:
                    pickle.dump(commands, file)

            SCREEN.fill(BLACK)

            BRIDGE_OBJS.update()
            BRICK_OBJS.update()
            STEEL_OBJS.update()
            WATER_OBJS.update()

            # Game play
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                    

            BULLETS.update(ENEMY_TANKS)
            ENEMY_BULLETS.update([TANK])

            TANK.update(ENEMY_TANKS)

            if TANK.is_dead():
                self.game_stage = self.GAMEOVER

            ENEMY_TANKS.update([TANK])

            enemy_tank_dead = 0
            for enemy_tank in ENEMY_TANKS:
                if enemy_tank.is_dead():
                    enemy_tank_dead += 1;
            if enemy_tank_dead == len(ENEMY_TANKS):
                self.game_stage = self.GAMEOVER

            GRASS_OBJS.update()

            pygame.display.flip()

    def drawIntroScreen(self, put_on_surface=True):
        """ Draw intro (menu) screen
        @param boolean put_on_surface If True, flip display after drawing
        @return None
        """

        SCREEN.fill([0, 0, 0])

        if pygame.font.get_init():

            SCREEN.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])

        SCREEN.blit(self.player_image, [125, 245])

        self.writeInBricks("battle", [70, 80])
        self.writeInBricks("city", [135, 160])

        if put_on_surface:
            pygame.display.flip()

    def animateIntroScreen(self):
        """ Slide intro (menu) screen from bottom to top
        If Enter key is pressed, finish animation immediately
        @return None
        """


        self.drawIntroScreen(False)
        screen_cp = SCREEN.copy()

        SCREEN.fill([0, 0, 0])

        y = 416
        while (y > 0):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break

            SCREEN.blit(screen_cp, [0, y])
            pygame.display.flip()
            y -= 5

        SCREEN.blit(screen_cp, [0, 0])
        pygame.display.flip()

    def chunks(self, l, n):
        """ Split text string in chunks of specified size
        @param string l Input string
        @param int n Size (number of characters) of each chunk
        @return list
        """
        return [l[i:i + n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):
        """ Write specified text in "brick font"
        Only those letters are available that form words "Battle City" and "Game Over"
        Both lowercase and uppercase are valid input, but output is always uppercase
        Each letter consists of 7x7 bricks which is converted into 49 character long string
        of 1's and 0's which in turn is then converted into hex to save some bytes
        @return None
        """


        bricks = sprites.subsurface(56, 64, 8, 8)
        brick1 = bricks.subsurface((0, 0, 4, 4))
        brick2 = bricks.subsurface((4, 0, 4, 4))
        brick3 = bricks.subsurface((4, 4, 4, 4))
        brick4 = bricks.subsurface((0, 4, 4, 4))

        alphabet = {
            "a": "0071b63c7ff1e3",
            "b": "01fb1e3fd8f1fe",
            "c": "00799e0c18199e",
            "e": "01fb060f98307e",
            "g": "007d860cf8d99f",
            "i": "01f8c183060c7e",
            "l": "0183060c18307e",
            "m": "018fbffffaf1e3",
            "o": "00fb1e3c78f1be",
            "r": "01fb1e3cff3767",
            "t": "01f8c183060c18",
            "v": "018f1e3eef8e08",
            "y": "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i % 2 == 0 and j % 2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i % 2 == 1 and j % 2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i % 2 == 1 and j % 2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i % 2 == 0 and j % 2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            SCREEN.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16

clock = pygame.time.Clock()

game = Game()
game.gameCycle()
