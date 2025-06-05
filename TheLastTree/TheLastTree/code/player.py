import pygame

pygame.init()

class Player(pygame.sprite.Sprite):
    
    def __init__(self, groups, window_width, window_height, sprite):
        super().__init__(groups)
        self.image = sprite 
        self.rect = self.image.get_rect(center = (window_width / 2, window_height / 2))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
                self.rect.y -= 1
        if keys[pygame.K_s]:
                self.rect.y += 1
        if keys[pygame.K_a]:
                self.rect.x -= 1
        if keys[pygame.K_d]:
            self.rect.x += 1