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
background_image = pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/bg/mud.jpg").convert()
background_image = pygame.transform.scale(background_image, (window_width, window_height))

# Load assets
tree_image = pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/tree/tree.png").convert_alpha()
thunder_sound = pygame.mixer.Sound("/home/aashug/dev/TheLastTree/code/assets/sounds/thunder.mp3")
thunder_sound.set_volume(0.5)
slash_sound = pygame.mixer.Sound("/home/aashug/dev/TheLastTree/code/assets/sounds/slash.mp3")
game_over_sound = pygame.mixer.Sound("/home/aashug/dev/TheLastTree/code/assets/sounds/game_over.wav")
zombie_sound = pygame.mixer.Sound("/home/aashug/dev/TheLastTree/code/assets/sounds/zombie.wav")
zombie_sound.set_volume(0.3)

# Lightning vars
lightning_active = False
lightning_start_time = 0
lightning_interval = random.randint(5000, 15000)
last_lightning_time = 0
lightning_flash_duration = 100

# Zombie sound vars
next_zombie_sound_time = pygame.time.get_ticks() + random.randint(3000, 8000)

# Start message
start_message_displayed = True
start_message_start_time = pygame.time.get_ticks()
start_message_duration = 3000  # 3 seconds

# Fonts
font = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)

# Score system
score = 0
def add_score(points):
    global score
    score += points

# Sprite sheets
sprite_sheets = {
    "down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_down.png").convert_alpha(),
    "up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_up.png").convert_alpha(),
    "left": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_left_down.png").convert_alpha(),
    "right": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_right_down.png").convert_alpha(),
    "left_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_left_up.png").convert_alpha(),
    "left_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_left_down.png").convert_alpha(),
    "right_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_right_up.png").convert_alpha(),
    "right_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Walk/walk_right_down.png").convert_alpha(),
}
idle_sheets = {
    "down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_down.png").convert_alpha(),
    "up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_up.png").convert_alpha(),
    "left": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_left_down.png").convert_alpha(),
    "right": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_right_down.png").convert_alpha(),
    "left_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_left_up.png").convert_alpha(),
    "left_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_left_down.png").convert_alpha(),
    "right_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_right_up.png").convert_alpha(),
    "right_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/character/Idle/idle_right_down.png").convert_alpha(),
}
zombie_sheets = {
    "down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_down.png").convert_alpha(),
    "up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_up.png").convert_alpha(),
    "left": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_left_down.png").convert_alpha(),
    "right": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_right_down.png").convert_alpha(),
    "left_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_left_up.png").convert_alpha(),
    "left_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_left_down.png").convert_alpha(),
    "right_up": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_right_up.png").convert_alpha(),
    "right_down": pygame.image.load("/home/aashug/dev/TheLastTree/code/assets/zombie/zombie_right_down.png").convert_alpha(),
}

#sprite groups
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
countdown_active = False

game_over = False
endless_mode = False
final_wave_reached = 0

