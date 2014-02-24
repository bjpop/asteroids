import pygame
import sys
from vector2D import Vec2d
from pygame.locals import (QUIT, KEYDOWN, K_RETURN,
   K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_ESCAPE)
from random import choice, randint 

MAX_X = 800
MAX_Y = 600
START_X = MAX_X / 2
START_Y = MAX_Y / 2
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAX_SHIP_SPEED = 10
FPS = 40 
BULLET_SPEED = 15 
BULLET_LENGTH = 10 
BULLET_WIDTH = 2
MAX_BULLET_AGE = 15 
MIN_ROCK_RADIUS = 20
MAX_ROCK_RADIUS = 80
ROCK_RADIUS_SIZE_STEP = 10
ROCK_RADIUSES = range(MIN_ROCK_RADIUS, MAX_ROCK_RADIUS+1, ROCK_RADIUS_SIZE_STEP)
MIN_ROCK_SPEED = 1
MAX_ROCK_SPEED = 4
MIN_NUM_ROCKS = 5
MAX_BULLETS = 2 


def random_colour():
    return (randint(100, 255), randint(50, 150), randint(50, 100))

class Rock(object):
    def __init__(self, position, velocity, radius, colour):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.colour = colour 

    def draw(self, windowSurface):
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(windowSurface, self.colour, center, self.radius)

    def move(self):
        self.position = self.position + self.velocity
        if self.position.x >= MAX_X:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = MAX_X - 1
        if self.position.y >= MAX_Y:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = MAX_Y - 1

class Bullet(object):
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction.normalized()
        self.velocity = self.direction * BULLET_SPEED
        self.age = 0

    def draw(self, windowSurface):
        start_pos = (self.position.x, self.position.y)
        end_pos_vec = self.position + self.direction * BULLET_LENGTH
        end_pos = (end_pos_vec.x, end_pos_vec.y) 
        pygame.draw.line(windowSurface, RED, start_pos, end_pos, BULLET_WIDTH)

    def move(self):
        self.position = self.position + self.velocity
        if self.position.x >= MAX_X:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = MAX_X - 1
        if self.position.y >= MAX_Y:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = MAX_Y - 1

    def time_step(self):
        self.age += 1

    def alive(self):
        if self.age > MAX_BULLET_AGE:
           return False
        else:
           return True

class SpaceShip(object):
    def __init__(self, position, rotation, speed, size_major, size_minor):
        self.position = position
        self.rotation = rotation # degrees
        self.velocity = Vec2d(speed,0).rotated(rotation)
        self.size_major = size_major 
        self.size_minor = size_minor

    def draw(self, windowSurface):
        points = ship_points(self.position, self.size_major, self.size_minor, self.rotation) 
        pygame.draw.polygon(windowSurface, BLUE, points)

    def move(self):
        self.position = self.position + self.velocity
        if self.position.x >= MAX_X:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = MAX_X - 1
        if self.position.y >= MAX_Y:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = MAX_Y - 1

    def turn_left(self, angle):
        self.rotation -= angle

    def turn_right(self, angle):
        self.rotation += angle

    def accelerate(self, amount):
        self.velocity += Vec2d(1,0).rotated(self.rotation) * amount
        # limit the maximum speed of the ship
        speed = self.velocity.length
        if speed > MAX_SHIP_SPEED:
            scale = float(MAX_SHIP_SPEED) / speed
            self.velocity *= scale


def ship_points(position, size_major, size_minor, rotation):
    p1 = position + Vec2d(size_major, 0).rotated(rotation)
    p2 = position + Vec2d(size_minor, 0).rotated(rotation + 120)
    p3 = position + Vec2d(size_minor, 0).rotated(rotation + 240)
    return ((p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y))


def bullet_hit_rock(bullet, rock):
    end_pos = bullet.position + bullet.direction * BULLET_LENGTH
    return inside_circle(end_pos, Vec2d(rock.position), rock.radius)


def ship_hit_rock(ship, rock):
    points = ship_points(ship.position, ship.size_major, ship.size_minor, ship.rotation) 
    rock_vec = Vec2d(rock.position)
    for p in points:
        if inside_circle(Vec2d(p), rock_vec, rock.radius):
            return True
    return False
    

def inside_circle(point, center, radius):
    return point.get_distance(center) <= radius


def terminate():
    pygame.quit()
    sys.exit()


def spawn_init_rocks(num_rocks):
    rocks = []

    # initialise rocks off to the negative X side of the window
    for _count in range(0, num_rocks/2):
        rock_radius = choice(ROCK_RADIUSES)
        rock_position = Vec2d(-rock_radius / 2, randint(0, MAX_Y-1))
        rock_velocity = Vec2d(1, 0).rotated(randint(0, 359)) * randint(MIN_ROCK_SPEED, MAX_ROCK_SPEED)
        rocks.append(Rock(rock_position, rock_velocity, rock_radius, random_colour()))

    # initialise rocks off to the negative Y side of the window
    for _count in range(num_rocks/2, num_rocks):
        rock_radius = choice(ROCK_RADIUSES)
        rock_position = Vec2d(randint(0, MAX_X-1), -rock_radius / 2)
        rock_velocity = Vec2d(1, 0).rotated(randint(0, 359)) * randint(MIN_ROCK_SPEED, MAX_ROCK_SPEED)
        rocks.append(Rock(rock_position, rock_velocity, rock_radius, random_colour()))

    return rocks

