"""
Typing Racer 2D - UI Component Library
Contains modern interactive UI widgets: Button, TextInput (with password masking & toggle),
Card/Panel, and Toast Alerts.
"""
import time
import pygame
from typing import Optional, Callable, Tuple, List
from core.config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_SECONDARY, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_CHAR_WRONG, COLOR_CHAR_CORRECT
)


class Button:
    """Modern arcade button with hover animations and sound trigger."""
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        bg_color: Tuple[int, int, int] = (30, 36, 54),
        hover_color: Tuple[int, int, int] = (45, 54, 82),
        text_color: Tuple[int, int, int] = COLOR_TEXT_WHITE,
        border_color: Tuple[int, int, int] = COLOR_PANEL_BORDER,
        border_hover: Tuple[int, int, int] = COLOR_ACCENT_PRIMARY,
        border_radius: int = 8,
        on_click: Optional[Callable[[], None]] = None
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_hover = border_hover
        self.border_radius = border_radius
        self.on_click = on_click

        self.is_hovered: bool = False
        self.is_pressed: bool = False
        self.hover_progress: float = 0.0

    def handle_event(self, event: pygame.event.Event, sound_engine=None) -> bool:
        """Handles mouse hover and click events. Returns True if clicked."""
        if event.type == pygame.MOUSEMOTION:
            prev_hover = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if not prev_hover and self.is_hovered and sound_engine:
                sound_engine.play_click()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if sound_engine:
                    sound_engine.play_click()
                if self.on_click:
                    self.on_click()
                return True
            self.is_pressed = False

        return False

    def update(self, dt: float):
        """Animates hover transition."""
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * min(1.0, 15.0 * dt)

    def draw(self, surface: pygame.Surface):
        """Renders the styled button."""
        # Interpolate background color
        r = int(self.bg_color[0] + (self.hover_color[0] - self.bg_color[0]) * self.hover_progress)
        g = int(self.bg_color[1] + (self.hover_color[1] - self.bg_color[1]) * self.hover_progress)
        b = int(self.bg_color[2] + (self.hover_color[2] - self.bg_color[2]) * self.hover_progress)
        current_bg = (r, g, b)

        # Interpolate border color
        br = int(self.border_color[0] + (self.border_hover[0] - self.border_color[0]) * self.hover_progress)
        bg = int(self.border_color[1] + (self.border_hover[1] - self.border_color[1]) * self.hover_progress)
        bb = int(self.border_color[2] + (self.border_hover[2] - self.border_color[2]) * self.hover_progress)
        current_border = (br, bg, bb)

        # Draw button surface
        draw_rect = self.rect.copy()
        if self.is_pressed:
            draw_rect.y += 1

        pygame.draw.rect(surface, current_bg, draw_rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, current_border, draw_rect, width=2, border_radius=self.border_radius)

        # Text rendering
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        surface.blit(txt_surf, txt_rect)


