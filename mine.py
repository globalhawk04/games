import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (50, 50, 255)
DARK_GREY = (40, 40, 40) # Dungeon Floor
WALL_GREY = (80, 80, 80) # Dungeon Walls
YELLOW = (255, 255, 0)

# Player properties
PLAYER_SPEED = 5

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    """ The player character (Our Crab Hero) - TOP DOWN """
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # Create a crab-like appearance
        self.image_orig = pygame.Surface((40, 40))
        self.image_orig.set_colorkey(BLACK)
        pygame.draw.rect(self.image_orig, RED, (0, 5, 40, 30)) # Body
        pygame.draw.circle(self.image_orig, RED, (5, 5), 8) # Left Claw
        pygame.draw.circle(self.image_orig, RED, (35, 5), 8) # Right Claw
        self.image = self.image_orig.copy()
        
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        
        self.health = 100
        
        # Cooldowns for abilities
        self.last_shot = 0
        self.shot_delay = 1500 # milliseconds
        self.last_melee = 0
        self.melee_delay = 400
        
        self.direction = pygame.math.Vector2(1, 0) # Facing right initially

    def get_keys(self):
        self.vel = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = PLAYER_SPEED
            
        # Normalize diagonal movement to prevent faster speed
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        self.get_keys() # This handles movement input
        
        # ---!!! NEW CODE: COMBAT INPUT !!!---
        # Check for melee attack here instead of in the event loop.
        # This allows the player to hold down the spacebar to attack as fast as the cooldown allows.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.melee_attack()
        # ---!!! END OF NEW CODE !!!---
        
        # Update direction vector if moving
        if self.vel.length_squared() > 0:
            self.direction = self.vel.normalize()
        
        self.pos += self.vel
        self.rect.centerx = self.pos.x
        self.collide_with_walls('x')
        self.rect.centery = self.pos.y
        self.collide_with_walls('y')

    def collide_with_walls(self, dir):
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            if dir == 'x':
                if self.vel.x > 0:
                    self.rect.right = hits[0].rect.left
                if self.vel.x < 0:
                    self.rect.left = hits[0].rect.right
                self.pos.x = self.rect.centerx
            if dir == 'y':
                if self.vel.y > 0:
                    self.rect.bottom = hits[0].rect.top
                if self.vel.y < 0:
                    self.rect.top = hits[0].rect.bottom
                self.pos.y = self.rect.centery

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            bubble = WaterBubble(self.rect.centerx, self.rect.centery, self.direction)
            self.game.all_sprites.add(bubble)
            self.game.projectiles.add(bubble)
            
    def melee_attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_melee > self.melee_delay:
            self.last_melee = now
            # Create a hitbox in the direction the player is facing
            hitbox_pos = self.pos + self.direction * 30
            ClawSwipe(self.game, hitbox_pos)
            
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """ The enemy character (The Cat Menace) - WITH CHASE AI """
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((45, 45))
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, (128, 128, 128), self.image.get_rect()) # Body
        pygame.draw.circle(self.image, (200,200,0), (10,10), 5) # Left Eye
        pygame.draw.circle(self.image, (200,200,0), (35,10), 5) # Right Eye
        
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        
        self.speed = random.uniform(2.5, 4.0)
        self.health = 100
        self.vision_radius = 250 # How close the player needs to be for the cat to see them

    def update(self):
        # Basic Chase AI
        if self.game.player.alive():
            player_vec = self.game.player.pos
            enemy_vec = self.pos
            dist = player_vec.distance_to(enemy_vec)
            
            if dist < self.vision_radius:
                direction = (player_vec - enemy_vec).normalize()
                self.pos += direction * self.speed
        
        self.rect.centerx = self.pos.x
        self.collide_with_walls('x')
        self.rect.centery = self.pos.y
        self.collide_with_walls('y')
            
    def collide_with_walls(self, dir):
        # Similar collision logic to player to prevent walking through walls
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            if dir == 'x':
                if self.pos.x > hits[0].rect.centerx: # coming from right
                    self.rect.left = hits[0].rect.right
                else: # coming from left
                    self.rect.right = hits[0].rect.left
                self.pos.x = self.rect.centerx
            if dir == 'y':
                if self.pos.y > hits[0].rect.centery: # coming from bottom
                    self.rect.top = hits[0].rect.bottom
                else: # coming from top
                    self.rect.bottom = hits[0].rect.top
                self.pos.y = self.rect.centery

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

class WaterBubble(pygame.sprite.Sprite):
    """ The player's ranged projectile """
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, BLUE, (8, 8), 7)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        self.vel = direction * 10 # Speed of 10 in the given direction
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        # Kill after 1 second to prevent them flying forever
        if pygame.time.get_ticks() - self.spawn_time > 1000:
            self.kill()

