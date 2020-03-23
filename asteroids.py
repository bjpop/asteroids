'''
Asteroids game.

A simple arcade-style computer game. Fly a space ship through an asteroid
field of circular rocks. If the ship crashes into an asteroid your character
dies.

The ship can fire bullets and shoot the rocks. Large rocks break up into
smaller ones if they are hit by bullets. The smallest size rocks
disappear when hit by bullets.

Points are scored when the ship shoots a rock. Smaller rocks score more points
than larger rocks.

The ship can turn through 360 degrees on the spot. It can also accelerate
in the forwards direction.

If anything travels off the edge of the screen then it reappers on the opposite
side, maintaining its velocity.

If the number of rocks on the screen falls before some threshold value then
new rocks are spawned off screen.

The game relies on the pygame library to draw graphics and handle player input.

The game high score is kept in a text file called asteroids_high_score.txt.

To quit the game press the escape key, or close the game window.

Author: Bernie Pope (bjpope@unimelb.edu.au)

Revision history:

    Feb 2014: Initial working version.
    Sep 2014: Added documentation.

Desirable things to add in future versions

    - Sound effects.
    - Pretty graphics for the sprites (replace the geometric graphics).
    - Explosion effects.
    - More interesting levels.
    - Alien ships.
    - Multi-player mode.
    - Rocks to collide and bounce off each other.
    - Rock explosions to conserve momentum of exploded rock.

Future code improvements:

    - Refactor the game_loop function. It is far too complex.
    - Package up the game state into an object.
'''

import pygame
import sys
from pygame.math import Vector2
from pygame.locals import (QUIT, KEYDOWN, K_RETURN,
   K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_ESCAPE)
from random import choice, randint 

# Maximum X (horizontal) coordinate.
MAX_X = 800
# Maximum Y (vertical) coordinate.
MAX_Y = 600
# Initial X coordinate of the ship.
START_X = MAX_X / 2
# Initial Y coordinate of the ship.
START_Y = MAX_Y / 2
# Black colour in RGB.
BLACK = (0, 0, 0)
# White colour in RGB.
WHITE = (255, 255, 255)
# Red colour in RGB.
RED = (255, 0, 0)
# Green colour in RGB.
GREEN = (0, 255, 0)
# Blue colour in RGB.
BLUE = (0, 0, 255)
# Maximum speed of the ship.
MAX_SHIP_SPEED = 10
# Frames per second refresh rate for the game.
FPS = 40 
# Speed of ship bullets.
BULLET_SPEED = 15 
# Length of bullet sprite.
BULLET_LENGTH = 10 
# Width of bullet sprite.
BULLET_WIDTH = 2
# Maximum time a bullet may stay alive.
MAX_BULLET_AGE = 15 
# Minimum rock radius.
MIN_ROCK_RADIUS = 20
# Maximum rock radius.
MAX_ROCK_RADIUS = 80
# Difference in radius for each rock size.
ROCK_RADIUS_SIZE_STEP = 10
# Minimum speed of a rock.
MIN_ROCK_SPEED = 1
# Maximum speed of a rock.
MAX_ROCK_SPEED = 4
# Minimum number of rocks on the screen before we spawn more.
MIN_NUM_ROCKS = 5
# Maximum number of bullets which can be alive at any time.
# This puts a limit on how many rocks the ship can shoot
# at once.
MAX_BULLETS = 2 
# Minimum number of new rocks spawned when a rock explodes.
MIN_SPAWN_EXPLODE_ROCKS = 2
# Maximum number of new rocks spawned when a rock explodes.
MAX_SPAWN_EXPLODE_ROCKS = 3
# Size of large font for message screen.
LARGE_FONT_SIZE = 48
# Size of small font for message screen.
SMALL_FONT_SIZE = 32
# Size of the font to display the game score.
SCORE_FONT = 30
# Angle to rotate the ship if the player presses left or right arrow.
ROTATE_ANGLE = 10
# Name of the text file containing the high score.
HIGH_SCORE_FILE = 'asteroids_high_score.txt'


class GameObject(object):
    '''A GameObject. This is the base type of all objects in the game.
    All game objects have a position and a velocity, and they can
    move about the screen. When game objects reach the edge of the
    screen they move to the opposite site, preserving all their
    other state.
    '''
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def move(self):
        '''Update the current position of the object based on its
        old position and its velocity. If the object crosses the edge of
        the screen it will move to the opposite side.
        '''
        self.position = self.position + self.velocity
        if self.position.x >= MAX_X:
            # Object crossed the right side of screen.
            self.position.x = 0
        elif self.position.x < 0:
            # Object crossed the left side of screen.
            self.position.x = MAX_X - 1
        if self.position.y >= MAX_Y:
            # Object crossed the bottom side of screen.
            self.position.y = 0
        elif self.position.y < 0:
            # Object crossed the top side of screen.
            self.position.y = MAX_Y - 1


