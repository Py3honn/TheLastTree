import pygame
import math
import random

class Zombie(pygame.sprite.Sprite):
    def __init__(self, groups, position, sprite_sheets, target_rect, barriers, is_boss=False):
        super().__init__(groups)

        self.frame_width = 48
        self.frame_height = 64
        self.scale = 2.5 if is_boss else 2
        self.colorkey = (0, 0, 0)
        self.speed = 40 if is_boss else 60
        self.hp = 100 if is_boss else 30
        self.animation_time = 150
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.barriers = barriers
        self.target = target_rect

        self.direction = "down"
        self.sprite_sheets = sprite_sheets
        self.frames = self.load_all_frames(sprite_sheets)
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect(center=position)

    def load_all_frames(self, sheets):
        all_frames = {}
        for direction, sheet in sheets.items():
            frames = []
            sheet_width, _ = sheet.get_size()
            num_frames = sheet_width // self.frame_width
            for i in range(num_frames):
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
                frame.blit(sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
                frame = pygame.transform.scale(
                    frame, (int(self.frame_width * self.scale), int(self.frame_height * self.scale))
                )
                frame.set_colorkey(self.colorkey)
                frames.append(frame)
            all_frames[direction] = frames
        return all_frames

    def get_direction(self, dx, dy):
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

    def update(self, dt):
        prev_rect = self.rect.copy()
        stuck = False

        current_x, current_y = self.rect.center
        target_x, target_y = self.target.center
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance

        if distance > self.speed * dt:
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt

        if pygame.sprite.spritecollideany(self, self.barriers):
            self.rect = prev_rect
            stuck = True

        self.direction = self.get_direction(dx, dy)

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            self.last_update = now

        self.image = self.frames[self.direction][self.current_frame]

        if stuck:
            sidestep = random.choice([(5, 0), (-5, 0), (0, 5), (0, -5)])
            self.rect.move_ip(*sidestep)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()