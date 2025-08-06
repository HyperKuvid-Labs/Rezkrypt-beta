from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.prisma import prisma
from datetime import date

router = APIRouter(
    prefix="/companies",
    title="Company API",
    description="A simple FastAPI Company API",
    version="0.0.1",
)

# this is the schema from the prisma schema
# model Company {
#   id String @id @default(uuid()) @map("_id")
#   name String
#   contactPerson String
#   email String @unique
#   phone String @unique
#   website String?
#   industry String?
#   companySize String?
#   location String?
#   jobTitle String?
#   department String?
#   jobType String?
#   experienceLevel String?
#   salary String?
#   skills String?
#   jobDescription String?
#   requirements String?
#   benefits String?
#   applicationDeadline DateTime?
#   createdAt DateTime @default(now()) @map("created_at")
#   updatedAt DateTime @updatedAt @map("updated_at")
# }

class Company(BaseModel):
    name : str
    contactPerson : str
    email : str
    phone : str
    website : str | None
    industry : str | None
    companySize : str | None
    location : str | None
    jobTitle : str 
    department : str
    jobType : str
    experienceLevel : str | None
    salary : str | None
    skills : str | None
    jobDescription : str | None
    requirements : str | None
    benefits : str | None
    applicationDeadline : date 


@router.get("/")
async def company_welcome():
    return {"message": "welcome to the Company side API"}

@router.get("/error")
async def candidate_error():
    raise HTTPException(status_code=500, detail="This is a comapny side error")

@router.get("/prisma-test")
async def prisma_test():
    try:
        candidates = await prisma.company.find_many()
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/register")
async def register_company(company: Company):
    try:
        comp = await prisma.company.create(
            data={
                "name": company.name,
                "contactPerson": company.contactPerson,
                "email": company.email,
                "phone": company.phone,
                "website": company.website,
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
                "applicationDeadline": company.applicationDeadline,
            }
        )
        return {"message": "Company registered successfully", "company": comp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


