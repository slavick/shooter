#!/usr/bin/env python

import random


class FloaterMovement():
    UP, DOWN, LEFT, RIGHT = range(4)

    def __init__(self, speed=-1, direction=-1):
        self.speed = speed
        if speed == -1:
            self.speed = random.randint(1, 6)
        
        self.direction = direction
        if self.direction == -1:
            self.direction = random.randint(0, 3)

    def move(self, world_size, rect, ship_position):
        if self.direction == FloaterMovement.RIGHT:
            rect.left += self.speed
        elif self.direction == FloaterMovement.LEFT:
            rect.left -= self.speed
        elif self.direction == FloaterMovement.DOWN:
            rect.top += self.speed
        elif self.direction == FloaterMovement.UP:
            rect.top -= self.speed
        
        if rect.right >= world_size.right:
            rect.right = world_size.right
            self.direction = FloaterMovement.LEFT
        if rect.left < world_size.left:
            rect.left = world_size.left
            self.direction = FloaterMovement.RIGHT
        if rect.bottom >= world_size.bottom:
            rect.bottom = world_size.bottom
            self.direction = FloaterMovement.UP
        if rect.top < world_size.top:
            rect.top = world_size.top
            self.direction = FloaterMovement.DOWN


class FollowerMovement():
    def __init__(self, speed=-1):
        self.speed = speed
        if speed == -1:
            self.speed = random.randint(1, 6)

    def move(self, world_size, rect, ship_position):
        x_diff, y_diff = rect.centerx - ship_position[0], rect.centery - ship_position[1]
        
        if x_diff > 0:
            rect.left -= self.speed
        elif x_diff < 0:
            rect.left += self.speed
        
        if y_diff > 0:
            rect.top -= self.speed
        elif y_diff < 0:
            rect.top += self.speed