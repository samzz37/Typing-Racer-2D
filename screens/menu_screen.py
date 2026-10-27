"""
Typing Racer 2D - Main Menu Screen
Allows selecting difficulty, starting races, accessing the leaderboard,
customizing car in the garage, toggling audio, and logging out.
"""
import pygame
from typing import Dict, Any, Optional
from core.config import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD, COLOR_ACCENT_SECONDARY,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, DIFFICULTY_PRESETS, CAR_PALETTES
)
from ui.components import Button


class MenuScreen:
    """Arcade Main Menu Screen."""
    def __init__(
        self,
        user: Dict[str, Any],
        fonts: Dict[str, pygame.font.Font],
        sound_engine
    ):
        self.user = user
        self.fonts = fonts
        self.sound_engine = sound_engine

        # Current selected difficulty
        self.selected_difficulty: str = "Medium"

        # Action signal: None, "START_RACE", "LEADERBOARD", "GARAGE", "LOGOUT", "QUIT"
        self.action: Optional[str] = None

        # Build difficulty selection cards
        self.diff_buttons: Dict[str, Button] = {}
        diff_names = ["Easy", "Medium", "Hard", "Extreme Hard"]
        card_w = 270
        card_h = 100
        start_x = (1280 - (card_w * 4 + 30 * 3)) // 2
        card_y = 250

        for i, name in enumerate(diff_names):
            bx = start_x + i * (card_w + 30)
            btn = Button(
                pygame.Rect(bx, card_y, card_w, card_h),
                "",
                self.fonts["medium"],
                border_radius=10,
                on_click=lambda n=name: self._select_difficulty(n)
            )
            self.diff_buttons[name] = btn

        # Main Menu navigation buttons
        center_x = 1280 // 2
        self.btn_start = Button(
            pygame.Rect(center_x - 170, 400, 340, 54),
            "START CHAMPIONSHIP RACE",
            self.fonts["medium"],
            bg_color=(0, 190, 225),
            hover_color=(0, 230, 255),
            text_color=(10, 14, 24),
            border_radius=10,
            on_click=lambda: self._set_action("START_RACE")
        )

        self.btn_garage = Button(
            pygame.Rect(center_x - 260, 475, 240, 44),
            "GARAGE & CAR PAINT",
            self.fonts["small"],
            bg_color=(30, 36, 52),
            hover_color=(45, 54, 78),
            on_click=lambda: self._set_action("GARAGE")
        )

        self.btn_leaderboard = Button(
            pygame.Rect(center_x + 20, 475, 240, 44),
            "LEADERBOARD & STATS",
            self.fonts["small"],
            bg_color=(30, 36, 52),
            hover_color=(45, 54, 78),
            on_click=lambda: self._set_action("LEADERBOARD")
        )

        self.btn_audio = Button(
            pygame.Rect(center_x - 260, 535, 240, 42),
            "AUDIO: ON",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(38, 46, 68),
            on_click=self._toggle_audio
        )

        self.btn_quit = Button(
            pygame.Rect(center_x + 20, 535, 240, 42),
            "EXIT GAME",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(60, 25, 35),
            on_click=lambda: self._set_action("QUIT")
        )

        # Logout button in top-right
        self.btn_logout = Button(
            pygame.Rect(1280 - 140, 20, 110, 34),
            "LOGOUT",
            self.fonts["small"],
            bg_color=(40, 20, 30),
            hover_color=(75, 25, 35),
            border_color=(120, 40, 50),
            on_click=lambda: self._set_action("LOGOUT")
        )

    def _select_difficulty(self, diff_name: str):
        self.selected_difficulty = diff_name
        if self.sound_engine:
            self.sound_engine.play_click()

    def _set_action(self, act: str):
        self.action = act
        if self.sound_engine:
            self.sound_engine.play_click()

    def _toggle_audio(self):
        if self.sound_engine:
            muted = self.sound_engine.toggle_mute()
            self.btn_audio.text = "AUDIO: OFF" if muted else "AUDIO: ON"

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Processes events and returns chosen action if triggered."""
        for name, btn in self.diff_buttons.items():
            btn.handle_event(event, self.sound_engine)

        self.btn_start.handle_event(event, self.sound_engine)
        self.btn_garage.handle_event(event, self.sound_engine)
        self.btn_leaderboard.handle_event(event, self.sound_engine)
        self.btn_audio.handle_event(event, self.sound_engine)
        self.btn_quit.handle_event(event, self.sound_engine)
        self.btn_logout.handle_event(event, self.sound_engine)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "START_RACE"

        action = self.action
        self.action = None
        return action

    def update(self, dt: float):
        """Updates button animations."""
        for btn in self.diff_buttons.values():
            btn.update(dt)
        self.btn_start.update(dt)
        self.btn_garage.update(dt)
        self.btn_leaderboard.update(dt)
        self.btn_audio.update(dt)
        self.btn_quit.update(dt)
        self.btn_logout.update(dt)

    def draw(self, surface: pygame.Surface):
        """Renders main menu, driver profile banner, and difficulty cards."""
        surface.fill(COLOR_BG_DARK)

        # Subtle background grid
        for x in range(0, surface.get_width(), 60):
            pygame.draw.line(surface, (20, 24, 36), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 60):
            pygame.draw.line(surface, (20, 24, 36), (0, y), (surface.get_width(), y), 1)

        # 1. Driver Profile Bar at Top Left
        profile_rect = pygame.Rect(30, 16, 520, 52)
        pygame.draw.rect(surface, (20, 25, 38), profile_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, profile_rect, width=1, border_radius=8)

        # Driver details
        driver_name = self.user.get("full_name", "Driver")
        best_wpm = self.user.get("best_wpm", 0.0)
        races = self.user.get("total_races", 0)
        wins = self.user.get("total_wins", 0)

        name_surf = self.fonts["medium"].render(f"PILOT: {driver_name.upper()}", True, COLOR_TEXT_WHITE)
        surface.blit(name_surf, (profile_rect.x + 16, profile_rect.y + 8))

        stats_str = f"BEST: {int(best_wpm)} WPM  •  RACES: {races}  •  WINS: {wins}"
        stats_surf = self.fonts["small"].render(stats_str, True, COLOR_ACCENT_PRIMARY)
        surface.blit(stats_surf, (profile_rect.x + 16, profile_rect.y + 30))

        # Logout button
        self.btn_logout.draw(surface)

        # 2. Main Title Banner
        title_surf = self.fonts["title"].render("TYPING RACER 2D", True, COLOR_ACCENT_PRIMARY)
        title_rect = title_surf.get_rect(center=(surface.get_width() // 2, 120))
        surface.blit(title_surf, title_rect)

        sub_surf = self.fonts["medium"].render("SELECT DIFFICULTY CHAMPIONSHIP", True, COLOR_ACCENT_GOLD)
        sub_rect = sub_surf.get_rect(center=(surface.get_width() // 2, 175))
        surface.blit(sub_surf, sub_rect)

        # 3. Four Difficulty Cards
        for name, preset in DIFFICULTY_PRESETS.items():
            btn = self.diff_buttons[name]
            is_selected = (name == self.selected_difficulty)

            # Draw card container
            bg_col = (28, 35, 52) if is_selected else (20, 24, 36)
            border_col = preset["color"] if is_selected else COLOR_PANEL_BORDER
            border_w = 3 if is_selected else 1

            pygame.draw.rect(surface, bg_col, btn.rect, border_radius=10)
            pygame.draw.rect(surface, border_col, btn.rect, width=border_w, border_radius=10)

            # Card Header
            title_col = preset["color"] if is_selected else COLOR_TEXT_WHITE
            name_surf = self.fonts["medium"].render(name.upper(), True, title_col)
            surface.blit(name_surf, (btn.rect.x + 16, btn.rect.y + 12))

            # Tag
            tag_surf = self.fonts["small"].render(f"[{preset['difficulty_tag']}]", True, preset["color"])
            surface.blit(tag_surf, (btn.rect.right - tag_surf.get_width() - 14, btn.rect.y + 14))

            # Details: lines & time limit
            mins = preset["time_limit"] // 60
            secs = preset["time_limit"] % 60
            time_str = f"Time: {mins}m {secs:02d}s" if secs else f"Time: {mins}m"
            time_surf = self.fonts["small"].render(time_str, True, COLOR_TEXT_WHITE)
            surface.blit(time_surf, (btn.rect.x + 16, btn.rect.y + 42))

            lines_surf = self.fonts["small"].render(preset["lines_desc"], True, COLOR_TEXT_MUTED)
            surface.blit(lines_surf, (btn.rect.x + 16, btn.rect.y + 64))

            # Checkmark if selected
            if is_selected:
                sel_badge = self.fonts["small"].render("ACTIVE", True, (10, 14, 24))
                badge_bg = pygame.Rect(btn.rect.right - 70, btn.rect.bottom - 24, 60, 18)
                pygame.draw.rect(surface, preset["color"], badge_bg, border_radius=4)
                surface.blit(sel_badge, sel_badge.get_rect(center=badge_bg.center))

        # 4. Action Buttons
        self.btn_start.draw(surface)
        self.btn_garage.draw(surface)
        self.btn_leaderboard.draw(surface)
        self.btn_audio.draw(surface)
        self.btn_quit.draw(surface)

        # Controls hint
        hint = self.fonts["small"].render("Press ENTER or Click START to race  •  ESC to pause during race", True, (100, 110, 135))
        surface.blit(hint, hint.get_rect(center=(surface.get_width() // 2, 655)))
