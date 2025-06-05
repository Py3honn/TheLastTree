import pygame

class Barrier(pygame.sprite.Sprite):
    def __init__(self, groups, rect, debug=False):
        super().__init__(groups)
        self.image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        if debug:
            self.image.fill((255, 0, 0, 100))  # translucent red box

        self.rect = rect
