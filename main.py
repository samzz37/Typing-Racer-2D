"""
Typing Racer 2D - Main Game Launcher
Entry point and master state controller for Typing Racer 2D.
"""
import sys
import os
import pygame

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE, COLOR_BG_DARK
)
from database.db_manager import DatabaseManager
from core.sound_engine import SoundEngine
from screens.auth_screen import AuthScreen
from screens.menu_screen import MenuScreen
from screens.race_screen import RaceScreen
from screens.results_screen import ResultsScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.garage_screen import GarageScreen


def init_game_fonts():
    """Initializes high-clarity modern fonts with fallbacks."""
    fonts = {}
    try:
        fonts["title"] = pygame.font.SysFont(["Segoe UI", "Trebuchet MS", "Arial"], 34, bold=True)
        fonts["big"] = pygame.font.SysFont(["Segoe UI", "Impact", "Arial"], 68, bold=True)
        fonts["medium"] = pygame.font.SysFont(["Segoe UI", "Arial"], 19, bold=True)
        fonts["small"] = pygame.font.SysFont(["Segoe UI", "Arial"], 14)
        fonts["input"] = pygame.font.SysFont(["Segoe UI", "Arial"], 16)
        fonts["code"] = pygame.font.SysFont(["Consolas", "Courier New", "monospace"], 22, bold=True)
        fonts["hud"] = pygame.font.SysFont(["Segoe UI", "Arial"], 16, bold=True)
    except Exception as e:
        print("Font fallback warning:", e)
        # Fallback to default Pygame fonts
        fonts["title"] = pygame.font.Font(None, 42)
        fonts["big"] = pygame.font.Font(None, 78)
        fonts["medium"] = pygame.font.Font(None, 26)
        fonts["small"] = pygame.font.Font(None, 20)
        fonts["input"] = pygame.font.Font(None, 22)
        fonts["code"] = pygame.font.Font(None, 26)
        fonts["hud"] = pygame.font.Font(None, 22)
    return fonts


class TypingRacerGame:
    """Master game application loop and screen manager."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        # Create display surface
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Initialize Subsystems
        self.db = DatabaseManager()
        self.sound_engine = SoundEngine()
        self.fonts = init_game_fonts()

        # Session State
        self.current_user = None
        self.active_difficulty = "Medium"
        self.last_race_summary = None

        # Game Screens
        self.state = "AUTH"  # "AUTH", "MENU", "RACE", "RESULTS", "LEADERBOARD", "GARAGE"
        self.auth_screen = AuthScreen(self.db, self.fonts, self.sound_engine)
        self.menu_screen = None
        self.race_screen = None
        self.results_screen = None
        self.leaderboard_screen = None
        self.garage_screen = None

        # Start BGM loop
        if self.sound_engine:
            self.sound_engine.start_bgm()

    def run(self):
        """Main application game loop."""
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0
            # Clamp dt to prevent physics tunneling if window is dragged
            dt = min(dt, 0.1)

            self._handle_events()
            self._update(dt)
            self._render()

        # Cleanup on exit
        if self.sound_engine:
            self.sound_engine.stop_engine_hum()
            self.sound_engine.stop_bgm()
        pygame.quit()
        sys.exit(0)

    def _handle_events(self):
        """Polls and dispatches OS and user input events."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
                return

            # State-specific event handling
            if self.state == "AUTH":
                user = self.auth_screen.handle_event(event)
                if user:
                    self.current_user = user
                    self.menu_screen = MenuScreen(self.current_user, self.fonts, self.sound_engine)
                    self.state = "MENU"

            elif self.state == "MENU":
                action = self.menu_screen.handle_event(event)
                if action == "START_RACE":
                    self.active_difficulty = self.menu_screen.selected_difficulty
                    self._start_new_race(self.active_difficulty)
                elif action == "GARAGE":
                    self.garage_screen = GarageScreen(self.current_user, self.db, self.fonts, self.sound_engine)
                    self.state = "GARAGE"
                elif action == "LEADERBOARD":
                    self.leaderboard_screen = LeaderboardScreen(self.current_user, self.db, self.fonts, self.sound_engine)
                    self.state = "LEADERBOARD"
                elif action == "LOGOUT":
                    self.current_user = None
                    self.auth_screen = AuthScreen(self.db, self.fonts, self.sound_engine)
                    self.state = "AUTH"
                elif action == "QUIT":
                    self.is_running = False

            elif self.state == "RACE":
                action = self.race_screen.handle_event(event)
                if action == "RESULTS":
                    self.last_race_summary = self.race_screen.race_summary_data
                    self.results_screen = ResultsScreen(self.last_race_summary, self.fonts, self.sound_engine)
                    self.state = "RESULTS"
                elif action == "RESTART":
                    self._start_new_race(self.active_difficulty)
                elif action == "MENU":
                    self.menu_screen = MenuScreen(self.current_user, self.fonts, self.sound_engine)
                    self.state = "MENU"

            elif self.state == "RESULTS":
                action = self.results_screen.handle_event(event)
                if action == "REPLAY":
                    self._start_new_race(self.active_difficulty)
                elif action == "LEADERBOARD":
                    self.leaderboard_screen = LeaderboardScreen(self.current_user, self.db, self.fonts, self.sound_engine)
                    self.state = "LEADERBOARD"
                elif action == "MENU":
                    self.menu_screen = MenuScreen(self.current_user, self.fonts, self.sound_engine)
                    self.state = "MENU"

            elif self.state == "LEADERBOARD":
                action = self.leaderboard_screen.handle_event(event)
                if action == "MENU":
                    self.menu_screen = MenuScreen(self.current_user, self.fonts, self.sound_engine)
                    self.state = "MENU"

            elif self.state == "GARAGE":
                action = self.garage_screen.handle_event(event)
                if action == "MENU":
                    self.menu_screen = MenuScreen(self.current_user, self.fonts, self.sound_engine)
                    self.state = "MENU"

    def _start_new_race(self, difficulty: str):
        """Initializes a new race session."""
        self.race_screen = RaceScreen(
            difficulty=difficulty,
            user=self.current_user,
            db=self.db,
            fonts=self.fonts,
            sound_engine=self.sound_engine
        )
        self.state = "RACE"

    def _update(self, dt: float):
        """Updates game state logic for active screen."""
        if self.state == "AUTH":
            self.auth_screen.update(dt)
        elif self.state == "MENU":
            self.menu_screen.update(dt)
        elif self.state == "RACE":
            self.race_screen.update(dt)
            # Check if race finished automatically and transition
            if self.race_screen.race_finished and self.race_screen.time_remaining <= 0.0:
                pass
        elif self.state == "RESULTS":
            self.results_screen.update(dt)
        elif self.state == "LEADERBOARD":
            self.leaderboard_screen.update(dt)
        elif self.state == "GARAGE":
            self.garage_screen.update(dt)

    def _render(self):
        """Renders active screen to display surface."""
        if self.state == "AUTH":
            self.auth_screen.draw(self.screen)
        elif self.state == "MENU":
            self.menu_screen.draw(self.screen)
        elif self.state == "RACE":
            self.race_screen.draw(self.screen)
        elif self.state == "RESULTS":
            self.results_screen.draw(self.screen)
        elif self.state == "LEADERBOARD":
            self.leaderboard_screen.draw(self.screen)
        elif self.state == "GARAGE":
            self.garage_screen.draw(self.screen)

        pygame.display.flip()


def main():
    """Application entry point."""
    game = TypingRacerGame()
    game.run()


if __name__ == "__main__":
    main()