class Rock(GameObject):
    '''A rock object. Rocks are drawn as circles. The size of
    a rock is given by its radius.

    Rocks have the following state:
       - position of rock center (a vector Vector2)
       - velocity (a vector Vector2)
       - radius (an integer)
       - colour (R, G, B)

    Rocks keep moving with the same velocity (direction and
    speed) indefinitely.
    '''

    def __init__(self, position, velocity, radius, colour):
        super(Rock, self).__init__(position, velocity)
        self.radius = radius
        self.colour = colour 


    def draw(self, windowSurface):
        '''Draw the rock at its current position on the supplied
        windowSurface.'''
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(windowSurface, self.colour, center, self.radius)


class Bullet(GameObject):
    '''A bullet object. Bullets are drawn as short lines.

    Bullets have the following state:
       - position of bullet start point (a vector Vector2)
       - direction that the bullet is travelling 
         (a normalised vector Vector2)
       - velocity (a vector Vector2)
       - age (an integer)

    Bullets keep moving with the same velocity (direction and
    speed) while they are alive.
    '''
    def __init__(self, position, direction):
        norm_direction = direction.normalize()
        velocity = norm_direction * BULLET_SPEED
        super(Bullet, self).__init__(position, velocity)
        self.direction = norm_direction
        self.age = 0


    def draw(self, windowSurface):
        '''Draw a bullet at its current position on the supplied
        windowSurface. Bullets are drawn as line segments.
        The start of the line is the current position of the bullet.
        The end of the line is BULLET_LENGTH units away in the
        the direction that the bullet is travelling.
        '''
        start_pos = (self.position.x, self.position.y)
        end_pos_vec = self.position + self.direction * BULLET_LENGTH
        end_pos = (end_pos_vec.x, end_pos_vec.y) 
        pygame.draw.line(windowSurface, RED, start_pos, end_pos, BULLET_WIDTH)


    def time_step(self):
        '''Increment the age of the bullet by one.'''
        self.age += 1


    def alive(self):
        '''A bullet is alive if its age is less than the
        constant MAX_BULLET_AGE. This method returns True
        if the bullet is currently alive and False
        otherwise.'''
        if self.age > MAX_BULLET_AGE:
           return False
        else:
           return True


class SpaceShip(GameObject):
    '''A space ship object. Space ships are drawn as triangles.

    Presently there is only one space ship alive at any one time.

    The space ship is controlled by the player of the game.

    Space ships have the following state:
       - position of centre (a vector Vector2)
       - rotation (angle in degrees)
       - velocity (a vector Vector2)
       - size of major axis
       - size of minor axis

           ##       m 
          ####      i  a
         ######     n  x
        ########    o  i
       ##########   r  s

       major axis

    Space ships can rotate on the spot. Their angle of rotation
    affects their velocity if they try to accelerate. Zero degrees is
    facing upwards.
    '''
    def __init__(self, position, rotation, speed, size_major, size_minor):
        velocity = Vector2(speed,0).rotate(rotation)
        super(SpaceShip, self).__init__(position, velocity)
        self.rotation = rotation # degrees
        self.size_major = size_major 
        self.size_minor = size_minor


    def draw(self, windowSurface):
        '''Draw a space ship at its current position on the supplied
        windowSurface. Space ships are drawn as triangles.
        '''
        # Draw the triangle on the display.
        pygame.draw.polygon(windowSurface, BLUE, self.points())


    def turn_left(self, angle):
        '''Turn the space ship left by some angle.'''
        self.rotation -= angle


    def turn_right(self, angle):
        '''Turn the space ship right by some angle.'''
        self.rotation += angle


    def accelerate(self, amount):
        '''Accerlate the velocity of the space ship by
        some amount. Ships have a maximum speed which
        cannot be exceeded.'''

        # Compute a vector of acceleration in the direction
        # that the ship is currently facing.
        accel_vector = Vector2(1,0).rotate(self.rotation) * amount

        # The new velocity is equal to the current velocity plus
        # the acceleration vector.
        new_velocity = self.velocity + accel_vector

        # Compute the speed of the new_velocity.
        speed = self.velocity.length()

        # Limit the maximum speed of the ship.
        if speed > MAX_SHIP_SPEED:
            scale = float(MAX_SHIP_SPEED) / speed
            new_velocity *= scale

        self.velocity = new_velocity


    def points(self):
        '''Compute the coordinates of the three points on the triangle
        which defines the sprite for the ship.'''
        position = self.position
        size_major = self.size_major
        size_minor = self.size_minor
        rotation = self.rotation
        p1 = position + Vector2(size_major, 0).rotate(rotation)
        p2 = position + Vector2(size_minor, 0).rotate(rotation + 120)
        p3 = position + Vector2(size_minor, 0).rotate(rotation + 240)
        return ((p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y))


