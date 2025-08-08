from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.prisma import prisma
from datetime import date, datetime
from fastrtc import Stream, ReplyOnPause
import wave
import numpy as np
from backend.interview_audio.stt import STTFeed
from backend.interview_audio.tts import stream_tts_pcm_bytes_sync
import os
import subprocess
import json
import queue
import threading
import uuid

router = APIRouter(
    prefix="/interview_audio",
    title="Interview API",
    description="A simple FastAPI Interview API",
    version="0.0.1",
    responses={404: {"description": "Not found"}},
)

#so the interview is gonna handle the video stream as well as the audio stream distribute them and run their pipelines accordingly
#and i need to get the time now, and then find the candidate and the company


def get_candidate():
    time_now = date.today()

    cand = prisma.candidate.find_first(
        where={
            "interviewTime": {
                "gte": time_now
            }
        },
    )

    if not cand:
        print("No candidate found!!")
        return "No candidate found"

    #so returning only rhe scores and  reusmes, as this can be used to display the candidate's information
    return {
        "score" : cand.score,
        "resume": cand.resume,
    }

def get_compny():
    #so as of now only one comany is there, so retuning that
    company = prisma.company.find_first()
    if not company:
        print("No company found!!")
        return "No company found"
    
    #this is the compnay schema for my ref
    # odel Company {
    # id String @id @default(uuid()) @map("_id")
    # name String
    # contactPerson String
    # email String @unique
    # phone String @unique
    # website String?
    # industry String?
    # companySize String?
    # location String?
    # jobTitle String?
    # department String?
    # jobType String?
    # experienceLevel String?
    # salary String?
    # skills String?
    # jobDescription String?
    # requirements String?
    # benefits String?
    # applicationDeadline DateTime?
    # createdAt DateTime @default(now()) @map("created_at")
    # updatedAt DateTime @updatedAt @map("updated_at")
    # }
    return {
        "name": company.name,
        "industry": company.industry,
        "companySize": company.companySize,
        "location": company.location,
        "jobTitle": company.jobTitle,
        "department": company.department,
        "jobType": company.jobType,
        "experienceLevel": company.experienceLevel,
        "salary": company.salary,
        "skills": company.skills,
        "jobDescription": company.jobDescription,
        "requirements": company.requirements,
        "benefits": company.benefits,
    }

@router.get("/candidate")
async def get_candidate_info():
    candidate_info = get_candidate()
    if isinstance(candidate_info, str):
        raise HTTPException(status_code=404, detail=candidate_info)
    return candidate_info

@router.get("/company")
async def get_company_info():
    company_info = get_compny()
    if isinstance(company_info, str):
        raise HTTPException(status_code=404, detail=company_info)
    return company_info

#so gonna write the audio thing over here
BASE_DATA = "./data"
AUDIO_DIR = os.path.join(BASE_DATA, "audio_turns")
TRANSCRIPT_DIR = os.path.join(BASE_DATA, "transcripts")
EVAL_DIR = os.path.join(BASE_DATA, "evals")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)

stt_engine = STTFeed()
output_sr = 48000 # so this is basically for hume ai outputting 48khz of audio and send them accordingly

