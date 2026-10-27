"""
Typing Racer 2D - Race Heads-Up Display (HUD)
Renders live typing passage with character-by-character coloring, cursor box,
speedometer WPM gauge, accuracy meter, countdown timer, live placement rank,
and nitro streak meter.
"""
import math
import time
import pygame
from typing import List, Tuple, Dict, Any
from core.config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_GOLD, COLOR_ACCENT_SECONDARY, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_CHAR_CORRECT, COLOR_CHAR_WRONG,
    COLOR_CHAR_PENDING, COLOR_CURSOR_LINE
)


class RaceHUD:
    """Manages typing box rendering, telemetry gauges, and countdown overlay."""
    def __init__(self, font_code: pygame.font.Font, font_hud: pygame.font.Font, font_big: pygame.font.Font):
        self.font_code = font_code      # Monospace or clear font for typing text
        self.font_hud = font_hud        # For WPM, timer, and stats
        self.font_big = font_big        # For 3-2-1-GO countdown

        # Layout metrics
        self.panel_rect = pygame.Rect(40, 480, 1200, 225)
        
        # Cursor blinking
        self.cursor_blink_time: float = 0.0
        self.cursor_visible: bool = True

        # Precomputed passage wrapping lines
        self.cached_passage: str = ""
        self.wrapped_lines: List[str] = []
        self.char_line_map: List[Tuple[int, int]] = [] # char_idx -> (line_idx, col_idx)

    def prepare_passage(self, passage: str, max_width_px: int = 1140):
        """Precomputes word-wrapped lines and character coordinate mapping."""
        self.cached_passage = passage
        self.wrapped_lines = []
        self.char_line_map = []

        words = passage.split(' ')
        current_line = ""
        current_len_px = 0
        space_width = self.font_code.size(" ")[0]

        char_counter = 0

        for i, word in enumerate(words):
            word_str = word if i == 0 else " " + word
            word_w = self.font_code.size(word_str)[0]

            if current_len_px + word_w > max_width_px and current_line:
                self.wrapped_lines.append(current_line)
                current_line = word
                current_len_px = self.font_code.size(word)[0]
            else:
                current_line += word_str
                current_len_px += word_w

        if current_line:
            self.wrapped_lines.append(current_line)

        # Build character index to (line, col) mapping
        c_idx = 0
        for l_idx, line in enumerate(self.wrapped_lines):
            for col_idx in range(len(line)):
                self.char_line_map.append((l_idx, col_idx))
                c_idx += 1
            # Add implicit space between lines if not end
            if l_idx < len(self.wrapped_lines) - 1:
                # If wrapped word ended without trailing space, handle indexing
                pass

    def update(self, dt: float):
        """Updates cursor blink timer."""
        self.cursor_blink_time += dt
        if self.cursor_blink_time >= 0.45:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = 0.0

    def draw_typing_box(
        self,
        surface: pygame.Surface,
        passage: str,
        current_char_idx: int,
        has_error: bool
    ):
        """
        Renders the active typing box with green (correct), red (mistake),
        and glowing cyan cursor highlighting the next expected character.
        Automatically scrolls vertically so the active line is centered.
        """
        if self.cached_passage != passage:
            self.prepare_passage(passage, max_width_px=self.panel_rect.width - 60)

        # Draw panel container background
        pygame.draw.rect(surface, (18, 22, 34), self.panel_rect, border_radius=10)
        border_col = (255, 61, 113) if has_error else COLOR_PANEL_BORDER
        pygame.draw.rect(surface, border_col, self.panel_rect, width=2, border_radius=10)

        # Find active line
        active_line_idx = 0
        active_col_idx = 0
        if 0 <= current_char_idx < len(self.char_line_map):
            active_line_idx, active_col_idx = self.char_line_map[current_char_idx]
        elif current_char_idx >= len(self.char_line_map):
            active_line_idx = len(self.wrapped_lines) - 1
            active_col_idx = len(self.wrapped_lines[-1])

        # Vertical scrolling calculation
        line_height = self.font_code.get_linesize() + 6
        visible_lines_capacity = (self.panel_rect.height - 30) // line_height
        
        # Scroll offset so active line is in view
        scroll_line_offset = 0
        if active_line_idx >= 2:
            scroll_line_offset = active_line_idx - 1

        # Text clipping
        clip_rect = pygame.Rect(self.panel_rect.x + 25, self.panel_rect.y + 18, self.panel_rect.width - 50, self.panel_rect.height - 36)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        char_scan_idx = 0
        start_y = self.panel_rect.y + 20 - (scroll_line_offset * line_height)

        for l_idx, line in enumerate(self.wrapped_lines):
            line_y = start_y + l_idx * line_height
            
            # Skip lines out of vertical bounds
            if line_y < self.panel_rect.y - line_height or line_y > self.panel_rect.bottom + line_height:
                char_scan_idx += len(line)
                continue

            current_x = self.panel_rect.x + 30

            for col_idx, char in enumerate(line):
                char_w, _ = self.font_code.size(char)

                # Determine color and highlight
                if char_scan_idx < current_char_idx:
                    # Successfully typed character
                    char_surf = self.font_code.render(char, True, COLOR_CHAR_CORRECT)
                elif char_scan_idx == current_char_idx:
                    # Current character to type
                    if has_error:
                        # Draw error background box
                        err_rect = pygame.Rect(current_x - 1, line_y - 2, max(char_w + 2, 10), line_height - 2)
                        pygame.draw.rect(surface, (255, 60, 80, 160), err_rect, border_radius=3)
                        char_surf = self.font_code.render(char, True, (255, 255, 255))
                    else:
                        # Draw active cursor box with glowing border
                        if self.cursor_visible:
                            cursor_rect = pygame.Rect(current_x - 2, line_y - 2, max(char_w + 4, 12), line_height - 2)
                            pygame.draw.rect(surface, (0, 180, 255, 75), cursor_rect, border_radius=3)
                            pygame.draw.rect(surface, COLOR_ACCENT_PRIMARY, cursor_rect, width=2, border_radius=3)
                        char_surf = self.font_code.render(char, True, COLOR_TEXT_WHITE)
                else:
                    # Pending characters
                    char_surf = self.font_code.render(char, True, COLOR_CHAR_PENDING)

                surface.blit(char_surf, (current_x, line_y))
                current_x += char_w
                char_scan_idx += 1

        surface.set_clip(old_clip)

        # Helper hint at bottom of box
        hint_str = "Type each character accurately. Backspace corrects errors. Fast accurate typing activates NITRO!"
        hint_surf = self.font_code.render(hint_str, True, (90, 100, 125))
        surface.blit(hint_surf, (self.panel_rect.x + 30, self.panel_rect.bottom - 22))

    def draw_gauges(
        self,
        surface: pygame.Surface,
        wpm: float,
        net_wpm: float,
        accuracy: float,
        time_remaining: float,
        placement: int,
        nitro_streak: int,
        difficulty: str
    ):
        """Draws top HUD gauges: live WPM, Accuracy, Timer, Rank, Nitro."""
        # Top HUD Bar Container
        hud_bar_rect = pygame.Rect(40, 48, 1200, 32)
        pygame.draw.rect(surface, (20, 24, 36), hud_bar_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, hud_bar_rect, width=1, border_radius=6)

        # 1. Live Placement Badge
        rank_suffixes = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}
        rank_text = rank_suffixes.get(placement, f"{placement}th")
        rank_col = COLOR_ACCENT_GOLD if placement == 1 else ((192, 192, 192) if placement == 2 else COLOR_ACCENT_PRIMARY)
        
        rank_surf = self.font_hud.render(f"POS: {rank_text}", True, rank_col)
        surface.blit(rank_surf, (hud_bar_rect.x + 16, hud_bar_rect.centery - rank_surf.get_height() // 2))

        # 2. Live WPM / Speed Gauge
        wpm_str = f"SPEED: {int(wpm)} WPM (NET: {int(net_wpm)})"
        wpm_surf = self.font_hud.render(wpm_str, True, COLOR_ACCENT_PRIMARY)
        surface.blit(wpm_surf, (hud_bar_rect.x + 160, hud_bar_rect.centery - wpm_surf.get_height() // 2))

        # 3. Accuracy Percentage
        acc_str = f"ACCURACY: {accuracy:.1f}%"
        acc_col = COLOR_CHAR_CORRECT if accuracy >= 95.0 else ((255, 196, 0) if accuracy >= 88.0 else COLOR_CHAR_WRONG)
        acc_surf = self.font_hud.render(acc_str, True, acc_col)
        surface.blit(acc_surf, (hud_bar_rect.x + 480, hud_bar_rect.centery - acc_surf.get_height() // 2))

        # 4. Nitro Combo Streak Bar
        nitro_label = self.font_hud.render("NITRO:", True, (255, 215, 0))
        surface.blit(nitro_label, (hud_bar_rect.x + 720, hud_bar_rect.centery - nitro_label.get_height() // 2))
        
        # Mini Nitro gauge
        nitro_bar_x = hud_bar_rect.x + 790
        nitro_bar_w = 120
        nitro_bar_h = 12
        nitro_bar_y = hud_bar_rect.centery - nitro_bar_h // 2
        pygame.draw.rect(surface, (35, 42, 60), (nitro_bar_x, nitro_bar_y, nitro_bar_w, nitro_bar_h), border_radius=6)
        
        # Max streak for nitro boost is 25 chars
        nitro_ratio = min(1.0, nitro_streak / 25.0)
        fill_w = int(nitro_bar_w * nitro_ratio)
        if fill_w > 0:
            fill_col = (0, 229, 255) if nitro_ratio < 1.0 else (255, 215, 0)
            pygame.draw.rect(surface, fill_col, (nitro_bar_x, nitro_bar_y, fill_w, nitro_bar_h), border_radius=6)
        if nitro_ratio >= 1.0:
            boost_text = self.font_hud.render("BOOST!", True, (255, 230, 0))
            surface.blit(boost_text, (nitro_bar_x + nitro_bar_w + 8, hud_bar_rect.centery - boost_text.get_height() // 2))

        # 5. Countdown Timer
        mins = int(time_remaining) // 60
        secs = int(time_remaining) % 60
        ms = int((time_remaining - int(time_remaining)) * 10)
        timer_str = f"TIME: {mins:02d}:{secs:02d}.{ms}"
        timer_col = (255, 60, 80) if time_remaining < 20 else COLOR_TEXT_WHITE
        timer_surf = self.font_hud.render(timer_str, True, timer_col)
        surface.blit(timer_surf, (hud_bar_rect.right - timer_surf.get_width() - 16, hud_bar_rect.centery - timer_surf.get_height() // 2))

    def draw_countdown(self, surface: pygame.Surface, countdown_val: float):
        """Draws 3-2-1-GO! countdown banner overlay."""
        if countdown_val <= 0.0:
            return

        # Semi-transparent overlay backdrop
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((10, 14, 24, 150))
        surface.blit(overlay, (0, 0))

        # Text calculation
        if countdown_val > 3.0:
            text = "3"
            color = (255, 75, 75)
        elif countdown_val > 2.0:
            text = "2"
            color = (255, 196, 0)
        elif countdown_val > 1.0:
            text = "1"
            color = (0, 229, 255)
        else:
            text = "GO!"
            color = COLOR_CHAR_CORRECT

        # Pulsing scale effect based on fractional second
        frac = countdown_val % 1.0
        alpha = int(255 * (1.0 - frac * 0.4))

        count_surf = self.font_big.render(text, True, color)
        count_surf.set_alpha(alpha)
        count_rect = count_surf.get_rect(center=(surface.get_width() // 2, 260))
        surface.blit(count_surf, count_rect)

        sub_text = self.font_hud.render("GET READY TO RACE & TYPE!", True, COLOR_TEXT_WHITE)
        sub_rect = sub_text.get_rect(center=(surface.get_width() // 2, 330))
        surface.blit(sub_text, sub_rect)
