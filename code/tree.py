import pygame

class Tree(pygame.sprite.Sprite):
    def __init__(self, groups, image, position, scale=1):
        super().__init__(groups)

        # Scale tree image if needed
        self.original_image = image
        if scale != 1:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.original_image = pygame.transform.scale(image, (width, height))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=position)

        # Health
        self.max_hp = 200
        self.hp = self.max_hp
        self.last_damage_time = 0
        self.dead = False

        # Font for UI
        self.font = pygame.font.SysFont(None, 24)

    def damage_if_colliding(self, zombie_group):
        if self.dead:
            return

        now = pygame.time.get_ticks()
        if pygame.sprite.spritecollide(self, zombie_group, False):
            if now - self.last_damage_time >= 1000:  # 1 second delay
                self.hp = max(0, self.hp - 5)
                self.last_damage_time = now

                if self.hp == 0:
                    self.die()

    def die(self):
        self.dead = True
        self.image = pygame.Surface((0, 0))  # Disappear visually

    def draw_ui(self, surface):
        if self.dead:
            return

        # Get screen width to center the bar
        screen_width = surface.get_width()

        # Bar dimensions and position at top-center
        bar_width = 120
        bar_height = 14
        bar_x = screen_width // 2 - bar_width // 2
        bar_y = 20  # Padding from top

        fill_ratio = self.hp / self.max_hp
        fill_width = int(bar_width * fill_ratio)

        border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

        # Draw red bar + white border
        pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(surface, (255, 255, 255), border_rect, 2)

        # Draw text under the bar
        text = self.font.render(f"Tree HP: {self.hp} / {self.max_hp}", True, (255, 255, 255))
        text_rect = text.get_rect(midtop=(screen_width // 2, bar_y + bar_height + 4))
        surface.blit(text, text_rect)
