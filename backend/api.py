"""
API routes for Job Planner Assistant.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger
import time

from database import get_db, create_user, get_user, UserCreate
from agents import search_agent, phase2_agent, phase3_agent, phase4_agent
from services import llm_service
from agents import Phase3HRAgent

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

class EnhancedUserProfile(BaseModel):
    """增强的用户个人资料模型"""
    # 基本信息
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    target_position: Optional[str] = None
    
    # 个人简介
    summary: Optional[str] = None
    
    # 技能
    skills: List[str] = []
    
    # 工作经验
    experience: List[Dict[str, Any]] = []
    
    # 教育背景
    education: List[Dict[str, Any]] = []
    
    # 项目经验
    projects: List[Dict[str, Any]] = []
    
    # 其他信息
    languages: Optional[str] = None
    certifications: Optional[str] = None
    special_requirements: Optional[str] = None
    
    # 新增字段
    career_objective: Optional[str] = None  # 职业目标
    years_of_experience: Optional[int] = None  # 工作年限
    salary_expectation: Optional[str] = None  # 期望薪资
    availability: Optional[str] = None  # 到岗时间
    preferred_work_type: Optional[str] = None  # 工作类型偏好（远程/现场/混合）

class EnhancedJobPosting(BaseModel):
    """增强的职位信息模型"""
    job_title: str
    company_name: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: List[str] = []
    skills: List[str] = []
    description: Optional[str] = None
    source_url: Optional[str] = None
    
    # 新增字段
    company_size: Optional[str] = None  # 公司规模
    industry: Optional[str] = None  # 行业
    company_culture: Optional[str] = None  # 公司文化
    benefits: List[str] = []  # 福利待遇
    work_type: Optional[str] = None  # 工作类型
    experience_level: Optional[str] = None  # 经验要求
    education_requirement: Optional[str] = None  # 学历要求

class ResumeGenerationRequest(BaseModel):
    user_profile: EnhancedUserProfile
    job_posting: EnhancedJobPosting
    customization_level: Optional[str] = "high"  # 定制化程度: low, medium, high
    focus_areas: List[str] = []  # 重点突出领域
    template_style: Optional[str] = "professional"  # 模板风格

class HRReviewRequest(BaseModel):
    resume_content: Dict[str, Any]
    job_posting: EnhancedJobPosting
    hr_persona: str = "experienced"
    review_depth: Optional[str] = "detailed"  # 评估深度

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
        similar_jobs = search_agent.search_jobs(user_profile, n_results)
        
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
    """生成个性化简历"""
    try:
        logger.info(f"Generating resume for {request.user_profile.full_name} - {request.job_posting.job_title}")
        
        # 转换为字典格式
        user_profile_dict = request.user_profile.dict()
        job_posting_dict = request.job_posting.dict()
        
        # 添加额外的定制化参数
        generation_params = {
            "customization_level": request.customization_level,
            "focus_areas": request.focus_areas,
            "template_style": request.template_style
        }
        
        # 调用增强的简历生成Agent
        result = phase2_agent.generate_enhanced_resume(
            user_profile_dict, 
            job_posting_dict,
            generation_params
        )
        
        if result["success"]:
            return BaseResponse(
                success=True,
                message="个性化简历生成成功",
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "简历生成失败")
            )
            
    except Exception as e:
        logger.error(f"Error in resume generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"简历生成失败: {str(e)}"
        )

@router.post("/phase2/optimize", response_model=BaseResponse)
async def optimize_resume(request: dict):
    """基于HR反馈优化简历内容"""
    try:
        logger.info("Starting resume optimization request")
        
        resume_content = request.get("resume_content")
        feedback = request.get("feedback")
        optimization_focus = request.get("optimization_focus", [])
        
        logger.info(f"Request data - resume_content exists: {resume_content is not None}")
        logger.info(f"Request data - feedback exists: {feedback is not None}")
        logger.info(f"Request data - optimization_focus: {optimization_focus}")
        
        if not resume_content:
            logger.error("Missing resume_content in request")
            raise HTTPException(
                status_code=400,
                detail="resume_content is required"
            )
        
        if not feedback:
            logger.error("Missing feedback in request")
            raise HTTPException(
                status_code=400,
                detail="feedback is required"
            )
        
        logger.info("Calling phase2_agent.optimize_resume_content")
        result = phase2_agent.optimize_resume_content(
            resume_content, 
            feedback, 
            optimization_focus
        )
        
        logger.info(f"Agent result - success: {result.get('success', False)}")
        logger.info(f"Agent result - message: {result.get('message', 'No message')}")
        
        if result.get("success", False):
            return BaseResponse(
                success=True,
                message=result.get("message", "简历优化完成"),
                data=result.get("data", result)
            )
        else:
            logger.error(f"Agent optimization failed: {result.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "简历优化失败")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"简历优化失败: {str(e)}"
        )

@router.post("/phase2/analyze-match", response_model=BaseResponse)
async def analyze_job_match(request: dict):
    """分析用户与职位的匹配度"""
    try:
        user_profile = request.get("user_profile")
        job_posting = request.get("job_posting")
        
        if not user_profile or not job_posting:
            raise HTTPException(
                status_code=400,
                detail="Missing user_profile or job_posting"
            )
        
        result = phase2_agent.analyze_job_user_match(
            user_profile,
            job_posting
        )
        
        return BaseResponse(
            success=True,
            message="匹配度分析完成",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error analyzing job match: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"匹配度分析失败: {str(e)}"
        )


# Phase 3 APIs - HR Simulation
@router.post("/phase3/hr-review", response_model=BaseResponse)
async def hr_review(request: Dict[str, Any]):
    """HR评估接口"""
    try:
        # logger.info(f"Starting HR review with persona: {request.hr_persona}")
        resume_content = request.get("resume_content")
        job_posting = request.get("job_posting") 
        hr_persona = request.get("hr_persona", "experienced")        
        # # Call Phase3HRAgent for detailed evaluation
        # # Convert Pydantic models to dictionaries
        # resume_dict = request.resume_content
        # job_posting_dict = request.job_posting.dict() if hasattr(request.job_posting, 'dict') else request.job_posting
        logger.info(f"收到HR评估请求: hr_persona={hr_persona}")        
        result = phase3_agent.simulate_hr_review(
            resume_content=resume_content,
            job_posting=job_posting,
            hr_persona=hr_persona
        )
        
        
        return BaseResponse(
            success=result["success"],
            message=result["message"], 
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"HR评估异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HR评估失败: {str(e)}"
        )

async def generate_improvement_plan(resume_content: Dict[str, Any], job_posting: Dict[str, Any], 
                                  feedback: Dict[str, Any], hr_persona: str) -> Dict[str, Any]:
    """Generate detailed improvement plan based on HR feedback."""
    try:
        # 获取HR人设配置
        persona_config = phase3_agent.HR_PERSONAS.get(hr_persona, phase3_agent.HR_PERSONAS["experienced"])
        
        improvement_prompt = f"""
        基于以下HR反馈，为候选人制定详细的简历改进计划：

        ## HR反馈信息：
        HR类型：{persona_config['name']} - {persona_config['description']}
        总体评分：{feedback.get('overall_score', 0)}/100
        是否通过初筛：{'否' if not feedback.get('passes_initial_screening', False) else '是'}
        
        详细评分：
        {json.dumps(feedback.get('detailed_scores', {}), ensure_ascii=False, indent=2)}
        
        主要优势：
        {json.dumps(feedback.get('strengths', []), ensure_ascii=False, indent=2)}
        
        主要不足：
        {json.dumps(feedback.get('weaknesses', []), ensure_ascii=False, indent=2)}
        
        HR建议：
        {json.dumps(feedback.get('improvement_suggestions', []), ensure_ascii=False, indent=2)}

        ## 目标职位信息：
        {json.dumps(job_posting, ensure_ascii=False, indent=2)}

        ## 当前简历：
        {json.dumps(resume_content, ensure_ascii=False, indent=2)}

        请制定一个详细的改进计划，返回JSON格式：
        {{
            "improvement_priority": "high",
            "target_score": 85,
            "estimated_improvement": 20,
            "immediate_actions": [
                {{
                    "action": "具体改进行动",
                    "section": "简历部分",
                    "priority": "high",
                    "expected_impact": "预期影响描述",
                    "implementation_steps": ["步骤1", "步骤2"],
                    "before_example": "改进前示例",
                    "after_example": "改进后示例"
                }}
            ],
            "skills_to_add": [
                {{
                    "skill": "技能名称",
                    "reason": "添加理由",
                    "learning_resources": ["学习资源1"],
                    "certification_options": ["认证选项1"]
                }}
            ],
            "next_steps": ["下一步行动1", "下一步行动2"]
        }}
        """
        
        improvement_result = llm_service.call_phase2_model(improvement_prompt)
        
        # Parse JSON result
        json_match = re.search(r'\{.*\}', improvement_result, re.DOTALL)
        if json_match:
            improvement_plan = json.loads(json_match.group())
            return improvement_plan
        else:
            return {"error": "Failed to parse improvement plan", "raw_result": improvement_result}
            
    except Exception as e:
        logger.error(f"Error generating improvement plan: {e}")
        return {"error": str(e)}

@router.post("/phase3/apply-improvements", response_model=BaseResponse)
async def apply_improvements(
    resume_content: Dict[str, Any], 
    improvement_plan: Dict[str, Any],
    selected_improvements: List[str] = None
):
    """Apply selected improvements to resume."""
    try:
        # If no specific improvements selected, apply all high priority ones
        if not selected_improvements:
            selected_improvements = [
                action["action"] for action in improvement_plan.get("immediate_actions", [])
                if action.get("priority") == "high"
            ]
        
        apply_prompt = f"""
        请根据以下改进计划，对简历进行优化：

        ## 当前简历：
        {json.dumps(resume_content, ensure_ascii=False, indent=2)}

        ## 改进计划：
        {json.dumps(improvement_plan, ensure_ascii=False, indent=2)}

        ## 要应用的改进：
        {json.dumps(selected_improvements, ensure_ascii=False, indent=2)}

        请返回优化后的完整简历JSON，并说明具体做了哪些改进：
        {{
            "optimized_resume": {{
                "personal_info": {{}},
                "summary": "",
                "experience": [],
                "education": [],
                "skills": [],
                "projects": []
            }},
            "improvements_applied": [
                {{
                    "section": "改进的部分",
                    "change_description": "具体改进描述",
                    "before": "改进前内容",
                    "after": "改进后内容"
                }}
            ],
            "optimization_summary": "整体优化总结"
        }}
        """
        
        optimization_result = llm_service.call_phase2_model(apply_prompt)
        
        # Parse JSON result
        import re
        json_match = re.search(r'\{.*\}', optimization_result, re.DOTALL)
        if json_match:
            optimized_data = json.loads(json_match.group())
            
            return BaseResponse(
                success=True,
                message="Resume optimization completed",
                data=optimized_data
            )
        else:
            return BaseResponse(
                success=False,
                message="Failed to parse optimization result",
                data={"raw_result": optimization_result}
            )
            
    except Exception as e:
        logger.error(f"Error applying improvements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume optimization failed"
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

@router.post("/phase4/multi-llm-recommendation", response_model=BaseResponse)
async def multi_llm_recommendation(request: dict):
    """Multi-LLM job recommendation analysis."""
    try:
        personal_info = request.get("personal_info", {})
        jobs = request.get("jobs", [])
        
        if not jobs:
            raise HTTPException(
                status_code=400,
                detail="职位列表不能为空"
            )
        
        result = phase4_agent.multi_llm_recommendation(personal_info, jobs)
        
        return BaseResponse(
            success=True,
            message="多LLM推荐分析完成",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error in multi-LLM recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"多LLM推荐分析失败: {str(e)}"
        )

@router.post("/phase4/multi-agent-discussion", response_model=BaseResponse)
async def multi_agent_discussion_complete(request: SchedulingRequest):
    """Complete multi-agent discussion workflow including ranking and scheduling."""
    try:
        # 调用完整的 Phase4 工作流程
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
        logger.error(f"Error in complete multi-agent discussion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完整多Agent讨论失败: {str(e)}"
        )

# Health check and utility APIs
@router.get("/health", response_model=BaseResponse)
async def health_check():
    """健康检查"""
    return BaseResponse(
        success=True,
        message="API服务正常运行",
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
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
        resume_result = phase2_agent.generate_enhanced_resume(
            user_profile, 
            first_job, 
            {}  # generation_params
        )
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

# 在 api.py 中添加批量生成接口
@router.post("/phase2/generate-batch", response_model=BaseResponse)
async def generate_batch_resumes(request: dict):
    """批量生成多份简历"""
    try:
        user_profile = request.get("user_profile")
        job_postings = request.get("job_postings", [])
        
        if not user_profile or not job_postings:
            raise HTTPException(
                status_code=400,
                detail="Missing user_profile or job_postings"
            )
        
        results = []
        
        for i, job_posting in enumerate(job_postings):
            try:
                logger.info(f"Generating resume {i+1}/{len(job_postings)} for {job_posting.get('company_name', 'Unknown')}")
                
                result = phase2_agent.generate_enhanced_resume(
                    user_profile, 
                    job_posting,
                    {}
                )
                
                results.append({
                    "job_index": i,
                    "job_title": job_posting.get("job_title"),
                    "company_name": job_posting.get("company_name"),
                    "success": result["success"],
                    "data": result["data"] if result["success"] else None,
                    "error": result.get("message") if not result["success"] else None
                })
                
            except Exception as e:
                logger.error(f"Error generating resume for job {i}: {e}")
                results.append({
                    "job_index": i,
                    "job_title": job_posting.get("job_title"),
                    "company_name": job_posting.get("company_name"),
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return BaseResponse(
            success=True,
            message=f"批量生成完成，成功 {success_count}/{len(job_postings)} 份简历",
            data={
                "results": results,
                "total_jobs": len(job_postings),
                "success_count": success_count,
                "batch_id": f"batch_{int(time.time())}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in batch resume generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"批量生成简历失败: {str(e)}"
        )

from fastapi import Body

@router.post("/phase3/self-introduction", response_model=BaseResponse)
async def generate_self_introduction(
    strengths: List[str] = Body(..., embed=True),
    weaknesses: List[str] = Body(..., embed=True),
    min_length: int = Body(300, embed=True),
    resume_content: Optional[Dict[str, Any]] = Body(None, embed=True),
    job_posting: Optional[Dict[str, Any]] = Body(None, embed=True),
    hr_persona: Optional[str] = Body("experienced", embed=True),
    hr_feedback: Optional[Dict[str, Any]] = Body(None, embed=True)
):
    """
    根据简历内容、HR评估结果和HR性格生成个性化自我介绍
    """
    try:
        logger.info(f"生成个性化自我介绍请求 - HR类型: {hr_persona}, 优势: {strengths}, 劣势: {weaknesses}")
        
        # 验证输入参数
        if not strengths and not weaknesses:
            return BaseResponse(
                success=False,
                message="请提供至少一个优势或劣势信息",
                data={}
            )
        
        # 调用增强版自我介绍生成
        intro = Phase3HRAgent.generate_self_introduction(
            strengths=strengths, 
            weaknesses=weaknesses, 
            min_length=min_length,
            resume_content=resume_content,
            job_posting=job_posting,
            hr_persona=hr_persona,
            hr_feedback=hr_feedback
        )
        
        logger.info(f"个性化自我介绍生成成功，长度: {len(intro)}")
        
        return BaseResponse(
            success=True,
            message="个性化自我介绍生成成功",
            data={
                "self_introduction": intro,
                "length": len(intro),
                "personalization": {
                    "hr_persona": hr_persona,
                    "based_on_resume": resume_content is not None,
                    "based_on_job": job_posting is not None,
                    "based_on_feedback": hr_feedback is not None
                },
                "generation_context": {
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "target_job": job_posting.get('job_title') if job_posting else None,
                    "target_company": job_posting.get('company_name') if job_posting else None
                }
            }
        )
    except Exception as e:
        logger.error(f"生成自我介绍失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"自我介绍生成失败: {str(e)}"
        )

@router.post("/phase3/generate-interview-questions", response_model=BaseResponse)
async def generate_interview_questions(
    hr_persona: str = Body(..., embed=True),
    resume_content: Dict[str, Any] = Body(..., embed=True),
    job_posting: Dict[str, Any] = Body(..., embed=True),
    num_questions: int = Body(3, embed=True)
):
    """
    根据HR人设和用户简历生成面试问题
    """
    try:
        logger.info(f"生成面试问题请求 - HR类型: {hr_persona}, 问题数量: {num_questions}")
        
        # 验证输入参数
        if not hr_persona:
            return BaseResponse(
                success=False,
                message="请选择HR类型",
                data={}
            )
        
        if not resume_content:
            return BaseResponse(
                success=False,
                message="请提供简历内容",
                data={}
            )
        
        # 调用agent生成面试问题 
        result = Phase3HRAgent.generate_interview_questions(
            hr_persona=hr_persona,
            resume_content=resume_content,
            job_posting=job_posting,
            num_questions=num_questions
        )
        
        logger.info(f"面试问题生成完成")
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"生成面试问题失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"面试问题生成失败: {str(e)}"
        )

@router.post("/phase3/evaluate-interview-answer", response_model=BaseResponse)
async def evaluate_interview_answer(
    hr_persona: str = Body(..., embed=True),
    question: Dict[str, Any] = Body(..., embed=True),
    user_answer: str = Body(..., embed=True),
    resume_content: Dict[str, Any] = Body(..., embed=True),
    job_posting: Dict[str, Any] = Body(..., embed=True)
):
    """
    评估用户的面试回答并给出优化建议
    """
    try:
        logger.info(f"评估面试回答请求 - HR类型: {hr_persona}, 问题ID: {question.get('id', 'N/A')}")
        logger.debug(f"用户回答长度: {len(user_answer) if user_answer else 0}")
        
        # 验证输入参数
        if not hr_persona or not question or not user_answer:
            logger.warning(f"参数验证失败 - hrPersona: {bool(hr_persona)}, question: {bool(question)}, userAnswer: {bool(user_answer)}")
            return BaseResponse(
                success=False,
                message="请提供完整的评估信息",
                data={}
            )
        
        # 调用agent评估回答
        result = Phase3HRAgent.evaluate_interview_answer(
            hr_persona=hr_persona,
            question=question,
            user_answer=user_answer,
            resume_content=resume_content,
            job_posting=job_posting
        )
        
        logger.info(f"面试回答评估完成 - 成功: {result.get('success', False)}")
        
        return BaseResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except Exception as e:
        logger.error(f"评估面试回答失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"面试回答评估失败: {str(e)}"
        )