class TextInput:
    """
    Polished text input field supporting tab navigation,
    password masking with eye toggle, placeholder, and validation states.
    """
    def __init__(
        self,
        rect: pygame.Rect,
        font: pygame.font.Font,
        placeholder: str = "",
        is_password: bool = False,
        max_length: int = 64
    ):
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.is_password = is_password
        self.show_password = False
        self.max_length = max_length

        self.text: str = ""
        self.is_focused: bool = False
        self.cursor_visible: bool = True
        self.cursor_timer: float = 0.0

        # Eye icon toggle rect if password field
        self.toggle_rect = pygame.Rect(rect.right - 38, rect.y + 4, 32, rect.height - 8)

        # Key repeat timing for smooth backspacing
        self.backspace_pressed = False
        self.backspace_timer = 0.0
        self.backspace_delay = 0.35
        self.backspace_interval = 0.05

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Processes keyboard & mouse input.
        Returns 'SUBMIT' if Enter is pressed, 'TAB' if Tab is pressed.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_password and self.toggle_rect.collidepoint(event.pos):
                self.show_password = not self.show_password
                return None

            self.is_focused = self.rect.collidepoint(event.pos)
            self.cursor_visible = True
            self.cursor_timer = 0.0

        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_TAB:
                return "TAB"
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "SUBMIT"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.backspace_pressed = True
                self.backspace_timer = time.time() + self.backspace_delay
            elif event.key == pygame.K_ESCAPE:
                self.is_focused = False
            else:
                # Add unicode character
                if event.unicode and event.unicode.isprintable() and len(self.text) < self.max_length:
                    self.text += event.unicode
                    self.cursor_visible = True
                    self.cursor_timer = 0.0

        elif event.type == pygame.KEYUP and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_pressed = False

        return None

    def update(self, dt: float):
        """Updates cursor blink and key repeat."""
        if self.is_focused:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0

            # Repeat backspace while held
            if self.backspace_pressed and time.time() > self.backspace_timer:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                self.backspace_timer = time.time() + self.backspace_interval
        else:
            self.cursor_visible = False

    def draw(self, surface: pygame.Surface):
        """Draws the text input field."""
        bg_col = (20, 24, 36) if not self.is_focused else (24, 30, 46)
        border_col = COLOR_ACCENT_PRIMARY if self.is_focused else COLOR_PANEL_BORDER

        # Draw container box
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2 if self.is_focused else 1, border_radius=6)

        # Prepare display string
        if self.text:
            display_str = self.text if (not self.is_password or self.show_password) else "•" * len(self.text)
            text_surf = self.font.render(display_str, True, COLOR_TEXT_WHITE)
        else:
            text_surf = self.font.render(self.placeholder, True, COLOR_TEXT_MUTED)

        # Clipping area for text
        clip_w = self.rect.width - (50 if self.is_password else 20)
        text_clip_rect = pygame.Rect(self.rect.x + 12, self.rect.y + 4, clip_w, self.rect.height - 8)
        
        # Subsurface clipping
        old_clip = surface.get_clip()
        surface.set_clip(text_clip_rect)

        # Align right if text exceeds box width
        x_pos = self.rect.x + 12
        if text_surf.get_width() > clip_w:
            x_pos = (self.rect.x + 12 + clip_w) - text_surf.get_width()

        y_pos = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (x_pos, y_pos))

        # Draw blinking cursor
        if self.is_focused and self.cursor_visible:
            cursor_x = x_pos + text_surf.get_width() if self.text else self.rect.x + 12
            pygame.draw.line(surface, COLOR_ACCENT_PRIMARY, (cursor_x + 1, y_pos + 2), (cursor_x + 1, y_pos + text_surf.get_height() - 2), 2)

        surface.set_clip(old_clip)

        # Password visibility toggle button
        if self.is_password:
            eye_text = "HIDE" if self.show_password else "SHOW"
            eye_font_surf = self.font.render(eye_text, True, COLOR_ACCENT_PRIMARY if self.show_password else COLOR_TEXT_MUTED)
            eye_bg = pygame.Surface((self.toggle_rect.width, self.toggle_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(eye_bg, (35, 42, 60, 160), (0, 0, self.toggle_rect.width, self.toggle_rect.height), border_radius=4)
            surface.blit(eye_bg, self.toggle_rect.topleft)
            eye_r = eye_font_surf.get_rect(center=self.toggle_rect.center)
            surface.blit(eye_font_surf, eye_r)


class ToastAlert:
    """Animated status banner for success and error notifications."""
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.message: str = ""
        self.is_error: bool = False
        self.visible: bool = False
        self.timer: float = 0.0
        self.alpha: float = 0.0

    def show(self, message: str, is_error: bool = False, duration: float = 3.5):
        """Triggers a toast message."""
        self.message = message
        self.is_error = is_error
        self.visible = True
        self.timer = duration
        self.alpha = 0.0

    def update(self, dt: float):
        """Updates toast timer and smooth fade in/out."""
        if not self.visible:
            return

        self.timer -= dt
        if self.timer > 0.4:
            self.alpha = min(255.0, self.alpha + 700.0 * dt)
        elif self.timer > 0.0:
            self.alpha = max(0.0, self.alpha - 600.0 * dt)
        else:
            self.visible = False

    def draw(self, surface: pygame.Surface):
        """Draws toast notification banner centered at top of screen."""
        if not self.visible or self.alpha <= 0:
            return

        txt_surf = self.font.render(self.message, True, COLOR_TEXT_WHITE)
        pad_x, pad_y = 24, 10
        w = txt_surf.get_width() + pad_x * 2
        h = txt_surf.get_height() + pad_y * 2
        x = (surface.get_width() - w) // 2
        y = 20

        bg_col = (190, 40, 55) if self.is_error else (25, 140, 75)
        border_col = COLOR_CHAR_WRONG if self.is_error else COLOR_CHAR_CORRECT

        banner_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(banner_surf, (*bg_col, int(self.alpha)), (0, 0, w, h), border_radius=8)
        pygame.draw.rect(banner_surf, (*border_col, int(self.alpha)), (0, 0, w, h), width=2, border_radius=8)
        
        # Apply alpha to text
        txt_surf.set_alpha(int(self.alpha))
        banner_surf.blit(txt_surf, (pad_x, pad_y))

        surface.blit(banner_surf, (x, y))
