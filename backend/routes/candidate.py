from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from backend.prisma import prisma
from pydantic import BaseModel
from datetime import date, datetime, timedelta, time
import os
import google.generativeai as genai

router = APIRouter(
    prefix="/candidate",
    tags=["candidate"],
    responses={404: {"description": "Not found"}},
)

gemini_api_key = os.environ("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

#this is the schema from the prisma schema
# model Candidate {
#   id String @id @default(uuid()) @map("_id")
#   name String
#   email String @unique
#   phone String @unique
#   dateOfBirth DateTime?
#   university String?
#   degree String?
#   major String?
#   graduationDate DateTime?
#   cgpa Float?
#   resume String
#   createdAt DateTime @default(now()) @map("created_at")
#   updatedAt DateTime @updatedAt @map("updated_at")
#   score Score? @relation(fields: [id], references: [candidateId])
# }

# odel Score {
#   id String @id @default(uuid()) @map("_id")
#   candidateId String @unique
#   experience_score Float
#   skills_score Float
#   culture_fit_score Float
#   total_score Float
#   createdAt DateTime @default(now()) @map("created_at")
#   updatedAt DateTime @updatedAt @map("updated_at")

#   candidate Candidate?
# }

class Score(BaseModel):
    experience_score: float
    skills_score: float
    culture_fit_score: float
    total_score: float

class Candidate(BaseModel):
    name: str
    email : str 
    phone: str
    dateOfirth: date
    university: str
    degree: str
    major: str
    graduationDate: date
    cgpa: float
    resume: str
    score: Score = None # so here it is optional, as of now, and when the user gives the resume, and everything the scores will be calculated accordingly

evaluation_score_prompt = """
You will be provided with a person's resume details.

Your task:
1. Identify and count the distinct experiences listed.
2. For each experience, evaluate:
    - Impact Factor: Based on role seniority, achievements, and responsibilities. Scale from 0.5 (low impact) to 2.0 (high impact).
    - Company Weight: Based on employer reputation or brand strength. For example:
        - Top-tier multinational or well-known companies (e.g., Google, Microsoft): 1.5
        - Mid-tier companies: 1.2
        - Startups or lesser-known companies: 1.0
    - Duration Weight: Normalized to years spent in the role (e.g., 1.0 for 1 year, 1.5 for 1.5 years, etc.)

3. Calculate the total experience score by summing over all experiences:

    Score = Σ (Impact Factor × Company Weight × Duration Weight)

Output requirements:
- Return only a single float number representing the total score.
- Do NOT include any explanation, labels, or extra text.
- Round the score to 2 decimal places if necessary.

Example input:

Experience:
- Software Engineer at Google (2 years), led a project that increased efficiency by 20%
- Team Lead at Startup X (1 year), managed a team of 5 and launched new product features

Example output:
6.50
"""

skills_score_prompt = """
You will be provided with a person's resume.

Your task:
1. Evaluate each skill using these criteria:
    - **Match to Typical Requirements**: For each skill relevant to the target job or field, add to the score.
    - **Skill Type Weight**:
        - Hard skills (e.g., Accounting, Project Management, Data Analysis): weight 1.5
        - Soft skills (e.g., Communication, Leadership, Organization): weight 1.0
        - Certifications or licenses (e.g., CPA, PMP): weight 1.7
    - **Proficiency Level** (if specified): weight 2.0 for advanced/expert, 1.5 for intermediate, 1.0 for beginner/basic.
    - **Demonstrated Usage**: If evidence is given (in experience or education) of applying any skill, add 0.5 per such skill.
2. Calculate the total skill score using this formula:

    Score = Σ (Skill_Match × Skill_Type_Weight × Proficiency_Weight + Demonstrated_Usage_Weight)

3. If a job description or ideal skill list is provided, optionally normalize by dividing the total by the number of required skills; if not, just sum.

Output requirements:
- Return only a single float value representing the skills score, rounded to two decimal places.
- Do NOT include any explanation, label, or extra text.

Example input:

Skills:
- Project Management (Advanced)
- Teamwork
- Excel (Intermediate)
- CPA Certified

Example output:
6.20
"""
    
culture_fit_score_prompt = """
You will be provided with a candidate's profile, with emphasis on experiences, values, and behavior descriptions.

Your task:
1. Evaluate the candidate's cultural alignment using these dimensions (scoring each 1 to 5):
    - **Core Values Match:** Alignment of candidate’s stated/observable values with those of the organization.
    - **Work Style Compatibility:** Evidence the person’s communication, collaboration, and work approach matches org/team culture.
    - **Adaptability and Growth Mindset:** Ability to handle change, learn, and support evolving goals.
    - **Interpersonal & Team Fit:** Indications they thrive in the company's interpersonal/team setting.
    - **Motivation & Attitude:** Motivation and purpose are compatible with the role and organization.

2. For each dimension, apply this scale:
    - 1 = Very Poor Match
    - 2 = Limited Match
    - 3 = Moderate Match
    - 4 = Good Match
    - 5 = Excellent Match

3. Calculate the average of all five scores, and then normalize to produce a final culture fit score using this formula:

    Final Score = (Sum of all category scores) / 5

- Return ONLY the final float score, rounded to two decimal places.
- No explanations, labels, or extra text.

Example input:
- Values: Transparency, innovation, customer focus
- Work style: Collaborative, proactive communicator
- Attitude: Seeks growth, enjoys diverse teams

Example output:
4.20
"""

async def get_score(candidate: Candidate):
    if(not gemini_api_key):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set")
    
    base_prompt = f"This is the resume: \n\n" + {candidate.resume} + "\n\n"
    
    evaluation_score = await float(genai.GenerativeModel("gemini-2.5-flash-lite").generate_content(contents=base_prompt+evaluation_score_prompt, stream=True).text)
    culture_fit_score = await float(genai.GenerativeModel("gemini-2.5-flash-lite").generate_content(contents=base_prompt+culture_fit_score_prompt, stream=True).text)
    skills_score = await float(genai.GenerativeModel("gemini-2.5-flash-lite").generate_content(contents=base_prompt+skills_score_prompt, stream=True).text)
    #so need to decide the weightage for the scores
    #so as of me, experince matters more so 0.5, and then skills will be 0.3 and culture fit will be 0.2
    final_score = (evaluation_score * 0.5) + (skills_score * 0.3) + (culture_fit_score * 0.2)
    return round(final_score, 2)
    
@router.get("/")
async def candidate_welcome():
    return {"message": "welcome to the Candidate side API"}

@router.get("/error")
async def candidate_error():
    raise HTTPException(status_code=500, detail="This is a candidate error")

@router.get("/prisma-test")
async def prisma_test():
    try:
        candidates = await prisma.candidate.find_many()
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#so as of now im gonna block each user 10 mins, so accordingly need to mainatina a quue, and add the candidates intervieTimes, and then send them the mail accordingly, and doing this as the background taks values more, as we already added the score, now adding this too adn whenver the candidate is registers, i can do them accordingly

interview_slot_time = 10
interview_start_time = time(10, 0) # this ensures the interviews start from morning 10 am
# interview_end_time = time(18, 0)

async def schedule_interview(cand: Candidate):
    scheduled_count = await prisma.candidate.count(where={"interviewTime": {"not": None}})

    today = datetime.now().date()
    interview_datetime = datetime.combine(today, interview_start_time) + timedelta(minutes=scheduled_count * interview_slot_time)

    await prisma.candidate.update(
        where={"email": cand.email},
        data={
            "interviewTime": interview_datetime,
            "interviewSlotIndex": scheduled_count + 1,
        },
    )

    return interview_datetime
    
@router.post("/register")
async def register_candidate(candidate: Candidate, background_tasks: BackgroundTasks):
    try:
        cand = await prisma.candidate.create(
            data={
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone,
                "dateOfBirth": candidate.dateOfirth,
                "university": candidate.university,
                "degree": candidate.degree,
                "major": candidate.major,
                "graduationDate": candidate.graduationDate,
                "cgpa": candidate.cgpa,
                "resume": candidate.resume,
            }
        )
        score = background_tasks.add_task(get_score, candidate)
        await prisma.candidate.update(
            where={"id": cand.id},
            data={"score": score}
        )
        print(f"Score: {score}")
        interview_datetime = background_tasks.add_task(schedule_interview, cand)
        print(f"Interview Time: {interview_datetime}")
        return {"message": "Candidate registered successfully, score and interview time added", "candidate": cand, "Score" : score, "Interview Time": interview_datetime}
    except Exception as e:
        print(f"Error creating candidate: {e}")
        return {"message": "Error creating candidate"}
    
#so when the user now comes in the interview time, need to validate him, just taking his email, and then check if the interview time is set and now is the time for his interview

@router.post("/interview")
async def validate_candidate(email: str):
    try:
        cand = await prisma.candidate.find_first(where={"email": email})
        if cand is None:
            return {"message": "Candidate not found"}
        if cand.interviewTime is None:
            return {"message": "Interview time not set"}
        if cand.interviewTime > datetime.now():
            return {"message": "Interview not yet scheduled"}
        if cand.interviewTime < datetime.now():
            return {"message": "Interview already passed, sorry"}
        return {"message": "Candidate came at the right time for interview"}
    except Exception as e:
        print(f"Error validating candidate: {e}")
        return {"message": "Error validating candidate"}


