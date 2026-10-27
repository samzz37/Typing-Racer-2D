"""
Typing Racer 2D - Automated Test Suite
Verifies database auth & hashing, sound synthesis, telemetry, AI racers, and screen lifecycles.
"""
import os
import sys
import tempfile
import pygame

# Set dummy video driver for headless test execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from core.sound_engine import SoundEngine
from core.passages import get_random_passage, PASSAGES
from models.car import Car
from models.ai_racer import AIRacer
from models.particle import ParticleEmitter
from ui.track_renderer import TrackRenderer
from ui.hud import RaceHUD
from screens.auth_screen import AuthScreen
from screens.menu_screen import MenuScreen
from screens.race_screen import RaceScreen
from screens.results_screen import ResultsScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.garage_screen import GarageScreen


def test_database_and_auth():
    print("[TEST] Testing Database Manager & Authentication...")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = DatabaseManager(db_path=db_path)

    # 1. Register with short password (should fail)
    ok, msg, user = db.register_user("Speedy", "speed@racing.com", "short", "short")
    assert not ok, "Short password should fail validation"

    # 2. Register with mismatched password (should fail)
    ok, msg, user = db.register_user("Speedy", "speed@racing.com", "validpassword123", "different123")
    assert not ok, "Mismatched passwords should fail validation"

    # 3. Register valid user (should succeed)
    ok, msg, user = db.register_user("Speedy Racer", "speed@racing.com", "nitroboost99", "nitroboost99")
    assert ok and user is not None, f"Registration failed: {msg}"
    user_id = user["id"]

    # 4. Duplicate email registration (should fail)
    ok, msg, dup_user = db.register_user("Clone Racer", "speed@racing.com", "nitroboost99", "nitroboost99")
    assert not ok, "Duplicate email should be rejected"

    # 5. Login with wrong password (should fail)
    ok, msg, log_user = db.login_user("speed@racing.com", "wrongpassword")
    assert not ok, "Wrong password should fail login"

    # 6. Login with correct password (should succeed)
    ok, msg, log_user = db.login_user("speed@racing.com", "nitroboost99")
    assert ok and log_user["id"] == user_id, f"Login failed: {msg}"

    # 7. Record race result
    recorded = db.record_race_result(
        user_id=user_id,
        difficulty="Medium",
        wpm=78.5,
        net_wpm=76.0,
        accuracy=97.5,
        time_taken_seconds=42.3,
        placement=1,
        mistakes=2,
        total_chars=250
    )
    assert recorded, "Recording race result failed"

    # 8. Check leaderboard and stats
    leaderboard = db.get_leaderboard("Medium")
    assert len(leaderboard) == 1, "Leaderboard should have 1 record"
    assert leaderboard[0]["wpm"] == 78.5, "Leaderboard WPM mismatch"
    assert leaderboard[0]["racer_name"] == "Speedy Racer"

    stats = db.get_user_stats(user_id)
    assert stats["races"] == 1, "Stats races count mismatch"
    assert stats["wins"] == 1, "Stats wins count mismatch"
    assert stats["best_wpm"] == 78.5, "Stats best WPM mismatch"

    # Clean up temp db
    try:
        os.remove(db_path)
    except Exception:
        pass
    print("  -> Database & Authentication: PASSED")


def test_passages():
    print("[TEST] Testing Text Passages across 4 Difficulties...")
    for diff in ["Easy", "Medium", "Hard", "Extreme Hard"]:
        pool = PASSAGES[diff]
        assert len(pool) >= 2, f"Difficulty {diff} must have at least 2 passages"
        passage = get_random_passage(diff)
        assert len(passage) > 30, f"Passage for {diff} too short"
    print("  -> Text Passages: PASSED")


def test_sound_engine():
    print("[TEST] Testing Sound Engine Synthesis...")
    pygame.init()
    se = SoundEngine()
    # Verify core sounds exist
    expected = ["click", "error", "countdown_beep", "countdown_go", "nitro", "finish", "engine"]
    for s in expected:
        assert s in se.sounds, f"Missing sound {s}"
    print("  -> Sound Engine: PASSED")


