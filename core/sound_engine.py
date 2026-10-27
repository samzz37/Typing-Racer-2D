"""
Typing Racer 2D - Procedural Sound Engine & Audio Manager
Generates retro-arcade sound effects and synthwave background music
using standard library `wave` and `struct`, then plays them via `pygame.mixer`.
Requires zero external audio downloads.
"""
import math
import os
import struct
import wave
import random
from typing import Dict, Optional
import pygame

from core.config import SOUNDS_DIR


def generate_wav_file(filepath: str, duration_sec: float, sample_rate: int = 44100, wave_func=None):
    """Utility to generate a 16-bit mono PCM WAV file using a sample generator function."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_samples = int(duration_sec * sample_rate)
    
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)        # Mono
        wav.setsampwidth(2)        # 16-bit
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            sample_val = wave_func(t, i, num_samples, sample_rate) if wave_func else 0.0
            # Clamp to [-1.0, 1.0]
            sample_val = max(-1.0, min(1.0, sample_val))
            # Convert to signed 16-bit integer
            sample_int = int(sample_val * 32767)
            frames.extend(struct.pack('<h', sample_int))
        
        wav.writeframes(frames)


def ensure_sound_assets():
    """Generates all required game sound files if they do not exist."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)

    # 1. Mechanical Key Click (35ms crisp switch click)
    click_path = os.path.join(SOUNDS_DIR, "click.wav")
    if not os.path.exists(click_path):
        def click_gen(t, i, n, sr):
            env = math.exp(-t * 90.0)
            # High punch click + subtle low clack
            tone = 0.6 * math.sin(2 * math.pi * 1800 * t) + 0.4 * math.sin(2 * math.pi * 420 * t)
            noise = (random.random() * 2 - 1) * math.exp(-t * 200.0) * 0.4
            return (tone * 0.7 + noise) * env

        generate_wav_file(click_path, 0.045, 44100, click_gen)

    # 2. Error Buzz (130ms low square/saw warning)
    error_path = os.path.join(SOUNDS_DIR, "error.wav")
    if not os.path.exists(error_path):
        def error_gen(t, i, n, sr):
            env = math.exp(-t * 12.0)
            freq = 150.0 + 15.0 * math.sin(2 * math.pi * 30 * t)
            # Square wave
            sq = 1.0 if (t * freq) % 1.0 > 0.5 else -1.0
            saw = ((t * freq) % 1.0) * 2.0 - 1.0
            return (0.6 * sq + 0.4 * saw) * env * 0.7

        generate_wav_file(error_path, 0.15, 44100, error_gen)

    # 3. Countdown Beep (90ms crisp sine beep at 660 Hz)
    beep_path = os.path.join(SOUNDS_DIR, "countdown_beep.wav")
    if not os.path.exists(beep_path):
        def beep_gen(t, i, n, sr):
            env = 1.0 - (t / 0.09)
            tone = math.sin(2 * math.pi * 660.0 * t)
            return tone * max(0.0, env) * 0.8

        generate_wav_file(beep_path, 0.09, 44100, beep_gen)

    # 4. Countdown GO Chime (350ms bright harmonic chord)
    go_path = os.path.join(SOUNDS_DIR, "countdown_go.wav")
    if not os.path.exists(go_path):
        def go_gen(t, i, n, sr):
            env = math.exp(-t * 8.0)
            tone = (
                0.5 * math.sin(2 * math.pi * 1320.0 * t) +
                0.3 * math.sin(2 * math.pi * 1760.0 * t) +
                0.2 * math.sin(2 * math.pi * 2640.0 * t)
            )
            return tone * env * 0.85

        generate_wav_file(go_path, 0.35, 44100, go_gen)

    # 5. Nitro Boost Whoosh (500ms accelerating jet sweep)
    nitro_path = os.path.join(SOUNDS_DIR, "nitro.wav")
    if not os.path.exists(nitro_path):
        def nitro_gen(t, i, n, sr):
            env = math.sin(math.pi * (t / 0.5))
            freq = 200.0 + 800.0 * (t / 0.5)
            tone = 0.5 * math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * 0.5
            return (tone + noise) * env * 0.7

        generate_wav_file(nitro_path, 0.5, 44100, nitro_gen)

    # 6. Victory Fanfare (1.4s triumphant ascending arpeggio)
    finish_path = os.path.join(SOUNDS_DIR, "finish.wav")
    if not os.path.exists(finish_path):
        def finish_gen(t, i, n, sr):
            # C5 (523), E5 (659), G5 (784), C6 (1046)
            notes = [(0.0, 0.25, 523.25), (0.25, 0.50, 659.25), (0.50, 0.75, 783.99), (0.75, 1.4, 1046.50)]
            val = 0.0
            for start, end, f in notes:
                if start <= t < end:
                    local_t = t - start
                    env = math.exp(-local_t * 3.5) if (end - start) > 0.5 else (1.0 - local_t / (end - start))
                    val += math.sin(2 * math.pi * f * t) * env
            return val * 0.75

        generate_wav_file(finish_path, 1.4, 44100, finish_gen)

    # 7. Engine Hum (Looped 0.6s pulsing engine)
    engine_path = os.path.join(SOUNDS_DIR, "engine.wav")
    if not os.path.exists(engine_path):
        def engine_gen(t, i, n, sr):
            # Rich low frequency saw + pulse
            f0 = 85.0
            val = (
                0.5 * math.sin(2 * math.pi * f0 * t) +
                0.3 * math.sin(2 * math.pi * (f0 * 2) * t) +
                0.15 * math.sin(2 * math.pi * (f0 * 3) * t) +
                0.05 * (random.random() * 2 - 1)
            )
            # Slight modulation
            mod = 1.0 + 0.15 * math.sin(2 * math.pi * 12 * t)
            return val * mod * 0.45

        generate_wav_file(engine_path, 0.6, 44100, engine_gen)

    # 8. Synthwave Arcade Background Music (Seamless 8.0s loop, 120 BPM)
    bgm_path = os.path.join(SOUNDS_DIR, "arcade_bgm.wav")
    if not os.path.exists(bgm_path):
        # 120 BPM -> 1 beat = 0.5s. 16 beats = 8.0 seconds.
        # Key: A minor (A2=110Hz, C3=130.8Hz, D3=146.8Hz, E3=164.8Hz, G3=196Hz)
        bass_pattern = [
            110.0, 110.0, 110.0, 110.0,  # A
            130.8, 130.8, 146.8, 146.8,  # C -> D
            164.8, 164.8, 164.8, 164.8,  # E
            196.0, 164.8, 146.8, 130.8   # G -> E -> D -> C
        ]
        lead_pattern = [
            440.0, 523.2, 659.2, 523.2,
            587.3, 659.2, 784.0, 659.2,
            880.0, 784.0, 659.2, 587.3,
            659.2, 587.3, 523.2, 440.0
        ]

        def bgm_gen(t, i, n, sr):
            beat_idx = int((t / 0.5) % 16)
            local_t = t % 0.5
            
            # Bassline (punchy decay)
            bass_f = bass_pattern[beat_idx]
            bass_env = math.exp(-local_t * 6.0)
            bass = (
                0.6 * math.sin(2 * math.pi * bass_f * t) +
                0.3 * (((t * bass_f) % 1.0) * 2.0 - 1.0)
            ) * bass_env

            # Lead Arp
            sub_beat_idx = int((t / 0.25) % 16)
            lead_f = lead_pattern[sub_beat_idx]
            sub_local_t = t % 0.25
            lead_env = math.exp(-sub_local_t * 8.0)
            lead = math.sin(2 * math.pi * lead_f * t) * lead_env * 0.25

            # Kick drum on every beat (0.0s, 0.5s, 1.0s...)
            kick_env = math.exp(-local_t * 25.0)
            kick_f = max(45.0, 160.0 * math.exp(-local_t * 40.0))
            kick = math.sin(2 * math.pi * kick_f * local_t) * kick_env * 0.5

            # Hi-hat on 8th notes (0.25s)
            hat_t = local_t % 0.25
            hat_env = math.exp(-hat_t * 50.0)
            hat = (random.random() * 2 - 1) * hat_env * 0.12

            total = (bass * 0.5 + lead * 0.35 + kick * 0.6 + hat) * 0.65
            return total

        generate_wav_file(bgm_path, 8.0, 44100, bgm_gen)