def spawn_rocks_explosion(exploding_rock):
    rocks = []
    num_new_rocks = randint(2, 3)
    while len(rocks) < num_new_rocks:
        rock_position = exploding_rock.position
        rock_radius = choice(range(MIN_ROCK_RADIUS, exploding_rock.radius, ROCK_RADIUS_SIZE_STEP))
        rock_velocity = Vec2d(1, 0).rotated(randint(0, 359)) * randint(MIN_ROCK_SPEED, MAX_ROCK_SPEED)
        rocks.append(Rock(rock_position, rock_velocity, rock_radius, exploding_rock.colour))
    return rocks


def press_return_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing escape quits
                    terminate()
                elif event.key == K_RETURN:
                    return


def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, WHITE)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def start_screen(window_surface, message1, message2):
    font = pygame.font.SysFont(None, 48)
    window_surface.fill(BLACK)
    drawText(message1, font, window_surface, (MAX_X / 4), (MAX_Y / 3))

    font = pygame.font.SysFont(None, 30)
    drawText(message2, font, window_surface, (MAX_X / 4), (MAX_Y / 3) + 100)
    drawText('press escape key to quit', font, window_surface, (MAX_X / 4), (MAX_Y / 3) + 130)
    pygame.display.update()
    press_return_key()


def show_score(window_surface, score, high_score):
    font = pygame.font.SysFont(None, 30)
    drawText("HIGH:  " + str(high_score), font, window_surface, 10, 10)
    drawText("SCORE: " + str(score), font, window_surface, 10, 40)

def score_hit(radius):
    return (MAX_ROCK_RADIUS * 2) - radius


def game_loop(window_surface):

    score = 0
    high_score = get_high_score()
    clock = pygame.time.Clock()
    initial_rotation = randint(0, 359)
    ship = SpaceShip(Vec2d(START_X, START_Y), rotation=initial_rotation, speed=1, size_major=20, size_minor=10) 
    bullets = []
    rocks = []

    while True:
        window_surface.fill(BLACK)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_LEFT]:
            ship.turn_left(10)
        if key_pressed[K_RIGHT]:
            ship.turn_right(10)
        if key_pressed[K_UP]: 
            ship.accelerate(1)
        if key_pressed[K_SPACE]:
            # XXX maybe we should have a timer on the gun to limit
            # the rate at which bullets can be fired?
            if len(bullets) < MAX_BULLETS:
                direction = Vec2d(1, 0).rotated(ship.rotation)
                bullets.append(Bullet(ship.position, direction))

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()


        if len(rocks) < MIN_NUM_ROCKS:
            rocks.extend(spawn_init_rocks(MIN_NUM_ROCKS - len(rocks))) 

        alive_bullets = []
        spawned_rocks = []

        for b in bullets:
            b.time_step()
            if b.alive():
                b.move()
                alive_rocks = []
                hit = False
                for r in rocks:
                    if not hit and bullet_hit_rock(b, r):
                        score += score_hit(r.radius)
                        hit = True
                        if r.radius > MIN_ROCK_RADIUS:
                            spawned_rocks.extend(spawn_rocks_explosion(r))
                    else:
                        alive_rocks.append(r)
                if not hit:
                    b.draw(window_surface)
                    alive_bullets.append(b)
                rocks = alive_rocks

        rocks.extend(spawned_rocks)
        bullets = alive_bullets

        for r in rocks:
            r.move()
            if ship_hit_rock(ship, r):
                if score > high_score:
                    save_high_score(score)
                return
            r.draw(window_surface)

        ship.move()
        ship.draw(window_surface)

        show_score(window_surface, score, high_score)

        pygame.display.update()
        clock.tick(FPS)


def get_high_score():
    score = 0
    try:
        with open('asteroids_high_score.txt') as file:
            score = int(next(file))
    except:
        pass
    finally:
        return score

def save_high_score(score):
    try:
        with open('asteroids_high_score.txt', 'w') as file:
            file.write(str(score) + '\n')
    except:
        pass

def main():
    pygame.init()
    window_surface = pygame.display.set_mode((MAX_X, MAX_Y), 0, 32)
    pygame.display.set_caption('asteroids')

    start_screen(window_surface, 'ASTEROIDS', 'press return key to start')

    while True:
        game_loop(window_surface)
        start_screen(window_surface, 'GAME OVER', 'press return key to continue')
 

if __name__     == '__main__':
    main()
