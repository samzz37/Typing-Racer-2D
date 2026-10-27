"""
Typing Racer 2D - Car Model & 2D Arcade Renderer
Renders sleek 2D side-view sports cars with shadows, wheels, headlights,
neon underglow, and exhaust particle emitters.
"""
import math
import random
import pygame
from typing import Dict, Any, Tuple
from core.config import (
    TRACK_Y_START, LANE_HEIGHT, CAR_PALETTES,
    COLOR_TEXT_WHITE, COLOR_ACCENT_PRIMARY
)
from models.particle import ParticleEmitter


class Car:
    """Represents a race car (player or AI) on a dedicated horizontal lane."""
    def __init__(
        self,
        name: str,
        lane_index: int,
        palette_index: int,
        is_player: bool = False,
        emitter: ParticleEmitter = None
    ):
        self.name = name
        self.lane_index = lane_index
        self.palette_index = palette_index % len(CAR_PALETTES)
        self.palette = CAR_PALETTES[self.palette_index]
        self.is_player = is_player
        self.emitter = emitter

        # Lane dimensions
        self.lane_y = TRACK_Y_START + lane_index * LANE_HEIGHT
        self.center_y = self.lane_y + (LANE_HEIGHT // 2)

        # Race progression
        self.progress: float = 0.0          # 0.0 to 1.0 (finish line)
        self.world_x: float = 0.0           # World coordinate along track
        self.screen_x: float = 120.0        # Smoothly interpolated screen X
        self.target_screen_x: float = 120.0
        
        # Telemetry & performance
        self.current_wpm: float = 0.0
        self.current_speed_px_sec: float = 0.0
        self.nitro_active: bool = False
        self.finished: bool = False
        self.finish_time: float = 0.0
        self.placement: int = 0

        # Animation states
        self.wheel_angle: float = 0.0
        self.engine_shake_y: float = 0.0
        self.shake_time: float = random.uniform(0, 10)

        # Car dimensions
        self.length = 82
        self.height = 30

    def set_palette(self, index: int):
        """Updates car color palette."""
        self.palette_index = index % len(CAR_PALETTES)
        self.palette = CAR_PALETTES[self.palette_index]

    def update_motion(
        self,
        dt: float,
        progress: float,
        current_wpm: float,
        nitro: bool,
        track_start_x: float,
        track_finish_x: float
    ):
        """
        Updates car progress, smooth position lerp, and wheel animation.
        """
        self.progress = max(0.0, min(1.0, progress))
        self.current_wpm = current_wpm
        self.nitro_active = nitro

        # Target X on the visible track screen
        total_track_width = track_finish_x - track_start_x
        self.target_screen_x = track_start_x + (self.progress * total_track_width)

        # Smooth position interpolation (spring lerp)
        lerp_speed = 9.0 if self.is_player else 6.0
        self.screen_x += (self.target_screen_x - self.screen_x) * min(1.0, lerp_speed * dt)

        # Wheel rotation proportional to movement & typing speed
        speed_factor = max(15.0, self.current_wpm * 3.5)
        self.wheel_angle = (self.wheel_angle + speed_factor * dt * 25.0) % 360.0

        # Subtle micro-engine vibration
        self.shake_time += dt * 30.0
        self.engine_shake_y = math.sin(self.shake_time) * (0.8 if self.nitro_active else 0.4)

        # Particle effects
        if self.emitter:
            exhaust_x = self.screen_x - 38
            exhaust_y = self.center_y + 8 + self.engine_shake_y
            
            if self.nitro_active:
                glow_col = self.palette["glow"]
                self.emitter.emit_nitro_trail(exhaust_x, exhaust_y, glow_col)
            elif self.current_wpm > 20:
                self.emitter.emit_exhaust_smoke(exhaust_x, exhaust_y, intensity=0.6)

    def draw(self, surface: pygame.Surface, font_small: pygame.font.Font):
        """Renders the side-view arcade car with details."""
        car_x = int(self.screen_x)
        car_y = int(self.center_y + self.engine_shake_y)

        # 1. Asphalt Drop Shadow
        shadow_w = self.length + 12
        shadow_h = 14
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 140), (0, 0, shadow_w, shadow_h))
        surface.blit(shadow_surf, (car_x - shadow_w // 2, car_y + self.height // 2 - 2))

        # 2. Neon Underglow
        glow_color = self.palette["glow"]
        glow_w = self.length + 8
        glow_h = 18
        glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        glow_alpha = 90 if self.nitro_active else (65 if self.is_player else 35)
        pygame.draw.ellipse(glow_surf, (*glow_color[:3], glow_alpha), (0, 0, glow_w, glow_h))
        surface.blit(glow_surf, (car_x - glow_w // 2, car_y + self.height // 2 - 6))

        # 3. Headlight Light Beam (casting forward to the right)
        beam_length = 160 if self.nitro_active else 110
        beam_surf = pygame.Surface((beam_length, 45), pygame.SRCALPHA)
        beam_poly = [
            (0, 20),
            (beam_length, 0),
            (beam_length, 45),
            (0, 25)
        ]
        beam_alpha = 45 if self.nitro_active else 28
        pygame.draw.polygon(beam_surf, (255, 255, 230, beam_alpha), beam_poly)
        surface.blit(beam_surf, (car_x + self.length // 2 - 4, car_y - 12))

        # 4. Car Body Chassis (Side View Polygon)
        body_col = self.palette["body"]
        highlight_col = self.palette["highlight"]
        
        # Coordinates relative to car center
        # Nose is at +length//2, Tail is at -length//2
        half_l = self.length // 2
        half_h = self.height // 2

        # Aerodynamic Sports Coupe Silhouette
        chassis_points = [
            (car_x - half_l + 2, car_y + half_h - 4),       # Rear bottom bumper
            (car_x + half_l - 4, car_y + half_h - 4),       # Front bottom splitter
            (car_x + half_l, car_y + 2),                    # Front bumper tip
            (car_x + half_l - 12, car_y - 4),               # Hood start
            (car_x + half_l - 28, car_y - half_h + 3),      # Windshield base
            (car_x - 4, car_y - half_h),                    # Roof top
            (car_x - half_l + 18, car_y - half_h + 4),      # Rear window slope
            (car_x - half_l + 4, car_y - 2),                # Trunk deck
            (car_x - half_l, car_y + 4)                     # Rear fascia
        ]

        # Draw main chassis
        pygame.draw.polygon(surface, body_col, chassis_points)
        # Chassis border outline
        pygame.draw.polygon(surface, (15, 18, 26), chassis_points, 2)

        # 5. Cockpit & Tinted Windshield Glass
        cockpit_points = [
            (car_x + half_l - 30, car_y - 3),
            (car_x + half_l - 31, car_y - half_h + 5),
            (car_x - 3, car_y - half_h + 2),
            (car_x - half_l + 20, car_y - 3)
        ]
        # Glass fill
        glass_col = (40, 55, 80)
        pygame.draw.polygon(surface, glass_col, cockpit_points)
        # Windshield highlight glare streak
        pygame.draw.line(surface, (180, 215, 240), (car_x + 5, car_y - half_h + 4), (car_x - 12, car_y - 2), 2)

        # 6. Racing Stripe / Body Highlight
        stripe_points = [
            (car_x - half_l + 5, car_y + 3),
            (car_x + half_l - 6, car_y + 3),
            (car_x + half_l - 9, car_y),
            (car_x - half_l + 8, car_y)
        ]
        pygame.draw.polygon(surface, highlight_col, stripe_points)

        # 7. Rear Spoiler Wing
        spoiler_poly = [
            (car_x - half_l - 4, car_y - 12),
            (car_x - half_l + 10, car_y - 12),
            (car_x - half_l + 8, car_y - 8),
            (car_x - half_l - 6, car_y - 8)
        ]
        pygame.draw.polygon(surface, highlight_col, spoiler_poly)
        # Spoiler struts
        pygame.draw.line(surface, (30, 35, 45), (car_x - half_l + 2, car_y - 8), (car_x - half_l + 2, car_y - 1), 2)
        pygame.draw.line(surface, (30, 35, 45), (car_x - half_l + 6, car_y - 8), (car_x - half_l + 6, car_y - 1), 2)

        # 8. Front Headlight & Taillight
        # Front light
        pygame.draw.rect(surface, (255, 255, 240), (car_x + half_l - 5, car_y - 3, 5, 5), border_radius=1)
        # Rear light
        pygame.draw.rect(surface, (255, 30, 50), (car_x - half_l - 1, car_y + 1, 4, 6), border_radius=1)

        # 9. Wheels & Spinning Rims
        wheel_radius = 8
        rear_wheel_x = car_x - half_l + 18
        front_wheel_x = car_x + half_l - 18
        wheel_y = car_y + half_h - 2

        for wx in [rear_wheel_x, front_wheel_x]:
            # Tire rubber
            pygame.draw.circle(surface, (25, 28, 35), (wx, wheel_y), wheel_radius)
            # Rim edge
            pygame.draw.circle(surface, (180, 190, 205), (wx, wheel_y), wheel_radius - 2)
            # Inner hub
            pygame.draw.circle(surface, (40, 45, 55), (wx, wheel_y), wheel_radius - 4)
            # Rotating rim spokes
            rad = math.radians(self.wheel_angle)
            for spoke_offset in [0, 90, 180, 270]:
                spoke_rad = rad + math.radians(spoke_offset)
                sx = wx + math.cos(spoke_rad) * (wheel_radius - 2)
                sy = wheel_y + math.sin(spoke_rad) * (wheel_radius - 2)
                pygame.draw.line(surface, (230, 235, 245), (wx, wheel_y), (sx, sy), 1)

        # 10. Floating Driver Label & Telemetry Badge
        badge_y = car_y - half_h - 22
        label_text = "YOU" if self.is_player else self.name
        wpm_str = f"{int(self.current_wpm)} WPM"
        badge_str = f"{label_text} [{wpm_str}]" if self.current_wpm > 0 else label_text

        text_surf = font_small.render(badge_str, True, COLOR_TEXT_WHITE)
        pad_x, pad_y = 6, 2
        badge_rect = pygame.Rect(
            car_x - text_surf.get_width() // 2 - pad_x,
            badge_y - pad_y,
            text_surf.get_width() + pad_x * 2,
            text_surf.get_height() + pad_y * 2
        )

        # Badge background
        bg_col = (0, 140, 180, 220) if self.is_player else (25, 30, 42, 210)
        border_col = COLOR_ACCENT_PRIMARY if self.is_player else (70, 80, 105)
        
        badge_bg_surf = pygame.Surface((badge_rect.width, badge_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(badge_bg_surf, bg_col, (0, 0, badge_rect.width, badge_rect.height), border_radius=4)
        pygame.draw.rect(badge_bg_surf, border_col, (0, 0, badge_rect.width, badge_rect.height), width=1, border_radius=4)
        surface.blit(badge_bg_surf, badge_rect.topleft)
        surface.blit(text_surf, (car_x - text_surf.get_width() // 2, badge_y))

        # Nitro fire burst indicator on badge when active
        if self.nitro_active:
            nitro_tag = font_small.render("NITRO!", True, (255, 225, 0))
            surface.blit(nitro_tag, (badge_rect.right + 4, badge_y))
