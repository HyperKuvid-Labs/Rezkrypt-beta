#so this is the enhnaced script from gpt-5, just used it for testing, but this si the more enhanced version of "backend/interview_video/eyeTrackingNheadPosistion.py"
import os
import cv2
import json
import time
import math
import queue
import base64
import threading
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import mediapipe as mp

@dataclass
class DetectorConfig:
    max_faces: int = 2
    min_detect_conf: float = 0.5
    min_track_conf: float = 0.5
    zone_edge_ratio: float = 0.3
    dwell_warn_s: float = 3.0
    dwell_critical_s: float = 5.0
    glance_window_s: float = 60.0
    glance_threshold: int = 5
    # Deviation thresholds
    reference_deviation_px: float = 30.0
    cheek_iris_deviation_px: float = 18.0
    # Absence/tamper
    absence_warn_s: float = 3.0
    tamper_area_ratio: float = 0.33
    # Blink/freeze heuristics
    freeze_window_s: float = 8.0
    freeze_motion_thresh_px: float = 2.0
    blink_min_per_minute: int = 8  # heuristic; requires eye aspect ratio impl
    # Alerting
    alert_cooldown_s: float = 20.0
    # Evidence
    snapshot_dir: str = "./data/proctor_snapshots"
    log_dir: str = "./data/proctor_logs"
    save_snapshots: bool = True

# -------------------------
# Utilities
# -------------------------
def now_s() -> float:
    return time.time()

def ensure_dirs(cfg: DetectorConfig):
    os.makedirs(cfg.snapshot_dir, exist_ok=True)
    os.makedirs(cfg.log_dir, exist_ok=True)

def landmark_to_xy(lm, w, h) -> Tuple[int, int]:
    return int(lm.x * w), int(lm.y * h)

class EventLogger:
    def __init__(self, cfg: DetectorConfig, session_id: str):
        ensure_dirs(cfg)
        self.path = os.path.join(cfg.log_dir, f"{session_id}.jsonl")
        self.lock = threading.Lock()

    def log(self, event: Dict[str, Any]):
        event["ts"] = time.time()
        line = json.dumps(event, ensure_ascii=False)
        with self.lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

class AlertDispatcher:
    def __init__(self, cfg: DetectorConfig, logger: EventLogger):
        self.cfg = cfg
        self.logger = logger
        self.last_alert_ts: Dict[str, float] = {}

    def _cooldown_ok(self, key: str) -> bool:
        last = self.last_alert_ts.get(key, 0.0)
        if now_s() - last >= self.cfg.alert_cooldown_s:
            self.last_alert_ts[key] = now_s()
            return True
        return False

    def notify(self, key: str, payload: Dict[str, Any]):
        if not self._cooldown_ok(key):
            return
        self.logger.log({"type": "ALERT", "key": key, "payload": payload})
        # Extend for webhooks/WS/email here; keep non-blocking.

class EvidenceStore:
    def __init__(self, cfg: DetectorConfig, session_id: str):
        self.cfg = cfg
        self.session_id = session_id
        ensure_dirs(cfg)

    def save_snapshot(self, frame: np.ndarray, tag: str) -> Optional[str]:
        if not self.cfg.save_snapshots:
            return None
        ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        name = f"{self.session_id}_{ts}_{tag}.jpg"
        path = os.path.join(self.cfg.snapshot_dir, name)
        cv2.imwrite(path, frame)
        return path

