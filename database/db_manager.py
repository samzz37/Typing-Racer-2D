"""
Typing Racer 2D - Database Manager
Handles SQLite database connection, schema setup, user authentication with PBKDF2 hashing,
and race results statistics & leaderboards.
"""
import sqlite3
import hashlib
import os
import re
import hmac
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

from core.config import DB_PATH


class DatabaseManager:
    """Manages SQLite database operations for users and race statistics."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    best_wpm REAL DEFAULT 0.0,
                    total_races INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    preferred_car_color INTEGER DEFAULT 0
                )
            """)

            # Race results history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS race_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    difficulty TEXT NOT NULL,
                    wpm REAL NOT NULL,
                    net_wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    time_taken_seconds REAL NOT NULL,
                    placement INTEGER NOT NULL,
                    mistakes INTEGER DEFAULT 0,
                    total_chars INTEGER DEFAULT 0,
                    race_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    # --- Authentication Security Helpers ---

    @staticmethod
    def _hash_password(password: str, salt: bytes = None) -> Tuple[str, str]:
        """
        Hashes password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
        Returns (hex_hash, hex_salt).
        """
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return key.hex(), salt.hex()

    @staticmethod
    def _verify_password(password: str, stored_hash_hex: str, stored_salt_hex: str) -> bool:
        """Verifies password using constant-time comparison."""
        salt = bytes.fromhex(stored_salt_hex)
        computed_hash_hex, _ = DatabaseManager._hash_password(password, salt)
        return hmac.compare_digest(stored_hash_hex, computed_hash_hex)

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validates email format using regex."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    # --- User Authentication Operations ---

    def register_user(self, full_name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validates and registers a new user.
        Returns: (success: bool, message: str, user_dict or None)
        """
        full_name = full_name.strip()
        email = email.strip().lower()

        # Validation rules
        if not full_name:
            return False, "Please enter your full name.", None
        if len(full_name) < 2:
            return False, "Full name must be at least 2 characters long.", None
        
        if not email:
            return False, "Please enter your email address.", None
        if not self.validate_email_format(email):
            return False, "Please enter a valid email address (e.g. driver@racing.com).", None

        if not password:
            return False, "Please enter a password.", None
        if len(password) < 8:
            return False, "Password must be at least 8 characters long.", None

        if password != confirm_password:
            return False, "Passwords do not match.", None

        password_hash, salt = self._hash_password(password)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (full_name, email, password_hash, salt)
                    VALUES (?, ?, ?, ?)
                    """,
                    (full_name, email, password_hash, salt)
                )
                user_id = cursor.lastrowid
                conn.commit()

                user_data = {
                    "id": user_id,
                    "full_name": full_name,
                    "email": email,
                    "best_wpm": 0.0,
                    "total_races": 0,
                    "total_wins": 0,
                    "preferred_car_color": 0
                }
                return True, "Account created successfully! Welcome to the Championship.", user_data

        except sqlite3.IntegrityError:
            return False, "An account with this email address already exists.", None
        except Exception as e:
            return False, f"Database error: {str(e)}", None

    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticates an existing user.
        Returns: (success: bool, message: str, user_dict or None)
        """
        email = email.strip().lower()

        if not email or not password:
            return False, "Please enter both email and password.", None

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, full_name, email, password_hash, salt, best_wpm, total_races, total_wins, preferred_car_color
                    FROM users
                    WHERE email = ?
                    """,
                    (email,)
                )
                row = cursor.fetchone()

                if not row:
                    return False, "Invalid email or password. Please try again.", None

                if not self._verify_password(password, row["password_hash"], row["salt"]):
                    return False, "Invalid email or password. Please try again.", None

                user_data = {
                    "id": row["id"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "best_wpm": row["best_wpm"],
                    "total_races": row["total_races"],
                    "total_wins": row["total_wins"],
                    "preferred_car_color": row["preferred_car_color"]
                }
                return True, f"Welcome back, {row['full_name']}!", user_data

        except Exception as e:
            return False, f"Login error: {str(e)}", None

    def update_user_car_color(self, user_id: int, color_index: int):
        """Updates preferred car color for the user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET preferred_car_color = ? WHERE id = ?", (color_index, user_id))
                conn.commit()
        except Exception:
            pass

    # --- Race Results & Leaderboards ---

    def record_race_result(
        self,
        user_id: Optional[int],
        difficulty: str,
        wpm: float,
        net_wpm: float,
        accuracy: float,
        time_taken_seconds: float,
        placement: int,
        mistakes: int,
        total_chars: int
    ) -> bool:
        """Saves race result and updates user lifetime statistics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO race_results (
                        user_id, difficulty, wpm, net_wpm, accuracy,
                        time_taken_seconds, placement, mistakes, total_chars
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, difficulty, round(wpm, 1), round(net_wpm, 1), round(accuracy, 1),
                     round(time_taken_seconds, 2), placement, mistakes, total_chars)
                )

                if user_id:
                    # Update aggregate stats on user
                    is_win = 1 if placement == 1 else 0
                    cursor.execute(
                        """
                        UPDATE users
                        SET total_races = total_races + 1,
                            total_wins = total_wins + ?,
                            best_wpm = MAX(best_wpm, ?)
                        WHERE id = ?
                        """,
                        (is_win, round(wpm, 1), user_id)
                    )
                conn.commit()
                return True
        except Exception as e:
            print("Failed to record race result:", e)
            return False

    def get_leaderboard(self, difficulty: str = "Medium", limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the top racers ranked by WPM for a specific difficulty."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT r.id, r.wpm, r.net_wpm, r.accuracy, r.time_taken_seconds, r.placement, r.race_date,
                           COALESCE(u.full_name, 'Guest Driver') as racer_name
                    FROM race_results r
                    LEFT JOIN users u ON r.user_id = u.id
                    WHERE r.difficulty = ?
                    ORDER BY r.wpm DESC, r.accuracy DESC
                    LIMIT ?
                    """,
                    (difficulty, limit)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print("Leaderboard error:", e)
            return []

    def get_user_history(self, user_id: int, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns the most recent race history for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, difficulty, wpm, net_wpm, accuracy, time_taken_seconds, placement, mistakes, race_date
                    FROM race_results
                    WHERE user_id = ?
                    ORDER BY race_date DESC
                    LIMIT ?
                    """,
                    (user_id, limit)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception:
            return []

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Calculates aggregated performance statistics for a specific user."""
        defaults = {
            "races": 0,
            "wins": 0,
            "win_rate": 0.0,
            "best_wpm": 0.0,
            "avg_wpm": 0.0,
            "avg_accuracy": 0.0
        }
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(*) as races,
                           SUM(CASE WHEN placement = 1 THEN 1 ELSE 0 END) as wins,
                           MAX(wpm) as best_wpm,
                           AVG(wpm) as avg_wpm,
                           AVG(accuracy) as avg_accuracy
                    FROM race_results
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                row = cursor.fetchone()
                if row and row["races"] > 0:
                    races = row["races"]
                    wins = row["wins"] or 0
                    return {
                        "races": races,
                        "wins": wins,
                        "win_rate": round((wins / races) * 100, 1),
                        "best_wpm": round(row["best_wpm"] or 0.0, 1),
                        "avg_wpm": round(row["avg_wpm"] or 0.0, 1),
                        "avg_accuracy": round(row["avg_accuracy"] or 0.0, 1)
                    }
                return defaults
        except Exception:
            return defaults
