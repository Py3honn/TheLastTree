import pygame
import random
from zombie_1 import Zombie
from player import Player
from tree import Tree
from barrier import Barrier

pygame.init()

# Setup
info = pygame.display.Info()
window_width = info.current_w
window_height = info.current_h
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("TheLastTree")
clock = pygame.time.Clock()
running = True

# Load assets
tree_image = pygame.image.load("TheLastTree/code/assets/tree/tree.png").convert_alpha()

sprite_sheets = {
    "down": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_down.png").convert_alpha(),
    "up": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_up.png").convert_alpha(),
    "left": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_left_down.png").convert_alpha(),
    "right": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_right_down.png").convert_alpha(),
    "left_up": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_left_up.png").convert_alpha(),
    "left_down": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_left_down.png").convert_alpha(),
    "right_up": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_right_up.png").convert_alpha(),
    "right_down": pygame.image.load("TheLastTree/code/assets/character/Walk/walk_right_down.png").convert_alpha(),
}
idle_sheets = {
    "down": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_down.png").convert_alpha(),
    "up": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_up.png").convert_alpha(),
    "left": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_left_down.png").convert_alpha(),
    "right": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_right_down.png").convert_alpha(),
    "left_up": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_left_up.png").convert_alpha(),
    "left_down": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_left_down.png").convert_alpha(),
    "right_up": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_right_up.png").convert_alpha(),
    "right_down": pygame.image.load("TheLastTree/code/assets/character/Idle/idle_right_down.png").convert_alpha(),
}

# Sprite groups
all_sprites = pygame.sprite.Group()
barriers = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

# Game state
wave = 1
zombies_per_wave = 5
zombies_spawned = 0
zombie_spawn_interval = 1000
last_zombie_spawn_time = 0
wave_start_time = pygame.time.get_ticks()
time_between_waves = 5000
font = pygame.font.SysFont(None, 48)
countdown_active = False

game_over = False
endless_mode = False
final_wave_reached = 0

def create_tree():
    global tree, barrier
    tree = Tree(
        all_sprites,
        tree_image,
        position=(window_width // 2, window_height // 2 - 100),
        scale=1.5
    )
    barrier_rect = pygame.Rect(0, 0, 90, 112)
    barrier_rect.center = tree.rect.center
    barrier = Barrier([all_sprites, barriers], barrier_rect)

create_tree()

# Create player
player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group)
player.rect.centery += 150

def get_spawn_position_for_wave(wave, window_width, window_height):
    margin = 50
    if wave == 1:
        return (random.randint(0, window_width), window_height + margin)  # bottom
    elif wave == 2:
        return (-margin, random.randint(0, window_height))  # left
    elif wave == 3:
        return (window_width + margin, random.randint(0, window_height))  # right
    elif wave == 4:
        return (random.randint(0, window_width), -margin)  # top
    else:
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return (random.randint(0, window_width), -margin)
        elif side == "bottom":
            return (random.randint(0, window_width), window_height + margin)
        elif side == "left":
            return (-margin, random.randint(0, window_height))
        else:
            return (window_width + margin, random.randint(0, window_height))

# Game loop
while running:
    dt = clock.tick(60) / 1000
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart
                    all_sprites.empty()
                    barriers.empty()
                    zombie_group.empty()
                    wave = 1
                    zombies_per_wave = 5
                    zombies_spawned = 0
                    countdown_active = False
                    game_over = False
                    endless_mode = False
                    create_tree()
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, barriers, zombie_group)
                    player.rect.centery += 150
                elif event.key == pygame.K_e:
                    # Endless mode (no tree)
                    all_sprites.empty()
                    barriers.empty()
                    zombie_group.empty()
                    game_over = False
                    endless_mode = True
                    wave = final_wave_reached
                    zombies_spawned = 0
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, barriers, zombie_group)
                    player.rect.centery += 150
                elif event.key == pygame.K_ESCAPE:
                    running = False

    screen.fill("darkgrey")
    if not game_over:
        if not endless_mode:
            # Normal mode
            if zombies_spawned >= zombies_per_wave and not zombie_group:
                if not countdown_active:
                    countdown_active = True
                    wave_start_time = now
                remaining = time_between_waves - (now - wave_start_time)
                if remaining <= 0:
                    wave += 1
                    zombies_per_wave += 2
                    zombies_spawned = 0
                    last_zombie_spawn_time = now
                    countdown_active = False
                else:
                    seconds = remaining // 1000 + 1
                    text = font.render(f"Wave {wave + 1} in {seconds}", True, (255, 255, 255))
                    screen.blit(text, (20, 20))
            elif zombies_spawned < zombies_per_wave and not countdown_active:
                if now - last_zombie_spawn_time >= zombie_spawn_interval:
                    spawn_pos = get_spawn_position_for_wave(wave, window_width, window_height)
                    is_boss = wave >= 5 and random.random() < 0.2
                    zombie = Zombie(all_sprites, spawn_pos, sprite_sheets["up"], tree.rect, barriers, is_boss=is_boss)
                    zombie_group.add(zombie)
                    zombies_spawned += 1
                    last_zombie_spawn_time = now
        else:
            # Endless mode: zombies spawn constantly
            if now - last_zombie_spawn_time >= zombie_spawn_interval:
                spawn_pos = get_spawn_position_for_wave(wave, window_width, window_height)
                is_boss = random.random() < 0.2
                zombie = Zombie(all_sprites, spawn_pos, sprite_sheets["up"], player.rect, barriers, is_boss=is_boss)
                zombie_group.add(zombie)
                all_sprites.add(zombie)
                zombies_spawned += 1
                last_zombie_spawn_time = now

        # Update and logic
        all_sprites.update(dt)
        if not endless_mode:
            tree.damage_if_colliding(zombie_group)
            if tree.dead:
                game_over = True
                final_wave_reached = wave

    # Draw
    all_sprites.draw(screen)
    if not endless_mode:
        tree.draw_ui(screen)

    # Game Over screen
    if game_over:
        overlay = pygame.Surface((window_width, window_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        message = font.render("The Last Tree Has Fallen...", True, (255, 50, 50))
        screen.blit(message, message.get_rect(center=(window_width // 2, window_height // 2 - 60)))

        wave_info = font.render(f"You reached Wave {final_wave_reached}", True, (255, 255, 255))
        screen.blit(wave_info, wave_info.get_rect(center=(window_width // 2, window_height // 2)))

        restart_info = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(restart_info, restart_info.get_rect(center=(window_width // 2, window_height // 2 + 60)))

        endless_info = font.render("Press E for Endless Mode", True, (200, 200, 200))
        screen.blit(endless_info, endless_info.get_rect(center=(window_width // 2, window_height // 2 + 110)))

        quit_info = font.render("Press ESC to Quit", True, (180, 180, 180))
        screen.blit(quit_info, quit_info.get_rect(center=(window_width // 2, window_height // 2 + 160)))

    pygame.display.flip()
