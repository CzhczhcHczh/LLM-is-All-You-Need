"""
Database models and operations for Job Planner Assistant.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from config import settings

# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    phone = Column(String(20))
    target_position = Column(String(255))
    profile_data = Column(JSON)  # Store user profile as JSON
    created_at = Column(DateTime, default=datetime.utcnow)


class Company(Base):
    """Company model."""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    industry = Column(String(255))
    location = Column(String(255))
    website = Column(String(500))
    description = Column(Text)
    search_query = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


class JobPosting(Base):
    """Job posting model."""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    title = Column(String(255), index=True)
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(JSON)  # List of requirements (stored as JSON)
    skills_required = Column(JSON)  # List of skills (stored as JSON)
    salary_range = Column(String(100))
    application_url = Column(String(1000))
    source_url = Column(String(1000))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    search_query = Column(String(255))  # 搜索关键词


class Resume(Base):
    """Resume model."""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    job_posting_id = Column(Integer)
    title = Column(String(255))
    content = Column(JSON)  # Resume content as structured JSON
    version = Column(Integer, default=1)
    is_final = Column(Boolean, default=False)
    model_used = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class HRFeedback(Base):
    """HR feedback model."""
    __tablename__ = "hr_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    job_posting_id = Column(Integer)
    feedback_round = Column(Integer, default=1)
    overall_score = Column(Float)
    feedback_content = Column(JSON)  # Detailed feedback as JSON
    passes_screening = Column(Boolean)
    suggestions = Column(JSON)  # List of suggestions
    model_used = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class Interview(Base):
    """Interview model."""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    job_posting_id = Column(Integer)
    resume_id = Column(Integer)
    interview_type = Column(String(100))
    proposed_times = Column(JSON)  # List of proposed time slots
    scheduled_time = Column(DateTime)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(500))
    interviewer_info = Column(JSON)  # Interviewer details
    status = Column(String(100), default="invited")
    match_score = Column(Float)
    priority_rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Schedule(Base):
    """Schedule model."""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    schedule_name = Column(String(255))
    scheduled_interviews = Column(JSON)  # List of scheduled interviews
    optimization_result = Column(JSON)  # Optimization details
    agent_discussions = Column(JSON)  # Multi-agent discussion logs
    final_reasoning = Column(Text)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models for API
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    target_position: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None


class JobPostingCreate(BaseModel):
    company_id: int
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    skills: Optional[List[str]] = None  # 兼容搜索结果格式
    salary_range: Optional[str] = None
    application_url: Optional[str] = None
    source_url: Optional[str] = None
    search_query: Optional[str] = None
    job_title: Optional[str] = None  # 兼容搜索结果中的job_title字段
    company_name: Optional[str] = None  # 兼容搜索结果中的公司名称


class ResumeCreate(BaseModel):
    user_id: int
    job_posting_id: int
    title: str
    content: Dict[str, Any]


class HRFeedbackCreate(BaseModel):
    resume_id: int
    job_posting_id: int
    feedback_round: int = 1
    overall_score: Optional[float] = None
    feedback_content: Dict[str, Any]
    passes_screening: Optional[bool] = None
    suggestions: Optional[List[str]] = None


class InterviewCreate(BaseModel):
    user_id: int
    job_posting_id: int
    resume_id: int
    interview_type: Optional[str] = None
    proposed_times: Optional[List[str]] = None
    duration_minutes: int = 60
    location: Optional[str] = None
    interviewer_info: Optional[Dict[str, Any]] = None


class ScheduleCreate(BaseModel):
    user_id: int
    schedule_name: str
    scheduled_interviews: List[Dict[str, Any]]
    optimization_result: Optional[Dict[str, Any]] = None
    agent_discussions: Optional[List[Dict[str, Any]]] = None
    final_reasoning: Optional[str] = None


# Database operations
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


# CRUD operations
def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_job_posting(db: Session, job: JobPostingCreate):
    """Create a new job posting."""
    job_dict = job.dict()
    
    # 确保列表类型数据正确存储为JSON
    if isinstance(job_dict.get("requirements"), str) and job_dict.get("requirements"):
        try:
            # 如果是字符串形式的逗号分隔列表，转换回列表
            job_dict["requirements"] = job_dict["requirements"].split(", ")
        except:
            pass
            
    if isinstance(job_dict.get("skills_required"), str) and job_dict.get("skills_required"):
        try:
            # 如果是字符串形式的逗号分隔列表，转换回列表
            job_dict["skills_required"] = job_dict["skills_required"].split(", ")
        except:
            pass
    
    db_job = JobPosting(**job_dict)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job_postings(db: Session, skip: int = 0, limit: int = 100):
    """Get job postings."""
    return db.query(JobPosting).filter(JobPosting.is_active == True).offset(skip).limit(limit).all()


def create_resume(db: Session, resume: ResumeCreate):
    """Create a new resume."""
    db_resume = Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def get_resumes_by_user(db: Session, user_id: int):
    """Get resumes by user ID."""
    return db.query(Resume).filter(Resume.user_id == user_id).all()


def create_hr_feedback(db: Session, feedback: HRFeedbackCreate):
    """Create HR feedback."""
    db_feedback = HRFeedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def create_interview(db: Session, interview: InterviewCreate):
    """Create an interview."""
    db_interview = Interview(**interview.dict())
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview


def get_interviews_by_user(db: Session, user_id: int):
    """Get interviews by user ID."""
    return db.query(Interview).filter(Interview.user_id == user_id).all()


def create_schedule(db: Session, schedule: ScheduleCreate):
    """Create a schedule."""
    db_schedule = Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

