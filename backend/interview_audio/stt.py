import os
import logging
from RealtimeSTT import AudioToTextRecorder
import numpy as np
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

transcript_path = "../data/transcripts"
os.makedirs(transcript_path, exist_ok=True)

class STTFeed:
    def __init__(self):
        super().__init__()
        self.recorder = AudioToTextRecorder(
            use_microphone=False,
            device="cpu",
            model="small.en",
            enable_realtime_transcription=True,
            no_log_file=True
        )
        logger.info("STTFeed initialized with model: %s", self.recorder.model)

    def to_pcm16_16k(self, mono_float32: np.ndarray, sr: int): #os here the args are the audio data and sample rate
        target_sr = 16000
        x = mono_float32.astype(np.float32)
        if sr != target_sr:
            ratio = target_sr / sr
            new_len = int(len(x) * ratio)
            x = np.interp(np.linspace(0, len(x)-1, new_len), np.arange(len(x)), x)
        x = np.clip(x, -1.0, 1.0)
        return (x * 32767.0).astype(np.int16).tobytes()
    
    def feed_and_transcribe(self, mono_float32, sr):
        pcm = self.to_pcm16_16k(mono_float32, sr)

        self.recorder.feed_audio(pcm)

        out = []
        def cb(t: str):
            out.append(t)
            logger.info("Transcription: %s", t)

        self.recorder.text(cb)
        if out:
            txt = " ".join(out)
            fname = os.path.join(transcript_path, f"{uuid.uuid4()}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(txt)
            return txt
        return None

    


