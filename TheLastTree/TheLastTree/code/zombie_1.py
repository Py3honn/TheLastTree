import pygame
import math

pygame.init()

class Zombie(pygame.sprite.Sprite):
    
    def __init__(self, groups, window_width, window_height, sprite, target):
        super().__init__(groups)
        self.image = sprite 
        self.rect = self.image.get_rect(midbottom = (window_width / 2, window_height))
        self.target = target.center
        self.speed = 1

    def update(self):
        current_x, current_y = self.rect.center
        target_x, target_y = self.target
    
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

            if  distance > self.speed:
                self.rect.x += dx * self.speed 
                self.rect.y += dy * self.speed 
        