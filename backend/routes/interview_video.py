from fastapi import APIRouter, HTTPException, Depends
from datetime import time, datetime
import os
import cv2
import json
import uuid
from fastrtc import Stream
import numpy as np
import threading
from backend.interview_video.fraud_detection import VideoFraudDetector, DetectorConfig
import queue

router = APIRouter(
    prefix="/interview_video",
    title="Interview Video API for Rezkrypt-beta",
    version="0.0.1",
    responses={404: {"description": "Not found"}},
)

BASE_DATA = "../data"
FRAME_DIR = os.path.join(BASE_DATA, "video_frames")
os.makedirs(FRAME_DIR, exist_ok=True)

class InterviewVideoSess:
    def __init__(self, session_id, cfg): #so the args are session_id, and tehn detection config if want can be explicitly set
        self.session_id = session_id
        self.cfg = cfg or DetectorConfig()
        self.detector = VideoFraudDetector(session_id=session_id, cfg=self.cfg)
        self.frame_q = queue.Queue(maxsize=30)
        self.event_q = queue.Queue()

        self.stop_flag = threading.Event()

        self.worker = threading.Thread(target=self.process_loop, daemon=True)
        self.worker.start()

    def process_loop(self):
        while not self.stop_flag.is_set():
            try:
                frame, ts = self.frame_q.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                events = self.detector.process_frame(frame, capture_reference=False)

                for ev in events:
                    ev["session_id"] = self.session_id
                    ev["ts"] = ts
                    self.event_q.put(ev)
            except Exception as e:
                err = {"type": "ERROR", "error": str(e), "session_id": self.session_id, "ts": ts}
                self.event_q.put(err)
            finally:
                self.frame_q.task_done()

    def submit_frame(self, frame, ts):
        try:
            self.frame_q.put_nowait((frame, ts))
        except queue.Full:
            pass
        #so i thihnk if the queu is full, let it process, a little of realtime is good

    def poll_event(self, timeout=0.0):
        try:
            return self.event_q.get(timeout=timeout)
        except queue.Empty:
            return None
        
    def stop(self):
        self.stop_flag.set()
        try:
            #unblocking the queue to allow the worker to exit
            self.frame_q.put_nowait((np.zeros((1, 1, 3), dtype=np.uint8), datetime.utcnow().timestamp()))
        except Exception:
            pass

sess = {} #plural of sessions

def get_pr_create_session(conn_id: str):
    ses = sess.get(conn_id)
    if ses:
        return ses
    ses = InterviewVideoSess(session_id=conn_id)
    sess[conn_id] = ses
    return ses

def destroy_session(conn_id):
    ses = sess.pop(conn_id, None)
    if ses:
        ses.stop()

def ensure_bgr_frame(frame_or_bytes):
    if isinstance(frame_or_bytes, np.ndarray):
        arr = frame_or_bytes
        if arr.ndim == 3 and arr.shape[2] == 3:
            return arr
        if arr.ndim == 2:
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        return None

    if isinstance(frame_or_bytes, (bytes, bytearray)):
        nparr = np.frombuffer(frame_or_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    return None

def on_frame_handler(video, context):
    conn_id = str(context.get("connection_id", "default-video-conn"))
    sess = get_pr_create_session(conn_id)

    frame_np = None
    ts = datetime.utcnow().timestamp()

    if isinstance(video, tuple):
        if len(video) == 1:
            frame_np = ensure_bgr_frame(video[0])
        elif len(video) == 2:
            a, b = video
            f = b if isinstance(b, (np.ndarray, bytes, bytearray)) else a
            frame_np = ensure_bgr_frame(f)
            meta = a if isinstance(a, dict) else (b if isinstance(b, dict) else None)
            if isinstance(meta, dict) and "ts" in meta:
                try:
                    ts = float(meta["ts"])
                except Exception:
                    pass
        else:
            return
    else:
        frame_np = ensure_bgr_frame(video)

    if frame_np is None:
        return

    sess.submit_frame(frame_np, ts)

    max_to_send = 5
    sent = 0
    while sent < max_to_send:
        ev = sess.poll_event(timeout=0.0)
        if not ev:
            break
        payload = json.dumps(ev, ensure_ascii=False)
        yield {"type": "alert", "json": payload}
        sent += 1

stream = Stream(
    name="interview_video_stream_rezkrypt_beta",
    modality="video",
    mode="send-receive",
    tags=["interview", "video", "fraud_detection"],
    handler=on_frame_handler
)

stream.mount(app=router, path="/stream")

@router.post("/end/{conn_id}")
async def end_session(conn_id: str):
    if conn_id not in sess:
        raise HTTPException(status_code=404, detail="Session not found")
    destroy_session(conn_id)
    return {"status": "stopped", "conn_id": conn_id}