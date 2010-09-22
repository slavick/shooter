#!/usr/bin/env python

from Ships import *
from Strategies import *
import itertools
import math
import os
import pygame
from pygame import Rect
from pygame.locals import *

WIDTH = 1024
HEIGHT = 768

WALL_WIDTH = 4

WORLD_SIZE = pygame.rect.Rect(WALL_WIDTH, WALL_WIDTH, WIDTH - 2 * WALL_WIDTH, HEIGHT - 2 * WALL_WIDTH)

JOYSTICK_SENSITIVITY = 0.30


def start_game():
    game = Shooter()
    game.MainLoop()


class Shooter:
    def __init__(self, auto=False):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        
        self.using_joystick = False
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.using_joystick = True
        
        random.seed()
        
        self.done = False
        self.game_over = False
        self.paused = False
        self.restart = False
        self.lives = 3
        self.score = 0
        self.enemies_killed = 0
        self.change_strategy_on_enemies_killed = 0
		
        self.ClearAxes()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
        
        pygame.display.set_caption("Shooter")

    def ClearAxes(self):
        self.x_axis, self.y_axis = 0, 0
        
    def DrawCenteredString(self, string):
        (width, height) = self.font.size(string)
        self.DrawStringAtLocation(string, (WORLD_SIZE.centerx - width / 2, WORLD_SIZE.centery - height / 2))
    
    def DrawStringAtLocation(self, string, location):
        self.screen.blit(self.font.render(string, 1, (255, 255, 255)), location)
    
    def CheckForCollisions(self):
        for bullet in self.bullets:
            if bullet.rect.left < WORLD_SIZE.left or bullet.rect.right > WORLD_SIZE.right or bullet.rect.top < WORLD_SIZE.top or bullet.rect.bottom > WORLD_SIZE.bottom:
                bullet.kill()
        
        enemies_killed = list(itertools.chain(*pygame.sprite.groupcollide(self.bullets, self.enemies, True, True).values()))
        self.score += len(enemies_killed)
        self.enemies.add([enemy.on_bullet_hit() for enemy in enemies_killed])
        self.exploding_enemies.add([enemy for enemy in enemies_killed])
        
        self.enemies_killed += len(enemies_killed)
        if self.enemies_killed >= self.change_strategy_on_enemies_killed:
            self.strategy.choose_strategy()
            self.change_strategy_on_enemies_killed += self.strategy.num_enemies_to_kill()
        
        if not self.ship.spawning and pygame.sprite.spritecollideany(self.ship, self.enemies):
            self.lives -= 1
            if self.lives == 0:
                self.game_over = True
            else:
                [enemy.on_bullet_hit() for enemy in self.enemies]
                self.bullets.empty()
                self.ship = Ship()

    def MoveShips(self):
        self.exploding_enemies.update(pygame.time.get_ticks(), self.ship.rect.center)
        self.enemies.update(pygame.time.get_ticks(), self.ship.rect.center)
        self.bullets.update(pygame.time.get_ticks())
        self.ship.update(pygame.time.get_ticks(), self.x_axis, self.y_axis)

        if self.fire_bullet:
            self.bullets.add(Bullet((self.ship.rect.centerx - 4, self.ship.rect.centery - 4), self.fire_bullet_angle))

    def DrawShips(self):
        [self.screen.blit(enemy.image, enemy.rect) for enemy in self.exploding_enemies]
        [self.screen.blit(enemy.image, enemy.rect) for enemy in self.enemies]
        [self.screen.blit(bullet.image, bullet.rect) for bullet in self.bullets]
        self.screen.blit(self.ship.image, self.ship.rect)

    def LoadSprites(self):
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.exploding_enemies = pygame.sprite.Group()
        
        self.walls = [
            (0, 0, WIDTH, WALL_WIDTH), 
            (0, HEIGHT - WALL_WIDTH, WIDTH, WALL_WIDTH), 
            (0, 0, WALL_WIDTH, HEIGHT), 
            (WIDTH - WALL_WIDTH, 0, WALL_WIDTH, HEIGHT)
        ]
        
        self.ship = Ship()
        
        self.strategy = StrategyChooser(WORLD_SIZE)
        self.change_strategy_on_enemies_killed = self.strategy.num_enemies_to_kill()
        
        self.font = pygame.font.Font(None, 72)
        
    def HandleUserInput(self, events):
        if self.using_joystick:
            self.x_axis, self.y_axis, x_fire, y_fire = [self.joystick.get_axis(i) for i in [0, 1, 4, 3]]
            
            self.fire_bullet = math.fabs(x_fire) + math.fabs(y_fire) > 0.5
            self.fire_bullet_angle = math.atan2(y_fire, x_fire)
        else:
            self.ClearAxes()
            
            (x_mouse, y_mouse) = pygame.mouse.get_pos()
            
            x_diff = self.ship.rect.centerx - x_mouse
            y_diff = self.ship.rect.centery - y_mouse
            
            (button_left, button_middle, button_right) = pygame.mouse.get_pressed()
            self.fire_bullet = button_left
            self.fire_bullet_angle = math.atan2(y_diff, x_diff) - math.pi

            if button_right:
                if x_diff < 0:
                    self.x_axis += 1.0
                elif x_diff > 0:
                    self.x_axis -= 1.0
                    
                if y_diff < 0:
                    self.y_axis += 1.0
                elif y_diff > 0:
                    self.y_axis -= 1.0
        
        for event in events:
            if not self.paused and not self.game_over:
                if event.type == SPAWN_ENEMY_TIMER_EVENT:
                    self.enemies.add(self.strategy.spawn_enemy(self.ship.rect.center))
            
            if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.QUIT:
                self.done = True
            elif not self.game_over and ((event.type == KEYDOWN and event.key == K_SPACE) or (event.type == JOYBUTTONDOWN and event.button == 1)):
                self.paused = not self.paused
            elif self.game_over and event.type == KEYDOWN and event.key == K_r:
                self.done = True
                self.restart = True
    
    def MainLoop(self):
        self.LoadSprites()
        
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        [pygame.draw.rect(self.background, (255, 255, 255), wall) for wall in self.walls]
        
        clock = pygame.time.Clock()
        
        while not self.done:
            clock.tick(60)
        
            self.HandleUserInput(pygame.event.get())
            
            self.screen.blit(self.background, (0, 0))

            if not self.paused and not self.game_over:
                self.MoveShips()
                self.CheckForCollisions()
                
            self.DrawShips()
            
            if self.paused:
                self.DrawCenteredString("Paused")
            elif self.game_over:
                self.DrawCenteredString("Game Over (Press R to restart)")

            self.DrawStringAtLocation("Score: %s" % self.score, (10, HEIGHT + 3))
            self.DrawStringAtLocation("Lives: %s" % self.lives, (400, HEIGHT + 3))
    
            pygame.display.update()
        
        if self.restart:
            start_game()
        else:
            pygame.quit()


if __name__ == "__main__":
    start_game()