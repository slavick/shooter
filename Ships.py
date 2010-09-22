#!/usr/bin/env python

from EnemyMovement import *
import math
from Shooter import *
import spritesheet
from pygame import Rect
import random

SHIP_IMAGE = "sprites/ship.png"
BULLET_IMAGE = "sprites/bullet.png"
FLOATER_ENEMY_IMAGE = "sprites/floater.png"
SPLITTER_ENEMY_IMAGE = "sprites/splitter.png"
FOLLOWER_ENEMY_IMAGE = "sprites/follower.png"

EXPLODE1 = ("sprites/explode1.png", (0, 0, 23, 23), 8)
EXPLODE2 = ("sprites/explode2.png", (0, 0, 48, 48), 7)


def load_sprite_strip(params):
    return spritesheet.spritesheet(params[0]).load_strip(params[1], params[2])


class Ship(pygame.sprite.Sprite):
    sprite_image = None
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        if not Ship.sprite_image:
            Ship.sprite_image = pygame.image.load(SHIP_IMAGE)
        self.image = Ship.sprite_image
        
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect = self.rect.inflate(-self.rect.width / 6, -self.rect.height / 6)

        self.next_update_time = 0
        
        self.step = 4
        
        self.spawning = True
        self.spawn_stage = 0
        
    def update(self, current_time, x_axis, y_axis):
        if self.next_update_time < current_time:
            rect = self.rect
            
            if x_axis < -JOYSTICK_SENSITIVITY:
                rect.left -= self.step
            elif x_axis > JOYSTICK_SENSITIVITY:
                rect.left += self.step
                
            if y_axis < -JOYSTICK_SENSITIVITY:
                rect.top -= self.step
            elif y_axis > JOYSTICK_SENSITIVITY:
                rect.top += self.step
            
            if rect.left < WALL_WIDTH:
                rect.left = WALL_WIDTH
            elif rect.right >= WIDTH:
                rect.right = WIDTH - WALL_WIDTH
            
            if rect.top < WALL_WIDTH:
                rect.top = WALL_WIDTH
            elif rect.bottom >= HEIGHT:
                rect.bottom = HEIGHT
            
            self.next_update_time = current_time + 10
            
            if self.spawning:
                self.image = Ship.sprite_image
                if self.spawn_stage < 200:
                    if self.spawn_stage % 5 == 0:
                        surf = pygame.Surface([self.rect.width, self.rect.height])
                        surf.set_alpha(0)
                        surf.blit(self.image, (0, 0))
                        self.image = surf
                    self.spawn_stage += 1
                else:
                    self.spawning = False


class Bullet(pygame.sprite.Sprite):
    sprite_image = None

    def __init__(self, position, angle):
        pygame.sprite.Sprite.__init__(self)
    
        if not Bullet.sprite_image:
            Bullet.sprite_image = pygame.image.load(BULLET_IMAGE)
        self.image = Bullet.sprite_image
        
        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-12, -12)
        self.rect.center = position
        
        self.angle = angle
        self.step = 16
        
        self.next_update_time = 0
    
    def update(self, current_time):
        if self.next_update_time < current_time:
            self.rect.left += math.cos(self.angle) * self.step
            self.rect.top += math.sin(self.angle) * self.step
            self.next_update_time = current_time + 10


class Enemy(pygame.sprite.Sprite):
    sprite_images = {}
    explosions = {}
    
    def __init__(self, image_to_load, explosion_images, x, y, movement, ship_position):
        pygame.sprite.Sprite.__init__(self)
        
        self.movement = movement
        
        if not image_to_load in self.sprite_images:
            self.sprite_images[image_to_load] = pygame.image.load(image_to_load)
        self.image = self.sprite_images[image_to_load]
        
        if not explosion_images[0] in self.explosions:
            self.explosions[explosion_images[0]] = load_sprite_strip(explosion_images)
        self.exploding_images = self.explosions[explosion_images[0]]
        
        self.exploding_image_index = 0
        self.exploding = False
        
        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-self.rect.width / 6, -self.rect.height / 6)
        self.rect.topleft = (x, y)
        if x == -1 and y == -1:
            value = random.randint(0, 3)
            if value == 0:
                x = WORLD_SIZE.left
                y = random.randint(WORLD_SIZE.top, WORLD_SIZE.bottom - self.rect.height)
            elif value == 1:
                x = random.randint(WORLD_SIZE.left, WORLD_SIZE.right - self.rect.width)
                y = WORLD_SIZE.top
            elif value == 2:
                x = WORLD_SIZE.right - self.rect.width
                y = random.randint(WORLD_SIZE.top, WORLD_SIZE.bottom - self.rect.height)
            elif value == 3:
                x = random.randint(WORLD_SIZE.left, WORLD_SIZE.right - self.rect.width)
                y = WORLD_SIZE.bottom - self.rect.height
            self.rect.topleft = (x, y)

        self.next_update_time = 0

    def update(self, current_time, ship_position):
        if self.next_update_time < current_time:
            if not self.exploding:
                self.next_update_time = current_time + 10
                self.movement.move(WORLD_SIZE, self.rect, ship_position)
            else:
                self.next_update_time = current_time + 40
                if self.exploding_image_index < len(self.exploding_images):
                    previous_center = self.rect.center  
                
                    self.image = self.exploding_images[self.exploding_image_index]
                    self.image.set_colorkey((1, 1, 1))
                    self.rect = self.image.get_rect()
                    self.rect.center = previous_center
                    self.exploding_image_index += 1
                else:
                    self.kill()

    def on_bullet_hit(self):
        self.exploding = True
        return pygame.sprite.Group()


class FloaterEnemy(Enemy):
    def __init__(self, x=-1, y=-1, travel_direction=-1, speed=-1, ship_position=(-1, -1)):
        Enemy.__init__(self, FLOATER_ENEMY_IMAGE, EXPLODE1, x, y, FloaterMovement(speed, travel_direction), ship_position)

    def set_direction(self, direction):
        self.movement = FloaterMovement(self.movement.speed, direction)
    

class FollowerEnemy(Enemy):
    def __init__(self, x=-1, y=-1, ship_position=(-1, -1)):
        Enemy.__init__(self, FOLLOWER_ENEMY_IMAGE, EXPLODE1, x, y, FollowerMovement(1), ship_position)


class SplitterEnemy(Enemy):
    def __init__(self, x=-1, y=-1, ship_position=(-1, -1)):
        Enemy.__init__(self, SPLITTER_ENEMY_IMAGE, EXPLODE2, x, y, FollowerMovement(1), ship_position)
               
    def on_bullet_hit(self):
        group = Enemy.on_bullet_hit(self)
        group.add(FollowerEnemy(self.rect.left - 5, self.rect.top - 5))
        group.add(FollowerEnemy(self.rect.left - 5, self.rect.bottom + 5))
        group.add(FollowerEnemy(self.rect.right + 5, self.rect.top - 5))
        group.add(FollowerEnemy(self.rect.right + 5, self.rect.bottom + 5))
        return group