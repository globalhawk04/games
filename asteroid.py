import pygame
import random
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # For Game Over text and Player damage
ORANGE = (255, 165, 0) # Flame color
GRAY = (150, 150, 150) # For blinking effect
YELLOW = (255, 255, 0) # Particle color

# Player Constants
PLAYER_SIZE = 15
PLAYER_THRUST = 0.2
PLAYER_ROTATION_SPEED = 3
PLAYER_MAX_SPEED = 8
PLAYER_COLLISION_RADIUS = PLAYER_SIZE * 1.2
PLAYER_START_LIVES = 3
PLAYER_INVINCIBILITY_DURATION = 3000 # milliseconds after respawn/level start

# Flame Constants
FLAME_LENGTH = PLAYER_SIZE * 1.2
FLAME_WIDTH = PLAYER_SIZE * 0.8

# Bullet Constants
BULLET_SPEED = 10
BULLET_LIFESPAN = 1000 # milliseconds
BULLET_RADIUS = 2

# Code Block (Asteroid) Constants
CODE_BLOCK_SPEED_MIN = 1
CODE_BLOCK_SPEED_MAX = 4
CODE_BLOCK_START_COUNT = 4
# Points awarded for destroying different sizes (bigger blocks more points)
CODE_BLOCK_SCORES = {
    'large': 20,
    'medium': 50,
    'small': 100, # Smallest blocks give most points, classic arcade style
}

# Code Block Sizes and properties (base size for text/collision, split count, collision radius multiplier)
# We'll use these sizes more abstractly for text length and collision than visual shape
CODE_BLOCK_SIZES = {
    'large': {'base_size': 30, 'text_length': 30, 'split': 2, 'collision_mult': 1.0}, # base_size is for font/visual scale
    'medium': {'base_size': 20, 'text_length': 15, 'split': 2, 'collision_mult': 1.0},
    'small': {'base_size': 15, 'text_length': 8, 'split': 0, 'collision_mult': 1.0}, # Doesn't split, text is shorter
}

# Particle Constants
PARTICLE_LIFESPAN = 800 # milliseconds
PARTICLE_SPEED_MIN = 1
PARTICLE_SPEED_MAX = 5
PARTICLE_COUNT_MULTIPLIER = 1.5 # How many particles per character

# Game State Constants
WAIT_FOR_LEVEL_START = 3000 # milliseconds to wait before level starts or after death
GAME_OVER_WAIT = 5000 # milliseconds to show game over before allowing restart/quit


# --- Python Code Snippets ---
# Each element in this list is a block of code we can sample from
PYTHON_CODE_SNIPPETS = [
    "import pygame\n\ndef game_loop():\n  running = True\n  while running:\n    for event in pygame.event.get():\n      if event.type == pygame.QUIT:\n        running = False\n    # Update game state\n    # Draw everything\n    pygame.display.flip()\n  pygame.quit()",
    "class Vec2:\n  def __init__(self, x, y):\n    self.x = x\n    self.y = y\n  def add(self, other):\n    return Vec2(self.x + other.x, self.y + other.y)\n  def length(self):\n    return (self.x**2 + self.y**2)**0.5",
    "def collision(obj1, obj2):\n  distance = ((obj1.pos.x - obj2.pos.x)**2 + (obj1.pos.y - obj2.pos.y)**2)**0.5\n  return distance < (obj1.radius + obj2.radius)",
    "my_dict = {'apple': 3, 'banana': 1, 'cherry': 5}\n\nfor key, value in my_dict.items():\n  print(f'{key}: {value}')",
    "numbers = [x * 2 for x in range(10) if x % 2 == 0]\n\n# This is a list comprehension!",
    "try:\n  result = 10 / 0\nexcept ZeroDivisionError:\n  print('Cannot divide by zero!')",
    "def countdown(n):\n  if n <= 0:\n    print('Blast off!')\n  else:\n    print(n)\n    countdown(n - 1)",
    "x = 0\nwhile x < 5:\n  print(x)\n  x += 1",
    "data = [('a', 1), ('b', 2)]\nfor item in data:\n  key, value = item\n  print(f'{key}: {value}')",
    "def greet(name='World'):\n  return f'Hello, {name}!'\n\nmessage = greet('Pygame')",
    "import random\n\nrandom_number = random.randint(1, 100)"
    # Add more snippets for variety!
]

