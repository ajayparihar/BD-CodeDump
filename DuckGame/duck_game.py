"""
Duck Bitch
============
A webcam-controlled dodge game using MediaPipe pose detection.
Spikes hang from the top and scroll left — duck to survive!

Requirements:
    - mediapipe
    - opencv-python
    - numpy

Usage:
    python duck_game.py

Press 'q' to exit.
"""

import os
import sys
import time
import math
import random
import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import cv2
import numpy as np
import mediapipe as mp

# Import pose tracking components (renamed copy of smooth-pose.py)
from smooth_pose import (
    Camera,
    LandmarkSmoother,
    SmoothedLandmark,
    DetectionConfig,
    Landmarks,
    create_landmarker,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# GAME CONFIGURATION
# =============================================================================

@dataclass
class GameConfig:
    """All game-tuning parameters.  Tweak these constants to adjust gameplay."""

    # === WINDOW / RESOLUTION ===
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080
    WINDOW_TITLE: str = "Duck Bitch"

    # === CAMERA PROCESSING (lower = faster FPS) ===
    PROCESS_WIDTH: int = 320
    PROCESS_HEIGHT: int = 240

    # === SPIKE GEOMETRY ===
    SPIKE_WIDTH: int = 70               # base width of each spike triangle
    SPIKE_MIN_HEIGHT: int = 200         # min top-spike length from ceiling
    SPIKE_MAX_HEIGHT: int = 500         # max top-spike length from ceiling
    SPIKE_HORIZ_GAP_MIN: int = 350      # min horizontal gap between spike pairs
    SPIKE_HORIZ_GAP_MAX: int = 550      # max horizontal gap between spike pairs

    # === VERTICAL GAP (space between top & bottom spikes) ===
    VERT_GAP_MIN: int = 280             # minimum passable vertical gap
    VERT_GAP_MAX: int = 380             # maximum passable vertical gap
    BOTTOM_SPIKE_ENABLED: bool = True   # set False for top-only mode

    # === SPEED ===
    GAME_SPEED_MULTIPLIER: float = 3.0  # global multiplier — scales ALL speeds
    SPIKE_SPEED_INIT: float = 5.0       # starting scroll speed (px/frame)
    SPIKE_SPEED_MAX: float = 11.0       # cap
    SPIKE_SPEED_RAMP: float = 0.06      # speed increase per scored point
    GRID_SCROLL_SPEED: int = 2          # background grid scroll (px/frame)
    GRID_CELL_SIZE: int = 60            # grid cell size (px)

    # === DIFFICULTY / FORGIVENESS ===
    HITBOX_SHRINK: float = 0.65         # hitbox is this fraction of visual width
    GRACE_PX: int = 40                  # extra forgiveness at spike tips (px)
    LIVES: int = 3
    INVINCIBILITY_FRAMES: int = 90      # frames of i-frames after a hit

    # === HEAD MARKER ===
    HEAD_RADIUS: int = 22

    # === PLAYER X FRACTION (0-1, where the player line sits) ===
    PLAYER_X_FRAC: float = 0.33

    # === COLORS (BGR) ===
    BG: Tuple[int, int, int] = (15, 15, 20)
    SPIKE_FILL: Tuple[int, int, int] = (45, 45, 55)
    SPIKE_EDGE: Tuple[int, int, int] = (80, 80, 100)
    SPIKE_WARN: Tuple[int, int, int] = (40, 120, 220)
    SPIKE_DANGER: Tuple[int, int, int] = (50, 50, 230)
    HEAD_NORMAL: Tuple[int, int, int] = (0, 255, 180)
    HEAD_SAFE: Tuple[int, int, int] = (0, 255, 100)
    HEAD_DANGER: Tuple[int, int, int] = (100, 100, 255)
    SCORE_CLR: Tuple[int, int, int] = (255, 255, 255)
    LIFE_CLR: Tuple[int, int, int] = (80, 80, 255)
    DODGE_CLR: Tuple[int, int, int] = (0, 220, 120)
    HIT_FLASH: Tuple[int, int, int] = (0, 0, 180)
    SKEL_CLR: Tuple[int, int, int] = (60, 60, 60)
    SKEL_THICK: int = 3
    JOINT_RAD: int = 5
    GRID_CLR: Tuple[int, int, int] = (25, 25, 32)
    BOTTOM_SPIKE_FILL: Tuple[int, int, int] = (40, 50, 45)
    BOTTOM_SPIKE_EDGE: Tuple[int, int, int] = (70, 90, 80)


# =============================================================================
# SPIKE PAIR (top + optional bottom)
# =============================================================================

@dataclass
class SpikePair:
    """A column of spikes: one from top, optionally one from bottom."""
    x: float               # horizontal center
    top_h: float            # top spike extends this far down from y=0
    bot_y: float            # bottom spike starts at this y (extends to screen bottom)
    width: float            # triangle base width
    has_bottom: bool = True # whether bottom spike exists
    scored: bool = False

    def top_hitbox(self, shrink: float, grace: int):
        hw = (self.width * shrink) / 2
        return self.x - hw, self.x + hw, 0, self.top_h - grace

    def bot_hitbox(self, shrink: float, grace: int, screen_h: int):
        if not self.has_bottom:
            return 0, 0, 0, 0  # no collision
        hw = (self.width * shrink) / 2
        return self.x - hw, self.x + hw, self.bot_y + grace, screen_h


# =============================================================================
# EFFECTS
# =============================================================================

class Effects:
    def __init__(self):
        self.flash_frames = 0
        self.flash_color = (0, 0, 0)
        self.popups: List[dict] = []
        self.trail: deque = deque(maxlen=10)
        self.shake = 0

    def trigger_flash(self, color, dur=8):
        self.flash_frames = dur
        self.flash_color = color

    def trigger_shake(self, dur=12):
        self.shake = dur

    def add_popup(self, x, y, text, color):
        self.popups.append({"x": x, "y": y, "text": text, "ttl": 40, "color": color})

    def add_trail(self, x, y):
        self.trail.append((x, y))

    def tick(self):
        self.flash_frames = max(0, self.flash_frames - 1)
        self.shake = max(0, self.shake - 1)
        for p in self.popups:
            p["ttl"] -= 1
            p["y"] -= 2
        self.popups = [p for p in self.popups if p["ttl"] > 0]

    def render(self, canvas):
        # Flash
        if self.flash_frames > 0:
            alpha = self.flash_frames / 15.0
            ov = np.full_like(canvas, self.flash_color, dtype=np.uint8)
            cv2.addWeighted(ov, alpha * 0.3, canvas, 1.0, 0, canvas)
        # Shake
        if self.shake > 0:
            dx, dy = random.randint(-4, 4), random.randint(-4, 4)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            canvas[:] = cv2.warpAffine(canvas, M, (canvas.shape[1], canvas.shape[0]))
        # Trail
        pts = list(self.trail)
        for i, (tx, ty) in enumerate(pts):
            a = (i + 1) / len(pts) if pts else 0
            r = max(2, int(10 * a))
            cv2.circle(canvas, (tx, ty), r, (0, int(180 * a), int(120 * a)), -1, cv2.LINE_AA)
        # Popups
        for p in self.popups:
            a = p["ttl"] / 40.0
            c = tuple(int(v * a) for v in p["color"])
            cv2.putText(canvas, p["text"], (p["x"], p["y"]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, c, 2, cv2.LINE_AA)


# =============================================================================
# SKELETON CONNECTIONS (for background rendering)
# =============================================================================

BODY_CONNS = [
    (Landmarks.LEFT_SHOULDER, Landmarks.RIGHT_SHOULDER),
    (Landmarks.LEFT_SHOULDER, Landmarks.LEFT_HIP),
    (Landmarks.RIGHT_SHOULDER, Landmarks.RIGHT_HIP),
    (Landmarks.LEFT_HIP, Landmarks.RIGHT_HIP),
    (Landmarks.LEFT_SHOULDER, Landmarks.LEFT_ELBOW),
    (Landmarks.LEFT_ELBOW, Landmarks.LEFT_WRIST),
    (Landmarks.RIGHT_SHOULDER, Landmarks.RIGHT_ELBOW),
    (Landmarks.RIGHT_ELBOW, Landmarks.RIGHT_WRIST),
    (Landmarks.LEFT_HIP, Landmarks.LEFT_KNEE),
    (Landmarks.LEFT_KNEE, Landmarks.LEFT_ANKLE),
    (Landmarks.RIGHT_HIP, Landmarks.RIGHT_KNEE),
    (Landmarks.RIGHT_KNEE, Landmarks.RIGHT_ANKLE),
]

JOINT_IDS = [
    Landmarks.LEFT_SHOULDER, Landmarks.RIGHT_SHOULDER,
    Landmarks.LEFT_ELBOW, Landmarks.RIGHT_ELBOW,
    Landmarks.LEFT_WRIST, Landmarks.RIGHT_WRIST,
    Landmarks.LEFT_HIP, Landmarks.RIGHT_HIP,
    Landmarks.LEFT_KNEE, Landmarks.RIGHT_KNEE,
    Landmarks.LEFT_ANKLE, Landmarks.RIGHT_ANKLE,
]


# =============================================================================
# GAME STATES
# =============================================================================

class State:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3



# =============================================================================
# DUCK GAME
# =============================================================================

class DuckGame:

    def __init__(self):
        self.cfg = GameConfig()
        self.det = DetectionConfig(EMA_ALPHA=0.35)

        self._cam = Camera(source=0)
        self._lm = create_landmarker(self.det)
        self._sm = LandmarkSmoother(alpha=self.det.EMA_ALPHA)
        self._landmarks = None

        self._canvas = np.zeros(
            (self.cfg.WINDOW_HEIGHT, self.cfg.WINDOW_WIDTH, 3), dtype=np.uint8
        )

        self.state = State.MENU
        self.score = 0
        self.high_score = 0
        self.lives = self.cfg.LIVES
        self.spikes: List[SpikePair] = []
        self.speed = self.cfg.SPIKE_SPEED_INIT
        self.invincibility = 0
        self.frame_n = 0

        self.head_x = 0.5
        self.head_y = 0.5
        self.has_pose = False

        self._thread_running = False

        # Menu state
        self.menu_options = ["START GAME", "QUIT"]
        self.menu_sel = 0
        self.pause_options = ["RESUME", "MAIN MENU", "QUIT"]
        self.pause_sel = 0

        # Fixed x-line where the player "exists"
        self.player_x = int(self.cfg.WINDOW_WIDTH * self.cfg.PLAYER_X_FRAC)

        self.fx = Effects()
        self._fps_q: deque = deque(maxlen=30)
        self._t = time.time()
        self.running = True

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self):
        cfg = self.cfg
        cv2.namedWindow(cfg.WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(cfg.WINDOW_TITLE, cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT)
        logger.info("Duck Bitch — press 'q' to quit")

        self._thread_running = True
        cam_thread = threading.Thread(target=self._camera_thread, daemon=True)
        cam_thread.start()

        try:
            while self.running:
                loop_start = time.time()

                now = time.time()
                dt = now - self._t
                self._t = now
                if dt > 0:
                    self._fps_q.append(1.0 / dt)

                c = self._canvas
                c[:] = cfg.BG

                if self.state == State.MENU:
                    self._menu(c)
                elif self.state == State.PLAYING:
                    self._play(c)
                elif self.state == State.PAUSED:
                    self._pause_menu(c)
                elif self.state == State.GAME_OVER:
                    self._gameover(c)

                self.fx.tick()
                self.fx.render(c)
                self._draw_fps(c)

                cv2.imshow(cfg.WINDOW_TITLE, c)

                elapsed = time.time() - loop_start
                delay = max(1, int((1.0 / 60.0 - elapsed) * 1000))
                key = cv2.waitKeyEx(delay)
                if key != -1:
                    self._handle_input(key)
        finally:
            self._thread_running = False
            cam_thread.join(timeout=1.0)
            self._cam.release()
            cv2.destroyAllWindows()

    # ------------------------------------------------------------------
    # POSE DETECTION THREAD
    # ------------------------------------------------------------------

    def _camera_thread(self):
        while self._thread_running and self._cam.is_opened:
            ok, frame = self._cam.read()
            if not ok:
                break

            try:
                small = cv2.resize(
                    frame, (self.cfg.PROCESS_WIDTH, self.cfg.PROCESS_HEIGHT),
                    interpolation=cv2.INTER_NEAREST,
                )
                rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                ts = int(time.time() * 1000)
                res = self._lm.detect_for_video(img, ts)

                if res and res.pose_landmarks:
                    raw = res.pose_landmarks[0]
                    sm = self._sm.smooth(raw)
                    self._landmarks = sm
                    nose = sm[Landmarks.NOSE]
                    if nose.visibility > 0.5:
                        self.head_x = 1.0 - nose.x  # mirror
                        self.head_y = nose.y
                        self.has_pose = True
                        continue
                
                self.has_pose = False
                self._landmarks = None
                self._sm.reset()
            except Exception:
                logger.exception("Detection error")
                self.has_pose = False
                self._landmarks = None

    # ------------------------------------------------------------------
    # HEAD PIXEL
    # ------------------------------------------------------------------

    def _head_px(self):
        return (
            int(self.head_x * self.cfg.WINDOW_WIDTH),
            int(self.head_y * self.cfg.WINDOW_HEIGHT),
        )

    # ------------------------------------------------------------------
    # SKELETON (dimmed background)
    # ------------------------------------------------------------------

    def _draw_skel(self, canvas, alpha=0.25):
        lm = self._landmarks
        if not lm:
            return
        cfg = self.cfg
        w, h = cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT
        vis_thr = 0.5

        def px(idx):
            if idx < len(lm) and lm[idx].visibility > vis_thr:
                return (int((1.0 - lm[idx].x) * w), int(lm[idx].y * h))
            return None

        overlay = canvas.copy()
        for a, b in BODY_CONNS:
            pa, pb = px(a), px(b)
            if pa and pb:
                cv2.line(overlay, pa, pb, cfg.SKEL_CLR, cfg.SKEL_THICK, cv2.LINE_AA)
        for idx in JOINT_IDS:
            pt = px(idx)
            if pt:
                cv2.circle(overlay, pt, cfg.JOINT_RAD, cfg.SKEL_CLR, -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

    # ------------------------------------------------------------------
    # BACKGROUND GRID
    # ------------------------------------------------------------------

    def _draw_grid(self, canvas):
        cfg = self.cfg
        cell = cfg.GRID_CELL_SIZE
        offset = int(self.frame_n * cfg.GRID_SCROLL_SPEED * cfg.GAME_SPEED_MULTIPLIER) % cell
        for x in range(-offset, cfg.WINDOW_WIDTH + cell, cell):
            cv2.line(canvas, (x, 0), (x, cfg.WINDOW_HEIGHT), cfg.GRID_CLR, 1)
        for y in range(0, cfg.WINDOW_HEIGHT, cell):
            cv2.line(canvas, (0, y), (cfg.WINDOW_WIDTH, y), cfg.GRID_CLR, 1)

    # ------------------------------------------------------------------
    # DRAW SPIKE PAIR
    # ------------------------------------------------------------------

    def _draw_spike_pair(self, canvas, sp: SpikePair, hx: int):
        cfg = self.cfg
        hw = sp.width // 2

        # Color based on proximity
        dist = abs(sp.x - hx)
        if dist < 100:
            fill_t = cfg.SPIKE_DANGER
            edge_t = (100, 100, 255)
        elif dist < 250:
            fill_t = cfg.SPIKE_WARN
            edge_t = (80, 160, 255)
        else:
            fill_t = cfg.SPIKE_FILL
            edge_t = cfg.SPIKE_EDGE

        sx = int(sp.x)
        th = int(sp.top_h)

        # --- TOP SPIKE (hangs from ceiling) ---
        pts_top = np.array([[sx - hw, 0], [sx + hw, 0], [sx, th]], np.int32)
        cv2.fillPoly(canvas, [pts_top], fill_t, cv2.LINE_AA)
        cv2.polylines(canvas, [pts_top], True, edge_t, 2, cv2.LINE_AA)
        # detail lines
        cv2.line(canvas, (sx, 0), (sx, th - 10), edge_t, 1, cv2.LINE_AA)

        # --- BOTTOM SPIKE (rises from floor) ---
        if sp.has_bottom:
            fill_b = cfg.BOTTOM_SPIKE_FILL if dist >= 100 else cfg.SPIKE_DANGER
            edge_b = cfg.BOTTOM_SPIKE_EDGE if dist >= 100 else (100, 100, 255)
            by = int(sp.bot_y)
            bh = cfg.WINDOW_HEIGHT
            pts_bot = np.array([[sx - hw, bh], [sx + hw, bh], [sx, by]], np.int32)
            cv2.fillPoly(canvas, [pts_bot], fill_b, cv2.LINE_AA)
            cv2.polylines(canvas, [pts_bot], True, edge_b, 2, cv2.LINE_AA)
            cv2.line(canvas, (sx, bh), (sx, by + 10), edge_b, 1, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # DRAW HEAD
    # ------------------------------------------------------------------

    def _draw_head(self, canvas, hx, hy, color):
        cfg = self.cfg
        # Glow
        cv2.circle(canvas, (hx, hy), cfg.HEAD_RADIUS + 8,
                   tuple(int(c * 0.3) for c in color), -1, cv2.LINE_AA)
        # Solid
        cv2.circle(canvas, (hx, hy), cfg.HEAD_RADIUS, color, -1, cv2.LINE_AA)
        # White rim
        cv2.circle(canvas, (hx, hy), cfg.HEAD_RADIUS + 2,
                   (255, 255, 255), 1, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _draw_hud(self, canvas):
        cfg = self.cfg
        # Score top-left
        cv2.putText(canvas, f"Score: {self.score}", (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, cfg.SCORE_CLR, 3, cv2.LINE_AA)
        # Lives top-left below score
        for i in range(self.lives):
            cx = 30 + i * 35
            cv2.circle(canvas, (cx, 75), 10, cfg.LIFE_CLR, -1, cv2.LINE_AA)
        # Speed indicator
        sp_text = f"Speed: {self.speed:.1f}x"
        cv2.putText(canvas, sp_text, (20, cfg.WINDOW_HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 80), 1, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # FPS
    # ------------------------------------------------------------------

    def _draw_fps(self, canvas):
        if not self._fps_q:
            return
        fps = sum(self._fps_q) / len(self._fps_q)
        txt = f"FPS: {int(fps)}"
        ts = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        x = self.cfg.WINDOW_WIDTH - ts[0] - 15
        cv2.putText(canvas, txt, (x, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 1, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # MENU
    # ------------------------------------------------------------------

    def _draw_button(self, canvas, text, cx, cy, selected, width=300, height=60):
        # Professional look
        bg_color = (80, 180, 60) if selected else (40, 40, 50)
        border_color = (120, 255, 100) if selected else (80, 80, 100)
        text_color = (255, 255, 255) if selected else (180, 180, 180)
        thick = 2 if selected else 1
        
        # Transparent background
        overlay = canvas.copy()
        cv2.rectangle(overlay, (cx - width//2, cy - height//2), (cx + width//2, cy + height//2), bg_color, -1)
        alpha = 0.8 if selected else 0.6
        cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)
        
        # Border
        cv2.rectangle(canvas, (cx - width//2, cy - height//2), (cx + width//2, cy + height//2), border_color, thick, cv2.LINE_AA)
        
        # Text
        _ctext(canvas, text, cx, cy - 5, 0.8, text_color, 2 if selected else 1)

    def _menu(self, canvas):
        cfg = self.cfg
        cx, cy = cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT // 2

        if self.has_pose and self._landmarks:
            self._draw_skel(canvas, 0.3)
            hx, hy = self._head_px()
            self._draw_head(canvas, hx, hy, cfg.HEAD_NORMAL)

        # Title
        _ctext(canvas, "DUCK BITCH", cx, cy - 180, 2.5, (255, 255, 255), 5)
        _ctext(canvas, "Duck under the spikes to survive!", cx, cy - 100, 0.8, (180, 180, 180), 2)

        # Pose status
        if self.has_pose:
            _ctext(canvas, "Pose detected — you're ready!", cx, cy - 40, 0.6, (0, 255, 100), 1)
        else:
            _ctext(canvas, "Step into the camera view...", cx, cy - 40, 0.6, (0, 120, 255), 1)

        # Buttons
        for i, opt in enumerate(self.menu_options):
            b_cy = cy + 40 + i * 80
            self._draw_button(canvas, opt, cx, b_cy, i == self.menu_sel)

        _ctext(canvas, "Use W/S or UP/DOWN to navigate, SPACE to select", cx, cy + 220, 0.5, (100, 100, 100), 1)

        if self.high_score > 0:
            _ctext(canvas, f"High Score: {self.high_score}", cx, cy + 280, 0.8, (100, 200, 255), 2)

    def _pause_menu(self, canvas):
        cfg = self.cfg
        cx, cy = cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT // 2

        # Draw game background static elements
        self._draw_grid(canvas)
        cv2.line(canvas, (self.player_x, 0), (self.player_x, cfg.WINDOW_HEIGHT), (30, 30, 35), 1, cv2.LINE_AA)
        hx, hy = self._head_px()
        for s in self.spikes:
            self._draw_spike_pair(canvas, s, hx)
        
        if self.has_pose and self._landmarks:
            self._draw_skel(canvas, 0.2)

        self._draw_head(canvas, hx, hy, cfg.HEAD_SAFE)
        self._draw_hud(canvas)

        # Dim overlay for the pause menu
        ov = np.zeros_like(canvas)
        cv2.addWeighted(ov, 0.6, canvas, 0.4, 0, canvas)

        # Panel background
        panel_w, panel_h = 450, 450
        cv2.rectangle(ov, (cx - panel_w//2, cy - panel_h//2), (cx + panel_w//2, cy + panel_h//2), (20, 20, 25), -1)
        cv2.addWeighted(ov, 0.9, canvas, 0.1, 0, canvas)
        cv2.rectangle(canvas, (cx - panel_w//2, cy - panel_h//2), (cx + panel_w//2, cy + panel_h//2), (100, 150, 200), 2, cv2.LINE_AA)

        _ctext(canvas, "PAUSED", cx, cy - 140, 1.8, (255, 255, 255), 3)

        for i, opt in enumerate(self.pause_options):
            b_cy = cy - 20 + i * 80
            self._draw_button(canvas, opt, cx, b_cy, i == self.pause_sel, width=280)
            
        _ctext(canvas, "W/S to navigate, SPACE to select", cx, cy + 180, 0.5, (150, 150, 150), 1)

    def _handle_input(self, key):
        if key == ord("q"):
            self.running = False
            return
            
        if self.state == State.MENU:
            if key in (ord("w"), ord("W"), 2490368, 82): # Up
                self.menu_sel = (self.menu_sel - 1) % len(self.menu_options)
            elif key in (ord("s"), ord("S"), 2621440, 84): # Down
                self.menu_sel = (self.menu_sel + 1) % len(self.menu_options)
            elif key in (ord(" "), 13):
                if self.menu_sel == 0:
                    self._start()
                elif self.menu_sel == 1:
                    self.running = False
                    
        elif self.state == State.PLAYING:
            if key in (27, ord("p"), ord("P")): # Esc or P
                self.state = State.PAUSED
                self.pause_sel = 0
                
        elif self.state == State.PAUSED:
            if key in (27, ord("p"), ord("P")):
                self.state = State.PLAYING
            elif key in (ord("w"), ord("W"), 2490368, 82):
                self.pause_sel = (self.pause_sel - 1) % len(self.pause_options)
            elif key in (ord("s"), ord("S"), 2621440, 84):
                self.pause_sel = (self.pause_sel + 1) % len(self.pause_options)
            elif key in (ord(" "), 13):
                if self.pause_sel == 0:
                    self.state = State.PLAYING
                elif self.pause_sel == 1:
                    self.state = State.MENU
                elif self.pause_sel == 2:
                    self.running = False
                    
        elif self.state == State.GAME_OVER:
            if key in (ord(" "), 13):
                self.state = State.MENU

    # ------------------------------------------------------------------
    # START GAME
    # ------------------------------------------------------------------

    def _start(self):
        self.state = State.PLAYING
        self.score = 0
        self.lives = self.cfg.LIVES
        self.spikes.clear()
        self.speed = self.cfg.SPIKE_SPEED_INIT
        self.invincibility = 0
        self.frame_n = 0
        self.fx = Effects()
        self._spawn_batch()

    def _make_spike(self, x: float) -> SpikePair:
        cfg = self.cfg
        top_h = random.randint(cfg.SPIKE_MIN_HEIGHT, cfg.SPIKE_MAX_HEIGHT)
        vert_gap = random.randint(cfg.VERT_GAP_MIN, cfg.VERT_GAP_MAX)
        bot_y = top_h + vert_gap
        w = random.randint(cfg.SPIKE_WIDTH - 10, cfg.SPIKE_WIDTH + 20)
        return SpikePair(
            x=x, top_h=top_h, bot_y=bot_y, width=w,
            has_bottom=cfg.BOTTOM_SPIKE_ENABLED,
        )

    def _spawn_batch(self):
        cfg = self.cfg
        x = float(cfg.WINDOW_WIDTH + 150)
        for _ in range(5):
            gap = random.randint(cfg.SPIKE_HORIZ_GAP_MIN, cfg.SPIKE_HORIZ_GAP_MAX)
            self.spikes.append(self._make_spike(x))
            x += gap

    # ------------------------------------------------------------------
    # PLAY
    # ------------------------------------------------------------------

    def _play(self, canvas):
        cfg = self.cfg
        self.frame_n += 1

        # Background
        self._draw_grid(canvas)

        # Player line (subtle guide)
        cv2.line(canvas, (self.player_x, 0), (self.player_x, cfg.WINDOW_HEIGHT),
                 (30, 30, 35), 1, cv2.LINE_AA)

        # Move spikes (speed × global multiplier)
        effective_speed = self.speed * cfg.GAME_SPEED_MULTIPLIER
        for s in self.spikes:
            s.x -= effective_speed
        self.spikes = [s for s in self.spikes if s.x > -150]

        # Spawn more if needed
        if not self.spikes or self.spikes[-1].x < cfg.WINDOW_WIDTH + 80:
            last_x = self.spikes[-1].x if self.spikes else cfg.WINDOW_WIDTH
            gap = random.randint(cfg.SPIKE_HORIZ_GAP_MIN, cfg.SPIKE_HORIZ_GAP_MAX)
            self.spikes.append(self._make_spike(last_x + gap))

        # Head position
        hx, hy = self._head_px()

        # Draw spike pairs
        for s in self.spikes:
            self._draw_spike_pair(canvas, s, hx)

        # Skeleton
        if self.has_pose and self._landmarks:
            self._draw_skel(canvas, 0.2)

        # Head color logic — check if inside the safe gap
        head_color = cfg.HEAD_NORMAL
        for s in self.spikes:
            if abs(s.x - hx) < 150:
                in_top = hy < s.top_h - cfg.GRACE_PX
                in_bot = s.has_bottom and hy > s.bot_y + cfg.GRACE_PX
                if in_top or in_bot:
                    head_color = cfg.HEAD_DANGER
                else:
                    head_color = cfg.HEAD_SAFE
                break

        # Trail + head
        self.fx.add_trail(hx, hy)
        self._draw_head(canvas, hx, hy, head_color)

        # Invincibility
        if self.invincibility > 0:
            self.invincibility -= 1
            if self.frame_n % 6 < 3:
                cv2.circle(canvas, (hx, hy), cfg.HEAD_RADIUS + 16,
                           (255, 255, 255), 2, cv2.LINE_AA)
        else:
            # Collision check — top AND bottom spikes
            for s in self.spikes:
                hit = False
                # Top spike
                l, r, t, b = s.top_hitbox(cfg.HITBOX_SHRINK, cfg.GRACE_PX)
                if l <= hx <= r and t <= hy <= b:
                    hit = True
                # Bottom spike
                if not hit and s.has_bottom:
                    l, r, t, b = s.bot_hitbox(cfg.HITBOX_SHRINK, cfg.GRACE_PX, cfg.WINDOW_HEIGHT)
                    if l <= hx <= r and t <= hy <= b:
                        hit = True
                if hit:
                    self.lives -= 1
                    self.invincibility = cfg.INVINCIBILITY_FRAMES
                    self.fx.trigger_flash(cfg.HIT_FLASH, 12)
                    self.fx.trigger_shake(15)
                    if self.lives <= 0:
                        self._end_game()
                        return
                    break

        # Scoring — spike pair passed player line
        for s in self.spikes:
            if not s.scored and s.x < self.player_x - 50:
                s.scored = True
                self.score += 1
                self.speed = min(
                    cfg.SPIKE_SPEED_MAX,
                    cfg.SPIKE_SPEED_INIT + self.score * cfg.SPIKE_SPEED_RAMP,
                )
                self.fx.add_popup(hx + 30, hy - 20, "+1", cfg.DODGE_CLR)
                self.fx.trigger_flash((0, 60, 30), 3)

        # HUD
        self._draw_hud(canvas)

        # Danger warning — show safe zone for nearest approaching spike
        for s in self.spikes:
            if self.player_x - 80 < s.x < self.player_x + 300:
                top_tip = int(s.top_h)
                # Dashed line at top spike tip
                dash_len = 15
                for dx in range(0, cfg.WINDOW_WIDTH, dash_len * 2):
                    cv2.line(canvas, (dx, top_tip), (dx + dash_len, top_tip),
                             (40, 40, 60), 1, cv2.LINE_AA)
                if s.has_bottom:
                    bot_tip = int(s.bot_y)
                    for dx in range(0, cfg.WINDOW_WIDTH, dash_len * 2):
                        cv2.line(canvas, (dx, bot_tip), (dx + dash_len, bot_tip),
                                 (40, 60, 40), 1, cv2.LINE_AA)
                # Label
                cv2.putText(canvas, "SAFE ZONE", (cfg.WINDOW_WIDTH - 180, top_tip + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 100, 60), 1, cv2.LINE_AA)
                break

    # ------------------------------------------------------------------
    # GAME OVER
    # ------------------------------------------------------------------

    def _end_game(self):
        self.state = State.GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score

    def _gameover(self, canvas):
        cfg = self.cfg
        cx, cy = cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT // 2

        if self.has_pose and self._landmarks:
            self._draw_skel(canvas, 0.1)

        # Dim overlay
        ov = np.zeros_like(canvas)
        cv2.addWeighted(ov, 0.4, canvas, 0.6, 0, canvas)

        _ctext(canvas, "GAME OVER", cx, cy - 60, 2.5, (80, 80, 255), 5)
        _ctext(canvas, f"Score: {self.score}", cx, cy + 20, 1.3, (255, 255, 255), 3)

        if self.score >= self.high_score and self.score > 0:
            _ctext(canvas, "NEW BEST!", cx, cy + 75, 0.9, (0, 255, 200), 2)
        else:
            _ctext(canvas, f"Best: {self.high_score}", cx, cy + 75, 0.8, (100, 200, 255), 2)

        if int(time.time() * 2) % 2 == 0:
            _ctext(canvas, "Press SPACE to continue", cx, cy + 140, 0.7, (150, 150, 150), 1)


# =============================================================================
# HELPERS
# =============================================================================

def _ctext(canvas, text, cx, cy, scale, color, thick):
    """Draw centered text."""
    sz = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)[0]
    cv2.putText(canvas, text, (cx - sz[0] // 2, cy + sz[1] // 2),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    game = DuckGame()
    game.run()


if __name__ == "__main__":
    main()