class SoundEngine:
    """Manages playback of sound effects and music with volume control and mute toggle."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.enabled = True
        self.muted = False
        self.volume = 0.8
        self.music_volume = 0.6
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.engine_channel: Optional[pygame.mixer.Channel] = None
        self.bgm_sound: Optional[pygame.mixer.Sound] = None
        self.bgm_channel: Optional[pygame.mixer.Channel] = None

        self._init_mixer()

    def _init_mixer(self):
        """Initializes Pygame mixer and loads sounds."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Ensure WAV files are generated
            ensure_sound_assets()

            # Load sounds
            for sound_name in ["click", "error", "countdown_beep", "countdown_go", "nitro", "finish", "engine"]:
                filepath = os.path.join(SOUNDS_DIR, f"{sound_name}.wav")
                if os.path.exists(filepath):
                    s = pygame.mixer.Sound(filepath)
                    s.set_volume(self.volume)
                    self.sounds[sound_name] = s

            # Engine channel
            self.engine_channel = pygame.mixer.Channel(7)

            # BGM Sound
            bgm_path = os.path.join(SOUNDS_DIR, "arcade_bgm.wav")
            if os.path.exists(bgm_path):
                self.bgm_sound = pygame.mixer.Sound(bgm_path)
                self.bgm_sound.set_volume(self.music_volume)
                self.bgm_channel = pygame.mixer.Channel(6)

        except Exception as e:
            print("SoundEngine init warning (Audio disabled):", e)
            self.enabled = False

    def play(self, sound_name: str):
        """Plays a registered sound effect if audio is enabled and not muted."""
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def play_click(self):
        self.play("click")

    def play_error(self):
        self.play("error")

    def play_countdown_beep(self):
        self.play("countdown_beep")

    def play_countdown_go(self):
        self.play("countdown_go")

    def play_nitro(self):
        self.play("nitro")

    def play_finish(self):
        self.play("finish")

    def start_engine_hum(self):
        """Starts looping engine rumble."""
        if not self.enabled or self.muted or not self.engine_channel:
            return
        engine_sound = self.sounds.get("engine")
        if engine_sound and not self.engine_channel.get_busy():
            try:
                engine_sound.set_volume(0.35 * self.volume)
                self.engine_channel.play(engine_sound, loops=-1)
            except Exception:
                pass

    def stop_engine_hum(self):
        """Stops looping engine rumble."""
        if self.engine_channel:
            try:
                self.engine_channel.stop()
            except Exception:
                pass

    def start_bgm(self):
        """Starts arcade synthwave background music loop."""
        if not self.enabled or self.muted or not self.bgm_sound or not self.bgm_channel:
            return
        if not self.bgm_channel.get_busy():
            try:
                self.bgm_sound.set_volume(self.music_volume)
                self.bgm_channel.play(self.bgm_sound, loops=-1)
            except Exception:
                pass

    def stop_bgm(self):
        """Stops background music."""
        if self.bgm_channel:
            try:
                self.bgm_channel.stop()
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        """Toggles audio mute. Returns new mute state."""
        self.muted = not self.muted
        if self.muted:
            self.stop_engine_hum()
            self.stop_bgm()
        else:
            self.start_bgm()
        return self.muted

    def set_volume(self, volume: float):
        """Sets master volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        self.music_volume = self.volume * 0.75
        for s in self.sounds.values():
            s.set_volume(self.volume)
        if self.bgm_sound:
            self.bgm_sound.set_volume(self.music_volume)