# --- Helper Functions ---

def wrap_position(position, width, height):
    """Wraps an object's position around the screen edges."""
    x, y = position
    x %= width
    y %= height
    return x, y

def rotate_point(point, angle_degrees):
    """Rotate a pygame.math.Vector2 point around the origin (0,0)."""
    # pygame.math.Vector2.rotate() rotates counter-clockwise
    # Our base points are defined pointing UP (-90). To rotate them
    # to face the current 'self.angle', we need to rotate by self.angle - (-90) = self.angle + 90 CCW.
    rotation_angle_ccw = angle_degrees + 90
    return point.rotate(rotation_angle_ccw)

def draw_text(screen, text, size, color, x, y, antialias=True):
    """Helper function to draw text on the screen."""
    font = pygame.font.Font(None, size) # Use default font
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_player_lives(screen, lives, x, y):
    """Draws small player icons for remaining lives."""
    life_ship_points = [
         pygame.math.Vector2(0, -PLAYER_SIZE),
         pygame.math.Vector2(-PLAYER_SIZE * 0.7, PLAYER_SIZE * 0.7),
         pygame.math.Vector2(PLAYER_SIZE * 0.7, PLAYER_SIZE * 0.7)
    ]
    scale = 0.7 # Scale down the life icon
    scaled_points = [p * scale for p in life_ship_points]

    for i in range(lives):
        # Calculate position for each icon
        icon_x = x + i * (PLAYER_SIZE * scale * 2 + 5) # Position side-by-side with spacing
        icon_y = y
        # Translate scaled points to the icon's position
        translated_points = [(icon_x + p.x, icon_y + p.y) for p in scaled_points]
        pygame.draw.polygon(screen, WHITE, translated_points, 1) # Draw outline


# --- Classes ---

