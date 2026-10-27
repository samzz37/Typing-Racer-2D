# Typing Racer 2D — Arcade Championship

A complete, polished 2D arcade typing racing game built in Python and Pygame. Race five simultaneous competitors (1 human driver, 4 AI-controlled rivals) across 5 horizontal lanes from left to right. Your typing speed, precision, and combo streaks determine your vehicle's acceleration and nitro boosts!

---

## 🏎️ Key Features

* **5 Simultaneous Racers:** Five clearly separated horizontal lanes with the player in the spotlight lane and 4 AI opponents with unique colors, names, and human-like typing cadences.
* **Typing-Driven Physics:** Real-time Gross WPM, Net WPM, and Accuracy directly drive the player car's velocity, wheel spin, and nitro flames.
* **4 Distinct Difficulty Championships:**
  * **Easy:** 3 Lines (~20-25 words), 5 minutes time limit, AI ~26-36 WPM.
  * **Medium:** 6 Lines (~40-50 words), 2m 30s time limit, AI ~48-62 WPM.
  * **Hard:** 1 Paragraph (~70-85 words), 1m 30s time limit, AI ~72-86 WPM.
  * **Extreme Hard:** ~1.5 Paragraphs (~100-120 words), 1 minute time limit, AI ~96-112 WPM.
* **Nitro Boost System:** Achieve a streak of 25 consecutive correct characters to ignite nitro exhaust flames and surge ahead!
* **Parallax Scrolling Circuit:** Multi-layered scrolling skyline, grandstands with animated spectators, road markings, streetlamps, and a checkered overhead finish gantry.
* **Full Authentication & Security:** Sign In and Sign Up screens with field validation (regex email check, password confirmation, minimum 8 characters) and PBKDF2-HMAC-SHA256 password hashing with unique salts stored in SQLite. Also supports Quick Practice as Guest.
* **Garage & Customization:** Choose from 6 arcade paint jobs (Cyber Cyan, Solar Crimson, Arcade Gold, Emerald Phantom, Ultra Violet, Stealth Silver) with live turntable showroom preview and nitro test drive.
* **Podium & Hall of Fame:** 3D-styled arcade podium (1st, 2nd, 3rd) with victory confetti, comprehensive race telemetry, and global/personal leaderboards in SQLite.
* **Zero External Audio Dependencies:** Synthesized 16-bit PCM sound effects (mechanical keyboard click, error buzz, countdown beeps, nitro whoosh, engine hum, victory fanfare, and synthwave BGM loop) generated programmatically.

---

## 🛠️ Technology Stack & Requirements

* **Language:** Python 3.10+ (tested on Python 3.14 on Windows 10/11)
* **Framework:** `pygame-ce` (Community Edition, 2.5.8+)
* **Database:** SQLite3 (standard library)
* **Audio:** `pygame.mixer` with built-in procedural WAV generation

---

## 🚀 Installation & Running

### 1. Install Dependencies
In your terminal or Command Prompt, run:
```bash
pip install pygame-ce
```
*(or `pip install -r requirements.txt`)*

### 2. Launch the Game
```bash
python main.py
```

---

## 🎮 Game Controls

| Action | Control |
|---|---|
| **Type Passage** | Keyboard keys (letters, numbers, punctuation, spaces) |
| **Fix Mistake** | `Backspace` |
| **Pause Race** | `Escape` (`ESC`) |
| **Navigate Fields** | `Tab` / Mouse click |
| **Submit / Start** | `Enter` / `Return` or Mouse click |
| **Toggle Audio** | Click audio button in Menu / Settings |

---

## 📁 Project Architecture

```
typing_racer_2d/
├── main.py                     # Application entry point and state machine
├── requirements.txt            # Dependency definitions
├── README.md                   # Documentation
├── core/
│   ├── config.py               # Constants, colors, dimensions, and presets
│   ├── passages.py             # Curated texts for 4 difficulty levels
│   └── sound_engine.py         # Procedural WAV sound synthesis & mixer
├── database/
│   └── db_manager.py           # SQLite connection, PBKDF2 auth, leaderboards
├── models/
│   ├── car.py                  # 2D car entity, side-view graphics, physics
│   ├── ai_racer.py             # AI typing simulation with human cadence
│   └── particle.py             # Exhaust smoke, nitro flame trails, confetti
├── ui/
│   ├── components.py           # Button, TextInput (with password mask), Toast
│   ├── track_renderer.py       # 5 horizontal lanes, parallax background, radar
│   └── hud.py                  # Live typing box, character highlights, WPM gauges
└── screens/
    ├── auth_screen.py          # Sign In & Registration with validation
    ├── menu_screen.py          # Championship Menu & difficulty selector
    ├── race_screen.py          # Active race loop, 3-2-1 countdown, telemetry
    ├── results_screen.py       # 3D podium, stats breakdown, rematch
    ├── leaderboard_screen.py   # Global rankings & career race history
    └── garage_screen.py        # Car customization & showroom test drive
```

---

## 🛡️ Database Schema

The game automatically initializes `typing_racer.db` with two tables:

1. **`users` Table:**
   - `id`: Primary Key
   - `full_name`: Driver display name
   - `email`: Unique validated email
   - `password_hash`: PBKDF2-HMAC-SHA256 hex hash
   - `salt`: 16-byte random salt (hex)
   - `best_wpm`: Career high gross WPM
   - `total_races`: Career race count
   - `total_wins`: Total 1st-place victories
   - `preferred_car_color`: Saved paint job index

2. **`race_results` Table:**
   - `id`: Primary Key
   - `user_id`: Foreign key linked to `users` (or NULL for guests)
   - `difficulty`: Easy, Medium, Hard, Extreme Hard
   - `wpm`: Gross Words Per Minute
   - `net_wpm`: Net Words Per Minute
   - `accuracy`: Typing accuracy percentage
   - `time_taken_seconds`: Race duration in seconds
   - `placement`: Final rank (1 to 5)
   - `mistakes`: Uncorrected typo count
   - `total_chars`: Total characters typed
   - `race_date`: Timestamp