def test_models_and_physics():
    print("[TEST] Testing Car, AI Racer, and Particle Models...")
    emitter = ParticleEmitter()
    car = Car("Player", lane_index=2, palette_index=0, is_player=True, emitter=emitter)
    
    # Test car motion lerp
    car.update_motion(
        dt=0.1,
        progress=0.5,
        current_wpm=65.0,
        nitro=True,
        track_start_x=100.0,
        track_finish_x=1140.0
    )
    assert car.screen_x > 100.0, "Car position should have advanced"
    assert len(emitter.particles) > 0, "Nitro should emit particles"

    # Test AI Racer
    ai = AIRacer(car, base_wpm=55.0, passage="This is a test racing passage for testing.")
    ai.update(dt=0.5, race_active=True)
    assert ai.chars_typed > 0, "AI racer should have typed characters"
    assert ai.progress > 0, "AI racer progress should be > 0"
    print("  -> Models & Physics: PASSED")


def test_screens_and_typing_simulation():
    print("[TEST] Testing Screens & Live Typing Simulation...")
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    fonts = {
        "title": pygame.font.Font(None, 40),
        "big": pygame.font.Font(None, 64),
        "medium": pygame.font.Font(None, 24),
        "small": pygame.font.Font(None, 18),
        "input": pygame.font.Font(None, 20),
        "code": pygame.font.Font(None, 22),
        "hud": pygame.font.Font(None, 20)
    }
    se = SoundEngine()
    db = DatabaseManager()
    user = {"id": 1, "full_name": "Test Driver", "email": "test@test.com", "best_wpm": 60.0, "total_races": 5, "total_wins": 2, "preferred_car_color": 0}

    # 1. Test AuthScreen
    auth = AuthScreen(db, fonts, se)
    auth.update(0.016)
    auth.draw(surface)

    # 2. Test MenuScreen
    menu = MenuScreen(user, fonts, se)
    menu.update(0.016)
    menu.draw(surface)

    # 3. Test RaceScreen & Typing Gameplay
    race = RaceScreen("Easy", user, db, fonts, se)
    assert len(race.cars) == 5, "Must have exactly 5 racing cars"
    assert len(race.ai_racers) == 4, "Must have 4 AI racers"
    assert race.player_car.is_player, "Center car must be player car"

    # Advance countdown past 0
    race.countdown_timer = 0.05
    race.update(0.1)
    assert race.race_started, "Race should have started"

    # Simulate typing correct first 5 characters
    for _ in range(5):
        exp_char = race.passage[race.player_char_idx]
        key_event = pygame.event.Event(pygame.KEYDOWN, unicode=exp_char, key=ord(exp_char.lower()) if exp_char.isalpha() else pygame.K_SPACE)
        race._handle_typing_key(key_event)

    assert race.player_char_idx == 5, f"Expected 5 chars typed, got {race.player_char_idx}"
    assert race.correct_keystrokes == 5, "Correct keystrokes should be 5"
    assert not race.has_error, "Should not have error"

    # Simulate typing wrong character
    wrong_event = pygame.event.Event(pygame.KEYDOWN, unicode="~", key=pygame.K_BACKQUOTE)
    race._handle_typing_key(wrong_event)
    assert race.has_error, "Error should be flagged"
    assert race.mistakes == 1, "Mistakes count should be 1"

    # Backspace to clear error
    bs_event = pygame.event.Event(pygame.KEYDOWN, unicode="", key=pygame.K_BACKSPACE)
    race._handle_typing_key(bs_event)
    assert not race.has_error, "Error should be cleared after backspace"

    race.update(0.1)
    race.draw(surface)

    # 4. Test ResultsScreen
    summary = {
        "difficulty": "Easy",
        "placement": 1,
        "wpm": 68.0,
        "net_wpm": 66.0,
        "accuracy": 98.0,
        "time_taken": 25.5,
        "mistakes": 1,
        "total_chars": 120,
        "finish_order": [("Test Driver", True, 1, 25.5, (0, 229, 255)), ("TurboTyper", False, 2, 28.0, (255, 60, 80))]
    }
    results = ResultsScreen(summary, fonts, se)
    results.update(0.016)
    results.draw(surface)

    # 5. Test LeaderboardScreen
    leaderboard = LeaderboardScreen(user, db, fonts, se)
    leaderboard.update(0.016)
    leaderboard.draw(surface)

    # 6. Test GarageScreen
    garage = GarageScreen(user, db, fonts, se)
    garage.update(0.016)
    garage.draw(surface)

    print("  -> Screens & Typing Simulation: PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("STARTING TYPING RACER 2D TEST SUITE")
    print("=" * 60)
    test_database_and_auth()
    test_passages()
    test_sound_engine()
    test_models_and_physics()
    test_screens_and_typing_simulation()
    print("=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY! [FINISHED]")
    print("=" * 60)