# Moved Bullet class definition BEFORE Player class definition
class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, velocity, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = BULLET_RADIUS

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect(center=position)
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(velocity)

        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.position += self.velocity
        self.rect.center = (int(self.position.x), int(self.position.y))

        # Wrap around screen edges
        self.position.x, self.position.y = wrap_position(
            (self.position.x, self.position.y),
            self.screen_width, self.screen_height
        )

        # Remove bullet after lifespan
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFESPAN:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Define ship points relative to its center when pointing UP (-90 degrees)
        self._base_ship_points = [
            pygame.math.Vector2(0, -PLAYER_SIZE * 1.5),         # Nose (up)
            pygame.math.Vector2(-PLAYER_SIZE, PLAYER_SIZE * 1.5),  # Bottom-left
            pygame.math.Vector2(PLAYER_SIZE, PLAYER_SIZE * 1.5)   # Bottom-right
        ]

        # Define flame points relative to its center when pointing UP (-90 degrees)
        self._base_flame_points = [
            pygame.math.Vector2(-PLAYER_SIZE * 0.8, PLAYER_SIZE * 1.5), # Left base near ship corner
            pygame.math.Vector2(0, PLAYER_SIZE * 1.5 + FLAME_LENGTH),    # Tip of the flame
            pygame.math.Vector2(PLAYER_SIZE * 0.8, PLAYER_SIZE * 1.5)  # Right base near ship corner
        ]

        self.position = pygame.math.Vector2(screen_width // 2, screen_height // 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = -90 # Pointing upwards initially (-90 degrees from positive x)

        self.thrusting = False
        self.rotating_left = False
        self.rotating_right = False
        self.visible = True # To hide/show player during waits or death animation

        # Collision setup (using radius for collide_circle)
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA) # Dummy surface for sprite groups
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
        self.radius = PLAYER_COLLISION_RADIUS

        # Invincibility
        self.is_invincible = False
        self.invincibility_start_time = 0
        self._blink_toggle = False # For visual blink effect
        self._last_blink_time = 0
        self._blink_interval = 100 # milliseconds

    def activate_invincibility(self):
        """Starts the invincibility timer and visual effect."""
        self.is_invincible = True
        self.invincibility_start_time = pygame.time.get_ticks()
        self.visible = True # Make sure player is visible initially
        self._blink_toggle = True # Ensure we start blinking

    def get_transformed_points(self, base_points):
        """Rotates and translates base points to current world coordinates."""
        transformed_points = []
        for point in base_points:
            rotated_point = rotate_point(point, self.angle)
            translated_point = rotated_point + self.position
            transformed_points.append(translated_point)
        return transformed_points

    def update(self):
        # Only update if visible (or not in game over state)
        if self.visible: # We might make player invisible during waiting periods
            # Handle rotation
            if self.rotating_left:
                self.angle += PLAYER_ROTATION_SPEED
            if self.rotating_right:
                self.angle -= PLAYER_ROTATION_SPEED
            self.angle %= 360
            if self.angle < 0: self.angle += 360 # Keep angle positive

            # Handle thrust
            if self.thrusting:
                direction = pygame.math.Vector2(
                    math.cos(math.radians(self.angle)),
                    math.sin(math.radians(self.angle))
                )
                self.velocity += direction * PLAYER_THRUST

            # Apply friction/drag
            self.velocity *= 0.995

            # Limit speed
            if self.velocity.length() > PLAYER_MAX_SPEED:
                 self.velocity.scale_to_length(PLAYER_MAX_SPEED)

            # Update position based on velocity
            self.position += self.velocity

            # Wrap around screen edges
            self.position.x, self.position.y = wrap_position(
                (self.position.x, self.position.y),
                self.screen_width, self.screen_height
            )

            # Update the rect's center for collision checks
            self.rect.center = (int(self.position.x), int(self.position.y))

            # Handle invincibility timer
            if self.is_invincible:
                if pygame.time.get_ticks() - self.invincibility_start_time > PLAYER_INVINCIBILITY_DURATION:
                    self.is_invincible = False
                    self.visible = True # Ensure visible after invincibility
                else:
                    # Blink effect during invincibility
                    if pygame.time.get_ticks() - self._last_blink_time > self._blink_interval:
                        self._blink_toggle = not self._blink_toggle
                        self._last_blink_time = pygame.time.get_ticks()


    def draw(self, screen):
        """Draws the player spaceship and the flame if thrusting."""
        if self.visible and (not self.is_invincible or self._blink_toggle): # Only draw if visible AND (not invincible OR blinking)
            ship_points_world = self.get_transformed_points(self._base_ship_points)
            ship_points_tuple = [(p.x, p.y) for p in ship_points_world]
            pygame.draw.polygon(screen, WHITE, ship_points_tuple, 2) # Draw outline with thickness 2

            if self.thrusting:
                flame_points_world = self.get_transformed_points(self._base_flame_points)
                flame_points_tuple = [(p.x, p.y) for p in flame_points_world]
                pygame.draw.polygon(screen, ORANGE, flame_points_tuple) # Draw filled flame

    def shoot(self):
        """Creates a bullet fired from the player's position and direction."""
        if not self.visible: # Cannot shoot if player is not visible/active
            return None

        direction = pygame.math.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle))
        )
        # Start bullet from the ship's "nose" position
        ship_points_world = self.get_transformed_points(self._base_ship_points)
        nose_pos = ship_points_world[0] # Assuming the first point is the nose

        bullet_velocity = direction * BULLET_SPEED
        # The Bullet class is now defined above this, so this line works
        return Bullet(nose_pos, bullet_velocity, self.screen_width, self.screen_height)


