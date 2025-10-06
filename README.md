# My Python Game Development Journey: From Bouncing Shapes to a Mini-RPG

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.5-blue?logo=pygame)
![Arcade](https://img.shields.io/badge/Arcade-2.6-blue)

Welcome to my personal collection of game development projects, built with Python. This repository documents my learning journey, starting with the simple fundamentals of graphics and animation and progressing to more complex game mechanics, state management, and object-oriented design.

Each script represents a specific milestone in understanding how to bring interactive experiences to life with code.

---

### The Games: A Story of Progression

#### 1. `bouncing_rectangle.py` & `tanks.py` (Using the Arcade Library)
*   **Concept:** The absolute fundamentals. These scripts explore the basics of the Python `arcade` library.
*   **Core Skills Demonstrated:**
    *   **Window & Game Loop:** Setting up a game window and understanding the `on_draw` and `on_update` loop.
    *   **Basic Drawing:** Using the library's built-in functions to draw simple shapes (`draw_rectangle_filled`, `draw_rectangle_outline`).
    *   **Object-Oriented Basics:** Creating a simple `Item` class to manage a single object's state (position, velocity).
    *   **State & Animation:** Implementing simple physics for movement and boundary collision (bouncing).
*   **Purpose:** These were my "Hello, World!" for game development, proving I could get something moving on a screen.

#### 2. `asteroid.py` (Using the Pygame Library)
*   **Concept:** A complete, playable arcade game inspired by the classic "Asteroids," but with a fun twist: the asteroids are replaced by floating blocks of Python code.
*   **Core Skills Demonstrated:**
    *   **Advanced OOP:** Sophisticated classes for `Player`, `Bullet`, and `CodeBlock` sprites, each with its own state and methods.
    *   **Physics & Vector Math:** Implementing player thrust, rotation, velocity, and screen-wrapping using `pygame.math.Vector2`.
    *   **State Management:** Handling complex game states like "waiting to start," "invincibility," and "game over."
    *   **Collision Detection:** Using `pygame.sprite.groupcollide` and `collide_circle` for efficient hit detection.
    *   **Particle Effects:** Creating a dynamic particle system to "explode" destroyed code blocks into their individual characters.
    *   **Dynamic Content:** Randomly sampling Python code snippets to create unique and varied "asteroids" for each playthrough.

#### 3. `mine.py` (Using the Pygame Library)
*   **Concept:** The most complex project—a top-down, dungeon-crawling mini-RPG ("Crab's Dungeon").
*   **Core Skills Demonstrated:**
    *   **Complex Game Orchestration:** A main `Game` class that manages all sprites, game states (win/loss), and the main game loop.
    *   **AI and Pathfinding:** A simple but effective "chase" AI for the `Enemy` class, which moves towards the player within a vision radius.
    *   **Combat Mechanics:** Implementing both ranged (`WaterBubble`) and melee (`ClawSwipe`) attacks with cooldowns.
    *   **Tile-Based Collision:** Creating a `Wall` class and implementing robust collision detection to prevent characters from moving through the environment.
    *   **Advanced UI:** Drawing dynamic UI elements like player/enemy health bars and ability cooldown timers.
    *   **Event Handling:** Managing a variety of user inputs for movement and combat abilities.

---

### How to Run

#### Prerequisites
- Python 3.x
- Required libraries: `pygame` and `arcade`

Install with pip:
```bash
pip install pygame arcade