# Tree and player
def create_tree():
    global tree, barrier
    tree = Tree(all_sprites, tree_image, position=(window_width // 2, window_height // 2 - 100), scale=1.5)
    barrier_rect = pygame.Rect(0, 0, 80, 107)
    barrier_rect.center = tree.rect.center
    barrier = Barrier([all_sprites, barriers], barrier_rect)

create_tree()

player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group, slash_sound, add_score)
player.rect.centery += 150

def get_spawn_position_for_wave(wave, window_width, window_height):
    margin = 50
    side = ["top", "bottom", "left", "right"]
    if wave <= 4:
        return {
            1: (random.randint(0, window_width), window_height + margin),
            2: (-margin, random.randint(0, window_height)),
            3: (window_width + margin, random.randint(0, window_height)),
            4: (random.randint(0, window_width), -margin)
        }[wave]
    else:
        direction = random.choice(side)
        if direction == "top":
            return (random.randint(0, window_width), -margin)
        elif direction == "bottom":
            return (random.randint(0, window_width), window_height + margin)
        elif direction == "left":
            return (-margin, random.randint(0, window_height))
        else:
            return (window_width + margin, random.randint(0, window_height))

# Game loop
while running:
    dt = clock.tick(60) / 1000
    now = pygame.time.get_ticks()

    # Lightning
    if now - last_lightning_time >= lightning_interval:
        lightning_active = True
        lightning_start_time = now
        last_lightning_time = now
        lightning_interval = random.randint(5000, 15000)
        for zombie in list(zombie_group):
            if zombie.take_damage(10):
                add_score(50 if zombie.is_boss else 5)

    if lightning_active and now - lightning_start_time > lightning_flash_duration:
        lightning_active = False
        thunder_sound.play()

    # Zombie sound
    if zombie_group and now >= next_zombie_sound_time:
        zombie_sound.play()
        next_zombie_sound_time = now + random.randint(3000, 8000)

    # Events
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
                    score = 0
                    create_tree()
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group, slash_sound, add_score)
                    player.rect.centery += 150
                elif event.key == pygame.K_e:
                    all_sprites.empty()
                    barriers.empty()
                    zombie_group.empty()
                    game_over = False
                    endless_mode = True
                    wave = final_wave_reached
                    zombies_spawned = 0
                    score = 0
                    player = Player(all_sprites, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombie_group, slash_sound, add_score)
                    player.rect.centery += 150
                elif event.key == pygame.K_ESCAPE:
                    running = False

    # Drawing
    screen.blit(background_image, (0, 0))

    fog_surface = pygame.Surface((window_width, window_height))
    fog_alpha = min(60 + wave * 5, 200)
    fog_surface.set_alpha(fog_alpha)
    fog_surface.fill((100, 100, 100))
    screen.blit(fog_surface, (0, 0))

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
                    zombie = Zombie(all_sprites, spawn_pos, zombie_sheets, tree.rect, barriers, is_boss=is_boss)
                    zombie_group.add(zombie)
                    zombies_spawned += 1
                    last_zombie_spawn_time = now
        else:
            if now - last_zombie_spawn_time >= zombie_spawn_interval:
                spawn_pos = get_spawn_position_for_wave(wave, window_width, window_height)
                is_boss = random.random() < 0.2
                zombie = Zombie(all_sprites, spawn_pos, zombie_sheets, player.rect, barriers, is_boss=is_boss)
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

    all_sprites.draw(screen)
    if not endless_mode:
        tree.draw_ui(screen)

    # Draw Score
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (window_width - score_text.get_width() - 20, 20))

    # Start Message
    if start_message_displayed:
        if now - start_message_start_time < start_message_duration:
            message = font.render("Protect the Tree!", True, (255, 255, 0))
            screen.blit(message, message.get_rect(center=(window_width // 2, 80)))
        else:
            start_message_displayed = False

    # Lightning overlay
    if lightning_active:
        lightning_overlay = pygame.Surface((window_width, window_height))
        lightning_overlay.fill((255, 255, 255))
        lightning_overlay.set_alpha(200)
     
        screen.blit(lightning_overlay, (0, 0))
    #game over logic
    if game_over:
        overlay = pygame.Surface((window_width, window_height))
        overlay.set_alpha(180)
        game_over_sound.play()
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        message = font.render("The Last Tree Has Fallen...", True, (255, 50, 50))
        screen.blit(message, message.get_rect(center=(window_width // 2, window_height // 2 - 60)))

        wave_info = font.render(f"You reached Wave {final_wave_reached}", True, (255, 255, 255))
        screen.blit(wave_info, wave_info.get_rect(center=(window_width // 2, window_height // 2)))

        score_info = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_info, score_info.get_rect(center=(window_width // 2, window_height // 2 + 30)))

        restart_info = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(restart_info, restart_info.get_rect(center=(window_width // 2, window_height // 2 + 80)))

        endless_info = font.render("Press E for Endless Mode", True, (200, 200, 200))
        screen.blit(endless_info, endless_info.get_rect(center=(window_width // 2, window_height // 2 + 130)))

        quit_info = font.render("Press ESC to Quit", True, (180, 180, 180))
        screen.blit(quit_info, quit_info.get_rect(center=(window_width // 2, window_height // 2 + 180)))

    pygame.display.flip()

pygame.quit()