class CodeBlock(pygame.sprite.Sprite):
    def __init__(self, position, velocity, size_key, screen_width, screen_height, font_size_multiplier=1.0):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size_key = size_key

        self.base_size = CODE_BLOCK_SIZES[size_key]['base_size']
        self.text_length = CODE_BLOCK_SIZES[size_key]['text_length']
        self.split_count = CODE_BLOCK_SIZES[size_key]['split']
        # Collision radius should roughly match the visual size, estimate based on base_size
        self.collision_radius = self.base_size * 1.5 # Estimate collision radius based on text size

        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(velocity)

        self.font_size = int(self.base_size * font_size_multiplier)
        self.font = pygame.font.Font(None, self.font_size) # Font specific to this block size

        self.text_segment = self.choose_text_segment()
        self.image = self.render_text_surface()
        # Update rect center based on position, width/height come from rendered image
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))


    def choose_text_segment(self):
        """Selects a random snippet and a segment of text from it."""
        snippet = random.choice(PYTHON_CODE_SNIPPETS)
        # Remove leading/trailing whitespace and potentially split into lines
        lines = [line.strip() for line in snippet.splitlines() if line.strip()]
        clean_snippet = " ".join(lines) # Join lines for simpler single-line display for now

        if not clean_snippet: # Handle empty snippets if any exist
            return "pass"

        # Ensure text length doesn't exceed the snippet length
        text_len = min(self.text_length, len(clean_snippet))

        if text_len <= 0:
             return clean_snippet # Just show whatever is there or handle empty

        # Choose a random starting index
        # Make sure the end index doesn't go past the end of the string
        max_start_index = len(clean_snippet) - text_len
        start_index = random.randrange(0, max_start_index + 1) if max_start_index >= 0 else 0


        return clean_snippet[start_index : start_index + text_len]

    def render_text_surface(self):
        """Renders the text segment onto a surface."""
        color = WHITE

        # Handle potential empty string or errors during render
        try:
             text_surface = self.font.render(self.text_segment, True, color)
             # Draw a simple border around the text surface (optional)
             # Ensure surface has size before creating outline_surf
             if text_surface.get_width() == 0 or text_surface.get_height() == 0:
                 print(f"Warning: Rendered text surface is empty for '{self.text_segment}'")
                 # Return a minimal valid surface
                 fallback_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                 pygame.draw.rect(fallback_surf, RED, fallback_surf.get_rect(), 1)
                 return fallback_surf


             outline_surf = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), pygame.SRCALPHA)
             pygame.draw.rect(outline_surf, WHITE, outline_surf.get_rect(), 1)
             outline_surf.blit(text_surface, (2, 2))
             return outline_surf
        except pygame.error as e:
             print(f"Warning: Could not render text '{self.text_segment}': {e}")
             # Return a fallback surface
             fallback_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
             pygame.draw.rect(fallback_surf, RED, fallback_surf.get_rect(), 1)
             return fallback_surf


    def update(self):
        # Update position based on velocity
        self.position += self.velocity

        # Wrap around screen edges
        self.position.x, self.position.y = wrap_position(
            (self.position.x, self.position.y),
            self.screen_width, self.screen_height
        )

        # Update rect's center for collision checks (collide_circle uses this)
        self.rect.center = (int(self.position.x), int(self.position.y))

        # Code blocks don't visually rotate


    def split(self):
        """Does not return new asteroids. Returns the text content for particles."""
        # In this version, split just returns the text to explode
        return self.text_segment

    def get_score(self):
        """Returns the score awarded for destroying this code block."""
        return CODE_BLOCK_SCORES.get(self.size_key, 0)


class Particle(pygame.sprite.Sprite):
    def __init__(self, position, velocity, text, color, lifespan):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(velocity)
        self.text = text
        self.color = color
        self.lifespan = lifespan
        self.spawn_time = pygame.time.get_ticks()

        # Particles are drawn directly, no .image/.rect needed for rendering,
        # but Pygame sprite groups need a dummy image/rect for basic handling.
        # We'll draw the text manually in the main loop's drawing section for this group.
        # The rect is only used for position, size is irrelevant for drawing here
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.position)


    def update(self):
        self.position += self.velocity
        # Apply a little drag
        self.velocity *= 0.98

        # Apply a little gravity (optional, adds downward drift)
        # self.velocity.y += 0.1

        self.rect.center = (int(self.position.x), int(self.position.y)) # Keep rect updated for group management

        # Check lifespan
        if pygame.time.get_ticks() - self.spawn_time > self.lifespan:
            self.kill() # Remove from all groups


