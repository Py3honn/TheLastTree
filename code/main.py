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
background_image = pygame.image.load("TheLastTree/code/assets/bg/mud.jpg").convert()
background_image = pygame.transform.scale(background_image, (window_width, window_height))

# Load assets
tree_image = pygame.image.load("TheLastTree/code/assets/tree/tree.png").convert_alpha()
# Thunder sound
thunder_sound = pygame.mixer.Sound("TheLastTree/code/assets/sounds/thunder.mp3")

# Lightning vars
lightning_active = False
lightning_start_time = 0
lightning_interval = random.randint(5000, 15000)
last_lightning_time = 0
lightning_flash_duration = 100


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

    # Lightning logic
    if now - last_lightning_time >= lightning_interval:
        lightning_active = True
        lightning_start_time = now
        last_lightning_time = now
        lightning_interval = random.randint(5000, 15000)
        for zombie in zombie_group:
            zombie.take_damage(10)

    if lightning_active and now - lightning_start_time > lightning_flash_duration:
        lightning_active = False
        thunder_sound.play()

    # ✅ Event loop must always run
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
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
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group)
                    player.rect.centery += 150
                elif event.key == pygame.K_e:
                    all_sprites.empty()
                    barriers.empty()
                    zombie_group.empty()
                    game_over = False
                    endless_mode = True
                    wave = final_wave_reached
                    zombies_spawned = 0
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group)
                    player.rect.centery += 150
                elif event.key == pygame.K_ESCAPE:
                    running = False

    screen.blit(background_image, (0, 0))

    # 🌫️ Fog that thickens with each wave
    fog_surface = pygame.Surface((window_width, window_height))
    fog_alpha = min(60 + wave * 5, 200)
    fog_surface.set_alpha(fog_alpha)
    fog_surface.fill((100, 100, 100))
    screen.blit(fog_surface, (0, 0))

    # Game logic
    if not game_over:
        if not endless_mode:
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
            if now - last_zombie_spawn_time >= zombie_spawn_interval:
                spawn_pos = get_spawn_position_for_wave(wave, window_width, window_height)
                is_boss = random.random() < 0.2
                zombie = Zombie(all_sprites, spawn_pos, sprite_sheets["up"], player.rect, barriers, is_boss=is_boss)
                zombie_group.add(zombie)
                all_sprites.add(zombie)
                zombies_spawned += 1
                last_zombie_spawn_time = now

        all_sprites.update(dt)
        if not endless_mode:
            tree.damage_if_colliding(zombie_group)
            if tree.dead:
                game_over = True
                final_wave_reached = wave

    # Draw sprites and UI
    all_sprites.draw(screen)
    if not endless_mode:
        tree.draw_ui(screen)

    # Lightning flash overlay
    if lightning_active:
        lightning_overlay = pygame.Surface((window_width, window_height))
        lightning_overlay.fill((255, 255, 255))
        lightning_overlay.set_alpha(200)
        screen.blit(lightning_overlay, (0, 0))

    # Game Over UI
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

