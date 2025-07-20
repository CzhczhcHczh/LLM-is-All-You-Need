"""
API routes for Job Planner Assistant.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger

from database import get_db, create_user, get_user, UserCreate
from agents import search_agent, phase2_agent, phase3_agent, phase4_agent

# Create main router
router = APIRouter()

# Request/Response models
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Any
    timestamp: datetime = datetime.now()

class SearchRequest(BaseModel):
    search_query: str
    location: Optional[str] = None
    max_results: int = 20

class ResumeGenerationRequest(BaseModel):
    user_profile: Dict[str, Any]
    job_posting: Dict[str, Any]
    
class MultipleJobsResumeRequest(BaseModel):
    user_profile: Dict[str, Any]
    job_postings: List[Dict[str, Any]]

class HRReviewRequest(BaseModel):
    resume_content: Dict[str, Any]
    job_posting: Dict[str, Any]
    hr_persona: str = "experienced"

class SchedulingRequest(BaseModel):
    interviews: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None


# User Management APIs
@router.post("/users", response_model=BaseResponse)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        db_user = create_user(db, user)
        return BaseResponse(
            success=True,
            message="User created successfully",
            data={
                "user_id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/users/{user_id}", response_model=BaseResponse)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    try:
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return BaseResponse(
            success=True,
            message="User retrieved successfully",
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "target_position": user.target_position,
                "profile_data": user.profile_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


# Phase 1 APIs - Job Search
@router.post("/phase1/search", response_model=BaseResponse)
async def search_jobs(request: SearchRequest):
    """Search for job postings."""
    try:
        logger.info(f"Starting job search for query: '{request.search_query}', location: '{request.location}', max_results: {request.max_results}")
        
        result = search_agent.search_jobs(
            search_query=request.search_query,
            location=request.location,
            max_results=request.max_results
        )
        
        if not result["success"]:
            logger.warning(f"Search was unsuccessful: {result['message']}")
            
        logger.info(f"Search completed: found {len(result['data'].get('jobs', []))} jobs")
        
        # 确保返回数据格式一致性
        if "data" not in result or not isinstance(result["data"], dict):
            result["data"] = {"jobs": [], "companies": [], "search_query": request.search_query}
            
        if "jobs" not in result["data"]:
            result["data"]["jobs"] = []
            
        if "companies" not in result["data"]:
            result["data"]["companies"] = []
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error in job search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job search failed: {str(e)}"
        )

@router.post("/phase1/similar", response_model=BaseResponse)
async def find_similar_jobs(user_profile: Dict[str, Any], n_results: int = 5):
    """Find similar jobs based on user profile."""
    try:
        similar_jobs = search_agent.get_similar_jobs(user_profile, n_results)
        
        return BaseResponse(
            success=True,
            message=f"Found {len(similar_jobs)} similar jobs",
            data={"similar_jobs": similar_jobs}
        )
        
    except Exception as e:
        logger.error(f"Error finding similar jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar jobs"
        )


# Phase 2 APIs - Resume Generation
@router.post("/phase2/generate", response_model=BaseResponse)
async def generate_resume(request: ResumeGenerationRequest):
    """Generate a customized resume."""
    try:
        result = phase2_agent.generate_resume(
            user_profile=request.user_profile,
            job_posting=request.job_posting
        )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error generating resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume generation failed"
        )

@router.post("/phase2/optimize", response_model=BaseResponse)
async def optimize_resume(resume_content: Dict[str, Any], feedback: Dict[str, Any]):
    """Optimize resume based on feedback."""
    try:
        result = phase2_agent.optimize_resume(resume_content, feedback)
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume optimization failed"
        )

@router.post("/phase2/generate-multi", response_model=BaseResponse)
async def generate_resume_multiple_jobs(request: MultipleJobsResumeRequest):
    """Generate a customized resume based on multiple job postings."""
    try:
        if not request.job_postings or len(request.job_postings) == 0:
            raise ValueError("No job postings provided")
            
        # 如果只有一个职位，使用原来的方法
        if len(request.job_postings) == 1:
            result = phase2_agent.generate_resume(
                user_profile=request.user_profile,
                job_posting=request.job_postings[0]
            )
        else:
            # 多职位场景，调用专门的多职位简历生成方法
            # 注意：您可能需要在phase2_agent中实现这个方法
            result = phase2_agent.generate_resume_multiple_jobs(
                user_profile=request.user_profile,
                job_postings=request.job_postings
            )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error generating multi-job resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-job resume generation failed: {str(e)}"
        )


# Phase 3 APIs - HR Simulation
@router.post("/phase3/review", response_model=BaseResponse)
async def hr_review(request: HRReviewRequest):
    """Simulate HR review of resume."""
    try:
        result = phase3_agent.simulate_hr_review(
            resume_content=request.resume_content,
            job_posting=request.job_posting,
            hr_persona=request.hr_persona
        )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error in HR review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="HR review failed"
        )

@router.post("/phase3/iterative", response_model=BaseResponse)
async def iterative_feedback(
    resume_content: Dict[str, Any], 
    job_posting: Dict[str, Any],
    max_rounds: int = 3
):
    """Get iterative feedback for resume improvement."""
    try:
        result = phase3_agent.iterative_feedback(
            resume_content=resume_content,
            job_posting=job_posting,
            round_number=1,
            max_rounds=max_rounds
        )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error in iterative feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Iterative feedback failed"
        )


# Phase 4 APIs - Interview Scheduling
@router.post("/phase4/discuss", response_model=BaseResponse)
async def multi_agent_discussion(request: SchedulingRequest):
    """Conduct multi-agent discussion for scheduling."""
    try:
        result = phase4_agent.multi_agent_discussion(
            interviews=request.interviews,
            user_preferences=request.user_preferences
        )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error in multi-agent discussion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multi-agent discussion failed"
        )

@router.post("/phase4/optimize", response_model=BaseResponse)
async def optimize_schedule(request: SchedulingRequest):
    """Optimize interview schedule."""
    try:
        result = phase4_agent.optimize_schedule(
            interviews=request.interviews,
            constraints=request.constraints or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"Error optimizing schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schedule optimization failed"
        )


# Health check and utility APIs
@router.get("/health", response_model=BaseResponse)
async def health_check():
    """Health check endpoint."""
    return BaseResponse(
        success=True,
        message="API is healthy",
        data={"status": "ok", "version": "1.0.0"}
    )

@router.get("/models", response_model=BaseResponse)
async def get_available_models():
    """Get available AI models."""
    from config import settings
    
    return BaseResponse(
        success=True,
        message="Available models retrieved",
        data={
            "phase1_model": settings.phase1_model,
            "phase2_model": settings.phase2_model,
            "phase3_model": settings.phase3_model,
            "phase4_models": settings.phase4_models_list
        }
    )


# Demo/Test APIs
@router.post("/demo/full-workflow", response_model=BaseResponse)
async def demo_full_workflow(
    search_query: str,
    user_profile: Dict[str, Any],
    max_jobs: int = 3
):
    """Demo endpoint to run the full workflow."""
    try:
        workflow_results = {}
        
        # Phase 1: Search jobs
        logger.info("Demo: Starting Phase 1 - Job Search")
        search_result = search_agent.search_jobs(search_query, max_results=max_jobs)
        workflow_results["phase1"] = search_result
        
        if not search_result["success"] or not search_result["data"]["jobs"]:
            return BaseResponse(
                success=False,
                message="Demo failed: No jobs found",
                data=workflow_results
            )
        
        # Phase 2: Generate resume for first job
        logger.info("Demo: Starting Phase 2 - Resume Generation")
        first_job = search_result["data"]["jobs"][0]
        resume_result = phase2_agent.generate_resume(user_profile, first_job)
        workflow_results["phase2"] = resume_result
        
        if not resume_result["success"]:
            return BaseResponse(
                success=False,
                message="Demo failed: Resume generation failed",
                data=workflow_results
            )
        
        # Phase 3: HR Review
        logger.info("Demo: Starting Phase 3 - HR Review")
        hr_result = phase3_agent.simulate_hr_review(
            resume_result["data"]["content"],
            first_job,
            "experienced"
        )
        workflow_results["phase3"] = hr_result
        
        # Phase 4: Create mock interview and schedule
        logger.info("Demo: Starting Phase 4 - Scheduling")
        if hr_result["success"] and hr_result["data"]["feedback"].get("passes_initial_screening"):
            mock_interviews = [{
                "id": 1,
                "company_name": first_job.get("company_name", "Demo Company"),
                "position": first_job.get("job_title", "Demo Position"),
                "match_score": hr_result["data"]["feedback"].get("overall_score", 75),
                "proposed_times": ["2024-01-20 14:00", "2024-01-21 10:00"]
            }]
            
            schedule_result = phase4_agent.multi_agent_discussion(
                mock_interviews,
                {"preferred_time": "afternoon", "max_interviews_per_day": 2}
            )
            workflow_results["phase4"] = schedule_result
        
        return BaseResponse(
            success=True,
            message="Demo workflow completed successfully",
            data=workflow_results
        )
        
    except Exception as e:
        logger.error(f"Error in demo workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo workflow failed"
        )

