"""
Typing Racer 2D - Race Results Screen
Displays the 3D-styled arcade podium (1st, 2nd, 3rd), comprehensive player
telemetry (WPM, Net WPM, Accuracy, Time, Mistakes), and rematch options.
"""
import pygame
from typing import Dict, Any, Optional
from core.config import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_CHAR_CORRECT, COLOR_CHAR_WRONG
)
from models.particle import ParticleEmitter
from ui.components import Button


class ResultsScreen:
    """Arcade Podium & Telemetry Results Screen."""
    def __init__(
        self,
        summary_data: Dict[str, Any],
        fonts: Dict[str, pygame.font.Font],
        sound_engine
    ):
        self.data = summary_data
        self.fonts = fonts
        self.sound_engine = sound_engine

        # Confetti emitter
        self.emitter = ParticleEmitter()
        self.emitter.emit_confetti(640, 200, count=70)

        # Buttons
        cx = 1280 // 2
        self.btn_replay = Button(
            pygame.Rect(cx - 280, 620, 170, 46),
            "RACE AGAIN",
            self.fonts["medium"],
            bg_color=(0, 180, 220),
            hover_color=(0, 220, 255),
            text_color=(10, 14, 24),
            border_radius=8,
            on_click=lambda: self._set_action("REPLAY")
        )

        self.btn_leaderboard = Button(
            pygame.Rect(cx - 90, 620, 180, 46),
            "LEADERBOARD",
            self.fonts["medium"],
            bg_color=(35, 42, 60),
            hover_color=(50, 60, 85),
            border_radius=8,
            on_click=lambda: self._set_action("LEADERBOARD")
        )

        self.btn_menu = Button(
            pygame.Rect(cx + 110, 620, 170, 46),
            "MAIN MENU",
            self.fonts["medium"],
            bg_color=(25, 30, 44),
            hover_color=(38, 46, 68),
            border_radius=8,
            on_click=lambda: self._set_action("MENU")
        )

        self.action: Optional[str] = None

    def _set_action(self, act: str):
        self.action = act
        if self.sound_engine:
            self.sound_engine.play_click()

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handles button clicks."""
        self.btn_replay.handle_event(event, self.sound_engine)
        self.btn_leaderboard.handle_event(event, self.sound_engine)
        self.btn_menu.handle_event(event, self.sound_engine)

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return "REPLAY"

        act = self.action
        self.action = None
        return act

    def update(self, dt: float):
        """Updates buttons and confetti particles."""
        self.emitter.update(dt)
        self.btn_replay.update(dt)
        self.btn_leaderboard.update(dt)
        self.btn_menu.update(dt)

    def draw(self, surface: pygame.Surface):
        """Draws podium, telemetry stats cards, and action buttons."""
        surface.fill(COLOR_BG_DARK)

        # Background decorative lines
        for x in range(0, surface.get_width(), 60):
            pygame.draw.line(surface, (20, 24, 36), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 60):
            pygame.draw.line(surface, (20, 24, 36), (0, y), (surface.get_width(), y), 1)

        # Confetti
        self.emitter.draw(surface)

        # 1. Title Banner
        placement = self.data.get("placement", 1)
        title_text = "CHAMPIONSHIP VICTORY!" if placement == 1 else "RACE FINISHED"
        title_col = COLOR_ACCENT_GOLD if placement == 1 else COLOR_ACCENT_PRIMARY

        t_surf = self.fonts["title"].render(title_text, True, title_col)
        surface.blit(t_surf, t_surf.get_rect(center=(surface.get_width() // 2, 45)))

        sub_str = f"DIFFICULTY: {self.data.get('difficulty', 'Medium').upper()}  •  PLACE: {placement} OF 5"
        sub_surf = self.fonts["medium"].render(sub_str, True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, sub_surf.get_rect(center=(surface.get_width() // 2, 80)))

        # 2. Podium Render (Left: 2nd, Center: 1st, Right: 3rd)
        order = self.data.get("finish_order", [])
        podium_base_y = 330

        # Draw 1st place podium (Center)
        p1_rect = pygame.Rect(580, podium_base_y - 120, 120, 120)
        pygame.draw.rect(surface, (255, 196, 0), p1_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(surface, (200, 150, 0), p1_rect, width=2, border_top_left_radius=6, border_top_right_radius=6)
        p1_txt = self.fonts["big"].render("1", True, (15, 20, 32))
        surface.blit(p1_txt, p1_txt.get_rect(center=p1_rect.center))

        # Draw 2nd place podium (Left)
        p2_rect = pygame.Rect(440, podium_base_y - 85, 120, 85)
        pygame.draw.rect(surface, (190, 200, 215), p2_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(surface, (150, 160, 175), p2_rect, width=2, border_top_left_radius=6, border_top_right_radius=6)
        p2_txt = self.fonts["big"].render("2", True, (15, 20, 32))
        surface.blit(p2_txt, p2_txt.get_rect(center=p2_rect.center))

        # Draw 3rd place podium (Right)
        p3_rect = pygame.Rect(720, podium_base_y - 60, 120, 60)
        pygame.draw.rect(surface, (205, 127, 50), p3_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(surface, (160, 95, 35), p3_rect, width=2, border_top_left_radius=6, border_top_right_radius=6)
        p3_txt = self.fonts["big"].render("3", True, (15, 20, 32))
        surface.blit(p3_txt, p3_txt.get_rect(center=p3_rect.center))

        # Draw racer names above podium steps
        if len(order) >= 1:
            name1 = order[0][0]
            col1 = COLOR_ACCENT_GOLD if order[0][1] else COLOR_TEXT_WHITE
            s1 = self.fonts["medium"].render(name1, True, col1)
            surface.blit(s1, s1.get_rect(center=(p1_rect.centerx, p1_rect.y - 18)))

        if len(order) >= 2:
            name2 = order[1][0]
            col2 = COLOR_ACCENT_PRIMARY if order[1][1] else COLOR_TEXT_WHITE
            s2 = self.fonts["medium"].render(name2, True, col2)
            surface.blit(s2, s2.get_rect(center=(p2_rect.centerx, p2_rect.y - 18)))

        if len(order) >= 3:
            name3 = order[2][0]
            col3 = COLOR_ACCENT_PRIMARY if order[2][1] else COLOR_TEXT_WHITE
            s3 = self.fonts["medium"].render(name3, True, col3)
            surface.blit(s3, s3.get_rect(center=(p3_rect.centerx, p3_rect.y - 18)))

        # 3. Telemetry Stats Grid Cards
        stat_card_y = 370
        stat_w = 210
        stat_h = 95
        gap = 20
        total_w = stat_w * 4 + gap * 3
        start_x = (surface.get_width() - total_w) // 2

        stats_items = [
            ("GROSS WPM", f"{int(self.data.get('wpm', 0))} WPM", COLOR_ACCENT_PRIMARY),
            ("NET WPM", f"{int(self.data.get('net_wpm', 0))} WPM", COLOR_ACCENT_GOLD),
            ("ACCURACY", f"{self.data.get('accuracy', 0):.1f}%", COLOR_CHAR_CORRECT),
            ("TIME TAKEN", f"{self.data.get('time_taken', 0):.2f}s", COLOR_TEXT_WHITE)
        ]

        for i, (label, val, col) in enumerate(stats_items):
            box_x = start_x + i * (stat_w + gap)
            b_rect = pygame.Rect(box_x, stat_card_y, stat_w, stat_h)
            
            pygame.draw.rect(surface, COLOR_PANEL_BG, b_rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, b_rect, width=1, border_radius=8)

            lbl_surf = self.fonts["small"].render(label, True, COLOR_TEXT_MUTED)
            surface.blit(lbl_surf, (b_rect.centerx - lbl_surf.get_width() // 2, b_rect.y + 16))

            val_surf = self.fonts["title"].render(val, True, col)
            surface.blit(val_surf, (b_rect.centerx - val_surf.get_width() // 2, b_rect.y + 42))

        # Secondary stats row
        sec_y = 485
        sec_card = pygame.Rect(start_x, sec_y, total_w, 55)
        pygame.draw.rect(surface, (20, 24, 36), sec_card, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, sec_card, width=1, border_radius=8)

        mistakes = self.data.get("mistakes", 0)
        total_chars = self.data.get("total_chars", 0)
        
        detail_str = f"TOTAL CHARACTERS TYPED: {total_chars}   |   UNCHECKED MISTAKES: {mistakes}   |   RESULT SAVED TO DATABASE"
        d_surf = self.fonts["small"].render(detail_str, True, COLOR_TEXT_MUTED)
        surface.blit(d_surf, d_surf.get_rect(center=sec_card.center))

        # 4. Action Buttons
        self.btn_replay.draw(surface)
        self.btn_leaderboard.draw(surface)
        self.btn_menu.draw(surface)
