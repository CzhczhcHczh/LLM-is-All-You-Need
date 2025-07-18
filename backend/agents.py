"""
Core Agent implementations for Job Planner Assistant.
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from services import llm_service, serper_service, chromadb_service, text_service
from database import (
    get_db, create_job_posting, create_resume, create_hr_feedback, 
    create_interview, create_schedule, JobPostingCreate, ResumeCreate,
    HRFeedbackCreate, InterviewCreate, ScheduleCreate
)


class Phase1SearchAgent:
    """Phase 1: Job search and data collection agent."""
    
    @staticmethod
    def search_jobs(search_query: str, location: str = None, max_results: int = 20) -> Dict[str, Any]:
        """Search for job postings and extract structured data."""
        try:
            logger.info(f"Starting job search for: {search_query}")
            
            # Search using Serper API
            search_results = serper_service.search_jobs(
                query=search_query,
                location=location,
                num_results=max_results
            )
            
            if not search_results:
                return {
                    "success": False,
                    "message": "No search results found",
                    "data": {"jobs": [], "companies": []}
                }
            
            # Process search results with LLM
            jobs = []
            companies = {}
            
            for result in search_results:
                # Extract job information using LLM
                extraction_prompt = f"""
                请从以下搜索结果中提取招聘信息，返回JSON格式：
                
                标题: {result.get('title', '')}
                链接: {result.get('link', '')}
                描述: {result.get('snippet', '')}
                
                请提取以下信息并返回JSON格式：
                {{
                    "job_title": "职位名称",
                    "company_name": "公司名称",
                    "location": "工作地点",
                    "salary_range": "薪资范围",
                    "requirements": ["要求1", "要求2"],
                    "skills": ["技能1", "技能2"],
                    "description": "职位描述",
                    "is_valid_job": true/false
                }}
                
                如果这不是一个有效的招聘信息，请设置 is_valid_job 为 false。
                """
                
                try:
                    extraction_result = llm_service.call_phase1_model(extraction_prompt)
                    
                    # Parse JSON result
                    import re
                    json_match = re.search(r'\{.*\}', extraction_result, re.DOTALL)
                    if json_match:
                        job_data = json.loads(json_match.group())
                        
                        if job_data.get('is_valid_job', False):
                            # Add source information
                            job_data.update({
                                'source_url': result.get('link', ''),
                                'search_query': search_query,
                                'extracted_at': datetime.now().isoformat()
                            })
                            
                            jobs.append(job_data)
                            
                            # Collect company information
                            company_name = job_data.get('company_name', '')
                            if company_name and company_name not in companies:
                                companies[company_name] = {
                                    'name': company_name,
                                    'jobs_count': 1,
                                    'locations': [job_data.get('location', '')],
                                    'search_query': search_query
                                }
                            elif company_name:
                                companies[company_name]['jobs_count'] += 1
                                if job_data.get('location') not in companies[company_name]['locations']:
                                    companies[company_name]['locations'].append(job_data.get('location', ''))
                
                except Exception as e:
                    logger.error(f"Error processing search result: {e}")
                    continue
            
            # Store in vector database for similarity search
            for i, job in enumerate(jobs):
                job_text = f"{job.get('job_title', '')} {job.get('company_name', '')} {job.get('description', '')}"
                chromadb_service.add_job_posting(
                    job_id=f"search_{int(time.time())}_{i}",
                    job_text=job_text,
                    metadata=job
                )
            
            logger.info(f"Successfully processed {len(jobs)} jobs from {len(companies)} companies")
            
            return {
                "success": True,
                "message": f"Found {len(jobs)} job postings",
                "data": {
                    "jobs": jobs,
                    "companies": list(companies.values()),
                    "search_query": search_query,
                    "total_results": len(jobs)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            return {
                "success": False,
                "message": f"Search failed: {str(e)}",
                "data": {"jobs": [], "companies": []}
            }
    
    @staticmethod
    def get_similar_jobs(user_profile: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar jobs based on user profile."""
        try:
            # Create search query from user profile
            profile_text = f"{user_profile.get('target_position', '')} {' '.join(user_profile.get('skills', []))}"
            
            # Search similar jobs in vector database
            similar_jobs = chromadb_service.search_similar_jobs(profile_text, n_results)
            
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Error finding similar jobs: {e}")
            return []


