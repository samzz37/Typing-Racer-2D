"""
Typing Racer 2D - Garage Screen
Allows car customization, paint job selection, neon underglow tuning,
and interactive showroom test drive with audio.
"""
import pygame
from typing import Dict, Any, Optional
from core.config import (
    CAR_PALETTES, COLOR_BG_DARK, COLOR_PANEL_BG,
    COLOR_PANEL_BORDER, COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
)
from database.db_manager import DatabaseManager
from models.car import Car
from models.particle import ParticleEmitter
from ui.components import Button


class GarageScreen:
    """Arcade Garage for vehicle customization and showroom testing."""
    def __init__(
        self,
        user: Dict[str, Any],
        db: DatabaseManager,
        fonts: Dict[str, pygame.font.Font],
        sound_engine
    ):
        self.user = user
        self.db = db
        self.fonts = fonts
        self.sound_engine = sound_engine

        self.current_palette_idx = self.user.get("preferred_car_color", 0) % len(CAR_PALETTES)

        # Particle emitter for showroom nitro rev test
        self.emitter = ParticleEmitter()

        # Preview car instance centered in showroom
        self.preview_car = Car(
            name=self.user.get("full_name", "YOU"),
            lane_index=0,
            palette_index=self.current_palette_idx,
            is_player=True,
            emitter=self.emitter
        )
        self.preview_car.screen_x = 640.0
        self.preview_car.center_y = 260.0

        # Action signal
        self.action: Optional[str] = None

        # Build paint color selection buttons
        self.paint_buttons = []
        btn_w = 160
        btn_h = 48
        start_x = (1280 - (btn_w * 3 + 24 * 2)) // 2
        start_y = 390

        for i, pal in enumerate(CAR_PALETTES):
            col_x = start_x + (i % 3) * (btn_w + 24)
            col_y = start_y + (i // 3) * (btn_h + 20)
            btn = Button(
                pygame.Rect(col_x, col_y, btn_w, btn_h),
                pal["name"],
                self.fonts["small"],
                bg_color=(25, 30, 44),
                hover_color=(38, 46, 68),
                border_radius=8,
                on_click=lambda idx=i: self._select_palette(idx)
            )
            self.paint_buttons.append((btn, pal))

        # Showroom interaction buttons
        cx = 1280 // 2
        self.btn_test_nitro = Button(
            pygame.Rect(cx - 210, 550, 190, 46),
            ">> TEST NITRO <<",
            self.fonts["medium"],
            bg_color=(255, 60, 80),
            hover_color=(255, 90, 110),
            border_radius=8,
            on_click=self._trigger_nitro_test
        )

        self.btn_save = Button(
            pygame.Rect(cx + 20, 550, 190, 46),
            "SAVE & APPLY",
            self.fonts["medium"],
            bg_color=(46, 213, 115),
            hover_color=(60, 235, 130),
            text_color=(10, 14, 24),
            border_radius=8,
            on_click=self._save_car_customization
        )

        self.btn_back = Button(
            pygame.Rect(40, 25, 140, 38),
            "<- MAIN MENU",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(38, 46, 68),
            border_radius=6,
            on_click=lambda: self._set_action("MENU")
        )

        self.nitro_test_timer = 0.0

    def _select_palette(self, idx: int):
        self.current_palette_idx = idx
        self.preview_car.set_palette(idx)
        if self.sound_engine:
            self.sound_engine.play_click()

    def _trigger_nitro_test(self):
        self.nitro_test_timer = 1.8
        if self.sound_engine:
            self.sound_engine.play_nitro()

    def _save_car_customization(self):
        self.user["preferred_car_color"] = self.current_palette_idx
        user_id = self.user.get("id")
        if user_id:
            self.db.update_user_car_color(user_id, self.current_palette_idx)
        if self.sound_engine:
            self.sound_engine.play_countdown_go()
        self._set_action("MENU")

    def _set_action(self, act: str):
        self.action = act
        if self.sound_engine:
            self.sound_engine.play_click()

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handles paint selection and buttons."""
        self.btn_back.handle_event(event, self.sound_engine)
        self.btn_test_nitro.handle_event(event, self.sound_engine)
        self.btn_save.handle_event(event, self.sound_engine)

        for btn, _ in self.paint_buttons:
            btn.handle_event(event, self.sound_engine)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "MENU"

        act = self.action
        self.action = None
        return act

    def update(self, dt: float):
        """Updates particle animations and preview car motion."""
        self.emitter.update(dt)
        self.btn_back.update(dt)
        self.btn_test_nitro.update(dt)
        self.btn_save.update(dt)
        for btn, _ in self.paint_buttons:
            btn.update(dt)

        # Showroom nitro test
        is_nitro = False
        if self.nitro_test_timer > 0.0:
            self.nitro_test_timer -= dt
            is_nitro = True

        # Keep car centered on preview turntable with subtle idle wheel spin
        self.preview_car.center_y = 260.0
        self.preview_car.update_motion(
            dt=dt,
            progress=0.5,
            current_wpm=85.0 if is_nitro else 30.0,
            nitro=is_nitro,
            track_start_x=640.0,
            track_finish_x=640.0
        )

    def draw(self, surface: pygame.Surface):
        """Draws showroom turntable, preview car, and color palette cards."""
        surface.fill(COLOR_BG_DARK)

        # Background grid
        for x in range(0, surface.get_width(), 60):
            pygame.draw.line(surface, (20, 24, 36), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 60):
            pygame.draw.line(surface, (20, 24, 36), (0, y), (surface.get_width(), y), 1)

        # Back Button
        self.btn_back.draw(surface)

        # Header Title
        title_surf = self.fonts["title"].render("CHAMPIONSHIP GARAGE", True, COLOR_ACCENT_PRIMARY)
        surface.blit(title_surf, title_surf.get_rect(center=(surface.get_width() // 2, 45)))

        sub_surf = self.fonts["medium"].render("CUSTOMIZE VEHICLE LIVERY & PERFORMANCE NITRO", True, COLOR_ACCENT_GOLD)
        surface.blit(sub_surf, sub_surf.get_rect(center=(surface.get_width() // 2, 85)))

        # 1. Showroom Turntable Stage
        stage_rect = pygame.Rect(340, 140, 600, 210)
        pygame.draw.rect(surface, (18, 22, 34), stage_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, stage_rect, width=1, border_radius=12)

        # Showroom floor spotlight ellipse
        spot_surf = pygame.Surface((440, 80), pygame.SRCALPHA)
        pal = CAR_PALETTES[self.current_palette_idx]
        glow = pal["glow"]
        pygame.draw.ellipse(spot_surf, (*glow, 45), (0, 0, 440, 80))
        surface.blit(spot_surf, (stage_rect.centerx - 220, 245))

        # 2. Particle Effects & Car
        self.emitter.draw(surface)
        self.preview_car.draw(surface, self.fonts["small"])

        # 3. Paint Buttons Grid
        for i, (btn, pal) in enumerate(self.paint_buttons):
            is_active = (i == self.current_palette_idx)
            
            # Button color indicator swatch
            pygame.draw.rect(surface, (22, 26, 38), btn.rect, border_radius=8)
            border_col = pal["body"] if is_active else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, border_col, btn.rect, width=2 if is_active else 1, border_radius=8)

            # Circular color chip
            pygame.draw.circle(surface, pal["body"], (btn.rect.x + 22, btn.rect.centery), 8)
            pygame.draw.circle(surface, pal["highlight"], (btn.rect.x + 22, btn.rect.centery), 4)

            name_col = COLOR_TEXT_WHITE if is_active else COLOR_TEXT_MUTED
            n_surf = self.fonts["small"].render(pal["name"], True, name_col)
            surface.blit(n_surf, (btn.rect.x + 38, btn.rect.centery - n_surf.get_height() // 2))

        # 4. Action Buttons
        self.btn_test_nitro.draw(surface)
        self.btn_save.draw(surface)