class ClawSwipe(pygame.sprite.Sprite):
    """ A short-lived hitbox for the player's melee attack """
    def __init__(self, game, pos):
        self.groups = game.all_sprites, game.melee_hits
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((30, 30))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, YELLOW, (15,15), 15)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 100 # lives for 100ms

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class Wall(pygame.sprite.Sprite):
    """ A Wall block for the dungeon """
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w,h))
        self.image.fill(WALL_GREY)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# --- UI Functions ---
def draw_health_bar(surf, x, y, pct, color):
    if pct < 0: pct = 0
    BAR_LENGTH, BAR_HEIGHT = 150, 20
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_cooldown_bar(surf, x, y, pct, color):
    if pct > 1: pct = 1
    if pct < 0: pct = 0
    BAR_LENGTH, BAR_HEIGHT = 100, 15
    fill = pct * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

class Game:
    """ The main Game class to orchestrate everything """
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Crab's Dungeon")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

    def new(self):
        # Group setup
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.melee_hits = pygame.sprite.Group()

        # Player
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Dungeon layout
        wall_size = 32
        for x in range(0, SCREEN_WIDTH, wall_size):
            self.make_wall(x, 0, wall_size, wall_size) # Top wall
            self.make_wall(x, SCREEN_HEIGHT - wall_size, wall_size, wall_size) # Bottom wall
        for y in range(wall_size, SCREEN_HEIGHT - wall_size, wall_size):
            self.make_wall(0, y, wall_size, wall_size) # Left wall
            self.make_wall(SCREEN_WIDTH - wall_size, y, wall_size, wall_size) # Right wall
        # Some obstacles
        self.make_wall(300, 200, wall_size * 5, wall_size)
        self.make_wall(600, 500, wall_size * 5, wall_size)
        self.make_wall(200, 600, wall_size, wall_size * 4)

        # Enemies
        for i in range(5):
            x = random.randrange(wall_size * 2, SCREEN_WIDTH - wall_size * 2)
            y = random.randrange(wall_size * 2, SCREEN_HEIGHT - wall_size * 2)
            enemy = Enemy(self, x, y)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

        self.run()

    def make_wall(self, x, y, w, h):
        wall = Wall(x,y,w,h)
        self.all_sprites.add(wall)
        self.walls.add(wall)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        if self.game_over: return
            
        self.all_sprites.update()

        # Projectile hits enemy
        hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, False, True)
        for enemy in hits:
            enemy.take_damage(40) # Ranged is powerful

        # Melee hits enemy
        # Set dokill to False for melee so one swipe can hit multiple enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.melee_hits, False, False)
        for enemy in hits:
            enemy.take_damage(3) # Melee is consistent, low damage

        # Player hits enemy (contact damage)
        if self.player.alive():
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits:
                self.player.take_damage(1)
        
        # Check for win/loss
        if not self.player.alive():
            self.game_over = True
            self.winner = "Cats"
            
        if not self.enemies:
            self.game_over = True
            self.winner = "Crab"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            # ---!!! CODE CHANGED !!!---
            # Melee attack was removed from here.
            # Ranged attack is a special ability, so it stays as a single press event.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.player.shoot()
            # ---!!! END OF CHANGE !!!---

    def draw(self):
        self.screen.fill(DARK_GREY)
        self.all_sprites.draw(self.screen)
        
        # UI
        draw_health_bar(self.screen, 10, 10, self.player.health, GREEN)
        draw_text(self.screen, "CRAB HEALTH", 18, 85, 35, WHITE)
        
        # Ranged Cooldown UI
        now = pygame.time.get_ticks()
        shot_pct = (now - self.player.last_shot) / self.player.shot_delay
        draw_cooldown_bar(self.screen, 10, 60, shot_pct, BLUE)
        draw_text(self.screen, "Bubble Shot (F)", 15, 60, 80, WHITE)

        # Melee Cooldown UI (visual feedback for player)
        melee_pct = (now - self.player.last_melee) / self.player.melee_delay
        draw_cooldown_bar(self.screen, 10, 100, melee_pct, YELLOW)
        draw_text(self.screen, "Claw Swipe (Space)", 15, 75, 120, WHITE)

        # Enemy Health Bars (above their heads)
        for enemy in self.enemies:
            if enemy.health < 100: # Only show if damaged
                draw_health_bar(self.screen, enemy.rect.x, enemy.rect.y - 20, enemy.health, RED)
        
        if self.game_over:
            self.show_game_over_screen()
        
        pygame.display.flip()
        
    def show_game_over_screen(self):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,128))
        self.screen.blit(s, (0,0))
        
        draw_text(self.screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
        if self.winner == "Crab":
            draw_text(self.screen, "The Crab Cleared the Dungeon!", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, GREEN)
        else:
            draw_text(self.screen, "The Cats Overwhelmed You...", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, RED)
        
        draw_text(self.screen, "Press 'R' to try again or 'Q' to quit", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, WHITE)
        
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        waiting = False
                        self.running = False
                    if event.key == pygame.K_r:
                        waiting = False
                        self.game_over = False

# --- Start the game ---
g = Game()
while g.running:
    g.new()

pygame.quit()