def save_wav(path: str, sr: int, mono: np.ndarray) -> None:
    pcm16 = np.clip(mono, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

def bytes_to_float32_mono(arr_bytes: bytes) -> np.ndarray:
    pcm16 = np.frombuffer(arr_bytes, dtype=np.int16)
    float_mono = (pcm16.astype(np.float32) / 32768.0)
    return float_mono.reshape(1, -1)

def run_ollama(prompt: str, model: str = "llama3.1:8b") -> str:
    proc = subprocess.Popen(
        ["ollama", "run", model, prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out_lines = []
    for line in proc.stdout:
        out_lines.append(line)
    proc.wait()
    return "".join(out_lines).strip()

def build_greeting_and_questions_prompt(company, candidate, variations: int = 10, questions: int = 5) -> str:
    comp_json = json.dumps(company, ensure_ascii=False)
    cand_json = json.dumps(candidate, ensure_ascii=False)
    return f"""
You are an AI interview conductor. Based on the company and candidate info below, produce:
1) greeting_variations: {variations} concise greeting/introduction lines that a recruiter might speak to start an interview. Mix tone slightly across variations; keep each under 2 sentences.
2) questions: {questions} high-quality, structured interview questions tailored to the role/company. Cover fundamentals, experience, problem-solving, and culture fit. Keep each question under 2 sentences.
Return strict JSON with keys "greeting_variations" (array of strings) and "questions" (array of strings). No extra commentary.

company = {comp_json}
candidate = {cand_json}
"""

def parse_greetings_and_questions(llm_text: str):
    try:
        data = json.loads(llm_text)
        gv = data.get("greeting_variations", [])
        qs = data.get("questions", [])
        if isinstance(gv, list) and isinstance(qs, list):
            gv = [s for s in gv if isinstance(s, str) and s.strip()]
            qs = [s for s in qs if isinstance(s, str) and s.strip()]
            return gv, qs
    except Exception:
        pass
    lines = [l.strip("- •").strip() for l in llm_text.splitlines() if l.strip()]
    greetings = lines[:10]
    qs = lines[10:15]
    return greetings, qs

def build_evaluation_prompt(question: str, answer: str, company, candidate):
    comp = json.dumps(company, ensure_ascii=False)
    cand = json.dumps(candidate, ensure_ascii=False)
    return f"""
You are evaluating an interview response.

Context:
- Company: {comp}
- Candidate: {cand}

Question:
{question}

Answer:
{answer}

Tasks:
1) Provide a score from 1 to 10 (integer).
2) Provide a brief justification (2-4 sentences) referencing specific aspects of the answer.
3) Provide bullet-point notes (3-5 bullets).

Return strict JSON with keys: score (int), justification (string), notes (array of strings). No extra commentary.
"""

class INterviewSession:
    def __init__(self, session_id, comany, candidate):
        self.session_id = session_id
        self.company = comany
        self.candidate = candidate
        
        self.greetings = []
        self.questions = []
        self.greet_idx = 0
        self.q_idx = 0
        self.started = False

        self.answers = []

        self.eval_queue = queue.Queue()
        self.eval_thread = threading.Thread(target=self.eval_worker, daemon=True)
        self.eval_thread.start()

    def eval_worker(self):
        while True:
            item = self.eval_queue.get()
            if item is None:
                break
            try:
                question = item["question"]
                transcript = item["transcript"]
                eval_prompt = build_evaluation_prompt(question, transcript, self.company, self.candidate)
                result_raw = run_ollama(eval_prompt)
                
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                eval_path = os.path.join(EVAL_DIR, f"{self.session_id}_{ts}_q{item['q_idx']}.json")
                with open(eval_path, "w", encoding="utf-8") as f:
                    f.write(result_raw)
                item["eval_path"] = eval_path
            except Exception as e:
                err_path = os.path.join(EVAL_DIR, f"{self.session_id}_error.log")
                with open(err_path, "a", encoding="utf-8") as f:
                    f.write(f"Eval error: {e}\n")
            finally:
                self.eval_queue.task_done()

        def stop(self):
            try:
                self.eval_queue.put(None)
            except Exception:
                pass

sessions = []

def tts_yield_text(text):
    for pcm_bytes in stream_tts_pcm_bytes_sync([text]):
        yield (output_sr, bytes_to_float32_mono(pcm_bytes))

def init_session_if_needed(conn_id: str) -> INterviewSession:
    if conn_id in sessions:
        return sessions[conn_id]
    
    company = get_compny()
    candidate = get_candidate()

    if not company or not candidate:
        raise HTTPException(status_code=404, detail="Company or candidate not found")
    
    sess = INterviewSession(session_id=conn_id, comany=company, candidate=candidate)
    
    prompt = build_greeting_and_questions_prompt(company, candidate, variations=10, questions=5)
    ollama_output = run_ollama(prompt)
    greetins, questions = parse_greetings_and_questions(ollama_output)
    if not greetins:
        greetins = [
            "Hello, welcome to the interview. Please introduce yourself briefly.",
            "Hi there! Great to meet you. Could you introduce yourself?",
            "Hi! Glad to meet you. Could you tell me a bit about yourself?",
        ]

    if not questions:
        questions = [
            "Can you walk me through your most relevant experience for this role?",
            "Describe a challenging project you led and your specific contribution.",
            "How do you approach learning new tools or technologies?",
            "Tell me about a time you worked cross-functionally to deliver results.",
            "What about this role and company appeals to you most?",
        ]
    
    sess.greetings = greetins
    sess.questions = questions
    sessions[conn_id] = sess
    return sess

def on_pause_handler(audio, context):
    conn_id = str(context.get("connection_id", "default-conn"))

    sess = init_session_if_needed(conn_id)

    in_sr, in_arr = audio  
    mono = in_arr[0]

    if not sess.started:
        sess.started = True
        greet_text = sess.greetings[min(sess.greet_idx, len(sess.greetings) - 1)]
        sess.greet_idx += 1
        for out in tts_yield_text(greet_text):
            yield out
        if sess.questions:
            q_text = sess.questions[sess.q_idx]
            for out in tts_yield_text(q_text):
                yield out
        return

    uid = str(uuid.uuid4())
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    wav_path = os.path.join(AUDIO_DIR, f"{conn_id}_{ts}_q{sess.q_idx}_answer_{uid}.wav")
    save_wav(wav_path, in_sr, mono)

    transcript = stt_engine.feed_and_transcribe(mono, in_sr) or ""

    if 0 <= sess.q_idx < len(sess.questions):
        cur_q = sess.questions[sess.q_idx]
        sess.answers.append({
            "q_idx": sess.q_idx,
            "question": cur_q,
            "transcript": transcript,
            "audio_path": wav_path,
            "eval_path": None,
        })
        sess.eval_queue.put({
            "q_idx": sess.q_idx,
            "question": cur_q,
            "transcript": transcript,
            "audio_path": wav_path,
        })

    sess.q_idx += 1
    if sess.q_idx < len(sess.questions):
        next_q = sess.questions[sess.q_idx]
        for out in tts_yield_text(next_q):
            yield out
    else:
        closing = "Thank you for your responses. This concludes the interview section for now."
        for out in tts_yield_text(closing):
            yield out
        
stream = Stream(
    name="interview_audio_stream_rezkrypt_beta",
    modality="audio",
    mode="send-receive",
    tags=["interview", "audio"],
    handler=ReplyOnPause(on_pause_handler),
)

stream.mount(app=router, path="/stream")
