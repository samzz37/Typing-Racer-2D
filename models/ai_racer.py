"""
Typing Racer 2D - AI Opponent Simulation
Simulates realistic, human-like typing cadence with bursts, micro-hesitations,
and difficulty-scaled target speeds.
"""
import math
import random
from typing import Dict, Any
from models.car import Car


class AIRacer:
    """Controls an AI car's progress through realistic typing simulation."""
    def __init__(
        self,
        car: Car,
        base_wpm: float,
        passage: str
    ):
        self.car = car
        self.base_wpm = base_wpm
        self.passage = passage
        self.total_chars = max(1, len(passage))

        # Typing simulation states
        self.chars_typed: float = 0.0
        self.current_wpm: float = base_wpm
        self.is_finished: bool = False
        
        # Human variance parameters
        self.time_alive: float = 0.0
        self.speed_variance_phase: float = random.uniform(0, 10.0)
        self.hesitation_timer: float = 0.0
        self.burst_timer: float = 0.0
        self.burst_multiplier: float = 1.0

    def update(self, dt: float, race_active: bool):
        """Advances AI typing progress based on simulated human cadence."""
        if not race_active or self.is_finished:
            return

        self.time_alive += dt

        # Handle hesitation pauses (e.g. simulated hesitation at complex punctuation or word start)
        if self.hesitation_timer > 0.0:
            self.hesitation_timer -= dt
            self.car.update_motion(dt, self.progress, self.current_wpm * 0.4, False, 100.0, 1140.0)
            return

        # Random micro-hesitation trigger (approx once every 5-9 seconds)
        if random.random() < 0.012:
            self.hesitation_timer = random.uniform(0.12, 0.28)

        # Speed fluctuation: natural breathing rhythm (±12%)
        wave = math.sin(self.time_alive * 1.5 + self.speed_variance_phase) * 0.12
        
        # Occasional burst mode
        if self.burst_timer > 0.0:
            self.burst_timer -= dt
            self.burst_multiplier = 1.25
        else:
            self.burst_multiplier = 1.0
            if random.random() < 0.008:
                self.burst_timer = random.uniform(1.0, 2.5)

        # Calculate current dynamic WPM
        effective_wpm = max(15.0, self.base_wpm * (1.0 + wave) * self.burst_multiplier)
        self.current_wpm = effective_wpm

        # Calculate characters typed per second: standard formula 1 word = 5 characters
        chars_per_sec = (effective_wpm * 5.0) / 60.0
        self.chars_typed += chars_per_sec * dt

        if self.chars_typed >= self.total_chars:
            self.chars_typed = float(self.total_chars)
            self.is_finished = True

        nitro = (self.burst_multiplier > 1.1)

        # Update underlying car motion
        self.car.update_motion(
            dt=dt,
            progress=self.progress,
            current_wpm=self.current_wpm,
            nitro=nitro,
            track_start_x=100.0,
            track_finish_x=1140.0
        )

    @property
    def progress(self) -> float:
        """Returns 0.0 to 1.0 completion ratio."""
        return min(1.0, self.chars_typed / self.total_chars)