# --- Game Functions ---

def create_initial_code_blocks_for_level(level, screen_width, screen_height, player_pos):
    """Creates code blocks for a given level, avoiding the player."""
    code_blocks = []
    # Simple scaling: Add more large blocks each level
    count = CODE_BLOCK_START_COUNT + (level - 1) * 2
    count = min(count, 15) # Cap the max number of initial blocks

    # Potentially increase max speed slightly for higher levels
    current_max_speed = CODE_BLOCK_SPEED_MAX + (level - 1) * 0.5
    current_max_speed = min(current_max_speed, 8) # Cap maximum speed

    for _ in range(count):
        while True:
            pos = pygame.math.Vector2(
                random.randrange(screen_width),
                random.randrange(screen_height)
            )
            # Ensure it's a safe distance from the player spawn point
            safe_distance = max(screen_width, screen_height) / 3 - (level - 1) * 10
            safe_distance = max(safe_distance, 100) # Minimum safe distance
            if (pos - player_pos).length() > safe_distance:
                break

        angle = random.uniform(0, 360)
        speed = random.uniform(CODE_BLOCK_SPEED_MIN, current_max_speed)
        vel = pygame.math.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * speed

        code_blocks.append(CodeBlock(pos, vel, 'large', screen_width, screen_height))
    return code_blocks


def draw_game_over(screen):
    """Draws a simple game over message."""
    font = pygame.font.Font(None, 74) # Default font, size 74
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    font_small = pygame.font.Font(None, 36)
    restart_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)


# --- Game Loop State Management ---
def reset_game(screen_width, screen_height, all_sprites, code_blocks, bullets, players, particles):
    """Resets all game variables and sprites for a new game."""
    global score, lives, level, game_over, waiting_to_start_level, level_start_time

    score = 0
    lives = PLAYER_START_LIVES
    level = 1
    game_over = False
    waiting_to_start_level = True # Start by waiting for the first level
    level_start_time = pygame.time.get_ticks() # Start timer

    # Clear existing sprites from ALL relevant groups
    # Using empty() removes from the group and calls kill(), which removes from all_sprites
    all_sprites.empty() # Clear all sprites first for a clean slate
    code_blocks.empty()
    bullets.empty()
    players.empty()
    particles.empty()

    # Create player (player is created but invisible/invincible initially)
    player = Player(screen_width, screen_height)
    all_sprites.add(player)
    players.add(player)

    # Initial code blocks will be created after the wait period in start_level

    return player # Return the created player instance

