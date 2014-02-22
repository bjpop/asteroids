#!/opt/local/bin/python2.7

import pygame
import sys
from vector2D import Vec2d
from pygame.locals import (QUIT, KEYDOWN,
   K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_ESCAPE)
from random import randint

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
BULLET_SPEED = 30
BULLET_LENGTH = 10 
BULLET_WIDTH = 2
MAX_BULLET_AGE = 30
MIN_ROCK_RADIUS = 10 
MAX_ROCK_RADIUS = 50
MIN_ROCK_SPEED = 1
MAX_ROCK_SPEED = 3
MAX_ROCKS = 5

class Rock(object):
    def __init__(self, position, velocity, radius):
        self.position = position
        self.velocity = velocity
        self.radius = radius

    def draw(self, windowSurface):
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(windowSurface, WHITE, center, self.radius)

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

    def grow_older(self):
        self.age += 1

    def alive(self):
        if self.age > MAX_BULLET_AGE:
           return False
        else:
           return True

class SpaceShip(object):
    def __init__(self, position, rotation, size_major, size_minor):
        self.position = position
        self.rotation = rotation # degrees
        self.velocity = Vec2d(0,0)
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


def terminate():
    pygame.quit()
    sys.exit()


def spawn_rocks():
    rocks = []
    while len(rocks) < MAX_ROCKS:
        rock_position = Vec2d(randint(0, MAX_X-1), randint(0, MAX_Y-1))
        rock_radius = randint(MIN_ROCK_RADIUS, MAX_ROCK_RADIUS)
        rock_velocity = Vec2d(1, 0).rotated(randint(0, 359)) * randint(MIN_ROCK_SPEED, MAX_ROCK_SPEED)
        rocks.append(Rock(rock_position, rock_velocity, rock_radius))
    return rocks

def main():
    pygame.init()
    clock = pygame.time.Clock()
    ship = SpaceShip(Vec2d(START_X, START_Y), rotation=0, size_major=20, size_minor=10) 
    window_surface = pygame.display.set_mode((MAX_X, MAX_Y), 0, 32)
    pygame.key.set_repeat(50, 50)
    bullets = []
    rocks = spawn_rocks()

    while True:
        window_surface.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_LEFT:
                    ship.turn_left(10)
                if event.key == K_RIGHT:
                    ship.turn_right(10)
                if event.key == K_UP: 
                    ship.accelerate(1)
                if event.key == K_SPACE:
                    direction = Vec2d(1, 0).rotated(ship.rotation)
                    bullets.append(Bullet(ship.position, direction))


        alive_bullets = []
        for b in bullets:
            b.grow_older()
            b.move()
            b.draw(window_surface)
            if b.alive():
                alive_bullets.append(b)
        bullets = alive_bullets

        for r in rocks:
            r.move()
            r.draw(window_surface)

        ship.move()
        ship.draw(window_surface)

        pygame.display.update()
        clock.tick(FPS)

if __name__     == '__main__':
    main()
