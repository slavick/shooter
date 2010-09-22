#!/usr/bin/env python

from EnemyMovement import *
import Ships
from Shooter import *
import pygame
from pygame.locals import *
import random

SPAWN_ENEMY_TIMER_EVENT = USEREVENT + 2

def set_timer(event, interval):
    pygame.time.set_timer(event, interval)

def start_spawn_enemy_timer(interval):
    set_timer(SPAWN_ENEMY_TIMER_EVENT, interval)
    
def stop_spawn_enemy_timer():
    set_timer(SPAWN_ENEMY_TIMER_EVENT, 0)
    

class StrategyChooser():
    def __init__(self, world_size):
        random.seed()
        
        self.world_size = world_size
        
        self.strategy = TrickleStrategy(self.world_size)
        self.run()

    def run(self):
        start_spawn_enemy_timer(self.strategy.interval)

    def end(self):
        stop_spawn_enemy_timer()

    def choose_strategy(self):
        self.end()
            
        value = random.randint(0, 2)
        if value == 0:
            self.strategy = TrickleStrategy(self.world_size)
        elif value == 1:
            self.strategy = CornerStrategy(self.world_size)
        elif value == 2:
            self.strategy = WallStrategy(self.world_size)

        self.run()

    def spawn_enemy(self, ship_position):
        return self.strategy.spawn_enemy(ship_position)

    def num_enemies_to_kill(self):
        return self.strategy.num_enemies_to_kill()


class TrickleStrategy():
    def __init__(self, world_size):
        self.interval = 200
        self.world_size = world_size
        
    def spawn_enemy(self, ship_position):
        world_size = self.world_size
    
        value = random.randint(0, 2)
        if value == 0 or value == 1:
            floater = Ships.FloaterEnemy(ship_position=ship_position)
            if floater.rect.left == world_size.left or floater.rect.right == world_size.right:
                floater.set_direction(FloaterMovement.LEFT)
            elif floater.rect.top == world_size.top or floater.rect.bottom == world_size.bottom:
                floater.set_direction(FloaterMovement.UP)
            return floater
        elif value == 2:
            return Ships.SplitterEnemy(ship_position=ship_position)
    
    def num_enemies_to_kill(self):
        return 200
        
    def get_name(self):
        return "TrickleStrategy"


class CornerStrategy():
    def __init__(self, world_size):
        self.interval = 100
        self.world_size = world_size
    
    def spawn_enemy(self, ship_position):
        world_size = self.world_size
    
        group = pygame.sprite.Group()
        group.add(Ships.FollowerEnemy(25, 25))
        group.add(Ships.FollowerEnemy(world_size.width - 25, 25))
        group.add(Ships.FollowerEnemy(25, world_size.height - 25))
        group.add(Ships.FollowerEnemy(world_size.width - 25, world_size.height - 25))
        return group

    def num_enemies_to_kill(self):
        return 500

    def get_name(self):
        return "CornerStrategy"


class WallStrategy():
    def __init__(self, world_size):
        self.interval = 100
        self.world_size = world_size
        
        self.enemy_rect = Ships.FloaterEnemy().rect

    def spawn_enemy(self, ship_position):
        world_size = self.world_size
    
        stop_spawn_enemy_timer()
        start_spawn_enemy_timer(4000)
        
        group = pygame.sprite.Group()

        for i in xrange(world_size.width / self.enemy_rect.width):
            x = i * self.enemy_rect.width + world_size.left
            group.add(Ships.FloaterEnemy(x, world_size.top, FloaterMovement.DOWN, speed=2))
            group.add(Ships.FloaterEnemy(x, world_size.bottom - self.enemy_rect.height, FloaterMovement.UP, speed=2))
        
        for i in xrange(world_size.height / self.enemy_rect.height):
            y = i * self.enemy_rect.height + world_size.top
            group.add(Ships.FloaterEnemy(world_size.left, y, FloaterMovement.RIGHT, speed=3))
            group.add(Ships.FloaterEnemy(world_size.right - self.enemy_rect.width, y, FloaterMovement.LEFT, speed=3))

        return group

    def num_enemies_to_kill(self):
        return ((int(self.world_size.width / self.enemy_rect.width) + int(self.world_size.height / self.enemy_rect.height)))

    def get_name(self):
        return "WallStrategy"