"""
Typing Racer 2D - Leaderboard & Statistics Screen
Displays high scores ranked by WPM across all difficulties,
as well as the player's personal race history and career telemetry.
"""
import pygame
from typing import Dict, Any, List, Optional
from core.config import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_CHAR_CORRECT
)
from database.db_manager import DatabaseManager
from ui.components import Button


class LeaderboardScreen:
    """Manages Global Leaderboards & Personal Career Statistics."""
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

        # Active view mode: "GLOBAL" or "PERSONAL"
        self.view_mode = "GLOBAL"
        self.selected_difficulty = "Medium"

        # Tab Buttons
        self.btn_tab_global = Button(
            pygame.Rect(400, 95, 230, 40),
            "GLOBAL LEADERBOARD",
            self.fonts["small"],
            border_radius=6,
            on_click=lambda: self._set_view_mode("GLOBAL")
        )
        self.btn_tab_personal = Button(
            pygame.Rect(650, 95, 230, 40),
            "MY CAREER STATS",
            self.fonts["small"],
            border_radius=6,
            on_click=lambda: self._set_view_mode("PERSONAL")
        )

        # Difficulty filter buttons for global view
        self.diff_buttons: Dict[str, Button] = {}
        diff_names = ["Easy", "Medium", "Hard", "Extreme Hard"]
        for i, d in enumerate(diff_names):
            btn = Button(
                pygame.Rect(320 + i * 160, 150, 150, 34),
                d.upper(),
                self.fonts["small"],
                border_radius=6,
                on_click=lambda name=d: self._set_difficulty(name)
            )
            self.diff_buttons[d] = btn

        # Back to Menu button
        self.btn_back = Button(
            pygame.Rect(40, 25, 140, 38),
            "<- MAIN MENU",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(38, 46, 68),
            border_radius=6,
            on_click=lambda: self._set_action("MENU")
        )

        self.action: Optional[str] = None

        # Data cache
        self.global_records: List[Dict[str, Any]] = []
        self.personal_history: List[Dict[str, Any]] = []
        self.career_stats: Dict[str, Any] = {}
        self._refresh_data()

    def _set_view_mode(self, mode: str):
        self.view_mode = mode
        if self.sound_engine:
            self.sound_engine.play_click()
        self._refresh_data()

    def _set_difficulty(self, diff: str):
        self.selected_difficulty = diff
        if self.sound_engine:
            self.sound_engine.play_click()
        self._refresh_data()

    def _set_action(self, act: str):
        self.action = act
        if self.sound_engine:
            self.sound_engine.play_click()

    def _refresh_data(self):
        """Fetches latest records from SQLite database."""
        self.global_records = self.db.get_leaderboard(self.selected_difficulty, limit=10)
        user_id = self.user.get("id")
        if user_id:
            self.personal_history = self.db.get_user_history(user_id, limit=12)
            self.career_stats = self.db.get_user_stats(user_id)
        else:
            self.personal_history = []
            self.career_stats = {"races": 0, "wins": 0, "win_rate": 0.0, "best_wpm": 0.0, "avg_wpm": 0.0, "avg_accuracy": 0.0}

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handles button clicks and ESC to exit."""
        self.btn_back.handle_event(event, self.sound_engine)
        self.btn_tab_global.handle_event(event, self.sound_engine)
        self.btn_tab_personal.handle_event(event, self.sound_engine)

        if self.view_mode == "GLOBAL":
            for btn in self.diff_buttons.values():
                btn.handle_event(event, self.sound_engine)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "MENU"

        act = self.action
        self.action = None
        return act

    def update(self, dt: float):
        """Updates button animations."""
        self.btn_back.update(dt)
        self.btn_tab_global.update(dt)
        self.btn_tab_personal.update(dt)
        for btn in self.diff_buttons.values():
            btn.update(dt)

    def draw(self, surface: pygame.Surface):
        """Renders leaderboard tables and user statistics."""
        surface.fill(COLOR_BG_DARK)

        # Background grid
        for x in range(0, surface.get_width(), 60):
            pygame.draw.line(surface, (20, 24, 36), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 60):
            pygame.draw.line(surface, (20, 24, 36), (0, y), (surface.get_width(), y), 1)

        # Back Button
        self.btn_back.draw(surface)

        # Title Header
        title_surf = self.fonts["title"].render("HALL OF FAME & STATISTICS", True, COLOR_ACCENT_PRIMARY)
        surface.blit(title_surf, title_surf.get_rect(center=(surface.get_width() // 2, 45)))

        # 1. Main Tabs
        # Active tab indicator
        if self.view_mode == "GLOBAL":
            self.btn_tab_global.bg_color = (0, 180, 220)
            self.btn_tab_global.text_color = (10, 14, 24)
            self.btn_tab_personal.bg_color = (25, 30, 44)
            self.btn_tab_personal.text_color = COLOR_TEXT_WHITE
        else:
            self.btn_tab_global.bg_color = (25, 30, 44)
            self.btn_tab_global.text_color = COLOR_TEXT_WHITE
            self.btn_tab_personal.bg_color = (0, 180, 220)
            self.btn_tab_personal.text_color = (10, 14, 24)

        self.btn_tab_global.draw(surface)
        self.btn_tab_personal.draw(surface)

        # 2. Render Selected View
        if self.view_mode == "GLOBAL":
            self._draw_global_view(surface)
        else:
            self._draw_personal_view(surface)

    def _draw_global_view(self, surface: pygame.Surface):
        """Draws global leaderboard table."""
        # Difficulty filter buttons
        for d, btn in self.diff_buttons.items():
            if d == self.selected_difficulty:
                btn.bg_color = (46, 213, 115)
                btn.text_color = (10, 14, 24)
            else:
                btn.bg_color = (25, 30, 44)
                btn.text_color = COLOR_TEXT_MUTED
            btn.draw(surface)

        # Table Container Panel
        table_rect = pygame.Rect(120, 200, 1040, 480)
        pygame.draw.rect(surface, COLOR_PANEL_BG, table_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, table_rect, width=1, border_radius=10)

        # Table Columns Header
        header_y = table_rect.y + 16
        headers = [
            ("RANK", 160),
            ("RACER PILOT", 260),
            ("SPEED (WPM)", 520),
            ("NET WPM", 670),
            ("ACCURACY", 800),
            ("TIME", 940)
        ]
        for title, x in headers:
            h_surf = self.fonts["small"].render(title, True, COLOR_TEXT_MUTED)
            surface.blit(h_surf, (x, header_y))

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (table_rect.x + 20, header_y + 28), (table_rect.right - 20, header_y + 28), 1)

        # Table Rows
        row_y = header_y + 38
        if not self.global_records:
            empty_msg = self.fonts["medium"].render("No race records yet for this difficulty. Be the first to claim #1!", True, COLOR_TEXT_MUTED)
            surface.blit(empty_msg, empty_msg.get_rect(center=(table_rect.centerx, table_rect.centery)))
            return

        for idx, rec in enumerate(self.global_records):
            rank = idx + 1
            # Alternate row background
            if idx % 2 == 0:
                row_bg = pygame.Rect(table_rect.x + 10, row_y - 4, table_rect.width - 20, 36)
                pygame.draw.rect(surface, (28, 34, 50), row_bg, border_radius=4)

            # Rank Medal colors
            rank_col = COLOR_ACCENT_GOLD if rank == 1 else ((210, 215, 225) if rank == 2 else ((205, 127, 50) if rank == 3 else COLOR_TEXT_WHITE))
            rank_text = f"#{rank}"

            r_surf = self.fonts["medium"].render(rank_text, True, rank_col)
            surface.blit(r_surf, (160, row_y))

            pilot_name = rec["racer_name"]
            p_surf = self.fonts["medium"].render(pilot_name, True, COLOR_TEXT_WHITE)
            surface.blit(p_surf, (260, row_y))

            wpm_surf = self.fonts["medium"].render(f"{int(rec['wpm'])} WPM", True, COLOR_ACCENT_PRIMARY)
            surface.blit(wpm_surf, (520, row_y))

            net_surf = self.fonts["medium"].render(f"{int(rec['net_wpm'])} WPM", True, COLOR_ACCENT_GOLD)
            surface.blit(net_surf, (670, row_y))

            acc_surf = self.fonts["medium"].render(f"{rec['accuracy']:.1f}%", True, COLOR_CHAR_CORRECT)
            surface.blit(acc_surf, (800, row_y))

            time_surf = self.fonts["medium"].render(f"{rec['time_taken_seconds']:.1f}s", True, COLOR_TEXT_MUTED)
            surface.blit(time_surf, (940, row_y))

            row_y += 38

    def _draw_personal_view(self, surface: pygame.Surface):
        """Draws user career stats summary cards and race history log."""
        # Top Stats Summary Cards
        start_x = 120
        card_y = 155
        card_w = 160
        card_h = 75
        gap = 16

        summary_metrics = [
            ("TOTAL RACES", str(self.career_stats.get("races", 0)), COLOR_ACCENT_PRIMARY),
            ("VICTORIES", str(self.career_stats.get("wins", 0)), COLOR_ACCENT_GOLD),
            ("WIN RATE", f"{self.career_stats.get('win_rate', 0):.1f}%", COLOR_CHAR_CORRECT),
            ("BEST WPM", f"{int(self.career_stats.get('best_wpm', 0))} WPM", COLOR_ACCENT_PRIMARY),
            ("AVG WPM", f"{int(self.career_stats.get('avg_wpm', 0))} WPM", COLOR_TEXT_WHITE),
            ("AVG ACCURACY", f"{self.career_stats.get('avg_accuracy', 0):.1f}%", COLOR_CHAR_CORRECT)
        ]

        for i, (lbl, val, col) in enumerate(summary_metrics):
            bx = start_x + i * (card_w + gap)
            b_rect = pygame.Rect(bx, card_y, card_w, card_h)
            pygame.draw.rect(surface, COLOR_PANEL_BG, b_rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, b_rect, width=1, border_radius=8)

            l_surf = self.fonts["small"].render(lbl, True, COLOR_TEXT_MUTED)
            surface.blit(l_surf, (b_rect.centerx - l_surf.get_width() // 2, b_rect.y + 12))

            v_surf = self.fonts["medium"].render(val, True, col)
            surface.blit(v_surf, (b_rect.centerx - v_surf.get_width() // 2, b_rect.y + 38))

        # Personal Race History Table
        table_rect = pygame.Rect(120, 245, 1040, 440)
        pygame.draw.rect(surface, COLOR_PANEL_BG, table_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, table_rect, width=1, border_radius=10)

        header_y = table_rect.y + 14
        headers = [
            ("DIFFICULTY", 160),
            ("PLACEMENT", 340),
            ("GROSS WPM", 490),
            ("NET WPM", 630),
            ("ACCURACY", 770),
            ("ERRORS", 890),
            ("TIME", 990)
        ]
        for title, x in headers:
            h_surf = self.fonts["small"].render(title, True, COLOR_TEXT_MUTED)
            surface.blit(h_surf, (x, header_y))

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (table_rect.x + 20, header_y + 26), (table_rect.right - 20, header_y + 26), 1)

        row_y = header_y + 36
        if not self.personal_history:
            empty_msg = self.fonts["medium"].render("No recorded race history yet. Complete races to build your career log!", True, COLOR_TEXT_MUTED)
            surface.blit(empty_msg, empty_msg.get_rect(center=(table_rect.centerx, table_rect.centery)))
            return

        for idx, rec in enumerate(self.personal_history):
            if idx % 2 == 0:
                row_bg = pygame.Rect(table_rect.x + 10, row_y - 4, table_rect.width - 20, 32)
                pygame.draw.rect(surface, (28, 34, 50), row_bg, border_radius=4)

            d_surf = self.fonts["medium"].render(rec["difficulty"], True, COLOR_TEXT_WHITE)
            surface.blit(d_surf, (160, row_y))

            place = rec["placement"]
            p_col = COLOR_ACCENT_GOLD if place == 1 else ((210, 215, 225) if place == 2 else COLOR_TEXT_WHITE)
            p_surf = self.fonts["medium"].render(f"{place}th Place" if place > 3 else (f"{place}st Place" if place == 1 else f"{place}nd Place"), True, p_col)
            surface.blit(p_surf, (340, row_y))

            wpm_surf = self.fonts["medium"].render(f"{int(rec['wpm'])} WPM", True, COLOR_ACCENT_PRIMARY)
            surface.blit(wpm_surf, (490, row_y))

            net_surf = self.fonts["medium"].render(f"{int(rec['net_wpm'])} WPM", True, COLOR_ACCENT_GOLD)
            surface.blit(net_surf, (630, row_y))

            acc_surf = self.fonts["medium"].render(f"{rec['accuracy']:.1f}%", True, COLOR_CHAR_CORRECT)
            surface.blit(acc_surf, (770, row_y))

            err_surf = self.fonts["medium"].render(str(rec.get("mistakes", 0)), True, (255, 75, 75) if rec.get("mistakes", 0) > 0 else COLOR_TEXT_MUTED)
            surface.blit(err_surf, (890, row_y))

            t_surf = self.fonts["medium"].render(f"{rec['time_taken_seconds']:.1f}s", True, COLOR_TEXT_MUTED)
            surface.blit(t_surf, (990, row_y))

            row_y += 32
