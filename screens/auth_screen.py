"""
Typing Racer 2D - Authentication Screen
Provides Sign In, Registration with full validation and PBKDF2 hashing,
and optional Guest Practice mode.
"""
import pygame
from typing import Optional, Dict, Any, Tuple
from core.config import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED
)
from database.db_manager import DatabaseManager
from ui.components import Button, TextInput, ToastAlert


class AuthScreen:
    """Manages User Login and Sign Up authentication workflows."""
    def __init__(
        self,
        db: DatabaseManager,
        fonts: Dict[str, pygame.font.Font],
        sound_engine
    ):
        self.db = db
        self.fonts = fonts
        self.sound_engine = sound_engine

        # Screen mode: "LOGIN" or "REGISTER"
        self.mode = "LOGIN"

        # Toast notification system
        self.toast = ToastAlert(self.fonts["small"])

        # Layout card bounds
        self.card_rect = pygame.Rect(440, 110, 400, 520)

        # Common input dimensions
        input_w = 340
        input_h = 42
        start_x = self.card_rect.x + (self.card_rect.width - input_w) // 2

        # --- Login Form Inputs ---
        self.login_email = TextInput(
            pygame.Rect(start_x, 240, input_w, input_h),
            self.fonts["input"],
            placeholder="Email address (e.g. speed@racer.com)"
        )
        self.login_password = TextInput(
            pygame.Rect(start_x, 310, input_w, input_h),
            self.fonts["input"],
            placeholder="Password",
            is_password=True
        )

        # --- Register Form Inputs ---
        self.reg_name = TextInput(
            pygame.Rect(start_x, 215, input_w, input_h),
            self.fonts["input"],
            placeholder="Full Name / Driver Tag"
        )
        self.reg_email = TextInput(
            pygame.Rect(start_x, 275, input_w, input_h),
            self.fonts["input"],
            placeholder="Email address"
        )
        self.reg_pass = TextInput(
            pygame.Rect(start_x, 335, input_w, input_h),
            self.fonts["input"],
            placeholder="Password (min 8 chars)",
            is_password=True
        )
        self.reg_confirm = TextInput(
            pygame.Rect(start_x, 395, input_w, input_h),
            self.fonts["input"],
            placeholder="Confirm Password",
            is_password=True
        )

        # Focus indices
        self.login_inputs = [self.login_email, self.login_password]
        self.reg_inputs = [self.reg_name, self.reg_email, self.reg_pass, self.reg_confirm]
        self.active_input_idx = 0
        self.login_email.is_focused = True

        # --- Action Buttons ---
        self.btn_submit_login = Button(
            pygame.Rect(start_x, 385, input_w, 46),
            "SIGN IN & RACE",
            self.fonts["medium"],
            bg_color=(0, 180, 220),
            hover_color=(0, 220, 255),
            text_color=(10, 14, 24),
            border_radius=8,
            on_click=self._submit_login
        )

        self.btn_submit_register = Button(
            pygame.Rect(start_x, 465, input_w, 46),
            "CREATE RACER ACCOUNT",
            self.fonts["medium"],
            bg_color=(46, 213, 115),
            hover_color=(60, 235, 130),
            text_color=(10, 14, 24),
            border_radius=8,
            on_click=self._submit_register
        )

        self.btn_switch_to_reg = Button(
            pygame.Rect(start_x, 445, input_w, 38),
            "New racer? Create Account",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(35, 42, 60),
            on_click=self._switch_to_reg
        )

        self.btn_switch_to_login = Button(
            pygame.Rect(start_x, 525, input_w, 38),
            "Already have an account? Sign In",
            self.fonts["small"],
            bg_color=(25, 30, 44),
            hover_color=(35, 42, 60),
            on_click=self._switch_to_login
        )

        self.btn_guest_play = Button(
            pygame.Rect(start_x, 500, input_w, 38),
            "Quick Practice as Guest",
            self.fonts["small"],
            bg_color=(30, 36, 52),
            hover_color=(45, 54, 76),
            border_color=(65, 75, 105),
            on_click=self._play_as_guest
        )

        # Authentication output
        self.authenticated_user: Optional[Dict[str, Any]] = None

    def _switch_to_reg(self):
        self.mode = "REGISTER"
        self.card_rect.height = 570
        for inp in self.reg_inputs:
            inp.is_focused = False
        self.reg_name.is_focused = True
        self.active_input_idx = 0

    def _switch_to_login(self):
        self.mode = "LOGIN"
        self.card_rect.height = 520
        for inp in self.login_inputs:
            inp.is_focused = False
        self.login_email.is_focused = True
        self.active_input_idx = 0

    def _submit_login(self):
        email = self.login_email.text.strip()
        pwd = self.login_password.text.strip()

        success, msg, user = self.db.login_user(email, pwd)
        if success:
            self.authenticated_user = user
            self.toast.show(msg, is_error=False)
            if self.sound_engine:
                self.sound_engine.play_countdown_go()
        else:
            self.toast.show(msg, is_error=True)
            if self.sound_engine:
                self.sound_engine.play_error()

    def _submit_register(self):
        name = self.reg_name.text.strip()
        email = self.reg_email.text.strip()
        pwd = self.reg_pass.text.strip()
        confirm = self.reg_confirm.text.strip()

        success, msg, user = self.db.register_user(name, email, pwd, confirm)
        if success:
            self.authenticated_user = user
            self.toast.show(msg, is_error=False)
            if self.sound_engine:
                self.sound_engine.play_countdown_go()
        else:
            self.toast.show(msg, is_error=True)
            if self.sound_engine:
                self.sound_engine.play_error()

    def _play_as_guest(self):
        self.authenticated_user = {
            "id": None,
            "full_name": "Guest Driver",
            "email": "guest@local",
            "best_wpm": 0.0,
            "total_races": 0,
            "total_wins": 0,
            "preferred_car_color": 0
        }
        self.toast.show("Entering Practice Mode as Guest...", is_error=False)

    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Processes events and returns authenticated user if login succeeds."""
        current_inputs = self.login_inputs if self.mode == "LOGIN" else self.reg_inputs

        for i, inp in enumerate(current_inputs):
            res = inp.handle_event(event)
            if res == "TAB":
                inp.is_focused = False
                self.active_input_idx = (i + 1) % len(current_inputs)
                current_inputs[self.active_input_idx].is_focused = True
                break
            elif res == "SUBMIT":
                if self.mode == "LOGIN":
                    self._submit_login()
                else:
                    self._submit_register()
                break

        # Process Buttons
        if self.mode == "LOGIN":
            self.btn_submit_login.handle_event(event, self.sound_engine)
            self.btn_switch_to_reg.handle_event(event, self.sound_engine)
            self.btn_guest_play.handle_event(event, self.sound_engine)
        else:
            self.btn_submit_register.handle_event(event, self.sound_engine)
            self.btn_switch_to_login.handle_event(event, self.sound_engine)

        return self.authenticated_user

    def update(self, dt: float):
        """Updates animations and timers."""
        self.toast.update(dt)
        current_inputs = self.login_inputs if self.mode == "LOGIN" else self.reg_inputs
        for inp in current_inputs:
            inp.update(dt)

        if self.mode == "LOGIN":
            self.btn_submit_login.update(dt)
            self.btn_switch_to_reg.update(dt)
            self.btn_guest_play.update(dt)
        else:
            self.btn_submit_register.update(dt)
            self.btn_switch_to_login.update(dt)

    def draw(self, surface: pygame.Surface):
        """Draws authentication card, fields, and title graphics."""
        # 1. Background Fill
        surface.fill(COLOR_BG_DARK)

        # Decorative background grid lines
        for x in range(0, surface.get_width(), 60):
            pygame.draw.line(surface, (20, 24, 36), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 60):
            pygame.draw.line(surface, (20, 24, 36), (0, y), (surface.get_width(), y), 1)

        # 2. Main Game Header
        title_surf = self.fonts["title"].render("TYPING RACER 2D", True, COLOR_ACCENT_PRIMARY)
        title_rect = title_surf.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(title_surf, title_rect)

        sub_surf = self.fonts["small"].render("ARCADE CHAMPIONSHIP • TYPE TO WIN", True, COLOR_ACCENT_GOLD)
        sub_rect = sub_surf.get_rect(center=(surface.get_width() // 2, 85))
        surface.blit(sub_surf, sub_rect)

        # 3. Card Container Panel
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.card_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.card_rect, width=2, border_radius=12)

        # Card Title Header
        header_text = "SIGN IN TO YOUR GARAGE" if self.mode == "LOGIN" else "CREATE RACER PROFILE"
        card_header = self.fonts["medium"].render(header_text, True, COLOR_TEXT_WHITE)
        surface.blit(card_header, (self.card_rect.centerx - card_header.get_width() // 2, self.card_rect.y + 24))

        # Divider line
        pygame.draw.line(
            surface,
            COLOR_PANEL_BORDER,
            (self.card_rect.x + 30, self.card_rect.y + 60),
            (self.card_rect.right - 30, self.card_rect.y + 60),
            1
        )

        # 4. Form Inputs & Labels
        if self.mode == "LOGIN":
            lbl_email = self.fonts["small"].render("Email Address", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_email, (self.login_email.rect.x, self.login_email.rect.y - 20))
            self.login_email.draw(surface)

            lbl_pass = self.fonts["small"].render("Password", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_pass, (self.login_password.rect.x, self.login_password.rect.y - 20))
            self.login_password.draw(surface)

            self.btn_submit_login.draw(surface)
            self.btn_switch_to_reg.draw(surface)
            self.btn_guest_play.draw(surface)

        else:
            lbl_name = self.fonts["small"].render("Driver Name", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_name, (self.reg_name.rect.x, self.reg_name.rect.y - 18))
            self.reg_name.draw(surface)

            lbl_email = self.fonts["small"].render("Email Address", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_email, (self.reg_email.rect.x, self.reg_email.rect.y - 18))
            self.reg_email.draw(surface)

            lbl_pass = self.fonts["small"].render("Password (8+ chars)", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_pass, (self.reg_pass.rect.x, self.reg_pass.rect.y - 18))
            self.reg_pass.draw(surface)

            lbl_confirm = self.fonts["small"].render("Confirm Password", True, COLOR_TEXT_MUTED)
            surface.blit(lbl_confirm, (self.reg_confirm.rect.x, self.reg_confirm.rect.y - 18))
            self.reg_confirm.draw(surface)

            self.btn_submit_register.draw(surface)
            self.btn_switch_to_login.draw(surface)

        # 5. Toast Notifications
        self.toast.draw(surface)
