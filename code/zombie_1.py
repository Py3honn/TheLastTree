import pygame
import math

class Zombie(pygame.sprite.Sprite):
    def __init__(self, groups, position, sprite_sheet, target_rect, barriers, is_boss=False):
        super().__init__(groups)

        self.frame_width = 48
        self.frame_height = 64
        self.scale = 2.5 if is_boss else 2
        self.colorkey = (0, 0, 0)
        self.speed = 40 if is_boss else 60
        self.hp = 100 if is_boss else 30  # ✅ Boss has more HP
        self.animation_time = 150
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.barriers = barriers

        self.frames = self.load_frames(sprite_sheet)
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=position)
        self.target = target_rect.center

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

    def update(self, dt):
        prev_rect = self.rect.copy()

        current_x, current_y = self.rect.center
        target_x, target_y = self.target
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance

        if distance > self.speed * dt:
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.last_update = now

        if pygame.sprite.spritecollideany(self, self.barriers):
            self.rect = prev_rect

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
