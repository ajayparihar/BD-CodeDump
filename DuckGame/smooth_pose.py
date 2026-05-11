"""
Skeleton Tracker
================
A real-time pose detection application using MediaPipe that renders
a minimalist white stickman on a black background with FPS overlay.

Requirements:
    - mediapipe
    - opencv-python
    - numpy

Usage:
    python smooth-pose.py

Press 'q' to exit.
"""

import os
import time
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import (
    PoseLandmarker,
    PoseLandmarkerOptions,
    RunningMode,
)
from mediapipe.tasks.python.core.base_options import BaseOptions


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SmoothedLandmark:
    """A single smoothed pose landmark with position and visibility."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    visibility: float = 0.0


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class DisplayConfig:
    """Display and rendering configuration.

    TWEAK THESE VALUES to adjust visual quality and performance.
    """
    # === RESOLUTION SETTINGS ===
    # PROCESSING resolution (lower = faster FPS, less CPU usage)
    # MediaPipe works on this resolution — 480x360 is fast, 640x480 balanced
    PROCESS_WIDTH: int = 640
    PROCESS_HEIGHT: int = 480

    # RENDER resolution (final output quality — can be higher than process)
    # The skeleton is rendered at this resolution for crisp display
    RENDER_WIDTH: int = 1920
    RENDER_HEIGHT: int = 1080

    # Window display size (what you actually see on screen)
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080

    # === VISUAL STYLE ===
    # cv2.LINE_AA = smooth anti-aliased lines (2-3× slower than LINE_8)
    # cv2.LINE_8  = pixelated 8-connected lines (faster)
    LINE_TYPE: int = cv2.LINE_AA

    # === SKELETON APPEARANCE ===
    SKELETON_THICKNESS: int = 8
    JOINT_RADIUS: int = 12
    HEAD_RADIUS_MIN: int = 40
    HEAD_SCALE_FACTOR: float = 0.6

    # === TEXT APPEARANCE ===
    FPS_FONT_SCALE: float = 1.6
    POSE_FONT_SCALE: float = 3.0
    TEXT_THICKNESS_FPS: int = 2
    TEXT_THICKNESS_POSE: int = 4

    # === LAYOUT POSITIONS ===
    FPS_MARGIN_RIGHT: int = 30
    FPS_MARGIN_TOP: int = 50
    POSE_Y_OFFSET: int = 100

    WINDOW_TITLE: str = "Skeleton Tracker"

    # === COLORS (BGR format for OpenCV) ===
    BG_COLOR: Tuple[int, int, int] = (0, 0, 0)
    SKELETON_COLOR: Tuple[int, int, int] = (255, 255, 255)
    FPS_COLOR: Tuple[int, int, int] = (0, 255, 0)
    POSE_JUMP_COLOR: Tuple[int, int, int] = (0, 255, 0)
    POSE_DUCK_COLOR: Tuple[int, int, int] = (0, 0, 255)
    POSE_IDLE_COLOR: Tuple[int, int, int] = (255, 255, 255)


@dataclass(frozen=True)
class DetectionConfig:
    """MediaPipe detection configuration."""
    MODEL_URL: str = (
        "https://storage.googleapis.com/mediapipe-models/"
        "pose_landmarker/pose_landmarker_lite/float16/latest/"
        "pose_landmarker_lite.task"
    )
    MODEL_PATH: str = "pose_landmarker.task"

    MIN_DETECTION_CONFIDENCE: float = 0.6
    MIN_TRACKING_CONFIDENCE: float = 0.7
    MIN_VISIBILITY: float = 0.5
    NUM_POSES: int = 1
    PROCESS_EVERY_NTH_FRAME: int = 1

    # === SMOOTHING ===
    # EMA_ALPHA: 0.0–1.0, lower = more smoothing but more lag (try 0.15–0.4)
    EMA_ALPHA: float = 0.3


# =============================================================================
# SKELETON DEFINITION — Body parts to render (MediaPipe landmark indices)
# Reference: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
# =============================================================================

class Landmarks:
    """MediaPipe pose landmark indices."""
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28


# Simplified body connections — no face, fingers, or toes
BODY_CONNECTIONS: List[Tuple[int, int]] = [
    # Torso
    (Landmarks.LEFT_SHOULDER, Landmarks.RIGHT_SHOULDER),
    (Landmarks.LEFT_SHOULDER, Landmarks.LEFT_HIP),
    (Landmarks.RIGHT_SHOULDER, Landmarks.RIGHT_HIP),
    (Landmarks.LEFT_HIP, Landmarks.RIGHT_HIP),
    # Arms
    (Landmarks.LEFT_SHOULDER, Landmarks.LEFT_ELBOW),
    (Landmarks.LEFT_ELBOW, Landmarks.LEFT_WRIST),
    (Landmarks.RIGHT_SHOULDER, Landmarks.RIGHT_ELBOW),
    (Landmarks.RIGHT_ELBOW, Landmarks.RIGHT_WRIST),
    # Legs
    (Landmarks.LEFT_HIP, Landmarks.LEFT_KNEE),
    (Landmarks.LEFT_KNEE, Landmarks.LEFT_ANKLE),
    (Landmarks.RIGHT_HIP, Landmarks.RIGHT_KNEE),
    (Landmarks.RIGHT_KNEE, Landmarks.RIGHT_ANKLE),
]

# Landmarks rendered as filled joint circles
JOINT_LANDMARKS: List[int] = [
    Landmarks.LEFT_SHOULDER, Landmarks.RIGHT_SHOULDER,
    Landmarks.LEFT_ELBOW, Landmarks.RIGHT_ELBOW,
    Landmarks.LEFT_WRIST, Landmarks.RIGHT_WRIST,
    Landmarks.LEFT_HIP, Landmarks.RIGHT_HIP,
    Landmarks.LEFT_KNEE, Landmarks.RIGHT_KNEE,
    Landmarks.LEFT_ANKLE, Landmarks.RIGHT_ANKLE,
]


# =============================================================================
# LANDMARK SMOOTHER
# =============================================================================

class LandmarkSmoother:
    """Applies Exponential Moving Average (EMA) smoothing to pose landmarks.

    Reduces frame-to-frame jitter without adding noticeable lag at
    typical alpha values (0.2–0.4).
    """

    def __init__(self, alpha: float = 0.3):
        self._alpha = alpha
        self._ema: Optional[List[SmoothedLandmark]] = None

    def reset(self) -> None:
        """Clear smoothing state (e.g. when a person re-enters frame)."""
        self._ema = None

    def smooth(self, landmarks) -> List[SmoothedLandmark]:
        """Blend current landmarks with the EMA state.

        Args:
            landmarks: Raw MediaPipe pose landmarks for one person.

        Returns:
            List of SmoothedLandmark with temporally smoothed positions.
        """
        if self._ema is None or len(self._ema) != len(landmarks):
            # First frame or landmark count changed — seed EMA
            self._ema = [
                SmoothedLandmark(lm.x, lm.y, lm.z, lm.visibility)
                for lm in landmarks
            ]
            return list(self._ema)

        alpha = self._alpha
        inv_alpha = 1.0 - alpha
        result: List[SmoothedLandmark] = []

        for i, current in enumerate(landmarks):
            prev = self._ema[i]
            smoothed = SmoothedLandmark(
                x=alpha * current.x + inv_alpha * prev.x,
                y=alpha * current.y + inv_alpha * prev.y,
                z=alpha * current.z + inv_alpha * prev.z,
                visibility=current.visibility,
            )
            result.append(smoothed)

        self._ema = result
        return result


# =============================================================================
# SKELETON RENDERER
# =============================================================================

class SkeletonRenderer:
    """Renders a simplified stickman skeleton onto a pre-allocated canvas."""

    def __init__(self, display_cfg: DisplayConfig, detection_cfg: DetectionConfig):
        self._cfg = display_cfg
        self._det_cfg = detection_cfg
        # Pre-allocate canvas once (avoids ~6 MB allocation per frame)
        self._canvas = np.zeros(
            (display_cfg.RENDER_HEIGHT, display_cfg.RENDER_WIDTH, 3),
            dtype=np.uint8,
        )

    def _landmark_to_pixel(
        self, landmarks, idx: int, width: int, height: int
    ) -> Optional[Tuple[int, int]]:
        """Convert a normalized landmark to pixel coordinates.

        Returns None if the landmark is below the visibility threshold.
        """
        if idx < len(landmarks) and landmarks[idx].visibility > self._det_cfg.MIN_VISIBILITY:
            lm = landmarks[idx]
            return (int(lm.x * width), int(lm.y * height))
        return None

    def _get_neck_point(
        self, landmarks, width: int, height: int
    ) -> Optional[Tuple[int, int]]:
        """Calculate the neck as the midpoint between both shoulders."""
        left = self._landmark_to_pixel(landmarks, Landmarks.LEFT_SHOULDER, width, height)
        right = self._landmark_to_pixel(landmarks, Landmarks.RIGHT_SHOULDER, width, height)
        if left and right:
            return ((left[0] + right[0]) // 2, (left[1] + right[1]) // 2)
        return None

    def render(self, landmarks) -> np.ndarray:
        """Render the skeleton onto the internal canvas and return it.

        Args:
            landmarks: Smoothed pose landmarks for one person.

        Returns:
            BGR image (numpy array) with the rendered skeleton.
        """
        canvas = self._canvas
        canvas.fill(0)

        if not landmarks:
            return canvas

        cfg = self._cfg
        width, height = cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT
        color = cfg.SKELETON_COLOR
        thickness = cfg.SKELETON_THICKNESS
        line_type = cfg.LINE_TYPE

        # Draw body connections
        for start_idx, end_idx in BODY_CONNECTIONS:
            pt1 = self._landmark_to_pixel(landmarks, start_idx, width, height)
            pt2 = self._landmark_to_pixel(landmarks, end_idx, width, height)
            if pt1 and pt2:
                cv2.line(canvas, pt1, pt2, color, thickness, line_type)

        # Draw circular head
        nose = self._landmark_to_pixel(landmarks, Landmarks.NOSE, width, height)
        neck = self._get_neck_point(landmarks, width, height)

        if nose and neck:
            neck_to_nose = abs(neck[1] - nose[1])
            head_radius = max(
                int(neck_to_nose * cfg.HEAD_SCALE_FACTOR),
                cfg.HEAD_RADIUS_MIN,
            )
            head_center = (nose[0], nose[1] + head_radius // 2)
            cv2.circle(canvas, head_center, head_radius, color, thickness, line_type)

        # Draw joints as filled circles
        for idx in JOINT_LANDMARKS:
            pt = self._landmark_to_pixel(landmarks, idx, width, height)
            if pt:
                cv2.circle(canvas, pt, cfg.JOINT_RADIUS, color, -1, line_type)

        return canvas


# =============================================================================
# MODEL MANAGER
# =============================================================================

def ensure_model(config: DetectionConfig) -> str:
    """Download the MediaPipe model if it doesn't exist locally.

    Returns:
        Path to the model file.
    """
    if not os.path.exists(config.MODEL_PATH):
        import urllib.request
        logger.info("Downloading Pose Landmarker model...")
        urllib.request.urlretrieve(config.MODEL_URL, config.MODEL_PATH)
        logger.info("Model downloaded to %s", config.MODEL_PATH)
    return config.MODEL_PATH


def create_landmarker(config: DetectionConfig) -> PoseLandmarker:
    """Create and return a configured PoseLandmarker instance."""
    model_path = ensure_model(config)
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=RunningMode.VIDEO,
        num_poses=config.NUM_POSES,
        min_pose_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_pose_presence_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
    )
    return PoseLandmarker.create_from_options(options)


# =============================================================================
# CAMERA
# =============================================================================

class Camera:
    """Thin wrapper around cv2.VideoCapture with DirectShow fallback."""

    def __init__(self, source: int = 0, buffer_size: int = 1):
        # Try DirectShow backend on Windows first (better compatibility)
        self._cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            logger.warning("DirectShow failed, falling back to default backend.")
            self._cap = cv2.VideoCapture(source)

        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open video source {source}")

        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
        time.sleep(0.5)  # Camera warmup
        logger.info("Camera initialised (source=%s)", source)

    @property
    def is_opened(self) -> bool:
        return self._cap.isOpened()

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        return self._cap.read()

    def release(self) -> None:
        self._cap.release()


# =============================================================================
# SKELETON TRACKER (orchestrator)
# =============================================================================

class SkeletonTracker:
    """Real-time skeleton tracking with EMA-smoothed rendering.

    Orchestrates camera capture → MediaPipe inference → smoothing → rendering.
    """

    def __init__(
        self,
        source: int = 0,
        display_cfg: Optional[DisplayConfig] = None,
        detection_cfg: Optional[DetectionConfig] = None,
        on_pose: Optional[Callable] = None,
    ):
        """Initialise the tracker.

        Args:
            source: Video source index (0 for default webcam).
            display_cfg: Display/rendering config (uses defaults if None).
            detection_cfg: Detection/smoothing config (uses defaults if None).
            on_pose: Optional callback ``fn(smoothed_landmarks)`` called each frame.
        """
        self.display_cfg = display_cfg or DisplayConfig()
        self.detection_cfg = detection_cfg or DetectionConfig()
        self.on_pose = on_pose

        # Components
        self._camera = Camera(source)
        self._landmarker = create_landmarker(self.detection_cfg)
        self._smoother = LandmarkSmoother(alpha=self.detection_cfg.EMA_ALPHA)
        self._renderer = SkeletonRenderer(self.display_cfg, self.detection_cfg)

        # FPS tracking
        self._fps_history: deque = deque(maxlen=30)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main loop — capture, detect, smooth, render, display."""
        cfg = self.display_cfg
        det_cfg = self.detection_cfg
        process_size = (cfg.PROCESS_WIDTH, cfg.PROCESS_HEIGHT)
        window_size = (cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT)
        render_size = (cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT)

        frame_counter = 0
        last_landmarks = None

        cv2.namedWindow(cfg.WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(cfg.WINDOW_TITLE, *window_size)

        logger.info("Skeleton Tracker running — press 'q' to exit")

        try:
            while self._camera.is_opened:
                ret, frame = self._camera.read()
                if not ret:
                    break

                frame_counter += 1
                start_time = time.time()

                # --- Pose detection (optionally skip frames) ---
                if frame_counter % det_cfg.PROCESS_EVERY_NTH_FRAME == 0:
                    last_landmarks = self._detect(frame, process_size)

                elapsed = time.time() - start_time

                # --- Smoothing + rendering ---
                if last_landmarks is not None:
                    smoothed = self._smoother.smooth(last_landmarks)
                    if self.on_pose:
                        self.on_pose(smoothed)
                    canvas = self._renderer.render(smoothed)
                else:
                    self._smoother.reset()
                    canvas = self._renderer.render(None)

                # --- FPS overlay ---
                self._draw_fps(canvas, elapsed)

                # --- Resize for display if render ≠ window ---
                if render_size != window_size:
                    canvas = cv2.resize(canvas, window_size, interpolation=cv2.INTER_LINEAR)

                cv2.imshow(cfg.WINDOW_TITLE, canvas)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            self._cleanup()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect(self, frame: np.ndarray, process_size: Tuple[int, int]):
        """Run MediaPipe detection on a down-scaled frame.

        Returns the raw landmarks for the first detected pose, or None.
        """
        try:
            small = cv2.resize(frame, process_size, interpolation=cv2.INTER_NEAREST)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.time() * 1000)
            results = self._landmarker.detect_for_video(mp_image, timestamp_ms)
            if results and results.pose_landmarks:
                return results.pose_landmarks[0]
        except Exception:
            logger.exception("Pose detection failed")
        return None

    def _draw_fps(self, canvas: np.ndarray, elapsed: float) -> None:
        """Render FPS counter onto the top-right of the canvas."""
        if elapsed > 0:
            self._fps_history.append(1.0 / elapsed)

        if not self._fps_history:
            return

        cfg = self.display_cfg
        fps = sum(self._fps_history) / len(self._fps_history)
        fps_text = f"FPS: {int(fps)}"
        text_size = cv2.getTextSize(
            fps_text, cv2.FONT_HERSHEY_SIMPLEX,
            cfg.FPS_FONT_SCALE, cfg.TEXT_THICKNESS_FPS,
        )[0]
        x = cfg.RENDER_WIDTH - text_size[0] - cfg.FPS_MARGIN_RIGHT
        y = cfg.FPS_MARGIN_TOP
        cv2.putText(
            canvas, fps_text, (x, y),
            cv2.FONT_HERSHEY_SIMPLEX, cfg.FPS_FONT_SCALE,
            cfg.FPS_COLOR, cfg.TEXT_THICKNESS_FPS, cfg.LINE_TYPE,
        )

    def _cleanup(self) -> None:
        """Release all resources."""
        self._camera.release()
        cv2.destroyAllWindows()
        logger.info("Cleaned up resources")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    """Application entry point."""
    tracker = SkeletonTracker(source=0)
    tracker.run()


if __name__ == "__main__":
    main()
