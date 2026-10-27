"""
Typing Racer 2D - Core Configuration & Constants
"""
import os
import pygame

# --- Screen & Display Settings ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Typing Racer 2D - Arcade Championship"

# --- Colors (Curated Modern Arcade Palette) ---
COLOR_BG_DARK = (15, 17, 26)        # Deep space navy
COLOR_PANEL_BG = (24, 28, 42)       # Sleek card background
COLOR_PANEL_BORDER = (45, 52, 75)   # Border accent
COLOR_ACCENT_PRIMARY = (0, 229, 255) # Cyber Cyan / Nitro Blue
COLOR_ACCENT_SECONDARY = (255, 61, 113) # Neon Coral / Crimson
COLOR_ACCENT_GOLD = (255, 196, 0)   # Arcade Gold
COLOR_ACCENT_PURPLE = (179, 102, 255) # Electric Violet
COLOR_TEXT_WHITE = (245, 247, 250)
COLOR_TEXT_MUTED = (140, 150, 175)
COLOR_TEXT_DARK = (40, 44, 55)

# Racing Colors
COLOR_ASPHALT = (32, 35, 45)
COLOR_ASPHALT_LINE = (230, 235, 245)
COLOR_GRASS_TOP = (18, 42, 25)
COLOR_GRASS_BOTTOM = (12, 30, 18)
COLOR_KERB_RED = (235, 45, 60)
COLOR_KERB_WHITE = (245, 245, 250)
COLOR_GUARD_RAIL = (70, 80, 100)

# Typing Feedback Colors
COLOR_CHAR_PENDING = (120, 130, 155)
COLOR_CHAR_CORRECT = (46, 213, 115)     # Vibrant Emerald Green
COLOR_CHAR_WRONG = (255, 71, 87)        # Bright Error Red
COLOR_CURSOR_BOX = (0, 229, 255, 100)   # Cyan translucent glow
COLOR_CURSOR_LINE = (0, 229, 255)

# --- Racing Track Dimensions ---
TRACK_Y_START = 85
TRACK_HEIGHT = 380
NUM_LANES = 5
LANE_HEIGHT = TRACK_HEIGHT // NUM_LANES # 76 px per lane
TRACK_WORLD_LENGTH = 12000.0            # Virtual track distance units
FINISH_LINE_RATIO = 0.95                # 95% is the finish gantry line

# --- Difficulty Presets ---
DIFFICULTY_PRESETS = {
    "Easy": {
        "time_limit": 300,        # 5 minutes
        "lines_desc": "3 Lines (~20-25 words)",
        "ai_wpm_range": (26, 36), # AI opponents typing speed
        "color": (46, 213, 115),
        "difficulty_tag": "NOVICE"
    },
    "Medium": {
        "time_limit": 150,        # 2 minutes 30 seconds
        "lines_desc": "6 Lines (~40-50 words)",
        "ai_wpm_range": (48, 62),
        "color": (0, 229, 255),
        "difficulty_tag": "INTERMEDIATE"
    },
    "Hard": {
        "time_limit": 90,         # 1 minute 30 seconds
        "lines_desc": "1 Paragraph (~70-85 words)",
        "ai_wpm_range": (72, 86),
        "color": (255, 196, 0),
        "difficulty_tag": "ADVANCED"
    },
    "Extreme Hard": {
        "time_limit": 60,         # 1 minute
        "lines_desc": "1.5 Paragraphs (~100-120 words)",
        "ai_wpm_range": (96, 112),
        "color": (255, 61, 113),
        "difficulty_tag": "MASTER"
    }
}

# --- Car Color Options ---
CAR_PALETTES = [
    {"name": "Cyber Cyan", "body": (0, 210, 255), "highlight": (160, 245, 255), "glow": (0, 180, 255)},
    {"name": "Solar Crimson", "body": (255, 50, 75), "highlight": (255, 150, 160), "glow": (255, 30, 60)},
    {"name": "Arcade Gold", "body": (255, 190, 0), "highlight": (255, 235, 120), "glow": (255, 170, 0)},
    {"name": "Emerald Phantom", "body": (30, 215, 110), "highlight": (130, 255, 180), "glow": (20, 190, 90)},
    {"name": "Ultra Violet", "body": (175, 75, 255), "highlight": (220, 170, 255), "glow": (150, 50, 240)},
    {"name": "Stealth Silver", "body": (210, 215, 225), "highlight": (255, 255, 255), "glow": (180, 190, 205)},
]

# AI Competitors Names & Profiles
AI_PROFILES = [
    {"name": "TurboTyper", "palette_idx": 1, "skill_offset": -2.5},
    {"name": "NitroNova", "palette_idx": 2, "skill_offset": 1.5},
    {"name": "ApexAce", "palette_idx": 3, "skill_offset": 3.0},
    {"name": "ByteRacer", "palette_idx": 4, "skill_offset": -1.0},
]

# Project Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DB_PATH = os.path.join(BASE_DIR, "typing_racer.db")