class VideoFraudDetector:
    def __init__(self, session_id: str, cfg: Optional[DetectorConfig] = None):
        self.cfg = cfg or DetectorConfig()
        self.logger = EventLogger(self.cfg, session_id)
        self.alerts = AlertDispatcher(self.cfg, self.logger)
        self.evidence = EvidenceStore(self.cfg, session_id)

        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=self.cfg.max_faces,
            refine_landmarks=True,
            min_detection_confidence=self.cfg.min_detect_conf,
            min_tracking_confidence=self.cfg.min_track_conf,
        )
        self.face_det = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=self.cfg.min_detect_conf
        )

        self.bg_sub = cv2.createBackgroundSubtractorMOG2()
        self.kernel = np.ones((5, 5), np.uint8)

        # State
        self.reference_landmarks: Dict[int, List[Tuple[int, int]]] = {}
        self.reference_cheek_iris: Dict[int, Tuple[float, float]] = {}
        self.last_seen_ts: Optional[float] = None
        self.zone_start_times: List[Dict[str, float]] = [dict() for _ in range(self.cfg.max_faces)]
        self.freq_zone_times: List[Dict[str, List[float]]] = [dict() for _ in range(self.cfg.max_faces)]
        self.last_landmarks_xy: Dict[int, List[Tuple[int, int]]] = {}
        self.landmark_motion_buf: List[List[Tuple[int, int]]] = []  # optional rolling window

    def coarse_zone(self, x, y, w, h) -> str:
        if x < w * self.cfg.zone_edge_ratio:
            return "LEFT"
        if x > w * (1 - self.cfg.zone_edge_ratio):
            return "RIGHT"
        if y < h * self.cfg.zone_edge_ratio:
            return "TOP"
        if y > h * (1 - self.cfg.zone_edge_ratio):
            return "BOTTOM"
        return "CENTER"

    def detailed_zone(self, x, y, w, h) -> str:
        zr = self.cfg.zone_edge_ratio
        left = x < w * zr
        right = x > w * (1 - zr)
        top = y < h * zr
        bottom = y > h * (1 - zr)
        if left and top: return "TL"
        if left and bottom: return "BL"
        if right and top: return "TR"
        if right and bottom: return "BR"
        if left: return "LEFT"
        if right: return "RIGHT"
        if top: return "TOP"
        if bottom: return "BOTTOM"
        return "CENTER"

    def capture_reference(self, idx: int, landmarks, w: int, h: int, frame) -> None:
        pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in [1, 10]]
        cheek1 = (int(landmarks[234].x * w), int(landmarks[234].y * h))
        cheek2 = (int(landmarks[454].x * w), int(landmarks[454].y * h))
        iris_l = (int(landmarks[468].x * w), int(landmarks[468].y * h))
        iris_r = (int(landmarks[473].x * w), int(landmarks[473].y * h))

        self.reference_landmarks[idx] = pts
        if iris_l and iris_r:
            d1 = math.hypot(cheek1[0] - iris_l[0], cheek1[1] - iris_l[1])
            d2 = math.hypot(cheek2[0] - iris_r[0], cheek2[1] - iris_r[1])
            self.reference_cheek_iris[idx] = (d1, d2)
        self.logger.log({"type": "INFO", "event": "REFERENCE_CAPTURED", "face_idx": idx})
        self.evidence.save_snapshot(frame, f"ref_face{idx}")
    def process_frame(self, frame: np.ndarray, capture_reference: bool = False) -> List[Dict[str, Any]]:
        h, w = frame.shape[:2]
        ts = now_s()
        self.last_seen_ts = ts

        # Face detection (multi-face) for intrusion/absence monitor
        det_res = self.face_det.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        n_faces = len(det_res.detections) if det_res and det_res.detections else 0

        events: List[Dict[str, Any]] = []
        if n_faces == 0:
            # Absence tracking
            events.append({"type": "ABSENCE_TICK", "faces": 0})
        elif n_faces > 1:
            events.append({"type": "MULTI_FACE", "faces": n_faces})

        # Face mesh for gaze/landmarks
        mesh_res = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not mesh_res.multi_face_landmarks:
            # Tamper/background check even if no face
            self._check_tamper(frame, w, h, events)
            return events

        for idx, lmks in enumerate(mesh_res.multi_face_landmarks[: self.cfg.max_faces]):
            landmarks = lmks.landmark
            nose = landmarks[1]
            fh = landmarks[10]
            nose_xy = (int(nose.x * w), int(nose.y * h))
            fh_xy = (int(fh.x * w), int(fh.y * h))
            cheek1 = (int(landmarks[234].x * w), int(landmarks[234].y * h))
            cheek2 = (int(landmarks[454].x * w), int(landmarks[454].y * h))
            iris_l = (int(landmarks[468].x * w), int(landmarks[468].y * h))
            iris_r = (int(landmarks[473].x * w), int(landmarks[473].y * h))

            if capture_reference:
                self.capture_reference(idx, landmarks, w, h, frame)

            # Deviation from reference
            if idx in self.reference_landmarks:
                ref_pts = self.reference_landmarks[idx]
                cur_pts = [nose_xy, fh_xy]
                deviations = [math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(ref_pts, cur_pts)]
                if any(d > self.cfg.reference_deviation_px for d in deviations):
                    events.append({"type": "REF_DEVIATION", "face_idx": idx, "deviation_px": max(deviations)})

            if idx in self.reference_cheek_iris and iris_l and iris_r:
                d1 = math.hypot(cheek1[0] - iris_l[0], cheek1[1] - iris_l[1])
                d2 = math.hypot(cheek2[0] - iris_r[0], cheek2[1] - iris_r[1])
                rd1, rd2 = self.reference_cheek_iris[idx]
                if abs(d1 - rd1) > self.cfg.cheek_iris_deviation_px or abs(d2 - rd2) > self.cfg.cheek_iris_deviation_px:
                    events.append({"type": "CHEEK_IRIS_DRIFT", "face_idx": idx, "d1": d1, "d2": d2})

            # Zones
            cz = self.coarse_zone(nose_xy[0], nose_xy[1], w, h)
            dz = self.detailed_zone(nose_xy[0], nose_xy[1], w, h)
            self._update_zone_timers(idx, cz, dz, events)

            # Freeze heuristic using landmark jitter
            self._check_freeze(idx, [nose_xy, fh_xy], events)

        # Tamper/background scene changes
        self._check_tamper(frame, w, h, events)

        # Rollup rules and alerting
        self._apply_rules_and_alert(events, frame)

        # Structured logging
        for ev in events:
            self.logger.log(ev)

        return events

    # ---------------------
    # Helpers
    # ---------------------
    def _update_zone_timers(self, idx: int, coarse: str, detailed: str, events: List[Dict[str, Any]]):
        t = now_s()
        # Dwell timers on coarse zones
        zmap = self.zone_start_times[idx]
        for z in list(zmap.keys()):
            if z != coarse:
                del zmap[z]
        if coarse not in zmap:
            zmap[coarse] = t
        dwell = t - zmap[coarse]
        if coarse != "CENTER":
            if self.cfg.dwell_warn_s < dwell <= self.cfg.dwell_critical_s:
                events.append({"type": "DWELL_WARN", "face_idx": idx, "zone": coarse, "seconds": round(dwell, 2)})
            elif dwell > self.cfg.dwell_critical_s:
                events.append({"type": "DWELL_CRITICAL", "face_idx": idx, "zone": coarse, "seconds": round(dwell, 2)})

        # Frequent glance tracking on detailed off-center AOIs
        if detailed != "CENTER":
            fzt = self.freq_zone_times[idx].setdefault(detailed, [])
            # prune
            cutoff = now_s() - self.cfg.glance_window_s
            fzt[:] = [x for x in fzt if x >= cutoff]
            fzt.append(now_s())
            if len(fzt) >= self.cfg.glance_threshold:
                events.append({"type": "FREQUENT_GLANCE", "face_idx": idx, "zone": detailed, "count": len(fzt)})

    def _check_freeze(self, idx: int, pts: List[Tuple[int, int]], events: List[Dict[str, Any]]):
        last_pts = self.last_landmarks_xy.get(idx)
        self.last_landmarks_xy[idx] = pts
        if last_pts:
            max_move = max(math.hypot(a[0]-b[0], a[1]-b[1]) for a, b in zip(pts, last_pts))
            # Track over window by embedding into events; simplified heuristic
            if max_move <= self.cfg.freeze_motion_thresh_px:
                events.append({"type": "FREEZE_TICK", "face_idx": idx})

    def _check_tamper(self, frame: np.ndarray, w: int, h: int, events: List[Dict[str, Any]]):
        fgmask = self.bg_sub.apply(frame)
        fgmask = cv2.erode(fgmask, self.kernel, iterations=2)
        fgmask = cv2.dilate(fgmask, self.kernel, iterations=2)
        contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        total_area = 0
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            if cw >= 40 or ch >= 40:
                total_area += cw * ch
        if total_area >= (w * h * self.cfg.tamper_area_ratio):
            events.append({"type": "TAMPER_DETECTED", "area_ratio": round(total_area / (w*h), 2)})

    def _apply_rules_and_alert(self, events: List[Dict[str, Any]], frame: np.ndarray):
        # Aggregate signals and trigger alerts with cooldown + evidence snapshot
        types = [e["type"] for e in events]
        # Absence detection (count consecutive)
        if "ABSENCE_TICK" in types:
            # Use last_seen_ts to escalate after threshold
            if self.last_seen_ts and now_s() - self.last_seen_ts >= self.cfg.absence_warn_s:
                snap = self.evidence.save_snapshot(frame, "absence")
                self.alerts.notify("absence", {"msg": "No face detected", "snapshot": snap})
        # Multi-face intrusion
        for e in events:
            if e["type"] == "MULTI_FACE":
                snap = self.evidence.save_snapshot(frame, "multi_face")
                self.alerts.notify("multi_face", {"msg": f"{e['faces']} faces detected", "snapshot": snap})
        # Prolonged off-center dwell
        for e in events:
            if e["type"] in ("DWELL_CRITICAL", "FREQUENT_GLANCE"):
                snap = self.evidence.save_snapshot(frame, "gaze")
                self.alerts.notify("gaze", {"event": e, "snapshot": snap})
        # Reference deviation or cheek-iris drift
        for e in events:
            if e["type"] in ("REF_DEVIATION", "CHEEK_IRIS_DRIFT"):
                snap = self.evidence.save_snapshot(frame, "pose")
                self.alerts.notify("pose", {"event": e, "snapshot": snap})
        # Tamper
        for e in events:
            if e["type"] == "TAMPER_DETECTED":
                snap = self.evidence.save_snapshot(frame, "tamper")
                self.alerts.notify("tamper", {"event": e, "snapshot": snap})
        # Freeze heuristic: if many FREEZE_TICKs in recent window, escalate
        freeze_ticks = sum(1 for t in types if t == "FREEZE_TICK")
        if freeze_ticks >= 10:  # heuristic; adjust
            snap = self.evidence.save_snapshot(frame, "freeze")
            self.alerts.notify("freeze", {"msg": "Low facial motion observed", "ticks": freeze_ticks, "snapshot": snap})
