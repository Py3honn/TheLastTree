#imports
import pygame
from zombie_1 import Zombie
from player import Player

pygame.init()

# constants
info = pygame.display.Info()
window_width = info.current_w
window_height = info.current_h
running = True
clock = pygame.time.Clock()
pygame.display.set_caption("TheLastTree")
screen = pygame.display.set_mode((window_width, window_height))

tree_image = pygame.image.load("assets/tree/Trees.png").convert_alpha()
tree_rect = tree_image.get_rect(center = (window_width / 2, window_height / 3))


#sprites
character_image = pygame.image.load("assets/character/Idle/idle_down.png").convert_alpha()
all_sprite = pygame.sprite.Group()
zombie1 = Zombie(all_sprite, window_width, window_height, character_image, tree_rect)
player = Player(all_sprite, window_width, window_height, character_image)

#game loop
while running:
  dt = clock.tick(60) / 1000

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  screen.fill("darkgrey")
  screen.blit(tree_image, tree_rect)
  all_sprite.draw(screen)
  all_sprite.update()
 
  pygame.display.flip()