class Phase2ResumeAgent:
    """Phase 2: Resume generation and optimization agent."""
    
    @staticmethod
    def generate_resume(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a customized resume for a specific job posting."""
        try:
            logger.info(f"Generating resume for job: {job_posting.get('job_title', 'Unknown')}")
            
            # Create resume generation prompt
            prompt = f"""
            请根据以下用户信息和职位要求，生成一份个性化的简历。返回JSON格式。
            
            用户信息：
            姓名: {user_profile.get('full_name', '')}
            邮箱: {user_profile.get('email', '')}
            电话: {user_profile.get('phone', '')}
            目标职位: {user_profile.get('target_position', '')}
            技能: {', '.join(user_profile.get('skills', []))}
            工作经验: {json.dumps(user_profile.get('experience', []), ensure_ascii=False)}
            教育背景: {json.dumps(user_profile.get('education', []), ensure_ascii=False)}
            项目经验: {json.dumps(user_profile.get('projects', []), ensure_ascii=False)}
            
            目标职位信息：
            职位名称: {job_posting.get('job_title', '')}
            公司名称: {job_posting.get('company_name', '')}
            职位要求: {', '.join(job_posting.get('requirements', []))}
            技能要求: {', '.join(job_posting.get('skills', []))}
            职位描述: {job_posting.get('description', '')}
            
            请生成一份针对该职位的简历，返回以下JSON格式：
            {{
                "personal_info": {{
                    "name": "姓名",
                    "email": "邮箱",
                    "phone": "电话",
                    "location": "地址"
                }},
                "summary": "个人简介，突出与目标职位的匹配度",
                "experience": [
                    {{
                        "company": "公司名称",
                        "position": "职位",
                        "duration": "时间段",
                        "description": "工作描述，突出相关技能和成就",
                        "achievements": ["成就1", "成就2"]
                    }}
                ],
                "education": [
                    {{
                        "school": "学校",
                        "degree": "学位",
                        "major": "专业",
                        "duration": "时间段"
                    }}
                ],
                "skills": ["技能1", "技能2"],
                "projects": [
                    {{
                        "name": "项目名称",
                        "description": "项目描述",
                        "technologies": ["技术1", "技术2"],
                        "achievements": ["成果1", "成果2"]
                    }}
                ],
                "highlighted_skills": ["与职位最匹配的技能"],
                "customization_notes": "针对该职位的定制说明"
            }}
            
            请确保简历内容与目标职位高度匹配，突出相关技能和经验。
            """
            
            # Generate resume using LLM
            start_time = time.time()
            resume_result = llm_service.call_phase2_model(prompt)
            generation_time = time.time() - start_time
            
            # Parse JSON result
            import re
            json_match = re.search(r'\{.*\}', resume_result, re.DOTALL)
            if json_match:
                resume_content = json.loads(json_match.group())
                
                return {
                    "success": True,
                    "message": "Resume generated successfully",
                    "data": {
                        "content": resume_content,
                        "generation_time": generation_time,
                        "model_used": "phase2_model",
                        "job_title": job_posting.get('job_title', ''),
                        "company_name": job_posting.get('company_name', ''),
                        "created_at": datetime.now().isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to parse resume content",
                    "data": {"raw_result": resume_result}
                }
                
        except Exception as e:
            logger.error(f"Error generating resume: {e}")
            return {
                "success": False,
                "message": f"Resume generation failed: {str(e)}",
                "data": {}
            }
    
    @staticmethod
    def optimize_resume(resume_content: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resume based on feedback."""
        try:
            optimization_prompt = f"""
            请根据以下反馈优化简历内容：
            
            当前简历：
            {json.dumps(resume_content, ensure_ascii=False, indent=2)}
            
            反馈意见：
            {json.dumps(feedback, ensure_ascii=False, indent=2)}
            
            请根据反馈意见优化简历，返回优化后的JSON格式简历。
            重点关注：
            1. 补充缺失的关键词
            2. 改进表述方式
            3. 突出相关经验
            4. 优化格式和结构
            
            返回完整的优化后简历JSON。
            """
            
            optimized_result = llm_service.call_phase2_model(optimization_prompt)
            
            # Parse optimized resume
            import re
            json_match = re.search(r'\{.*\}', optimized_result, re.DOTALL)
            if json_match:
                optimized_content = json.loads(json_match.group())
                
                return {
                    "success": True,
                    "message": "Resume optimized successfully",
                    "data": {
                        "content": optimized_content,
                        "optimization_notes": "Based on HR feedback"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to parse optimized resume",
                    "data": {"raw_result": optimized_result}
                }
                
        except Exception as e:
            logger.error(f"Error optimizing resume: {e}")
            return {
                "success": False,
                "message": f"Resume optimization failed: {str(e)}",
                "data": {}
            }


class Phase3HRAgent:
    """Phase 3: HR simulation and feedback agent."""
    
    @staticmethod
    def simulate_hr_review(resume_content: Dict[str, Any], job_posting: Dict[str, Any], 
                          hr_persona: str = "experienced") -> Dict[str, Any]:
        """Simulate HR review of resume."""
        try:
            logger.info(f"Simulating HR review for {job_posting.get('company_name', 'Unknown')} position")
            
            # Define HR personas
            hr_personas = {
                "experienced": "经验丰富的HR，注重技能匹配和工作经验",
                "conservative": "保守的HR，重视教育背景和稳定性",
                "progressive": "开放的HR，看重潜力和学习能力",
                "technical": "技术背景的HR，专注技术技能和项目经验"
            }
            
            persona_description = hr_personas.get(hr_persona, hr_personas["experienced"])
            
            # Create HR review prompt
            prompt = f"""
            你是{job_posting.get('company_name', '某公司')}的HR，{persona_description}。
            请评估以下简历是否适合我们的职位，并提供详细反馈。
            
            职位信息：
            职位名称: {job_posting.get('job_title', '')}
            职位要求: {', '.join(job_posting.get('requirements', []))}
            技能要求: {', '.join(job_posting.get('skills', []))}
            职位描述: {job_posting.get('description', '')}
            
            候选人简历：
            {json.dumps(resume_content, ensure_ascii=False, indent=2)}
            
            请从以下几个方面评估并返回JSON格式：
            {{
                "overall_score": 85,  // 总体评分 (0-100)
                "passes_initial_screening": true,  // 是否通过初筛
                "strengths": ["优势1", "优势2"],
                "weaknesses": ["不足1", "不足2"],
                "missing_keywords": ["缺失关键词1", "缺失关键词2"],
                "experience_feedback": "工作经验评价",
                "skills_feedback": "技能评价",
                "education_feedback": "教育背景评价",
                "suggestions": ["改进建议1", "改进建议2"],
                "interview_invitation": {{
                    "invited": true,
                    "interview_type": "技术面试",
                    "proposed_times": ["2024-01-20 14:00", "2024-01-21 10:00"],
                    "duration": 60,
                    "location": "线上/公司地址",
                    "interviewer": "技术经理",
                    "preparation_notes": "准备要点"
                }},
                "hr_comments": "HR的整体评价和建议"
            }}
            
            请基于{persona_description}的角度进行评估。
            """
            
            # Get HR feedback
            start_time = time.time()
            hr_result = llm_service.call_phase3_model(prompt)
            generation_time = time.time() - start_time
            
            # Parse feedback
            import re
            json_match = re.search(r'\{.*\}', hr_result, re.DOTALL)
            if json_match:
                feedback_content = json.loads(json_match.group())
                
                return {
                    "success": True,
                    "message": "HR review completed",
                    "data": {
                        "feedback": feedback_content,
                        "hr_persona": hr_persona,
                        "company_name": job_posting.get('company_name', ''),
                        "job_title": job_posting.get('job_title', ''),
                        "generation_time": generation_time,
                        "model_used": "phase3_model",
                        "review_date": datetime.now().isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to parse HR feedback",
                    "data": {"raw_result": hr_result}
                }
                
        except Exception as e:
            logger.error(f"Error in HR simulation: {e}")
            return {
                "success": False,
                "message": f"HR simulation failed: {str(e)}",
                "data": {}
            }
    
    @staticmethod
    def iterative_feedback(resume_content: Dict[str, Any], job_posting: Dict[str, Any], 
                          round_number: int = 1, max_rounds: int = 3) -> Dict[str, Any]:
        """Provide iterative feedback for resume improvement."""
        try:
            if round_number > max_rounds:
                return {
                    "success": False,
                    "message": f"Maximum feedback rounds ({max_rounds}) reached",
                    "data": {}
                }
            
            # Get initial HR feedback
            hr_feedback = Phase3HRAgent.simulate_hr_review(resume_content, job_posting)
            
            if not hr_feedback["success"]:
                return hr_feedback
            
            feedback_data = hr_feedback["data"]["feedback"]
            
            # If passes screening or max rounds reached, finalize
            if feedback_data.get("passes_initial_screening", False) or round_number >= max_rounds:
                return {
                    "success": True,
                    "message": f"Feedback completed after {round_number} rounds",
                    "data": {
                        "final_feedback": feedback_data,
                        "rounds_completed": round_number,
                        "passes_screening": feedback_data.get("passes_initial_screening", False)
                    }
                }
            
            # Generate improved resume based on feedback
            improved_resume = Phase2ResumeAgent.optimize_resume(resume_content, feedback_data)
            
            if improved_resume["success"]:
                # Recursively get feedback for improved resume
                return Phase3HRAgent.iterative_feedback(
                    improved_resume["data"]["content"], 
                    job_posting, 
                    round_number + 1, 
                    max_rounds
                )
            else:
                return improved_resume
                
        except Exception as e:
            logger.error(f"Error in iterative feedback: {e}")
            return {
                "success": False,
                "message": f"Iterative feedback failed: {str(e)}",
                "data": {}
            }


class Phase4ScheduleAgent:
    """Phase 4: Interview scheduling and optimization agent."""
    
    @staticmethod
    def multi_agent_discussion(interviews: List[Dict[str, Any]], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct multi-agent discussion for optimal scheduling."""
        try:
            logger.info(f"Starting multi-agent discussion for {len(interviews)} interviews")
            
            # Prepare discussion context
            discussion_context = f"""
            需要安排以下面试：
            {json.dumps(interviews, ensure_ascii=False, indent=2)}
            
            用户偏好：
            {json.dumps(user_preferences, ensure_ascii=False, indent=2)}
            
            请从以下角度分析最优的面试安排方案：
            1. 时间冲突检测和解决
            2. 公司匹配度排序
            3. 面试准备时间考虑
            4. 交通和地理位置优化
            
            请提供你的分析和建议。
            """
            
            # Get responses from multiple models
            agent_responses = llm_service.call_phase4_models(discussion_context)
            
            # Synthesize final decision
            synthesis_prompt = f"""
            以下是多个AI助手对面试安排的分析：
            
            {json.dumps(agent_responses, ensure_ascii=False, indent=2)}
            
            请综合所有建议，制定最终的面试安排方案，返回JSON格式：
            {{
                "recommended_schedule": [
                    {{
                        "interview_id": "面试ID",
                        "company_name": "公司名称",
                        "position": "职位",
                        "scheduled_time": "2024-01-20 14:00",
                        "priority_rank": 1,
                        "match_score": 85,
                        "reasoning": "安排理由"
                    }}
                ],
                "conflict_resolutions": [
                    {{
                        "conflict": "冲突描述",
                        "resolution": "解决方案"
                    }}
                ],
                "optimization_summary": "整体优化说明",
                "agent_consensus": "各AI助手的共识",
                "final_reasoning": "最终决策理由"
            }}
            """
            
            final_result = llm_service.call_phase1_model(synthesis_prompt)  # Use any model for synthesis
            
            # Parse final schedule
            import re
            json_match = re.search(r'\{.*\}', final_result, re.DOTALL)
            if json_match:
                schedule_data = json.loads(json_match.group())
                
                return {
                    "success": True,
                    "message": "Multi-agent scheduling completed",
                    "data": {
                        "schedule": schedule_data,
                        "agent_discussions": agent_responses,
                        "discussion_timestamp": datetime.now().isoformat(),
                        "total_interviews": len(interviews)
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to parse scheduling result",
                    "data": {"raw_result": final_result}
                }
                
        except Exception as e:
            logger.error(f"Error in multi-agent discussion: {e}")
            return {
                "success": False,
                "message": f"Multi-agent scheduling failed: {str(e)}",
                "data": {}
            }
    
    @staticmethod
    def optimize_schedule(interviews: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize interview schedule based on constraints."""
        try:
            # Calculate match scores for each interview
            scored_interviews = []
            for interview in interviews:
                # Simple scoring algorithm (can be enhanced)
                base_score = interview.get('match_score', 50)
                
                # Adjust score based on company reputation, salary, etc.
                company_bonus = 10 if 'BAT' in interview.get('company_name', '') else 0
                salary_bonus = 5 if interview.get('salary_range', '').find('20k') > -1 else 0
                
                final_score = min(100, base_score + company_bonus + salary_bonus)
                
                scored_interviews.append({
                    **interview,
                    'calculated_score': final_score
                })
            
            # Sort by score (descending)
            scored_interviews.sort(key=lambda x: x.get('calculated_score', 0), reverse=True)
            
            # Assign priority ranks
            for i, interview in enumerate(scored_interviews):
                interview['priority_rank'] = i + 1
            
            return {
                "success": True,
                "message": "Schedule optimized successfully",
                "data": {
                    "optimized_interviews": scored_interviews,
                    "optimization_criteria": constraints,
                    "total_interviews": len(scored_interviews)
                }
            }
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {
                "success": False,
                "message": f"Schedule optimization failed: {str(e)}",
                "data": {}
            }


# Initialize agent instances
phase1_agent = Phase1SearchAgent()
phase2_agent = Phase2ResumeAgent()
phase3_agent = Phase3HRAgent()
phase4_agent = Phase4ScheduleAgent()