def start_level(screen_width, screen_height, level, player, all_sprites, code_blocks, bullets, particles):
    """Prepares for and starts a new level."""
    global waiting_to_start_level, level_start_time

    print(f"Starting Level {level}") # Debugging

    waiting_to_start_level = False # Game is no longer waiting
    level_start_time = 0 # Reset timer

    # Clear old game objects by emptying their specific groups.
    # Calling empty() on a group also removes the sprites from any other group
    # they belong to, including all_sprites.
    code_blocks.empty()
    bullets.empty()
    particles.empty()
    # The player sprite should persist and not be removed here.

    # Respawn player if needed (handled in reset_game or player_hit)
    # Ensure player is visible and invincible for the start of the level
    player.position = pygame.math.Vector2(screen_width // 2, screen_height // 2)
    player.velocity = pygame.math.Vector2(0, 0)
    player.activate_invincibility() # Grant invincibility at level start

    # Create new code blocks for this level
    initial_code_blocks = create_initial_code_blocks_for_level(level, screen_width, screen_height, player.position)
    all_sprites.add(initial_code_blocks)
    code_blocks.add(initial_code_blocks)


def player_hit(player, game_state, all_sprites, code_blocks, bullets, particles):
    """Handles the player being hit by a code block."""
    global lives, game_over, waiting_to_start_level, level_start_time

    if player.is_invincible:
        return # Do nothing if player is invincible

    lives -= 1
    print(f"Player Hit! Lives remaining: {lives}") # Debugging

    if lives <= 0:
        game_over = True
        waiting_to_start_level = True # Use the wait state to show Game Over
        level_start_time = pygame.time.get_ticks()
        player.visible = False # Hide player on death
        # Clear remaining game objects on screen
        # We need to clear CodeBlocks, Bullets, Particles
        code_blocks.empty()
        bullets.empty()
        particles.empty()
    else:
        # Player loses a life but game continues
        # Clear existing objects
        code_blocks.empty()
        bullets.empty()
        particles.empty()

        # Reset player position and grant temporary invincibility
        player.position = pygame.math.Vector2(game_state['screen_width'] // 2, game_state['screen_height'] // 2)
        player.velocity = pygame.math.Vector2(0, 0)
        player.activate_invincibility()

        waiting_to_start_level = True # Wait before next wave appears
        level_start_time = pygame.time.get_ticks()


# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Code Asteroids")
    clock = pygame.time.Clock()

    # Global game state variables
    global score, lives, level, game_over, waiting_to_start_level, level_start_time

    # Sprite groups
    all_sprites = pygame.sprite.Group()   # All sprites that need update()
    code_blocks = pygame.sprite.Group() # CodeBlocks (formerly asteroids) for draw() and collision
    bullets = pygame.sprite.Group()       # Bullets for draw() and collision
    players = pygame.sprite.Group()       # Player(s) for collision
    particles = pygame.sprite.Group()     # Particles for draw() and update()

    # Dictionary to pass game state info easily
    game_state = {
        'screen_width': WIDTH,
        'screen_height': HEIGHT,
        # Add other state if needed
    }

    # --- Initial Game Setup ---
    # Pass all relevant groups to reset_game
    player = reset_game(WIDTH, HEIGHT, all_sprites, code_blocks, bullets, players, particles)


    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Player controls only during active gameplay
                if not game_over and not waiting_to_start_level:
                    if event.key == pygame.K_LEFT:
                        player.rotating_left = True
                    if event.key == pygame.K_RIGHT:
                        player.rotating_right = True
                    if event.key == pygame.K_UP:
                        player.thrusting = True
                    if event.key == pygame.K_SPACE:
                         bullet = player.shoot()
                         if bullet:
                             all_sprites.add(bullet)
                             bullets.add(bullet)

                # Game over restart/quit
                if game_over:
                    # Only allow restart/quit after the game over message has been shown for a bit
                    if pygame.time.get_ticks() - level_start_time > GAME_OVER_WAIT:
                        if event.key == pygame.K_r: # Restart
                             # Pass all relevant groups to reset_game
                            player = reset_game(WIDTH, HEIGHT, all_sprites, code_blocks, bullets, players, particles)
                        elif event.key == pygame.K_q: # Quit
                             running = False

            if event.type == pygame.KEYUP:
                if not game_over and not waiting_to_start_level:
                    if event.key == pygame.K_LEFT:
                        player.rotating_left = False
                    if event.key == pygame.K_RIGHT:
                        player.rotating_right = False
                    if event.key == pygame.K_UP:
                        player.thrusting = False


        # --- Game Logic (Updates) ---

        # Handle waiting state
        if waiting_to_start_level:
            if not game_over and pygame.time.get_ticks() - level_start_time > WAIT_FOR_LEVEL_START:
                # Start the level, passing all relevant groups
                start_level(WIDTH, HEIGHT, level, player, all_sprites, code_blocks, bullets, particles)
            # If game_over, we wait until GAME_OVER_WAIT duration is over before allowing restart/quit keypresses
        else: # Game is in active play
            # Update all sprites
            all_sprites.update() # Updates player, code blocks, bullets, AND particles

            # Check for collisions: Bullet vs CodeBlock
            # Use collide_circle for collision check
            collisions = pygame.sprite.groupcollide(bullets, code_blocks, True, True, collided=pygame.sprite.collide_circle)

            # Process code block collisions (explode into particles and add score)
            for bullet, hit_blocks in collisions.items():
                for block in hit_blocks:
                    score += block.get_score() # Add score for destroyed block

                    # Create particles from the block's text segment
                    block_text = block.split() # Get the text segment from the destroyed block
                    num_particles = int(len(block_text) * PARTICLE_COUNT_MULTIPLIER)
                    # Ensure at least one particle if there was any text
                    if num_particles == 0 and len(block_text) > 0: num_particles = 1
                    # Cap max particles per explosion to prevent lag if a huge string somehow gets through
                    num_particles = min(num_particles, 50)


                    for i in range(num_particles):
                        char_index = i % len(block_text) if len(block_text) > 0 else 0 # Cycle through characters
                        char = block_text[char_index] if len(block_text) > 0 else " " # Use a space if text is empty

                        # Random velocity spreading out from the block's position
                        angle = random.uniform(0, 360)
                        speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
                        vel = pygame.math.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * speed

                        # Slight random offset from the center for particle spawn
                        offset_amount = block.collision_radius * 0.5
                        spawn_pos = block.position + pygame.math.Vector2(random.uniform(-offset_amount, offset_amount), random.uniform(-offset_amount, offset_amount))

                        particle = Particle(spawn_pos, vel, char, YELLOW, PARTICLE_LIFESPAN)
                        all_sprites.add(particle)
                        particles.add(particle)


            # Check for collisions: Player vs CodeBlock
            if not player.is_invincible and not game_over:
                player_collisions = pygame.sprite.spritecollide(player, code_blocks, False, collided=pygame.sprite.collide_circle)
                if player_collisions:
                    # Pass the particles group to player_hit so it can clear them
                    player_hit(player, game_state, all_sprites, code_blocks, bullets, particles)


            # Check for level completion (all code blocks destroyed)
            if not code_blocks and not game_over and not waiting_to_start_level:
                 level += 1 # Advance level
                 waiting_to_start_level = True # Enter wait state before next level
                 level_start_time = pygame.time.get_ticks()
                 player.visible = False # Hide player during the wait


        # --- Drawing ---
        screen.fill(BLACK) # Fill background

        # Draw sprites that use the standard .image and .rect (CodeBlocks, Bullets)
        # CodeBlocks now handle rendering their text onto their image surface
        code_blocks.draw(screen)
        bullets.draw(screen)

        # Draw the player using its custom draw method
        player.draw(screen) # Player drawing handles its own visibility/blinking

        # Draw particles manually, as they don't have standard images for group.draw
        # Particles draw their single character text
        for particle in particles:
             # Ensure the particle still exists (wasn't killed in the same frame's update)
             if particle.alive():
                 draw_text(screen, particle.text, 12, particle.color, particle.position.x, particle.position.y, antialias=False) # Use small font, no antialiasing for retro look


        # Draw UI (Score, Lives, Level)
        draw_text(screen, f"Score: {score}", 30, WHITE, 10, 10)
        draw_player_lives(screen, lives, WIDTH - (PLAYER_SIZE * 0.7 * 2 * PLAYER_START_LIVES + 5 * (PLAYER_START_LIVES - 1) + 10), 10) # Position lives near top right
        draw_text(screen, f"Level: {level}", 30, WHITE, 10, 40)


        # Draw Game Over or Level Start messages
        if game_over:
            draw_game_over(screen)
        elif waiting_to_start_level:
             # Display level number briefly at the start of a level wait
             # Only show the message if not game over
             if pygame.time.get_ticks() - level_start_time < WAIT_FOR_LEVEL_START * 0.75 and not game_over: # Show for 3/4 of the wait time
                level_font = pygame.font.Font(None, 74)
                level_text = level_font.render(f"Level {level}", True, WHITE)
                level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(level_text, level_rect)


        # --- Update Display ---
        pygame.display.flip()

        # --- Cap Frame Rate ---
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# --- Run the game ---
if __name__ == "__main__":
    # Initialize global variables before calling main
    score = 0
    lives = PLAYER_START_LIVES
    level = 1
    game_over = False
    waiting_to_start_level = True
    level_start_time = 0 # Will be set in reset_game

    main()