def bullet_hit_rock(bullet, rock):
    '''Test for a collision between a bullet and a rock.
    Returns True if they collide and False otherwise.
    A bullet has hit a rock if its end position (the front of
    the bullet) is inside the circle defined for the rock.'''
    end_pos = bullet.position + bullet.direction * BULLET_LENGTH
    return is_inside_circle(end_pos, Vector2(rock.position), rock.radius)


def ship_hit_rock(ship, rock):
    '''Test for a collision between a space ship and a rock.
    Returns True if they collide and False otherwise.
    A space ship has hit a rock if any of the three corner
    vertices of the space ship triangle are inside the circle
    defined for the rock.'''
    rock_vec = Vector2(rock.position)
    for point in ship.points():
        if is_inside_circle(Vector2(point), rock_vec, rock.radius):
            return True
    return False
    

def is_inside_circle(point, center, radius):
    '''Test if a point is inside a circle.'''
    #return point.get_distance(center) <= radius
    return point.distance_to(center) <= radius


def random_colour():
    '''Generate a random RGB colour which is not too dark.
    The range of intensity values of each colour channel are fairly
    arbitrary. The colours are used for newly spawned rocks, so
    all we care about is whether they look reasonbly good.
    '''
    return (randint(100, 255), randint(50, 150), randint(50, 100))


def spawn_rock(position, min_radius, max_radius):
    '''Spawn a new rock at a specified position
    with a radius randomly chosen between min_radius
    and max_radius.
    The rock will be given a random velocity and a
    random colour.
    '''
    # Choose the radius of the new rock.
    radius = choice(range(min_radius, max_radius, ROCK_RADIUS_SIZE_STEP))
    # Compute a random velocity for the rock.
    angle = randint(0, 359)
    direction_vector = Vector2(1, 0).rotate(angle)
    speed = randint(MIN_ROCK_SPEED, MAX_ROCK_SPEED)
    velocity = direction_vector * speed
    # Choose a random colour for the rock.
    colour = random_colour() 
    return Rock(position, velocity, radius, colour)


