"""
Typing Racer 2D - Track Renderer & Parallax Scenery
Renders the 5-lane horizontal racing circuit with animated dashed lane markings,
multi-layered parallax background (city skyline, grandstands, lamp posts),
and checkered finish gantry.
"""
import math
import random
import pygame
from core.config import (
    TRACK_Y_START, TRACK_HEIGHT, NUM_LANES, LANE_HEIGHT,
    COLOR_ASPHALT, COLOR_ASPHALT_LINE, COLOR_KERB_RED, COLOR_KERB_WHITE,
    COLOR_GUARD_RAIL, COLOR_BG_DARK, COLOR_ACCENT_PRIMARY, COLOR_ACCENT_GOLD
)


class TrackRenderer:
    """Renders 5 horizontal racing lanes with animated parallax scenery."""
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        self.width = screen_width
        self.height = screen_height

        self.track_top = TRACK_Y_START
        self.track_bottom = TRACK_Y_START + TRACK_HEIGHT

        # Finish line X coordinate
        self.start_line_x = 100.0
        self.finish_line_x = 1140.0

        # Parallax scroll offsets
        self.scroll_sky: float = 0.0
        self.scroll_stands: float = 0.0
        self.scroll_road: float = 0.0
        self.dash_scroll: float = 0.0

        # Generate procedural city skyline buildings
        self.skyline = []
        x = 0
        while x < self.width * 2:
            bw = random.randint(45, 95)
            bh = random.randint(35, 70)
            col_tone = random.randint(18, 28)
            col = (col_tone, col_tone + 2, col_tone + 8)
            self.skyline.append((x, bw, bh, col))
            x += bw

        # Billboards in midground
        self.billboard_texts = ["CYBER RACE GP", "TYPE FOR SPEED", "NITRO ACCEL", "APEX APPAREL", "OCTANE 99"]
        self.billboards = []
        bx = 150
        for i in range(8):
            self.billboards.append({"x": bx, "text": self.billboard_texts[i % len(self.billboard_texts)]})
            bx += random.randint(320, 480)

        # Street lamps
        self.street_lamps = [i * 260 for i in range(10)]

    def update(self, dt: float, reference_speed_wpm: float):
        """Advances scrolling offsets proportional to current speed."""
        # Speed translation: base scroll speed + typing WPM boost
        scroll_speed = max(40.0, reference_speed_wpm * 4.2)

        self.scroll_sky = (self.scroll_sky + scroll_speed * 0.15 * dt) % self.width
        self.scroll_stands = (self.scroll_stands + scroll_speed * 0.45 * dt) % self.width
        self.scroll_road = (self.scroll_road + scroll_speed * 1.0 * dt) % 80.0
        self.dash_scroll = (self.dash_scroll + scroll_speed * 1.1 * dt) % 60.0

    def draw(self, surface: pygame.Surface, font_small: pygame.font.Font, font_medium: pygame.font.Font):
        """Renders complete background and track environment."""
        # 1. Distant Dark Blue Sky Gradient
        sky_rect = pygame.Rect(0, 0, self.width, self.track_top)
        pygame.draw.rect(surface, (10, 12, 20), sky_rect)

        # 2. Distant Neon City Skyline (Parallax Layer 1)
        sky_offset = int(self.scroll_sky)
        for x, bw, bh, col in self.skyline:
            draw_x = (x - sky_offset) % (self.width * 2) - 100
            if -100 <= draw_x <= self.width + 100:
                y = self.track_top - bh
                pygame.draw.rect(surface, col, (draw_x, y, bw, bh))
                # Window lights
                for wy in range(y + 8, self.track_top - 6, 12):
                    for wx in range(draw_x + 6, draw_x + bw - 6, 14):
                        if (wx * 13 + wy * 7) % 5 == 0:
                            pygame.draw.rect(surface, (235, 210, 120), (wx, wy, 4, 6))

        # 3. Grandstands & Audience Strip (Parallax Layer 2)
        stand_y = self.track_top - 24
        stand_h = 24
        pygame.draw.rect(surface, (24, 28, 40), (0, stand_y, self.width, stand_h))
        # Animated cheering crowd dots
        stands_offset = int(self.scroll_stands)
        for i in range(0, self.width + 100, 18):
            crowd_x = (i - stands_offset) % self.width
            crowd_col = (200, 70, 80) if i % 3 == 0 else ((70, 180, 220) if i % 3 == 1 else (230, 210, 90))
            pygame.draw.circle(surface, crowd_col, (crowd_x, stand_y + 8), 3)

        # 4. Top Road Guard Rail & Apex Curbing
        guard_rail_y = self.track_top - 6
        pygame.draw.rect(surface, COLOR_GUARD_RAIL, (0, guard_rail_y, self.width, 6))
        
        # Red & White Top Curbs
        curb_width = 32
        curb_offset = int(self.scroll_road) % (curb_width * 2)
        for cx in range(-curb_width * 2, self.width + curb_width * 2, curb_width):
            draw_cx = cx - curb_offset
            col = COLOR_KERB_RED if (cx // curb_width) % 2 == 0 else COLOR_KERB_WHITE
            pygame.draw.rect(surface, col, (draw_cx, self.track_top, curb_width, 5))

        # 5. Main 5-Lane Asphalt Highway
        track_rect = pygame.Rect(0, self.track_top, self.width, TRACK_HEIGHT)
        pygame.draw.rect(surface, COLOR_ASPHALT, track_rect)

        # Subtle road surface grain lines
        for offset_y in range(12, TRACK_HEIGHT, 24):
            pygame.draw.line(
                surface,
                (36, 40, 52),
                (0, self.track_top + offset_y),
                (self.width, self.track_top + offset_y),
                1
            )

        # 6. Lane Dividers (4 Dashed White Lines)
        dash_len = 36
        dash_gap = 24
        cycle = dash_len + dash_gap
        offset_x = int(self.dash_scroll) % cycle

        for lane_idx in range(1, NUM_LANES):
            lane_y = self.track_top + lane_idx * LANE_HEIGHT
            
            # Subtle solid dark line under dashes
            pygame.draw.line(surface, (25, 28, 36), (0, lane_y), (self.width, lane_y), 2)

            # Dashes
            for x in range(-cycle, self.width + cycle, cycle):
                start_x = x - offset_x
                end_x = start_x + dash_len
                pygame.draw.line(surface, COLOR_ASPHALT_LINE, (start_x, lane_y), (end_x, lane_y), 3)

        # 7. Bottom Road Curbing
        bottom_curb_y = self.track_bottom - 5
        for cx in range(-curb_width * 2, self.width + curb_width * 2, curb_width):
            draw_cx = cx - curb_offset
            col = COLOR_KERB_RED if (cx // curb_width) % 2 == 0 else COLOR_KERB_WHITE
            pygame.draw.rect(surface, col, (draw_cx, bottom_curb_y, curb_width, 5))

        # 8. Bottom Guard Rail
        pygame.draw.rect(surface, COLOR_GUARD_RAIL, (0, self.track_bottom, self.width, 6))

        # 9. Starting Grid Markers
        grid_x = int(self.start_line_x)
        pygame.draw.line(surface, (255, 255, 255), (grid_x, self.track_top), (grid_x, self.track_bottom), 4)
        for l in range(NUM_LANES):
            ly = self.track_top + l * LANE_HEIGHT + (LANE_HEIGHT // 2)
            pygame.draw.line(surface, (255, 215, 0), (grid_x - 18, ly), (grid_x, ly), 3)

        # 10. Checkered Finish Line & Gantry
        fin_x = int(self.finish_line_x)
        sq_size = 12
        num_rows = TRACK_HEIGHT // sq_size
        for row in range(num_rows):
            for col in range(2):
                bx = fin_x + col * sq_size
                by = self.track_top + row * sq_size
                color = (250, 250, 250) if (row + col) % 2 == 0 else (20, 20, 20)
                pygame.draw.rect(surface, color, (bx, by, sq_size, sq_size))

        # Overhead Finish Gantry Banner
        gantry_rect = pygame.Rect(fin_x - 18, self.track_top - 46, sq_size * 2 + 36, 42)
        pygame.draw.rect(surface, (20, 25, 38), gantry_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_GOLD, gantry_rect, width=2, border_radius=6)
        
        fin_text = font_small.render("FINISH", True, COLOR_ACCENT_GOLD)
        surface.blit(fin_text, fin_text.get_rect(center=gantry_rect.center))
        # Gantry support pillars
        pygame.draw.line(surface, (100, 110, 130), (fin_x - 14, self.track_top - 4), (fin_x - 14, self.track_bottom), 5)
        pygame.draw.line(surface, (100, 110, 130), (fin_x + sq_size * 2 + 14, self.track_top - 4), (fin_x + sq_size * 2 + 14, self.track_bottom), 5)

        # 11. Billboards in Foreground Grass/Strip
        for bb in self.billboards:
            draw_bx = bb["x"] - int(self.scroll_stands) * 1.5
            draw_bx = (draw_bx + self.width * 2) % (self.width * 2) - 100
            if -120 <= draw_bx <= self.width + 120:
                b_surf = pygame.Surface((100, 20), pygame.SRCALPHA)
                pygame.draw.rect(b_surf, (15, 20, 32, 220), (0, 0, 100, 20), border_radius=3)
                pygame.draw.rect(b_surf, (0, 229, 255, 180), (0, 0, 100, 20), width=1, border_radius=3)
                txt = font_small.render(bb["text"], True, COLOR_ACCENT_PRIMARY)
                b_surf.blit(txt, txt.get_rect(center=(50, 10)))
                surface.blit(b_surf, (draw_bx, self.track_top - 22))

    def draw_track_radar(self, surface: pygame.Surface, racers: list, font_small: pygame.font.Font):
        """
        Renders a sleek top-screen mini-map radar track showing
        all 5 racers' real-time relative positions from 0% to 100%.
        """
        radar_x = 360
        radar_y = 12
        radar_w = 560
        radar_h = 24

        # Radar track container
        radar_bg = pygame.Surface((radar_w, radar_h), pygame.SRCALPHA)
        pygame.draw.rect(radar_bg, (18, 22, 32, 200), (0, 0, radar_w, radar_h), border_radius=12)
        pygame.draw.rect(radar_bg, (45, 52, 75, 220), (0, 0, radar_w, radar_h), width=1, border_radius=12)
        surface.blit(radar_bg, (radar_x, radar_y))

        # Start and Finish flags
        start_lbl = font_small.render("START", True, (130, 140, 165))
        fin_lbl = font_small.render("100%", True, COLOR_ACCENT_GOLD)
        surface.blit(start_lbl, (radar_x + 8, radar_y + 4))
        surface.blit(fin_lbl, (radar_x + radar_w - fin_lbl.get_width() - 8, radar_y + 4))

        # Checkered finish pip
        pygame.draw.rect(surface, (255, 255, 255), (radar_x + radar_w - 48, radar_y + 5, 4, radar_h - 10))

        # Draw racer blips
        track_inner_x = radar_x + 60
        track_inner_w = radar_w - 110

        for r in racers:
            prog = max(0.0, min(1.0, r.progress))
            blip_x = track_inner_x + int(prog * track_inner_w)
            blip_y = radar_y + radar_h // 2
            
            blip_col = r.palette["body"]
            if r.is_player:
                # Player blip has prominent glowing cyan ring
                pygame.draw.circle(surface, (255, 255, 255), (blip_x, blip_y), 6)
                pygame.draw.circle(surface, COLOR_ACCENT_PRIMARY, (blip_x, blip_y), 4)
            else:
                pygame.draw.circle(surface, blip_col, (blip_x, blip_y), 4)
