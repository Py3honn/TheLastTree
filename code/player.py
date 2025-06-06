import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, window_width, window_height, sprite_sheets, idle_sheets, barriers, zombies, sound):
        super().__init__(groups)

        self.frame_width = 48
        self.frame_height = 64
        self.scale = 2.5
        self.colorkey = (0, 0, 0)

        self.sound = sound

        self.animation_time = 100
        self.speed = 200

        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.direction = "down"
        self.barriers = barriers
        self.zombies = zombies
        self.can_attack = True

        self.animations = {
            direction: self.load_frames(sheet)
            for direction, sheet in sprite_sheets.items()
        }

        self.idle_animations = {
            direction: self.load_frames(sheet)
            for direction, sheet in idle_sheets.items()
        }

        self.frames = self.animations[self.direction]
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(window_width / 2, window_height / 2))

    def load_frames(self, sprite_sheet):
        sheet_width, _ = sprite_sheet.get_size()
        num_frames = sheet_width // self.frame_width
        frames = []

        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
            frame.blit(sprite_sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(
                frame, (self.frame_width * self.scale, self.frame_height * self.scale)
            )
            frame.set_colorkey(self.colorkey)
            frames.append(frame)

        return frames

    def get_direction(self, dx, dy):
        if dx == 0 and dy < 0: return "up"
        if dx == 0 and dy > 0: return "down"
        if dx < 0 and dy < 0: return "left_up"
        if dx < 0 and dy > 0: return "left_down"
        if dx > 0 and dy < 0: return "right_up"
        if dx > 0 and dy > 0: return "right_down"
        if dx < 0: return "left_down"
        if dx > 0: return "right_down"
        return self.direction  # Return last direction if no new input

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]

        move_x = dx * self.speed * dt
        move_y = dy * self.speed * dt

        prev_rect = self.rect.copy()
        self.rect.x += move_x
        self.rect.y += move_y

        now = pygame.time.get_ticks()

        if dx != 0 or dy != 0:
            self.direction = self.get_direction(dx, dy)
            self.frames = self.animations[self.direction]
            if now - self.last_update > self.animation_time:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_update = now
        else:
            self.frames = self.idle_animations[self.direction]
            if now - self.last_update > self.animation_time:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_update = now

        self.image = self.frames[self.current_frame]

        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        self.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height))

        if pygame.sprite.spritecollideany(self, self.barriers):
            self.rect = prev_rect

        # One attack per click
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            if self.can_attack:
                self.can_attack = False
                attack_range = 80
                self.sound.play()
                attack_damage = 10
                for zombie in self.zombies:
                    dx = self.rect.centerx - zombie.rect.centerx
                    dy = self.rect.centery - zombie.rect.centery
                    if abs(dx) <= attack_range and abs(dy) <= attack_range:
                        zombie.take_damage(attack_damage)
        else:
            self.can_attack = True
