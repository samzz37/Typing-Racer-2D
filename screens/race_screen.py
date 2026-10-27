"""
Typing Racer 2D - Race Screen
The primary gameplay controller managing the 5-racer simulation, typing engine,
physics, HUD telemetry, audio triggers, and race completion logic.
"""
import time
import pygame
from typing import Dict, Any, List, Optional
from core.config import (
    DIFFICULTY_PRESETS, CAR_PALETTES, AI_PROFILES,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD, COLOR_TEXT_WHITE
)
from core.passages import get_random_passage
from models.car import Car
from models.ai_racer import AIRacer
from models.particle import ParticleEmitter
from ui.track_renderer import TrackRenderer
from ui.hud import RaceHUD
from ui.components import Button


class RaceScreen:
    """Controls the live 5-car typing race."""
    def __init__(
        self,
        difficulty: str,
        user: Dict[str, Any],
        db,
        fonts: Dict[str, pygame.font.Font],
        sound_engine
    ):
        self.difficulty = difficulty
        self.user = user
        self.db = db
        self.fonts = fonts
        self.sound_engine = sound_engine

        # Difficulty parameters
        self.preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS["Medium"])
        self.time_limit = float(self.preset["time_limit"])
        self.time_remaining = self.time_limit

        # Select race passage
        self.passage = get_random_passage(difficulty)
        self.total_chars = len(self.passage)

        # Particle emitter
        self.emitter = ParticleEmitter()

        # Track & HUD
        self.track_renderer = TrackRenderer()
        self.hud = RaceHUD(self.fonts["code"], self.fonts["hud"], self.fonts["big"])
        self.hud.prepare_passage(self.passage)

        # Setup 5 Cars across 5 lanes
        self.cars: List[Car] = []
        self.ai_racers: List[AIRacer] = []
        self.player_car: Optional[Car] = None
        self._setup_racers()

        # Race state flags
        self.countdown_timer: float = 3.6  # 3.6s countdown down to 0
        self.last_beep_second: int = 4
        self.race_started: bool = False
        self.race_finished: bool = False
        self.is_paused: bool = False
        self.race_start_timestamp: float = 0.0

        # Player typing telemetry
        self.player_char_idx: int = 0
        self.has_error: bool = False
        self.total_keystrokes: int = 0
        self.correct_keystrokes: int = 0
        self.mistakes: int = 0
        self.player_wpm: float = 0.0
        self.player_net_wpm: float = 0.0
        self.player_accuracy: float = 100.0
        self.nitro_streak: int = 0
        self.nitro_active: bool = False
        self.nitro_timer: float = 0.0

        # Placements tracking
        self.finish_order: List[Car] = []
        self.player_final_placement: int = 1
        self.time_taken: float = 0.0

        # Screen transition result
        self.next_screen: Optional[str] = None
        self.race_summary_data: Optional[Dict[str, Any]] = None

        # Pause menu buttons
        cx = 1280 // 2
        self.btn_resume = Button(
            pygame.Rect(cx - 130, 290, 260, 44),
            "RESUME RACE",
            self.fonts["medium"],
            on_click=self._resume_race
        )
        self.btn_restart = Button(
            pygame.Rect(cx - 130, 350, 260, 44),
            "RESTART RACE",
            self.fonts["medium"],
            on_click=self._restart_race
        )
        self.btn_menu = Button(
            pygame.Rect(cx - 130, 410, 260, 44),
            "EXIT TO MENU",
            self.fonts["medium"],
            on_click=self._exit_to_menu
        )

        # Start ambient engine hum
        if self.sound_engine:
            self.sound_engine.start_engine_hum()

    def _setup_racers(self):
        """Initializes 5 cars: player in lane 2, 4 AI in lanes 0, 1, 3, 4."""
        player_palette = self.user.get("preferred_car_color", 0)

        # Lane assignment:
        # Lane 0: AI 0 (TurboTyper)
        # Lane 1: AI 1 (NitroNova)
        # Lane 2: Player (YOU)
        # Lane 3: AI 2 (ApexAce)
        # Lane 4: AI 3 (ByteRacer)

        min_ai_wpm, max_ai_wpm = self.preset["ai_wpm_range"]
        ai_idx = 0

        for lane in range(5):
            if lane == 2:
                # Human Player
                self.player_car = Car(
                    name=self.user.get("full_name", "YOU"),
                    lane_index=lane,
                    palette_index=player_palette,
                    is_player=True,
                    emitter=self.emitter
                )
                self.cars.append(self.player_car)
            else:
                ai_info = AI_PROFILES[ai_idx % len(AI_PROFILES)]
                car = Car(
                    name=ai_info["name"],
                    lane_index=lane,
                    palette_index=ai_info["palette_idx"],
                    is_player=False,
                    emitter=self.emitter
                )
                self.cars.append(car)

                # Compute AI target WPM
                wpm_span = max_ai_wpm - min_ai_wpm
                target_wpm = min_ai_wpm + (ai_idx / 3.0) * wpm_span + ai_info["skill_offset"]
                ai_racer = AIRacer(car, target_wpm, self.passage)
                self.ai_racers.append(ai_racer)
                ai_idx += 1

    def _resume_race(self):
        self.is_paused = False

    def _restart_race(self):
        self.next_screen = "RESTART"

    def _exit_to_menu(self):
        if self.sound_engine:
            self.sound_engine.stop_engine_hum()
        self.next_screen = "MENU"

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handles keyboard typing, pause toggling, and button interactions."""
        # ESC toggles pause
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_paused = not self.is_paused
            if self.sound_engine:
                self.sound_engine.play_click()
            return None

        # Pause menu button handling
        if self.is_paused:
            self.btn_resume.handle_event(event, self.sound_engine)
            self.btn_restart.handle_event(event, self.sound_engine)
            self.btn_menu.handle_event(event, self.sound_engine)
            return self.next_screen

        # If race finished, click or enter advances to results
        if self.race_finished:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                return "RESULTS"

        # Active typing input handling
        if self.race_started and not self.race_finished:
            if event.type == pygame.KEYDOWN:
                self._handle_typing_key(event)

        return self.next_screen

    def _handle_typing_key(self, event: pygame.event.Event):
        """Processes keystrokes against target passage with live accuracy and WPM."""
        if self.player_char_idx >= self.total_chars:
            return

        expected_char = self.passage[self.player_char_idx]

        if event.key == pygame.K_BACKSPACE:
            # Clear error state on backspace
            if self.has_error:
                self.has_error = False
                if self.sound_engine:
                    self.sound_engine.play_click()
            return

        # Check printable unicode input
        typed_char = event.unicode
        if not typed_char:
            return

        self.total_keystrokes += 1

        if not self.has_error and typed_char == expected_char:
            # Correct keystroke
            self.player_char_idx += 1
            self.correct_keystrokes += 1
            self.nitro_streak += 1

            if self.sound_engine:
                self.sound_engine.play_click()

            # Check for Nitro Activation (at 25 consecutive correct characters)
            if self.nitro_streak >= 25 and not self.nitro_active:
                self.nitro_active = True
                self.nitro_timer = 3.5
                if self.sound_engine:
                    self.sound_engine.play_nitro()

            # Check if player crossed finish line
            if self.player_char_idx >= self.total_chars:
                self._finish_player_race()

        else:
            # Typing mistake
            self.has_error = True
            self.mistakes += 1
            self.nitro_streak = 0
            self.nitro_active = False

            if self.sound_engine:
                self.sound_engine.play_error()

    def _finish_player_race(self):
        """Triggered when the player types the entire passage."""
        self.player_car.finished = True
        self.player_car.finish_time = time.time() - self.race_start_timestamp
        self.time_taken = self.player_car.finish_time

        if self.player_car not in self.finish_order:
            self.finish_order.append(self.player_car)
            self.player_final_placement = len(self.finish_order)
            self.player_car.placement = self.player_final_placement

        self.race_finished = True

        # Fanfare & Confetti
        if self.sound_engine:
            self.sound_engine.play_finish()
            self.sound_engine.stop_engine_hum()

        self.emitter.emit_confetti(self.player_car.screen_x, self.player_car.center_y, count=60)

        # Record to SQLite database
        user_id = self.user.get("id")
        self.db.record_race_result(
            user_id=user_id,
            difficulty=self.difficulty,
            wpm=self.player_wpm,
            net_wpm=self.player_net_wpm,
            accuracy=self.player_accuracy,
            time_taken_seconds=self.time_taken,
            placement=self.player_final_placement,
            mistakes=self.mistakes,
            total_chars=self.total_chars
        )

        # Prepare summary packet for results screen
        self.race_summary_data = {
            "difficulty": self.difficulty,
            "placement": self.player_final_placement,
            "wpm": self.player_wpm,
            "net_wpm": self.player_net_wpm,
            "accuracy": self.player_accuracy,
            "time_taken": self.time_taken,
            "mistakes": self.mistakes,
            "total_chars": self.total_chars,
            "finish_order": [(c.name, c.is_player, c.placement, c.finish_time, c.palette["body"]) for c in self.finish_order]
        }

    def update(self, dt: float):
        """Updates race countdown, AI racers, telemetry, and animations."""
        if self.is_paused:
            self.btn_resume.update(dt)
            self.btn_restart.update(dt)
            self.btn_menu.update(dt)
            return

        # 1. Countdown Phase (3-2-1-GO!)
        if not self.race_started:
            self.countdown_timer -= dt
            sec_floor = int(self.countdown_timer)

            if sec_floor != self.last_beep_second:
                self.last_beep_second = sec_floor
                if self.sound_engine:
                    if sec_floor in (3, 2, 1):
                        self.sound_engine.play_countdown_beep()
                    elif sec_floor == 0:
                        self.sound_engine.play_countdown_go()

            if self.countdown_timer <= 0.0:
                self.race_started = True
                self.race_start_timestamp = time.time()
                self.countdown_timer = 0.0

            # Idle track movement during countdown
            self.track_renderer.update(dt, reference_speed_wpm=10.0)
            self.emitter.update(dt)
            return

        # 2. Active Racing Phase
        elapsed = time.time() - self.race_start_timestamp
        self.time_remaining = max(0.0, self.time_limit - elapsed)

        # Check time limit expiration
        if self.time_remaining <= 0.0 and not self.race_finished:
            self._finish_player_race()
            return

        # Update Nitro timer
        if self.nitro_active:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0.0:
                self.nitro_active = False

        # Calculate live Player Telemetry (WPM & Accuracy)
        elapsed_minutes = max(0.005, elapsed / 60.0)
        # Gross WPM = (correct chars / 5) / minutes
        self.player_wpm = (self.correct_keystrokes / 5.0) / elapsed_minutes
        # Net WPM = max(0, gross - (mistakes / minutes))
        self.player_net_wpm = max(0.0, self.player_wpm - (self.mistakes / elapsed_minutes))

        if self.total_keystrokes > 0:
            self.player_accuracy = (self.correct_keystrokes / self.total_keystrokes) * 100.0

        # Update Player Car Motion
        player_progress = min(1.0, self.player_char_idx / max(1, self.total_chars))
        self.player_car.update_motion(
            dt=dt,
            progress=player_progress,
            current_wpm=self.player_wpm,
            nitro=self.nitro_active,
            track_start_x=100.0,
            track_finish_x=1140.0
        )

        # Update AI Racers
        for ai in self.ai_racers:
            ai.update(dt, race_active=self.race_started)
            
            # Check AI finish line crossing
            if ai.is_finished and ai.car not in self.finish_order:
                ai.car.finished = True
                ai.car.finish_time = elapsed
                self.finish_order.append(ai.car)
                ai.car.placement = len(self.finish_order)

        # Calculate current live placement ranking
        # Sort cars by progress descending
        sorted_cars = sorted(self.cars, key=lambda c: c.progress, reverse=True)
        for idx, car in enumerate(sorted_cars):
            if not car.finished:
                car.placement = idx + 1

        # Parallax road scrolling
        ref_speed = self.player_wpm if self.player_wpm > 0 else 25.0
        self.track_renderer.update(dt, reference_speed_wpm=ref_speed)

        # HUD & Particles
        self.hud.update(dt)
        self.emitter.update(dt)

    def draw(self, surface: pygame.Surface):
        """Renders track, cars, particles, HUD, and overlays."""
        # 1. Background, Parallax & Track
        self.track_renderer.draw(surface, self.fonts["small"], self.fonts["medium"])

        # 2. Radar Mini-Map Track at Top
        self.track_renderer.draw_track_radar(surface, self.cars, self.fonts["small"])

        # 3. Particle Effects
        self.emitter.draw(surface)

        # 4. Five Cars on 5 Lanes
        for car in self.cars:
            car.draw(surface, self.fonts["small"])

        # 5. Live Telemetry HUD Bar (WPM, Accuracy, Time, Nitro, Placement)
        self.hud.draw_gauges(
            surface=surface,
            wpm=self.player_wpm,
            net_wpm=self.player_net_wpm,
            accuracy=self.player_accuracy,
            time_remaining=self.time_remaining,
            placement=self.player_car.placement,
            nitro_streak=self.nitro_streak,
            difficulty=self.difficulty
        )

        # 6. Active Typing Passage Box
        self.hud.draw_typing_box(
            surface=surface,
            passage=self.passage,
            current_char_idx=self.player_char_idx,
            has_error=self.has_error
        )

        # 7. 3-2-1-GO! Countdown Overlay
        if self.countdown_timer > 0.0:
            self.hud.draw_countdown(surface, self.countdown_timer)

        # 8. Race Finished Banner Overlay
        if self.race_finished:
            fin_overlay = pygame.Surface((surface.get_width(), 90), pygame.SRCALPHA)
            pygame.draw.rect(fin_overlay, (15, 20, 32, 230), (0, 0, surface.get_width(), 90))
            pygame.draw.rect(fin_overlay, COLOR_ACCENT_GOLD, (0, 0, surface.get_width(), 90), width=2)
            surface.blit(fin_overlay, (0, 180))

            congrats_str = f"RACE FINISHED! YOU PLACED {self.player_final_placement}th"
            if self.player_final_placement == 1:
                congrats_str = "VICTORY! 1st PLACE CHAMPION!"
            
            c_surf = self.fonts["title"].render(congrats_str, True, COLOR_ACCENT_GOLD)
            surface.blit(c_surf, c_surf.get_rect(center=(surface.get_width() // 2, 215)))

            hint_surf = self.fonts["small"].render("PRESS ANY KEY OR CLICK TO VIEW PODIUM & RACE TELEMETRY", True, COLOR_TEXT_WHITE)
            surface.blit(hint_surf, hint_surf.get_rect(center=(surface.get_width() // 2, 250)))

        # 9. Pause Menu Overlay
        if self.is_paused:
            p_overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            p_overlay.fill((10, 14, 24, 200))
            surface.blit(p_overlay, (0, 0))

            card = pygame.Rect(1280 // 2 - 170, 200, 340, 280)
            pygame.draw.rect(surface, COLOR_PANEL_BG, card, border_radius=12)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, card, width=2, border_radius=12)

            pause_title = self.fonts["title"].render("RACE PAUSED", True, COLOR_ACCENT_PRIMARY)
            surface.blit(pause_title, pause_title.get_rect(center=(card.centerx, card.y + 45)))

            self.btn_resume.draw(surface)
            self.btn_restart.draw(surface)
            self.btn_menu.draw(surface)
