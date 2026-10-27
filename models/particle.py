"""
Typing Racer 2D - Particle System
Handles exhaust smoke, nitro boost fire trails, victory confetti, and speed sparks.
"""
import random
import pygame
from typing import List, Tuple


class Particle:
    """A single particle with position, velocity, color, life, and fade."""
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        life: float,
        size: float = 3.0,
        decay: float = 1.0,
        gravity: float = 0.0,
        shape: str = "circle"
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.decay = decay
        self.gravity = gravity
        self.shape = shape
        self.alpha = 255

    def update(self, dt: float) -> bool:
        """Updates particle physics. Returns False if dead."""
        self.life -= self.decay * dt
        if self.life <= 0:
            return False

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt

        # Calculate fade alpha
        progress = max(0.0, self.life / self.max_life)
        self.alpha = int(255 * progress)
        return True

    def draw(self, surface: pygame.Surface, camera_offset_x: float = 0.0):
        """Draws particle to surface with alpha."""
        draw_x = int(self.x - camera_offset_x)
        draw_y = int(self.y)

        if not (-50 <= draw_x <= surface.get_width() + 50 and -50 <= draw_y <= surface.get_height() + 50):
            return

        current_size = max(1, int(self.size * (self.life / self.max_life)))

        if self.shape == "rect":
            # For confetti
            s = pygame.Surface((current_size * 2, current_size * 1.2), pygame.SRCALPHA)
            s.fill((*self.color[:3], self.alpha))
            surface.blit(s, (draw_x - current_size, draw_y - current_size // 2))
        else:
            # Circle
            s = pygame.Surface((current_size * 2 + 2, current_size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], self.alpha), (current_size + 1, current_size + 1), current_size)
            surface.blit(s, (draw_x - current_size - 1, draw_y - current_size - 1))


class ParticleEmitter:
    """Manages active particles across the game."""
    def __init__(self):
        self.particles: List[Particle] = []

    def emit_exhaust_smoke(self, x: float, y: float, intensity: float = 1.0):
        """Emits subtle exhaust smoke behind a car."""
        count = int(1 * intensity)
        for _ in range(max(1, count)):
            vx = random.uniform(-60, -30)
            vy = random.uniform(-10, 10)
            life = random.uniform(0.3, 0.6)
            size = random.uniform(3, 6)
            gray = random.randint(140, 200)
            self.particles.append(Particle(x, y, vx, vy, (gray, gray, gray), life, size=size, decay=1.2))

    def emit_nitro_trail(self, x: float, y: float, color: Tuple[int, int, int] = (0, 229, 255)):
        """Emits fiery blue/cyan or orange nitro boost jet stream."""
        for _ in range(4):
            vx = random.uniform(-180, -100)
            vy = random.uniform(-15, 15)
            life = random.uniform(0.2, 0.45)
            size = random.uniform(4, 8)
            # Mix with white hot center
            c = (240, 255, 255) if random.random() < 0.35 else color
            self.particles.append(Particle(x, y, vx, vy, c, life, size=size, decay=1.8))

    def emit_confetti(self, x: float, y: float, count: int = 40):
        """Emits celebratory victory confetti burst."""
        colors = [
            (255, 75, 75), (0, 229, 255), (255, 215, 0),
            (46, 213, 115), (175, 75, 255), (255, 150, 50)
        ]
        for _ in range(count):
            vx = random.uniform(-120, 120)
            vy = random.uniform(-250, -50)
            life = random.uniform(1.5, 3.0)
            size = random.uniform(3, 6)
            c = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, c, life, size=size, decay=0.8, gravity=180.0, shape="rect"))

    def update(self, dt: float):
        """Updates all living particles and cleans up dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, camera_offset_x: float = 0.0):
        """Draws all particles."""
        for p in self.particles:
            p.draw(surface, camera_offset_x)

    def clear(self):
        """Removes all particles."""
        self.particles.clear()