def spawn_offscreen_rocks(num_rocks):
    '''Spawn rocks which start life outside the screen.
    Sometimes we want to spawn new rocks that will start outside the
    bounds of the screen, and eventually move into the bounds.
    The reason to do this is to avoid spawning new rocks that might
    immediately hit the ship, or that might be very close to the ship
    and cause a collision. Therefore we start them outside the bounds
    of the screen, and let them eventually drift into the screen. 

    Half of the new rocks start on the side of the screen. The other
    half start on the top of the screen. 

    New rocks are given a random size, random position, random
    velocity and random colour.
    '''
    rocks = []
    # initialise rocks off to the negative X side of the window
    x_pos = -MAX_ROCK_RADIUS / 2
    for _count in range(0, num_rocks // 2):
        # The Y position is randomly chosen from the screen Y coordinates.
        y_pos = randint(0, MAX_Y - 1)
        position = Vector2(x_pos, y_pos)
        new_rock = spawn_rock(position, MIN_ROCK_RADIUS, MAX_ROCK_RADIUS)
        rocks.append(new_rock)

    # initialise rocks off to the negative Y side of the window
    y_pos = -MAX_ROCK_RADIUS / 2
    for _count in range(num_rocks // 2, num_rocks):
        # The X position is randomly chosen from the screen X coordinates.
        x_pos = randint(0, MAX_X - 1) 
        position = Vector2(x_pos, y_pos)
        new_rock = spawn_rock(position, MIN_ROCK_RADIUS, MAX_ROCK_RADIUS)
        rocks.append(new_rock)
    return rocks


def spawn_rocks_explosion(exploding_rock):
    '''Spawn new rocks at the point where a rock explodes from being
    hit by a bullet. A small random number of new rocks are created
    which are no larger than the exploded rock.
    '''
    # Choose a small random number of new rocks to create.
    num_new_rocks = randint(MIN_SPAWN_EXPLODE_ROCKS, MAX_SPAWN_EXPLODE_ROCKS)
    rocks = []
    # The spawned rocks are created in the same place where the exploded
    # rock was.
    position = exploding_rock.position
    max_radius = exploding_rock.radius
    for _count in range(num_new_rocks):
        new_rock = spawn_rock(position, MIN_ROCK_RADIUS, max_radius)
        rocks.append(new_rock)
    return rocks


def press_return_or_escape():
    '''Wait for the player to press the return key to start
    the game, or to press the escape key to quit. Also
    terminate the game if the QUIT event occurs.'''
    while True:
        for event in pygame.event.get():
            # QUIT event terminates the game.
            # The QUIT event occurs if the player closes
            # the game window.
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                # Escape key quits the game.
                if event.key == K_ESCAPE:
                    terminate()
                # Return key allows game to start.
                elif event.key == K_RETURN:
                    return


def drawText(text, font, window_surface, x, y):
    '''Write some white text in a given font on the given
    surface at X and Y coordinates.'''
    textobj = font.render(text, 1, WHITE)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    window_surface.blit(textobj, textrect)


def info_screen(window_surface, message1, message2):
    '''Display an information screen for the game.
    Two message strings can be provided.
    The first message is displayed in a larger font size
    nearer the top of the screen and the second message is displayed
    in a smaller font size nearer the middle of the screen.
    The screen also displays text indicating how to quit
    the game just below the second message.
    Once the messages have been displayed this function
    will wait for the player to press Return to play
    the game or Escape to quit.
    '''
    # Display the first message in large font near the
    # top of the screen.
    font = pygame.font.SysFont(None, LARGE_FONT_SIZE)
    window_surface.fill(BLACK)
    drawText(message1, font, window_surface, MAX_X / 4, MAX_Y / 3)
    # Display the second message in a smaller font near
    # the middle of the screen.
    font = pygame.font.SysFont(None, SMALL_FONT_SIZE)
    drawText(message2, font, window_surface, MAX_X / 4, MAX_Y / 3 + 100)
    # Display the how-to-quit message below the second message.
    drawText('press escape key to quit', font, window_surface,
        MAX_X / 4, MAX_Y / 3 + 130)
    pygame.display.update()
    # Wait for the player to press a key.
    press_return_or_escape()


def show_score(window_surface, score, high_score):
    '''Show the game current score and high score
    near the top left corner of the screen.'''
    font = pygame.font.SysFont(None, SCORE_FONT)
    drawText("HIGH:  " + str(high_score), font, window_surface, 10, 10)
    drawText("SCORE: " + str(score), font, window_surface, 10, 40)


def score_hit(radius):
    '''Compute the score for a bullet hitting a rock.
    Smaller rocks are harder to hit, so they get a higher score.'''
    return (MAX_ROCK_RADIUS * 2) - radius


# XXX This should be decomposed into smaller functions.
# XXX Might be good to package up game state into an object.
def game_loop(window_surface, high_score):
    '''Play the game until the player quits or they ship
    crashes into a rock. This function loops over 
    game events and updates the state of the game.'''
    score = 0
    # Start the game clock.
    clock = pygame.time.Clock()
    # Choose an initial rotation for the ship.
    initial_rotation = randint(0, 359)
    ship_position = Vector2(START_X, START_Y)
    # Initialise the ship
    ship = SpaceShip(ship_position, rotation=initial_rotation,
        speed=1, size_major=20, size_minor=10) 
    # Initialise the alive bullets.
    bullets = []
    # Initialise the alive rocks.
    rocks = []

    # Loop indefinitely, handling game events.
    while True:

        # Draw the background of the screen as black.
        window_surface.fill(BLACK)

        # Check if the player pressed a key.
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_LEFT]:
            # Left arrow was pressed.
            # Roate the ship left.
            ship.turn_left(ROTATE_ANGLE)
        if key_pressed[K_RIGHT]:
            # Right arrow was pressed.
            # Rotate the ship right.
            ship.turn_right(ROTATE_ANGLE)
        if key_pressed[K_UP]: 
            # Up arrow was pressed.
            # Accelerate the ship by one unit.
            ship.accelerate(1)
        if key_pressed[K_SPACE]:
            # Space bar was pressed.
            # If there are fewer than MAX_BULLETS alive
            # then fire a bullet in the direction that
            # the ship is facing.
            if len(bullets) < MAX_BULLETS:
                # Choose the bullet direction to be the same
                # as the direction of the ship.
                direction = Vector2(1, 0).rotate(ship.rotation)
                bullets.append(Bullet(ship.position, direction))

        # Check if the player wants to quit the game.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

        # Spawn new rocks off screen if the number of alive rocks
        # is less than the minimum.
        if len(rocks) < MIN_NUM_ROCKS:
            new_rocks = spawn_offscreen_rocks(MIN_NUM_ROCKS - len(rocks)) 
            rocks.extend(new_rocks)

        # The list of bullets which have not hit any rocks
        # in the current time step.
        alive_bullets = []
        # The list of new rocks which have been spawned in
        # the current time step.
        spawned_rocks = []

        # Check if any bullet has hit a rock.
        # Also increment the age of each bullet, and forget
        # about any bullets which have exceeded their age limit.
        for bullet in bullets:
            # Increment the age of the bullet.
            bullet.time_step()
            # Check if the bullet's age is less than the maximum age.
            if bullet.alive():
                # Move the bullet to its new position.
                bullet.move()
                # Keep track of rocks that are not hit by bullets.
                alive_rocks = []
                # This bullet has not hit anything yet.
                hit = False
                # Check if this bullet hits any of the rocks.
                for rock in rocks:
                    # If the bullet has not already hit a rock, check
                    # if it hits this rock.
                    if not hit and bullet_hit_rock(bullet, rock):
                        # Update the score based on the size of the rock.
                        score += score_hit(rock.radius)
                        # This bullet has now hit a rock.
                        hit = True
                        # Possibly spawn new rocks.
                        if rock.radius > MIN_ROCK_RADIUS:
                            spawned_rocks.extend(spawn_rocks_explosion(rock))
                    else:
                        # This rock was not hit by this bullet.
                        alive_rocks.append(rock)
                # Check if this bullet did not hit any rocks at all.
                if not hit:
                    # Draw the bullet at its new position.
                    bullet.draw(window_surface)
                    # Keep this bullet alive for the future.
                    alive_bullets.append(bullet)
                # Reset rocks list to be all the alive rocks.
                rocks = alive_rocks

        # Add all newly spawned rocks to the list of alive rocks.
        rocks.extend(spawned_rocks)
        # Reset bullets to the currently alive bullets.
        bullets = alive_bullets

        # Move all of the rocks and check whether any of them collide
        # with the ship.
        for rock in rocks:
            # Move this rock to its new position.
            rock.move()
            # Check for a collision with the ship.
            if ship_hit_rock(ship, rock):
                return score
            # Draw the rock on the screen at its new position.
            rock.draw(window_surface)

        # Move the ship to its new position.
        ship.move()
        # Draw the ship on the screen at its new position.
        ship.draw(window_surface)

        # Show the score and high score on the screen.
        show_score(window_surface, score, high_score)

        # Redraw the screen.
        pygame.display.update()
        clock.tick(FPS)


def get_high_score():
    '''Try to read the high score from file.
    If the file does not exist or cannot be read
    then set the high score to 0.'''
    score = 0
    try:
        with open(HIGH_SCORE_FILE) as file:
            score = int(next(file))
    except:
        # Something bad happened when we tried to read
        # the high score file. We ignore it and
        # return the default high score.
        pass
    finally:
        return score


def save_high_score(score):
    '''Try to save the high score to file.'''
    try:
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(str(score) + '\n')
    except:
        # Something bad happened when we tried to save 
        # the high score file. We ignore it. 
        pass


def terminate():
    '''Exit the game.'''
    pygame.quit()
    sys.exit()


def main():
    '''The entry point for the entire game.'''
    # Initialise the pygame system.
    pygame.init()
    # Create a window surface to act as the screen for the game
    window_surface = pygame.display.set_mode((MAX_X, MAX_Y), 0, 32)
    pygame.display.set_caption('asteroids')

    # Try to read the saved game high score from file.
    high_score = get_high_score()

    # Show the start game info screen.
    # Wait for the player to press a key. 
    info_screen(window_surface, 'ASTEROIDS', 'press return key to start')

    # Keep playing the game until the player quits.
    while True:
        # Run the game loop.
        new_score = game_loop(window_surface, high_score)
        # Possibly update save high score.
        if new_score > high_score:
            high_score = new_score
            save_high_score(high_score)
        # Show the resume game info screen.
        # Wait for the player to press a key.
        info_screen(window_surface, 'GAME OVER',
            'press return key to continue')


if __name__ == '__main__':
    main()
