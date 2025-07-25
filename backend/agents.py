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

from SearchAgent import SearchAgent
from Phase4ScheduleAgent import Phase4ScheduleAgent as Phase4Agent

def ensure_dict(obj):
    """确保对象是字典格式"""
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return obj

def safe_get(obj, key, default=None):
    """安全地获取对象属性或字典值"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    elif hasattr(obj, key):
        return getattr(obj, key, default)
    else:
        return default

class Phase2ResumeAgent:
    """Phase 2: Enhanced Resume generation and optimization agent."""
    
    @staticmethod
    def generate_enhanced_resume(
        user_profile: Dict[str, Any], 
        job_posting: Dict[str, Any],
        generation_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成高度个性化的简历"""
        try:
            if generation_params is None:
                generation_params = {}
                
            logger.info(f"Generating enhanced resume for {job_posting.get('company_name', 'Unknown')} - {job_posting.get('job_title', 'Unknown')}")
            
            # 深度分析目标职位
            job_analysis = Phase2ResumeAgent._deep_analyze_job_requirements(job_posting)
            
            # 分析用户背景
            user_analysis = Phase2ResumeAgent._analyze_user_background(user_profile)
            
            # 技能和经验匹配分析
            match_analysis = Phase2ResumeAgent._comprehensive_match_analysis(user_profile, job_posting)
            
            # 生成个性化策略
            personalization_strategy = Phase2ResumeAgent._create_personalization_strategy(
                job_analysis, user_analysis, match_analysis, generation_params
            )
            
            # 创建超级个性化提示词
            prompt = Phase2ResumeAgent._create_super_personalized_prompt(
                user_profile, job_posting, job_analysis, user_analysis, 
                match_analysis, personalization_strategy
            )
            
            # 生成简历
            start_time = time.time()
            resume_result = llm_service.call_phase2_model(prompt)
            generation_time = time.time() - start_time
            
            logger.info(f"Enhanced resume generation completed in {generation_time:.2f}s")
            
            # 解析和验证结果
            resume_content = Phase2ResumeAgent._parse_and_validate_enhanced_resume(
                resume_result, user_profile, job_posting
            )
            
            # 质量评估
            quality_assessment = Phase2ResumeAgent._comprehensive_quality_assessment(
                resume_content, job_posting, match_analysis
            )
            
            # 生成改进建议
            improvement_suggestions = Phase2ResumeAgent._generate_improvement_suggestions(
                resume_content, job_posting, quality_assessment
            )
            
            return {
                "success": True,
                "message": "超级个性化简历生成成功",
                "data": {
                    "content": resume_content,
                    "generation_time": generation_time,
                    "job_analysis": job_analysis,
                    "match_analysis": match_analysis,
                    "quality_assessment": quality_assessment,
                    "improvement_suggestions": improvement_suggestions,
                    "personalization_strategy": personalization_strategy,
                    "customization_level": generation_params.get("customization_level", "high"),
                    "created_at": datetime.now().isoformat()
                }
            }
                
        except Exception as e:
            logger.error(f"Error generating enhanced resume: {e}")
            return Phase2ResumeAgent._create_enhanced_fallback_response(user_profile, job_posting, str(e))
    
    @staticmethod
    def _deep_analyze_job_requirements(job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """深度分析职位要求"""
        analysis = {
            "core_skills": [],
            "soft_skills": [],
            "technical_skills": [],
            "industry_skills": [],
            "experience_requirements": {
                "min_years": 0,
                "preferred_years": 0,
                "level": "entry"
            },
            "education_requirements": {
                "degree_level": "",
                "preferred_majors": []
            },
            "company_analysis": {
                "size": "",
                "culture": "",
                "industry": "",
                "growth_stage": "",
                "values": []
            },
            "role_analysis": {
                "seniority_level": "",
                "team_structure": "",
                "key_responsibilities": [],
                "success_metrics": []
            },
            "market_insights": {
                "salary_competitiveness": "",
                "demand_level": "",
                "career_growth_potential": ""
            }
        }
        
        # 分析技能要求
        job_skills = job_posting.get('skills', [])
        requirements = job_posting.get('requirements', [])
        description = job_posting.get('description', '')
        
        # 技能分类
        technical_keywords = [
            'Vue.js', 'React', 'Angular', 'JavaScript', 'TypeScript', 'Python', 'Java',
            'Node.js', 'MongoDB', 'MySQL', 'AWS', 'Docker', 'Kubernetes'
        ]
        soft_skill_keywords = [
            '沟通', '团队合作', '领导', '管理', '协调', '解决问题', '学习能力', '创新'
        ]
        
        for skill in job_skills:
            if any(tech in skill for tech in technical_keywords):
                analysis["technical_skills"].append(skill)
            elif any(soft in skill for soft in soft_skill_keywords):
                analysis["soft_skills"].append(skill)
            else:
                analysis["core_skills"].append(skill)
        
        # 分析经验要求
        for req in requirements:
            if "年" in req and "经验" in req:
                if "5年以上" in req or "5+" in req:
                    analysis["experience_requirements"]["min_years"] = 5
                    analysis["experience_requirements"]["level"] = "senior"
                elif "3年以上" in req or "3+" in req:
                    analysis["experience_requirements"]["min_years"] = 3
                    analysis["experience_requirements"]["level"] = "mid"
                elif "1年" in req:
                    analysis["experience_requirements"]["min_years"] = 1
                    analysis["experience_requirements"]["level"] = "junior"
        
        # 公司分析
        company_name = job_posting.get('company_name', '')
        if any(name in company_name for name in ['阿里', '腾讯', '百度', '字节', '美团', '滴滴']):
            analysis["company_analysis"]["size"] = "大型"
            analysis["company_analysis"]["culture"] = "大厂文化"
            analysis["company_analysis"]["values"] = ["技术驱动", "数据导向", "用户第一", "创新"]
        elif any(name in company_name for name in ['创业', '科技', 'AI', '智能']):
            analysis["company_analysis"]["size"] = "中小型"
            analysis["company_analysis"]["culture"] = "创业文化"
            analysis["company_analysis"]["values"] = ["快速迭代", "灵活应变", "结果导向"]
        
        # 职位层级分析
        job_title = job_posting.get('job_title', '').lower()
        if any(word in job_title for word in ['高级', 'senior', '资深', 'lead']):
            analysis["role_analysis"]["seniority_level"] = "senior"
        elif any(word in job_title for word in ['中级', 'mid', '经验']):
            analysis["role_analysis"]["seniority_level"] = "mid"
        else:
            analysis["role_analysis"]["seniority_level"] = "junior"
        
        return analysis
    
    @staticmethod
    def _analyze_user_background(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户背景"""
        analysis = {
            "career_stage": "",
            "skill_strengths": [],
            "experience_highlights": [],
            "education_advantage": "",
            "unique_selling_points": [],
            "improvement_areas": [],
            "career_trajectory": "",
            "specialization_areas": []
        }
        
        # 分析职业阶段
        experience = user_profile.get('experience', [])
        total_experience = len(experience)
        
        if total_experience >= 5:
            analysis["career_stage"] = "senior"
        elif total_experience >= 2:
            analysis["career_stage"] = "mid"
        else:
            analysis["career_stage"] = "junior"
        
        # 技能优势分析
        skills = user_profile.get('skills', [])
        frontend_skills = [s for s in skills if any(tech in s for tech in ['Vue', 'React', 'Angular', 'JavaScript'])]
        backend_skills = [s for s in skills if any(tech in s for tech in ['Python', 'Java', 'Node.js', 'Go'])]
        
        if len(frontend_skills) > len(backend_skills):
            analysis["specialization_areas"].append("前端开发")
        elif len(backend_skills) > len(frontend_skills):
            analysis["specialization_areas"].append("后端开发")
        else:
            analysis["specialization_areas"].append("全栈开发")
        
        # 教育背景优势
        education = user_profile.get('education', [])
        if education:
            top_edu = education[0]
            if any(school in top_edu.get('school', '') for school in ['清华', '北大', '985', '211']):
                analysis["education_advantage"] = "顶尖院校背景"
            elif '本科' in top_edu.get('degree', ''):
                analysis["education_advantage"] = "本科学历"
        
        # 项目亮点
        projects = user_profile.get('projects', [])
        if len(projects) >= 3:
            analysis["unique_selling_points"].append("丰富的项目经验")
        
        return analysis
    
    @staticmethod
    def _comprehensive_match_analysis(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """综合匹配度分析"""
        user_skills = set(user_profile.get('skills', []))
        job_skills = set(job_posting.get('skills', []))
        
        # 基础匹配计算
        matched_skills = user_skills.intersection(job_skills)
        missing_skills = job_skills - user_skills
        extra_skills = user_skills - job_skills
        
        skill_match_rate = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # 经验匹配分析
        user_experience_years = len(user_profile.get('experience', []))
        job_requirements = job_posting.get('requirements', [])
        
        required_years = 0
        for req in job_requirements:
            if "年" in req and "经验" in req:
                if "5年" in req:
                    required_years = 5
                elif "3年" in req:
                    required_years = 3
                elif "1年" in req:
                    required_years = 1
        
        experience_match = user_experience_years >= required_years
        
        # 教育匹配分析
        user_education = user_profile.get('education', [])
        education_match = len(user_education) > 0
        
        # 项目相关性分析
        user_projects = user_profile.get('projects', [])
        project_relevance_score = 0
        
        for project in user_projects:
            project_techs = set(project.get('technologies', []))
            relevance = len(project_techs.intersection(job_skills)) / len(job_skills) if job_skills else 0
            project_relevance_score = max(project_relevance_score, relevance)
        
        # 综合评分
        overall_match_score = (
            skill_match_rate * 0.4 +
            (1.0 if experience_match else 0.5) * 0.3 +
            (1.0 if education_match else 0.7) * 0.1 +
            project_relevance_score * 0.2
        ) * 100
        
        return {
            "overall_match_score": round(overall_match_score, 1),
            "skill_match": {
                "rate": round(skill_match_rate * 100, 1),
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "extra_skills": list(extra_skills)
            },
            "experience_match": {
                "meets_requirement": experience_match,
                "user_years": user_experience_years,
                "required_years": required_years
            },
            "education_match": education_match,
            "project_relevance": round(project_relevance_score * 100, 1),
            "match_grade": (
                "优秀" if overall_match_score >= 85 else
                "良好" if overall_match_score >= 70 else
                "一般" if overall_match_score >= 55 else "较低"
            ),
            "improvement_priority": Phase2ResumeAgent._get_improvement_priority(
                skill_match_rate, experience_match, project_relevance_score
            )
        }
    
    @staticmethod
    def _create_personalization_strategy(
        job_analysis: Dict[str, Any], 
        user_analysis: Dict[str, Any], 
        match_analysis: Dict[str, Any],
        generation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建个性化策略"""
        strategy = {
            "highlight_focus": [],
            "content_emphasis": {},
            "tone_style": "",
            "structure_priority": [],
            "keyword_optimization": [],
            "storytelling_approach": "",
            "differentiation_strategy": []
        }
        
        # 根据匹配度确定重点
        match_score = match_analysis.get("overall_match_score", 0)
        
        if match_score >= 80:
            strategy["highlight_focus"] = ["技能匹配", "项目成果", "专业深度"]
            strategy["tone_style"] = "自信专业"
        elif match_score >= 60:
            strategy["highlight_focus"] = ["学习能力", "项目经验", "成长潜力"]
            strategy["tone_style"] = "积极上进"
        else:
            strategy["highlight_focus"] = ["基础扎实", "学习意愿", "发展规划"]
            strategy["tone_style"] = "谦逊务实"
        
        # 内容重点分配
        company_culture = job_analysis.get("company_analysis", {}).get("culture", "")
        if "大厂" in company_culture:
            strategy["content_emphasis"] = {
                "技术深度": 30,
                "项目规模": 25,
                "系统思维": 20,
                "团队协作": 15,
                "学习能力": 10
            }
        else:
            strategy["content_emphasis"] = {
                "执行能力": 25,
                "业务理解": 20,
                "快速学习": 20,
                "沟通协调": 20,
                "结果导向": 15
            }
        
        # 修复：关键词优化 - 正确合并两个列表
        matched_skills = match_analysis.get("skill_match", {}).get("matched_skills", [])
        core_skills = job_analysis.get("core_skills", [])[:5]
        
        # 确保都是列表，然后合并并去重
        strategy["keyword_optimization"] = list(set(matched_skills + core_skills))
        
        return strategy
    
    @staticmethod
    def _create_super_personalized_prompt(
        user_profile: Dict[str, Any], 
        job_posting: Dict[str, Any],
        job_analysis: Dict[str, Any],
        user_analysis: Dict[str, Any],
        match_analysis: Dict[str, Any],
        personalization_strategy: Dict[str, Any]
    ) -> str:
        """创建超级个性化提示词"""
        
        company_name = job_posting.get('company_name', '')
        job_title = job_posting.get('job_title', '')
        
        prompt = f"""
你是一位顶级的简历撰写专家和职业规划师，具有15年以上的招聘和求职经验。请为求职者创建一份极具竞争力的个性化简历。

## 目标职位详情
公司名称：{company_name}
职位名称：{job_title}
工作地点：{job_posting.get('location', '')}
薪资范围：{job_posting.get('salary_range', '')}
公司规模：{job_posting.get('company_size', '')}
行业：{job_posting.get('industry', '')}

职位要求：
{json.dumps(job_posting.get('requirements', []), ensure_ascii=False, indent=2)}

技能要求：
{json.dumps(job_posting.get('skills', []), ensure_ascii=False, indent=2)}

福利待遇：
{json.dumps(job_posting.get('benefits', []), ensure_ascii=False, indent=2)}

职位描述：
{job_posting.get('description', '')}

## 求职者完整档案
{json.dumps(user_profile, ensure_ascii=False, indent=2)}

## 深度分析报告

### 职位深度分析：
- 核心技能要求：{', '.join(job_analysis.get('core_skills', []))}
- 技术技能要求：{', '.join(job_analysis.get('technical_skills', []))}
- 软技能要求：{', '.join(job_analysis.get('soft_skills', []))}
- 经验要求：{job_analysis.get('experience_requirements', {}).get('level', '')}级别，{job_analysis.get('experience_requirements', {}).get('min_years', 0)}年以上
- 公司文化：{job_analysis.get('company_analysis', {}).get('culture', '')}
- 公司价值观：{', '.join(job_analysis.get('company_analysis', {}).get('values', []))}
- 职位层级：{job_analysis.get('role_analysis', {}).get('seniority_level', '')}

### 候选人背景分析：
- 职业阶段：{user_analysis.get('career_stage', '')}
- 专业领域：{', '.join(user_analysis.get('specialization_areas', []))}
- 教育优势：{user_analysis.get('education_advantage', '')}
- 独特卖点：{', '.join(user_analysis.get('unique_selling_points', []))}

### 匹配度分析：
- 综合匹配度：{match_analysis.get('overall_match_score', 0)}%（{match_analysis.get('match_grade', '')}）
- 技能匹配率：{match_analysis.get('skill_match', {}).get('rate', 0)}%
- 匹配技能：{', '.join(match_analysis.get('skill_match', {}).get('matched_skills', []))}
- 缺失技能：{', '.join(match_analysis.get('skill_match', {}).get('missing_skills', []))}
- 项目相关性：{match_analysis.get('project_relevance', 0)}%

### 个性化策略：
- 突出重点：{', '.join(personalization_strategy.get('highlight_focus', []))}
- 语言风格：{personalization_strategy.get('tone_style', '')}
- 关键词优化：{', '.join(personalization_strategy.get('keyword_optimization', []))}
- 内容权重：{json.dumps(personalization_strategy.get('content_emphasis', {}), ensure_ascii=False)}

## 个性化要求

### 核心策略：
1. **精准定位**：根据{match_analysis.get('match_grade', '')}的匹配度，采用相应的展示策略
2. **优势放大**：突出{', '.join(personalization_strategy.get('highlight_focus', []))}
3. **弱项转化**：将缺失技能转化为学习机会和发展潜力
4. **文化契合**：体现与{job_analysis.get('company_analysis', {}).get('culture', '')}的匹配
5. **结果导向**：用数据和成果说话，体现{personalization_strategy.get('tone_style', '')}的风格

### 内容优化：
1. **个人简介**：融入{', '.join(job_analysis.get('company_analysis', {}).get('values', [])[:3])}等企业价值观
2. **技能排序**：优先展示{', '.join(match_analysis.get('skill_match', {}).get('matched_skills', [])[:5])}
3. **经验包装**：根据{job_analysis.get('role_analysis', {}).get('seniority_level', '')}层级调整描述深度
4. **项目选择**：重点展示与{', '.join(job_analysis.get('technical_skills', [])[:3])}相关的项目
5. **成果量化**：用具体数字体现{', '.join(personalization_strategy.get('highlight_focus', []))}

请生成以下JSON格式的简历：

```json
{{
    "personal_info": {{
        "name": "候选人姓名",
        "email": "邮箱地址",
        "phone": "联系电话",
        "location": "居住地址",
        "linkedin": "LinkedIn链接（如有）",
        "github": "GitHub链接（如有）",
        "portfolio": "作品集链接（如有）"
    }},
    "professional_summary": "个人简介（200-250字，融入企业价值观，突出核心竞争力和与职位的匹配度）",
    "core_competencies": [
        "核心竞争力1（结合职位要求）",
        "核心竞争力2（突出匹配优势）",
        "核心竞争力3（体现发展潜力）"
    ],
    "highlighted_skills": {{
        "technical_skills": ["技术技能1", "技术技能2", "技术技能3"],
        "frameworks_tools": ["框架工具1", "框架工具2", "框架工具3"],
        "soft_skills": ["软技能1", "软技能2", "软技能3"]
    }},
    "professional_experience": [
        {{
            "company": "公司名称",
            "position": "职位名称",
            "location": "工作地点",
            "duration": "工作时间",
            "employment_type": "工作类型（全职/兼职/实习）",
            "company_description": "公司简介（1-2句话）",
            "responsibilities": [
                "核心职责1（与目标职位高度相关）",
                "核心职责2（体现技能匹配）",
                "核心职责3（展现成长轨迹）"
            ],
            "key_achievements": [
                "关键成果1（用数字量化，体现业务价值）",
                "关键成果2（突出技术能力和解决问题的能力）",
                "关键成果3（展现团队协作和领导力）"
            ],
            "technologies_used": ["相关技术1", "相关技术2", "相关技术3"]
        }}
    ],
    "key_projects": [
        {{
            "name": "项目名称",
            "role": "项目角色",
            "duration": "项目周期",
            "team_size": "团队规模",
            "project_scale": "项目规模描述",
            "description": "项目描述（突出与目标职位的相关性）",
            "key_responsibilities": [
                "核心职责1（技术深度）",
                "核心职责2（业务理解）",
                "核心职责3（团队协作）"
            ],
            "technologies_stack": {{
                "frontend": ["前端技术"],
                "backend": ["后端技术"],
                "database": ["数据库技术"],
                "tools": ["开发工具"]
            }},
            "achievements_metrics": [
                "量化成果1（性能提升/成本节约等）",
                "量化成果2（用户增长/效率提升等）",
                "量化成果3（质量改进/创新突破等）"
            ],
            "challenges_solutions": "遇到的挑战及解决方案（体现问题解决能力）"
        }}
    ],
    "education": [
        {{
            "institution": "学校名称",
            "degree": "学位类型",
            "major": "专业名称",
            "location": "学校地点",
            "duration": "就读时间",
            "gpa": "GPA（如较高则展示）",
            "relevant_coursework": ["相关课程1", "相关课程2"],
            "academic_achievements": ["学术成就1", "学术成就2"],
            "graduation_thesis": "毕业论文题目（如相关）"
        }}
    ],
    "technical_skills": {{
        "programming_languages": ["编程语言"],
        "frameworks_libraries": ["框架和库"],
        "databases": ["数据库技术"],
        "cloud_platforms": ["云平台"],
        "development_tools": ["开发工具"],
        "methodologies": ["开发方法论"]
    }},
    "certifications": [
        {{
            "name": "证书名称",
            "issuer": "颁发机构",
            "date_obtained": "获得时间",
            "validity": "有效期",
            "credential_id": "证书编号（如有）"
        }}
    ],
    "languages": [
        {{
            "language": "语言名称",
            "proficiency": "熟练程度",
            "certifications": "相关证书"
        }}
    ],
    "professional_development": [
        "持续学习活动1（在线课程/会议/研讨会）",
        "持续学习活动2（开源贡献/技术分享）",
        "持续学习活动3（行业认证/技能提升）"
    ],
    "additional_information": {{
        "availability": "到岗时间",
        "salary_expectation": "薪资期望（可选）",
        "work_preference": "工作偏好（远程/现场/混合）",
        "relocation_willingness": "是否愿意搬迁",
        "travel_availability": "出差意愿"
    }},
    "customization_analysis": {{
        "target_company": "{company_name}",
        "target_position": "{job_title}",
        "match_score": {match_analysis.get('overall_match_score', 0)},
        "key_selling_points": [
            "针对此职位的核心卖点1",
            "针对此职位的核心卖点2",
            "针对此职位的核心卖点3"
        ],
        "differentiation_strategy": "与其他候选人的差异化优势",
        "cultural_fit_indicators": [
            "文化契合点1",
            "文化契合点2",
            "文化契合点3"
        ],
        "growth_potential": "在该职位的发展潜力说明",
        "value_proposition": "为公司带来的独特价值"
    }}
}}
```

## 特别要求：

1. **真实性**：所有内容必须基于用户提供的真实信息，不可虚构
2. **针对性**：每个部分都要体现与{company_name}{job_title}职位的高度相关性
3. **差异化**：突出候选人的独特优势和价值主张
4. **量化性**：尽可能使用具体数字和指标
5. **前瞻性**：体现学习能力和发展潜力
6. **专业性**：使用行业专业术语，体现专业素养
7. **可信度**：确保内容逻辑一致，经得起面试验证

请确保生成的简历既专业又有个性，既突出优势又诚实可信，能够在众多候选人中脱颖而出，同时为后续的面试环节奠定坚实基础。

只返回JSON格式的简历内容，不要包含其他解释文字。
请严格按照以上JSON格式返回简历内容。

重要说明：
- 只返回JSON格式的数据，不要包含任何其他文字说明
- 不要使用```json```代码块标记
- 确保JSON格式正确，所有字符串都用双引号包围
- 所有字段都必须填写，不能为空
- professional_summary尽量丰富，能够体现个人优势以及与目标公司的契合性
- 只能在措辞上进行包装，而不能歪曲事实，例如"完成10+活动页面交付"不能写成"完成20+活动页面交付"，“校二等奖学金”不能写成“校一等奖学金”
- "education"中的"academic_achievements"不能歪曲事实，没有就填优秀学生

请现在生成JSON简历,，注意以下要求：

1. **控制长度**：每个字段的内容要简洁明了
   - 每个achievement: 50字以内  
   - project description: 100字以内
   - growth_potential: 100字以内

2. **确保完整性**：必须返回完整的JSON，包含所有闭合括号

3. **避免截断**：如果内容过长，优先保证JSON结构完整

请严格按照JSON格式返回，确保所有字段都有完整的闭合标签。

只返回JSON内容，不要其他说明文字：
"""
        
        return prompt
    
    @staticmethod
    def _get_default_field_value(field: str, user_profile: Dict[str, Any]) -> Any:
        """获取默认字段值"""
        defaults = {
            'personal_info': {
                'name': user_profile.get('full_name', ''),
                'email': user_profile.get('email', ''),
                'phone': user_profile.get('phone', ''),
                'location': user_profile.get('location', '')
            },
            'summary': user_profile.get('summary', ''),
            'experience': user_profile.get('experience', []),
            'skills': user_profile.get('skills', [])
        }
        return defaults.get(field, '')
    
    @staticmethod
    def _get_default_resume(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """生成默认简历结构"""
        return {
            "personal_info": {
                "name": user_profile.get('full_name', '候选人姓名'),
                "email": user_profile.get('email', 'email@example.com'),
                "phone": user_profile.get('phone', '联系电话'),
                "location": user_profile.get('location', '居住地址')
            },
            "professional_summary": user_profile.get('summary', f"具有相关经验的{user_profile.get('target_position', '专业人士')}，致力于在{job_posting.get('company_name', '目标公司')}发挥专业技能，创造价值。"),
            "highlighted_skills": {
                "technical_skills": user_profile.get('skills', ['技能1', '技能2', '技能3'])[:3],
                "frameworks_tools": ['工具1', '工具2'],
                "soft_skills": ['沟通能力', '团队协作', '学习能力']
            },
            "professional_experience": user_profile.get('experience', []) or [
                {
                    "company": "某科技公司",
                    "position": user_profile.get('target_position', '相关职位'),
                    "duration": "2021-2024",
                    "responsibilities": ["负责相关工作"],
                    "key_achievements": ["取得相关成果"],
                    "technologies_used": user_profile.get('skills', ['技术1'])[:3]
                }
            ],
            "education": user_profile.get('education', []) or [
                {
                    "institution": "某大学",
                    "degree": "本科",
                    "major": "相关专业",
                    "duration": "2017-2021"
                }
            ],
            "key_projects": user_profile.get('projects', []) or [
                {
                    "name": "示例项目",
                    "description": "项目描述",
                    "technologies_stack": {"frontend": user_profile.get('skills', ['技术1'])[:2]},
                    "achievements_metrics": ["项目成果"]
                }
            ],
            "customization_analysis": {
                "target_company": job_posting.get('company_name', ''),
                "target_position": job_posting.get('job_title', ''),
                "match_score": 75,
                "key_selling_points": ["基础技能扎实", "学习能力强", "工作态度积极"],
                "value_proposition": "能够快速学习并为团队带来新的视角和活力"
            }
        }
    
    @staticmethod
    def _create_enhanced_fallback_response(user_profile: Dict[str, Any], job_posting: Dict[str, Any], error: str) -> Dict[str, Any]:
        """创建增强的降级响应"""
        return {
            "success": True,
            "message": "使用增强版演示模式生成简历",
            "data": {
                "content": Phase2ResumeAgent._get_default_resume(user_profile, job_posting),
                "generation_time": 0,
                "fallback_reason": error,
                "customization_level": "演示版本",
                "created_at": datetime.now().isoformat()
            }
        }
    
    # 其他辅助方法...
    @staticmethod
    def _get_improvement_priority(skill_match_rate: float, experience_match: bool, project_relevance: float) -> List[str]:
        """获取改进优先级"""
        priorities = []
        
        if skill_match_rate < 0.5:
            priorities.append("提升技能匹配度")
        if not experience_match:
            priorities.append("积累相关经验")
        if project_relevance < 0.6:
            priorities.append("增加相关项目经验")
        
        return priorities

    @staticmethod 
    def _parse_and_validate_enhanced_resume(resume_result: str, user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """解析和验证增强简历结果"""
        try:
            logger.debug(f"Raw resume result: {resume_result[:500]}...")  # 打印前500字符用于调试
            
            # 方法1: 直接尝试解析整个结果
            try:
                resume_content = json.loads(resume_result)
                logger.info("Successfully parsed JSON directly")
            except json.JSONDecodeError:
                # 方法2: 查找JSON代码块
                import re
                
                # 查找 ```json 代码块
                json_block_match = re.search(r'```json\s*(.*?)\s*```', resume_result, re.DOTALL)
                if json_block_match:
                    json_content = json_block_match.group(1)
                    logger.info("Found JSON in code block")
                    resume_content = json.loads(json_content)
                else:
                    # 方法3: 查找任何大括号包围的内容
                    json_match = re.search(r'\{.*\}', resume_result, re.DOTALL)
                    if json_match:
                        json_content = json_match.group()
                        logger.info("Found JSON in braces")
                        resume_content = json.loads(json_content)
                    else:
                        logger.error("No JSON content found in response")
                        raise json.JSONDecodeError("No JSON found", resume_result, 0)
            
            # 验证必要字段
            required_fields = [
                'personal_info', 'professional_summary', 'highlighted_skills', 
                'professional_experience', 'education'
            ]
            
            for field in required_fields:
                if field not in resume_content:
                    logger.warning(f"Missing field: {field}, adding default value")
                    # 提供默认值
                    if field == 'personal_info':
                        resume_content[field] = {
                            "name": user_profile.get('full_name', ''),
                            "email": user_profile.get('email', ''),
                            "phone": user_profile.get('phone', ''),
                            "location": user_profile.get('location', '')
                        }
                    elif field == 'professional_summary':
                        resume_content[field] = user_profile.get('summary', '经验丰富的前端开发工程师')
                    elif field == 'highlighted_skills':
                        resume_content[field] = {
                            "technical_skills": user_profile.get('skills', [])[:5],
                            "frameworks_tools": ['Vue.js', 'React'],
                            "soft_skills": ['沟通能力', '团队协作', '学习能力']
                        }
                    elif field == 'professional_experience':
                        resume_content[field] = user_profile.get('experience', [])
                    elif field == 'education':
                        resume_content[field] = user_profile.get('education', [])
            
            # 确保customization_analysis字段存在
            if 'customization_analysis' not in resume_content:
                resume_content['customization_analysis'] = {
                    "target_company": job_posting.get('company_name', ''),
                    "target_position": job_posting.get('job_title', ''),
                    "match_score": 70,
                    "key_selling_points": ["技术能力扎实", "学习能力强", "项目经验丰富"],
                    "value_proposition": "能够为团队带来专业的前端开发技能和创新思维"
                }
            
            logger.info("Resume parsing and validation completed successfully")
            return resume_content
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"Raw content: {resume_result}")
            return Phase2ResumeAgent._get_default_resume(user_profile, job_posting)
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            return Phase2ResumeAgent._get_default_resume(user_profile, job_posting)
    
    @staticmethod
    def _comprehensive_quality_assessment(resume_content: Dict[str, Any], job_posting: Dict[str, Any], match_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """综合质量评估"""
        
        assessment = {
            "overall_score": 0,
            "category_scores": {},
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }
        
        # 评估维度和权重
        dimensions = {
            "内容完整性": 0.2,
            "技能匹配度": 0.25,
            "经验相关性": 0.2,
            "表达专业性": 0.15,
            "个性化程度": 0.2
        }
        
        scores = {}
        
        # 内容完整性评分
        required_sections = ['personal_info', 'professional_summary', 'professional_experience', 'education']
        completeness = sum(1 for section in required_sections if resume_content.get(section)) / len(required_sections)
        scores["内容完整性"] = completeness * 100
        
        # 技能匹配度评分（使用已有的匹配分析）
        scores["技能匹配度"] = match_analysis.get("skill_match", {}).get("rate", 0)
        
        # 经验相关性评分
        experience_score = 70  # 基础分
        if resume_content.get('professional_experience'):
            experience_score = 85
        scores["经验相关性"] = experience_score
        
        # 表达专业性评分
        professional_score = 75  # 基础分
        if resume_content.get('professional_summary') and len(resume_content['professional_summary']) > 100:
            professional_score += 10
        if resume_content.get('customization_analysis'):
            professional_score += 10
        scores["表达专业性"] = min(professional_score, 100)
        
        # 个性化程度评分
        personalization_score = 60  # 基础分
        if resume_content.get('customization_analysis', {}).get('key_selling_points'):
            personalization_score += 20
        if resume_content.get('customization_analysis', {}).get('cultural_fit_indicators'):
            personalization_score += 20
        scores["个性化程度"] = min(personalization_score, 100)
        
        # 计算总分
        overall_score = sum(scores[dim] * weight for dim, weight in dimensions.items())
        
        assessment["overall_score"] = round(overall_score, 1)
        assessment["category_scores"] = scores
        
        # 生成优势和不足
        for dim, score in scores.items():
            if score >= 85:
                assessment["strengths"].append(f"{dim}表现优秀")
            elif score < 70:
                assessment["weaknesses"].append(f"{dim}需要改进")
        
        return assessment
    
    @staticmethod
    def _generate_improvement_suggestions(resume_content: Dict[str, Any], job_posting: Dict[str, Any], quality_assessment: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        scores = quality_assessment.get("category_scores", {})
        
        if scores.get("技能匹配度", 0) < 70:
            suggestions.append("建议在简历中更突出与职位要求匹配的技能")
        
        if scores.get("经验相关性", 0) < 75:
            suggestions.append("建议重新包装工作经验，突出与目标职位的相关性")
        
        if scores.get("个性化程度", 0) < 80:
            suggestions.append("建议增加针对目标公司和职位的个性化内容")
        
        if not resume_content.get('key_projects'):
            suggestions.append("建议添加相关项目经验以增强简历竞争力")
        
        return suggestions

    @staticmethod
    def analyze_job_user_match(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """分析工作和用户的匹配度"""
        try:
            job_analysis = Phase2ResumeAgent._deep_analyze_job_requirements(job_posting)
            user_analysis = Phase2ResumeAgent._analyze_user_background(user_profile)
            match_analysis = Phase2ResumeAgent._comprehensive_match_analysis(user_profile, job_posting)
            
            return {
                "job_analysis": job_analysis,
                "user_analysis": user_analysis,
                "match_analysis": match_analysis,
                "recommendations": Phase2ResumeAgent._get_improvement_priority(
                    match_analysis["skill_match"]["rate"] / 100,
                    match_analysis["experience_match"]["meets_requirement"],
                    match_analysis["project_relevance"] / 100
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job-user match: {e}")
            return {"error": str(e)}

    @staticmethod
    def optimize_resume_content(resume_content: Dict[str, Any], feedback: Dict[str, Any], optimization_focus: List[str] = None) -> Dict[str, Any]:
        """基于HR反馈优化简历内容"""
        try:
            import json
            import re
            import time
            from services import llm_service
            
            if optimization_focus is None:
                optimization_focus = []
            
            # 提取反馈数据
            feedback_data = feedback.get('data', {}).get('feedback', feedback) if 'data' in feedback else feedback
            company_name = feedback.get('data', {}).get('company_name', '目标公司')
            job_title = feedback.get('data', {}).get('job_title', '目标职位')
            hr_persona = feedback.get('data', {}).get('hr_persona', 'experienced')
            overall_score = feedback_data.get('overall_score', 0)
            detailed_scores = feedback_data.get('detailed_scores', {})
            strengths = feedback_data.get('strengths', [])
            weaknesses = feedback_data.get('weaknesses', [])
            improvement_suggestions = feedback_data.get('improvement_suggestions', [])
            
            # 创建优化提示词
            optimization_prompt = f"""
你是一位顶级的简历优化专家，具有15年以上的招聘和求职经验。现在需要你基于HR的专业反馈来优化简历，提升竞争力。

## HR评估反馈分析

### 基本信息
- 目标公司：{company_name}
- 目标职位：{job_title}
- HR类型：{hr_persona}
- 当前评分：{overall_score}/100分

### 详细评分
{json.dumps(detailed_scores, ensure_ascii=False, indent=2)}

### 主要优势（需要强化突出）
{json.dumps(strengths, ensure_ascii=False, indent=2)}

### 主要不足（需要重点优化）
{json.dumps(weaknesses, ensure_ascii=False, indent=2)}

### HR改进建议
{json.dumps(improvement_suggestions, ensure_ascii=False, indent=2)}

## 当前简历内容
{json.dumps(resume_content, ensure_ascii=False, indent=2)}

## 优化策略和要求

### 核心优化目标
1. **突出优势**：强化和放大HR认可的技能和经验优势
2. **弥补不足**：通过重新包装和角度调整来减少弱项影响
3. **提升匹配度**：更精准地对接目标职位需求
4. **增强说服力**：用更有力的数据和案例证明能力
5. **职业稳定性**：通过职业规划展示长期承诺

### 具体优化要求

#### 1. 个人简介优化
- 根据优势强化核心竞争力描述
- 融入{company_name}的企业价值观和文化
- 突出与{job_title}职位的高度匹配性
- 展现学习能力和发展潜力

#### 2. 工作经验优化
- 重新包装项目规模和复杂度描述
- 强化技术深度和业务影响力
- 突出团队协作和领导力体现
- 用更具体的量化数据证明成果

#### 3. 技能体系优化
- 优先展示匹配的核心技能
- 补充新兴技术学习能力
- 体现技术广度和深度平衡
- 展现持续学习和自我提升

#### 4. 项目经验优化
- 重新描述项目规模和影响力
- 突出技术难点和解决方案
- 强化架构设计和系统思维
- 展现创新能力和业务价值

#### 5. 职业发展优化
- 展现清晰的职业规划
- 体现对{company_name}的长期承诺
- 突出在该职位的发展潜力
- 展现适应大厂文化的能力

### 优化原则
1. **真实性第一**：所有优化必须基于真实信息，不可虚构
2. **针对性强化**：每个部分都要体现对反馈的针对性改进
3. **数据驱动**：用具体数字和成果证明能力
4. **差异化突出**：强化独特优势和价值主张
5. **格式一致**：严格按照原有JSON格式返回

请基于以上分析和要求，生成优化后的简历。确保：
- 针对每个弱项都有相应的改进措施
- 强化每个优势点的表达
- 整体提升职位匹配度和竞争力
- 保持所有字段格式与原简历完全一致

请生成以下JSON格式的优化简历：

{{
    "personal_info": {{
        "name": "候选人姓名",
        "email": "邮箱地址", 
        "phone": "联系电话",
        "location": "居住地址",
        "linkedin": "LinkedIn链接（如有）",
        "github": "GitHub链接（如有）",
        "portfolio": "作品集链接（如有）"
    }},
    "professional_summary": "个人简介（250-300字，强化优势，回应反馈，突出与目标职位匹配度）",
    "core_competencies": [
        "核心竞争力1（基于优势强化）",
        "核心竞争力2（针对弱项改进）",
        "核心竞争力3（体现发展潜力）"
    ],
    "highlighted_skills": {{
        "technical_skills": ["技术技能1", "技术技能2", "技术技能3"],
        "frameworks_tools": ["框架工具1", "框架工具2", "框架工具3"],
        "soft_skills": ["软技能1", "软技能2", "软技能3"]
    }},
    "professional_experience": [
        {{
            "company": "公司名称",
            "position": "职位名称",
            "location": "工作地点", 
            "duration": "工作时间",
            "employment_type": "工作类型",
            "company_description": "公司简介（强化规模和影响力描述）",
            "responsibilities": [
                "核心职责1（强化技术深度和复杂度）",
                "核心职责2（突出团队协作和领导力）",
                "核心职责3（体现业务影响和价值创造）"
            ],
            "key_achievements": [
                "关键成果1（用更具体数据量化业务价值）",
                "关键成果2（突出技术创新和解决方案）",
                "关键成果3（展现团队影响和领导能力）"
            ],
            "technologies_used": ["相关技术1", "相关技术2", "相关技术3"]
        }}
    ],
    "key_projects": [
        {{
            "name": "项目名称",
            "role": "项目角色（强化领导和责任）",
            "duration": "项目周期",
            "team_size": "团队规模",
            "project_scale": "项目规模描述（突出复杂度和影响力）",
            "description": "项目描述（强化技术难度和业务价值）",
            "key_responsibilities": [
                "核心职责1（突出架构设计和技术深度）",
                "核心职责2（强化业务理解和解决方案）",
                "核心职责3（体现团队协作和领导力）"
            ],
            "technologies_stack": {{
                "frontend": ["前端技术"],
                "backend": ["后端技术"],
                "database": ["数据库技术"],
                "tools": ["开发工具"]
            }},
            "achievements_metrics": [
                "量化成果1（更具体的性能提升数据）",
                "量化成果2（业务增长和用户价值）",
                "量化成果3（质量改进和创新突破）"
            ],
            "challenges_solutions": "遇到的挑战及解决方案（突出技术难点和创新思维）"
        }}
    ],
    "education": [
        {{
            "institution": "学校名称",
            "degree": "学位类型",
            "major": "专业名称",
            "location": "学校地点",
            "duration": "就读时间",
            "gpa": "GPA（如较高则展示）",
            "relevant_coursework": ["相关课程1", "相关课程2"],
            "academic_achievements": ["学术成就1", "学术成就2"],
            "graduation_thesis": "毕业论文题目（如相关）"
        }}
    ],
    "technical_skills": {{
        "programming_languages": ["编程语言"],
        "frameworks_libraries": ["框架和库"],
        "databases": ["数据库技术"],
        "cloud_platforms": ["云平台"],
        "development_tools": ["开发工具"],
        "methodologies": ["开发方法论"]
    }},
    "certifications": [
        {{
            "name": "证书名称",
            "issuer": "颁发机构",
            "date_obtained": "获得时间",
            "validity": "有效期",
            "credential_id": "证书编号（如有）"
        }}
    ],
    "languages": [
        {{
            "language": "语言名称",
            "proficiency": "熟练程度",
            "certifications": "相关证书"
        }}
    ],
    "professional_development": [
        "持续学习活动1（突出新技术学习）",
        "持续学习活动2（强化技术分享和影响力）",
        "持续学习活动3（体现行业认知和前瞻性）"
    ],
    "additional_information": {{
        "availability": "到岗时间",
        "salary_expectation": "薪资期望（可选）",
        "work_preference": "工作偏好（远程/现场/混合）",
        "relocation_willingness": "是否愿意搬迁",
        "travel_availability": "出差意愿"
    }},
    "customization_analysis": {{
        "target_company": "{company_name}",
        "target_position": "{job_title}",
        "match_score": "预期提升的匹配分数",
        "key_selling_points": [
            "基于反馈优化的核心卖点1",
            "基于反馈优化的核心卖点2", 
            "基于反馈优化的核心卖点3"
        ],
        "differentiation_strategy": "针对反馈弱项的差异化优势重塑",
        "cultural_fit_indicators": [
            "文化契合点1（体现长期承诺）",
            "文化契合点2（展现学习能力）",
            "文化契合点3（突出适应性）"
        ],
        "growth_potential": "基于反馈的发展潜力重新阐述（突出在该职位的成长空间和贡献能力）",
        "value_proposition": "针对弱项改进后的独特价值主张"
    }}
}}

重要说明：
- 只返回JSON格式的数据，不要包含任何其他文字说明
- 不要使用```json```代码块标记
- 确保JSON格式正确，所有字符串都用双引号包围
- 所有字段都必须填写，不能为空
- 必须基于真实信息进行优化，不可虚构事实
- 针对HR反馈的每个弱项都要有相应的改进体现
- 强化HR认可的每个优势点的表达
- 整体提升与目标职位的匹配度

请严格按照JSON格式返回优化后的简历内容：
"""

            # 调用LLM生成优化简历
            start_time = time.time()
            optimized_result = llm_service.call_phase2_model(optimization_prompt)
            generation_time = time.time() - start_time
            
            logger.info(f"LLM optimization completed in {generation_time:.2f}s")
            logger.debug(f"LLM response length: {len(optimized_result)} characters")
            
            # 解析JSON结果 - 更强健的解析逻辑
            json_match = re.search(r'\{.*\}', optimized_result, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    # 清理可能的额外字符
                    json_str = json_str.strip()
                    
                    # 尝试解析JSON
                    optimized_resume = json.loads(json_str)
                    
                    # 验证必要字段
                    required_fields = [
                        'personal_info', 'professional_summary', 'core_competencies',
                        'highlighted_skills', 'professional_experience', 'key_projects',
                        'education', 'technical_skills'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in optimized_resume:
                            missing_fields.append(field)
                            # 使用原简历数据填补缺失字段
                            optimized_resume[field] = resume_content.get(field, {} if field in ['personal_info', 'highlighted_skills', 'technical_skills', 'additional_information', 'customization_analysis'] else [])
                    
                    if missing_fields:
                        logger.warning(f"Missing fields in optimized resume: {missing_fields}, filled with original data")
                    
                    # 确保关键字段不为空
                    if not optimized_resume.get('professional_summary'):
                        optimized_resume['professional_summary'] = resume_content.get('professional_summary', '专业且经验丰富的候选人，具备相关技能和经验。')
                    
                    logger.info("Resume optimization completed successfully")
                    
                    return {
                        "success": True,
                        "message": "简历优化完成",
                        "data": {
                            "content": optimized_resume,
                            "optimization_summary": {
                                "original_score": overall_score,
                                "target_improvements": improvement_suggestions[:3],
                                "optimization_focus": [
                                    "强化技能匹配度展示",
                                    "突出项目复杂度和影响力",
                                    "展现职业稳定性和发展规划",
                                    "增强团队协作和领导力体现"
                                ],
                                "expected_improvements": [
                                    f"技能匹配度提升：针对{', '.join(strengths[:2]) if strengths else '核心技能'}进一步强化",
                                    f"弱项改善：在{', '.join(weaknesses[:2]) if weaknesses else '关键领域'}方面重新包装表达",
                                    "整体竞争力提升：预期评分提升10-15分"
                                ]
                            },
                            "generation_time": generation_time,
                            "optimization_type": "hr_feedback_based",
                            "created_at": datetime.now().isoformat()
                        }
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse optimized resume JSON: {e}")
                    logger.error(f"JSON content preview: {json_str[:500]}...")
                    
                    # 返回原简历作为备选方案
                    return {
                        "success": True,
                        "message": "简历优化完成（使用备选方案）",
                        "data": {
                            "content": resume_content,  # 返回原简历
                            "optimization_summary": {
                                "original_score": overall_score,
                                "target_improvements": improvement_suggestions[:3],
                                "optimization_focus": ["技能匹配优化", "经验表述优化", "格式专业化"],
                                "expected_improvements": ["基础优化已应用"],
                                "note": "由于格式解析问题，返回了原始简历内容"
                            },
                            "generation_time": generation_time,
                            "optimization_type": "fallback",
                            "created_at": datetime.now().isoformat()
                        }
                    }
            else:
                logger.error("No valid JSON found in optimization result")
                logger.error(f"LLM response preview: {optimized_result[:500]}...")
                
                # 返回原简历作为备选方案
                return {
                    "success": True,
                    "message": "简历优化完成（使用备选方案）",
                    "data": {
                        "content": resume_content,  # 返回原简历
                        "optimization_summary": {
                            "original_score": overall_score,
                            "target_improvements": improvement_suggestions[:3],
                            "optimization_focus": ["技能匹配优化", "经验表述优化", "格式专业化"],
                            "expected_improvements": ["基础优化已应用"],
                            "note": "由于响应格式问题，返回了原始简历内容"
                        },
                        "generation_time": generation_time,
                        "optimization_type": "fallback",
                        "created_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error optimizing resume content: {e}")
            return {
                "success": False,
                "message": "简历优化过程中发生错误",
                "error": str(e)
            }

class Phase3HRAgent:
    """Phase 3: HR simulation and feedback agent."""
    
    HR_PERSONAS = {
        "experienced": {
            "name": "资深HR经理",
            "description": "拥有10年以上招聘经验的专业HR，注重技能匹配和工作经验",
            "prompt_template": """
你是一位拥有10年以上招聘经验的资深HR经理，在多个行业有着丰富的招聘经验。你以专业、严谨的态度评估每一份简历。

## 你的评估风格：
- 重视工作经验的连续性和相关性
- 关注候选人技能与岗位要求的精确匹配
- 看重过往工作成果和业绩表现
- 注重职业发展路径的合理性
- 对简历的完整性和专业度要求较高

## 评估标准和权重：
1. **工作经验匹配度** (35%) - 工作年限、行业经验、职位层级是否匹配
2. **技能专业程度** (25%) - 专业技能深度、技能证书、实际应用能力
3. **业绩表现** (20%) - 具体成果、数据支撑、影响力
4. **职业稳定性** (15%) - 工作稳定性、跳槽频率、发展轨迹
5. **简历专业性** (5%) - 简历格式、表述清晰度、信息完整性

## 面试邀请标准：
- 总分70分以上：强烈推荐，优先安排面试
- 总分60-69分：条件合格，可以安排面试
- 总分60分以下：不符合要求，建议不予考虑

请仔细评估以下候选人：

### 职位信息：
{job_posting}

### 候选人简历：
{resume_content}

请返回详细的评估报告，格式如下：
{{
    "overall_score": 75,
    "passes_initial_screening": true,
    "detailed_scores": {{
        "experience_match": 80,
        "skills_proficiency": 85,
        "performance_results": 70,
        "career_stability": 75,
        "resume_professionalism": 80
    }},
    "strengths": ["10年相关工作经验", "技能匹配度高", "有具体业绩数据"],
    "weaknesses": ["缺少某项关键技能", "跳槽频率稍高"],
    "detailed_analysis": {{
        "experience_analysis": "工作经验详细分析：候选人有{experience_match}分的工作经验匹配度...",
        "skills_analysis": "技能评估详细说明：候选人在技能方面得分{skills_proficiency}...", 
        "performance_analysis": "业绩表现分析：从简历中可以看出候选人的业绩表现为{performance_results}分...",
        "stability_analysis": "职业稳定性分析：候选人的职业稳定性评分为{career_stability}分..."
    }},
    "improvement_suggestions": [
        "补充相关技能证书，特别是缺失的关键技能",
        "在简历中更明确地展示工作稳定性和忠诚度",
        "增加量化的业绩数据来支撑工作成果",
        "优化简历格式，提高专业度"
    ],
    "specific_recommendations": {{
        "skills_to_add": ["建议补充的具体技能1", "建议补充的具体技能2"],
        "experience_highlight": "建议重点突出的经验部分",
        "format_improvements": ["改进建议1", "改进建议2"]
    }},
    "interview_recommendation": {{
        "should_interview": true,
        "interview_type": "技术面试 + HR面试",
        "focus_areas": ["深入了解项目经验", "验证技能熟练度", "评估文化匹配度"],
        "estimated_success_rate": 75,
        "key_questions": [
            "请详细介绍您最有挑战性的项目经验",
            "您如何看待频繁跳槽对职业发展的影响",
            "您期望的薪资范围和职业发展路径"
        ]
    }},
    "hr_comments": "从我10年的招聘经验来看，这位候选人具有较好的技能基础和工作经验，总体评分为{overall_score}分。主要优势在于技能匹配度较高，有相关的工作经验。但需要关注的是职业稳定性和某些关键技能的补充。建议进行面试以进一步了解候选人的实际能力和文化匹配度。",
    "risk_assessment": "中等风险。主要风险在于职业稳定性，建议在面试中重点了解跳槽原因和未来职业规划的稳定性。",
    "salary_negotiation_advice": "基于候选人的背景，建议薪资谈判空间为10-15%，重点关注技能匹配度和经验价值。"
}}
            """,
            "weights": {
                "experience_match": 0.35,
                "skills_proficiency": 0.25,
                "performance_results": 0.20,
                "career_stability": 0.15,
                "resume_professionalism": 0.05
            },
            "pass_threshold": 70,
            "personality_traits": ["严谨", "专业", "经验丰富", "注重细节"]
        },
        
        "conservative": {
            "name": "保守型HR主管",
            "description": "传统企业背景的HR，重视教育背景、工作稳定性和企业文化匹配",
            "prompt_template": """
你是一家大型传统企业的HR主管，有着保守而稳健的招聘理念。你特别重视候选人的教育背景、工作稳定性和对企业文化的适应性。

## 你的评估风格：
- 优先考虑名校毕业生和知名企业工作经历
- 极其重视工作稳定性，不喜欢频繁跳槽
- 关注候选人的品格和价值观匹配
- 偏好有完整职业规划的候选人
- 对新技术和新趋势相对保守

## 评估标准和权重：
1. **教育背景** (30%) - 学历层次、学校声誉、专业匹配度
2. **工作稳定性** (25%) - 在职时长、跳槽频率、离职原因
3. **企业文化匹配** (20%) - 价值观、工作风格、团队协作
4. **技能基础** (15%) - 基础技能扎实度、学习态度
5. **品格素养** (10%) - 诚信度、责任感、职业操守

## 面试邀请标准：
- 总分75分以上：完全符合要求，强烈推荐
- 总分65-74分：基本符合，可以考虑
- 总分65分以下：不符合企业文化，不予考虑

请以传统企业的严格标准评估以下候选人：

### 职位信息：
{job_posting}

### 候选人简历：
{resume_content}

请返回详细的评估报告：
{{
    "overall_score": 72,
    "passes_initial_screening": true,
    "detailed_scores": {{
        "education_background": 85,
        "work_stability": 90,
        "culture_fit": 70,
        "basic_skills": 75,
        "character_assessment": 80
    }},
    "strengths": ["985院校毕业，教育背景优秀", "工作稳定，平均在职3年以上", "价值观端正，符合企业文化"],
    "weaknesses": ["缺乏大企业经验", "技能相对传统，需要与时俱进"],
    "detailed_analysis": {{
        "education_analysis": "教育背景得分{education_background}分，重点关注学校和专业的匹配度。",
        "stability_analysis": "工作稳定性评分{work_stability}分，考虑在职时长和跳槽频率。",
        "culture_analysis": "企业文化匹配度为{culture_fit}分，评估价值观和工作风格的契合度。",
        "character_analysis": "品格素养评分为{character_assessment}分，侧重诚信度和责任感。"
    }},
    "improvement_suggestions": [
        "补充权威的行业认证和资格证书",
        "在简历中更突出对企业忠诚度和长期承诺",
        "展示在传统企业或大型企业的工作经验",
        "强调团队协作和服从管理的能力"
    ],
    "cultural_concerns": [
        "是否能够适应传统企业的层级管理文化",
        "对加班文化和企业规章制度的接受度",
        "是否具备长期服务企业的意愿和稳定性"
    ],
    "interview_recommendation": {{
        "should_interview": true,
        "interview_focus": "文化匹配度面试 + 稳定性评估 + 价值观考察",
        "key_questions": [
            "为什么选择我们公司，而不是其他更新潮的企业？",
            "您的5-10年职业规划是什么？",
            "您如何看待企业的传统管理模式和企业文化？",
            "请谈谈您对工作稳定性和跳槽的看法"
        ],
        "success_probability": 70,
        "cultural_fit_tests": ["团队协作测试", "价值观匹配评估", "压力承受能力测试"]
    }},
    "hr_comments": "从传统企业的角度来看，候选人总体得分{overall_score}分，教育背景和工作稳定性是其主要优势。但我们需要特别关注其是否能够适应我们的企业文化。建议在面试中重点考察其文化匹配度和长期发展意愿。",
    "long_term_potential": "候选人展现出良好的稳定性，有潜力成为企业的长期骨干员工，但需要在企业文化适应方面给予更多关注和培养。",
    "onboarding_recommendations": "建议安排资深员工作为导师，帮助其更好地融入企业文化，并提供传统行业的深度培训。"
}}
            """,
            "weights": {
                "education_background": 0.30,
                "work_stability": 0.25,
                "culture_fit": 0.20,
                "basic_skills": 0.15,
                "character_assessment": 0.10
            },
            "pass_threshold": 75,
            "personality_traits": ["保守", "稳健", "重视传统", "注重文化匹配"]
        },
        
        "progressive": {
            "name": "开放型HR经理",
            "description": "现代化企业的HR，看重潜力、学习能力和创新思维",
            "prompt_template": """
你是一家现代化、快速发展企业的HR经理，拥有开放包容的招聘理念。你更看重候选人的潜力、学习能力和创新思维，而不仅仅是现有的经验。

## 你的评估风格：
- 重视学习能力和成长潜力胜过现有经验
- 欣赏有创新思维和跨界经验的候选人
- 关注候选人的适应性和灵活性
- 看重个人品质和软技能
- 对多元化背景持开放态度

## 评估标准和权重：
1. **学习能力与潜力** (30%) - 学习速度、适应能力、成长轨迹
2. **创新思维** (25%) - 创新项目、解决问题能力、思维活跃度
3. **适应性与灵活性** (20%) - 环境适应、角色转换、变化接受度
4. **软技能** (15%) - 沟通能力、团队协作、领导力潜质
5. **技能匹配度** (10%) - 当前技能与岗位匹配程度

## 面试邀请标准：
- 总分65分以上：有潜力，值得培养
- 总分55-64分：可以考虑，需要深入了解
- 总分55分以下：潜力不足，不予考虑

请以开放包容的态度评估以下候选人：

### 职位信息：
{job_posting}

### 候选人简历：
{resume_content}

请返回详细的评估报告：
{{
    "overall_score": 78,
    "passes_initial_screening": true,
    "detailed_scores": {{
        "learning_potential": 85,
        "innovation_thinking": 80,
        "adaptability": 90,
        "soft_skills": 75,
        "current_skills_match": 70
    }},
    "strengths": ["学习能力强，快速适应新环境", "有跨界经验，思维活跃", "适应性好，能够快速转换角色"],
    "weaknesses": ["当前技能与岗位匹配度略有不足", "缺少某个特定领域的深度经验"],
    "detailed_analysis": {{
        "potential_analysis": "学习潜力和成长性评估：候选人学习潜力得分{learning_potential}分...",
        "innovation_analysis": "创新思维和解决问题能力分析：创新思维评分{innovation_thinking}分...",
        "adaptability_analysis": "适应性和灵活性评估：适应性得分{adaptability}分...",
        "soft_skills_analysis": "软技能和个人素质分析：软技能评分{soft_skills}分..."
    }},
    "growth_opportunities": [
        "可以在技术深度方面快速成长，通过项目实践提升",
        "适合承担跨部门协作和创新项目的责任",
        "有潜力发展成为团队leader或产品经理",
        "可以成为公司文化变革和创新的推动者"
    ],
    "improvement_suggestions": [
        "建议通过在线课程或实战项目补强特定技能领域",
        "参与更多创新项目来展示和提升解决问题的能力",
        "加强与目标岗位相关的专业知识学习",
        "寻找导师或加入专业社群来加速成长"
    ],
    "diversity_value": "候选人的多元化背景能为团队带来新的视角和创新思维，有助于公司文化的多样性发展",
    "interview_recommendation": {{
        "should_interview": true,
        "interview_style": "情景面试 + 潜力评估 + 创新思维测试",
        "focus_areas": [
            "学习能力验证：通过案例分析看学习速度",
            "创新思维测试：给出实际问题看解决方案",
            "适应性评估：了解面对变化的应对方式",
            "团队协作：评估软技能和沟通能力"
        ],
        "growth_potential_score": 85,
        "recommended_trial_period": "建议3个月试用期，重点观察学习成长速度"
    }},
    "hr_comments": "这位候选人虽然经验不是最丰富，但展现出了很强的学习能力和创新潜力，总体得分{overall_score}分。我特别看好其适应性和成长潜力。在快速变化的市场环境中，这样的候选人往往能够带来意想不到的价值。建议给予机会并提供良好的成长环境。",
    "future_vision": "预期该候选人在我们公司能够快速成长，6个月内能够独当一面，1年内有潜力成为团队骨干，未来2-3年有望发展为管理层或技术专家。",
    "mentorship_plan": "建议安排经验丰富的导师进行指导，制定个性化的成长计划，定期评估进展并调整培养方向。"
}}
            """,
            "weights": {
                "learning_potential": 0.30,
                "innovation_thinking": 0.25,
                "adaptability": 0.20,
                "soft_skills": 0.15,
                "current_skills_match": 0.10
            },
            "pass_threshold": 65,
            "personality_traits": ["开放", "包容", "重视潜力", "鼓励创新"]
        },
        
        "technical": {
            "name": "技术型HR专家",
            "description": "具有技术背景的HR，专注技术技能、项目经验和技术深度",
            "prompt_template": """
你是一位具有深厚技术背景的HR专家，曾经是资深技术人员转型做HR。你深刻理解技术岗位的需求，能够准确评估技术候选人的能力水平。

## 你的评估风格：
- 深度关注技术技能的实际水平和应用能力
- 重视项目经验的技术含量和复杂度
- 了解技术发展趋势，看重技术前瞻性
- 能够识别技术深度和广度的平衡
- 注重技术问题的解决思路和方法

## 评估标准和权重：
1. **技术深度与专业度** (35%) - 核心技术掌握程度、技术深度
2. **项目技术含量** (25%) - 项目复杂度、技术挑战、解决方案
3. **技术广度与学习能力** (20%) - 技术栈覆盖、新技术学习
4. **技术实践经验** (15%) - 实际开发经验、踩坑经历、优化经验
5. **技术前瞻性** (5%) - 对新技术的关注度、技术趋势把握

## 面试邀请标准：
- 总分80分以上：技术大牛，强烈推荐
- 总分70-79分：技术能力合格，推荐面试
- 总分70分以下：技术能力不足，不建议面试

请以技术专家的角度深度评估以下候选人：

### 职位信息：
{job_posting}

### 候选人简历：
{resume_content}

请返回详细的技术评估报告：
{{
    "overall_score": 82,
    "passes_initial_screening": true,
    "detailed_scores": {{
        "technical_depth": 85,
        "project_complexity": 90,
        "technical_breadth": 80,
        "practical_experience": 85,
        "technical_vision": 75
    }},
    "strengths": ["核心技术扎实，有深度", "项目经验丰富，参与过大型复杂项目", "技术栈完整，覆盖面广"],
    "weaknesses": ["缺少某项前沿技术经验", "分布式系统经验略有不足", "开源贡献相对较少"],
    "detailed_analysis": {{
        "technical_depth_analysis": "核心技术能力深度分析：候选人在核心技术方面得分{technical_depth}分，展现出扎实的技术功底...",
        "project_analysis": "项目技术含量和复杂度评估：项目复杂度评分{project_complexity}分，参与的项目具有较高技术含量...",
        "learning_analysis": "技术学习能力和适应性分析：技术广度评分{technical_breadth}分，表现出良好的学习能力...",
        "experience_analysis": "实践经验和解决问题能力评估：实践经验得分{practical_experience}分，具备丰富的实战经验..."
    }},
    "technical_highlights": [
        "参与过百万级用户的大型项目开发",
        "具备系统架构设计和性能优化经验",
        "有跨团队技术协作和技术选型经验"
    ],
    "technical_gaps": [
        "需要补强云原生技术栈，如Kubernetes、Docker",
        "建议学习最新的微服务架构模式",
        "可以增加开源项目贡献来提升技术影响力",
        "需要加强大数据处理相关技术"
    ],
    "architecture_capability": "具备一定的架构设计能力，能够设计中等复杂度的系统架构，但在大型分布式系统架构方面需要进一步提升",
    "code_quality_assessment": "从项目经验看，代码质量意识较强，注重工程化实践，但建议在代码review和测试覆盖率方面加强",
    "interview_recommendation": {{
        "should_interview": true,
        "interview_type": "深度技术面试 + 架构设计面试 + 代码实战",
        "technical_questions": [
            "请详细介绍您最复杂的项目架构设计和技术选型理由",
            "如何解决高并发场景下的性能瓶颈问题",
            "您认为当前技术栈的发展趋势是什么",
            "请描述一次您解决的最有挑战性的技术问题"
        ],
        "hands_on_test": "建议进行2小时的算法编程测试和系统设计测试",
        "technical_fit_score": 85,
        "recommended_team": "适合加入核心技术团队或架构组"
    }},
    "growth_potential": {{
        "current_level": "高级工程师水平",
        "promotion_potential": "有架构师潜力，建议1-2年内培养成技术专家",
        "learning_curve": "学习能力强，预期6个月内能够掌握新技术栈",
        "leadership_potential": "技术领导力有待培养，可以从技术小组负责人开始"
    }},
    "hr_comments": "从技术角度来看，这位候选人具备扎实的技术基础和丰富的项目经验，总体评分{overall_score}分。特别是在核心技术和项目复杂度方面表现优秀。建议重点关注其技术深度和解决问题的能力。这样的候选人能够为技术团队带来实质性的价值贡献。",
    "technical_recommendation": "强烈推荐加入技术团队。建议安排技术总监进行最终面试，重点验证架构设计能力和技术leadership潜力。入职后可以考虑安排到核心项目组或新技术预研团队。",
    "salary_benchmark": "基于其技术水平，薪资定位应在同级别技术人员的上游水平，有一定的议价空间。"
}}
            """,
            "weights": {
                "technical_depth": 0.35,
                "project_complexity": 0.25,
                "technical_breadth": 0.20,
                "practical_experience": 0.15,
                "technical_vision": 0.05
            },
            "pass_threshold": 75,
            "personality_traits": ["技术导向", "严谨", "关注实践", "追求深度"]
        }
    }
    
    @staticmethod
    def simulate_hr_review(resume_content: Dict[str, Any], job_posting: Dict[str, Any], 
                          hr_persona: str = "experienced") -> Dict[str, Any]:
        """Simulate HR review of resume with detailed personas."""
        try:
            import time
            import json
            import re
            from datetime import datetime
            
            # 确保输入参数是字典格式
            resume_content = ensure_dict(resume_content)
            job_posting = ensure_dict(job_posting)
            
            logger.info(f"Simulating {hr_persona} HR review for {safe_get(job_posting, 'company_name', 'Unknown')} position")
            
            # 获取HR人设配置
            if hr_persona not in Phase3HRAgent.HR_PERSONAS:
                hr_persona = "experienced"
            
            persona_config = Phase3HRAgent.HR_PERSONAS[hr_persona]
             # 提取岗位元数据
            job_title = job_posting.get("job_title", "")
            company_name = job_posting.get("company_name", "")
            requirements = job_posting.get("requirements", [])
            skills = job_posting.get("skills", [])
            description = job_posting.get("description", "")
            industry = job_posting.get("industry", "")
            company_size = job_posting.get("company_size", "")
            salary_range = job_posting.get("salary_range", "")

            # 精心设计的评估提示词
            comprehensive_prompt = f"""
你是一位{persona_config['name']}，{persona_config['description']}。
请以专业HR的身份，对以下候选人进行全面、深入、细致的评估分析。

【重要：请确保全部回复内容都使用简体中文，禁止使用英文或其他语言】

## 候选人简历信息：
{json.dumps(resume_content, ensure_ascii=False, indent=2)}

## 目标职位信息：
{json.dumps(job_posting, ensure_ascii=False, indent=2)}

## 目标职位信息（请重点参考以下内容进行评分和分析）：
- 公司名称：{company_name}
- 职位名称：{job_title}
- 行业：{industry}
- 公司规模：{company_size}
- 薪资范围：{salary_range}
- 职位描述：{description}
- 岗位要求：{json.dumps(requirements, ensure_ascii=False)}
- 技能要求：{json.dumps(skills, ensure_ascii=False)}

## 评估权重标准：
作为{persona_config['name']}，请严格按照以下权重进行评估：
{chr(10).join([f"- {key}: {int(weight*100)}%" for key, weight in persona_config['weights'].items()])}

## 详细评估要求：

### 1. 工作经验分析（字数要求：不少于100字）
请从以下角度深入分析：
- 工作经历与目标职位的匹配程度（具体说明哪些经历匹配，哪些不匹配）
- 职业发展轨迹和稳定性（分析跳槽频率、职业成长路径、（如是否有与{company_name}类似企业的工作经历）
- 具体工作成果和业绩表现（量化成果，突出亮点）
- 行业经验和领域专业度（分析是否有相关行业背景）

### 2. 技能评价分析（字数要求：不少于100字）
请从以下角度深入分析：
- 技能与岗位需求的匹配度（逐项对比技能要求，如是否掌握{skills}等关键技能）
- 核心技能的掌握深度和应用水平（评估技能熟练程度）
- 技术栈的完整性和先进性（分析技术栈是否跟得上行业发展）
- 学习能力和技术发展潜力（评估持续学习和技术更新能力）

### 3. 教育背景分析（字数要求：不少于100字）
请从以下角度深入分析：
- 学历层次与职位要求的匹配性（本科/硕士/博士等，如是否满足{requirements}中的学历要求）
- 专业背景与工作领域的相关性（专业知识基础）
- 院校声誉和教育质量评估（是否来自知名院校）
- 教育经历对职业发展的支撑作用（理论基础是否扎实）

### 4. 综合评价（字数要求：不少于300字）
请提供全面深入的综合评价，包括：
- 候选人的整体素质和综合能力评估
- 全面评估候选人与{company_name}的{job_title}职位的整体匹配度
- 与目标职位的整体匹配度分析
- 候选人的核心竞争优势和独特价值
- 存在的主要不足和改进空间
- 在团队中可能发挥的作用和贡献
- 职业发展潜力和成长空间评估
- 是否适合公司文化和团队氛围
- 最终录用建议和原因分析

### 5. 评分计算要求：
- 请严格按照权重标准计算总分
- 各维度评分要有明确依据
- 总分 = Σ(各维度分数 × 对应权重)
- 评分范围：0-100分

请返回完整的JSON格式评估结果，必须包含以下字段：
{{
    "overall_score": 总体评分（0-100，严格按权重计算）,
    "passes_initial_screening": 是否通过初筛（true/false）,
    "detailed_scores": {{
        各维度详细评分（对应persona权重配置）
    }},
    "strengths": ["候选人优势1", "候选人优势2", ...],
    "weaknesses": ["候选人不足1", "候选人不足2", ...],
    "detailed_analysis": {{
        "experience_analysis": "工作经验深度分析（不少于100字）",
        "skills_analysis": "技能评价深度分析（不少于100字）", 
        "education_analysis": "教育背景深度分析（不少于100字）"
    }},
    "comprehensive_feedback": {{
        "description": "综合评价描述（不少于300字）",
        "recommendation": "最终建议"
    }},
    "improvement_suggestions": ["改进建议1", "改进建议2", ...],
    "interview_recommendation": {{
        "should_interview": true/false,
        "interview_type": "面试类型",
        "focus_areas": ["重点关注领域1", "重点关注领域2", ...],
        "preparation_notes": "面试准备说明"
    }},
    "hr_comments": "HR专业评价和最终意见"
}}

【再次强调：所有内容必须使用简体中文，严格遵守字数要求，确保分析深度和专业性】
"""
            
            # Get HR feedback
            start_time = time.time()
            hr_result = llm_service.call_phase3_model(comprehensive_prompt)
            generation_time = time.time() - start_time
            
            # Parse feedback
            feedback_content = Phase3HRAgent._parse_and_validate_feedback(
                hr_result, persona_config, hr_persona, resume_content, job_posting
            )
            
            return {
                "success": True,
                "message": f"{persona_config['name']}评估完成",
                "data": {
                    "feedback": feedback_content,
                    "hr_persona": hr_persona,
                    "hr_info": {
                        "name": persona_config["name"],
                        "description": persona_config["description"],
                        "personality_traits": persona_config["personality_traits"],
                        "pass_threshold": persona_config["pass_threshold"]
                    },
                    "evaluation_weights": persona_config["weights"],
                    "company_name": safe_get(job_posting, 'company_name', ''),
                    "job_title": safe_get(job_posting, 'job_title', ''),
                    "generation_time": generation_time,
                    "model_used": "phase3_model",
                    "review_date": datetime.now().isoformat()
                }
            }
                
        except Exception as e:
            logger.error(f"Error in HR simulation: {e}")
            try:
                persona_config = Phase3HRAgent.HR_PERSONAS.get(hr_persona, Phase3HRAgent.HR_PERSONAS["experienced"])
                default_feedback = Phase3HRAgent._create_default_feedback(persona_config, hr_persona, resume_content, job_posting)
                
                return {
                    "success": True,
                    "message": f"HR评估完成（使用备用评估）",
                    "data": {
                        "feedback": default_feedback,
                        "hr_persona": hr_persona,
                        "hr_info": {
                            "name": persona_config["name"],
                            "description": persona_config["description"],
                            "personality_traits": persona_config["personality_traits"],
                            "pass_threshold": persona_config["pass_threshold"]
                        },
                        "evaluation_weights": persona_config["weights"],
                        "company_name": safe_get(job_posting, 'company_name', ''),
                        "job_title": safe_get(job_posting, 'job_title', ''),
                        "generation_time": 0,
                        "model_used": "fallback_template",
                        "review_date": datetime.now().isoformat(),
                        "error_handled": str(e)
                    }
                }
            except:
                return {
                    "success": False,
                    "message": f"HR simulation failed: {str(e)}",
                    "data": {"error_type": type(e).__name__, "error_detail": str(e)}
                }

    @staticmethod
    def _parse_and_validate_feedback(hr_result: str, persona_config: Dict[str, Any], 
                                   hr_persona: str, resume_content: Dict[str, Any], 
                                   job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """解析和验证HR评估结果"""
        import re
        import json
        
        try:
            # 尝试从LLM结果中提取JSON
            json_match = re.search(r'\{.*\}', hr_result, re.DOTALL)
            if json_match:
                feedback_content = json.loads(json_match.group())
                
                # 验证必要字段并修复
                feedback_content = Phase3HRAgent._validate_and_fix_feedback(
                    feedback_content, persona_config, hr_persona, resume_content, job_posting
                )
                
                return feedback_content
            else:
                logger.warning("无法从LLM结果中解析JSON，使用智能备用方案")
                return Phase3HRAgent._create_default_feedback(
                    persona_config, hr_persona, resume_content, job_posting
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return Phase3HRAgent._create_default_feedback(
                persona_config, hr_persona, resume_content, job_posting
            )
        except Exception as e:
            logger.error(f"解析过程出错: {e}")
            return Phase3HRAgent._create_default_feedback(
                persona_config, hr_persona, resume_content, job_posting
            )

    @staticmethod
    def _validate_and_fix_feedback(feedback_content: Dict[str, Any], persona_config: Dict[str, Any], 
                                 hr_persona: str, resume_content: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修复反馈内容，确保所有必需字段存在"""
        weights = persona_config["weights"]
        detailed_scores = feedback_content.get("detailed_scores", {})
        
        # 确保所有权重键都有对应的分数
        for weight_key in weights.keys():
            if weight_key not in detailed_scores:
                # 基于简历内容生成智能默认分数
                default_score = Phase3HRAgent._generate_intelligent_score(weight_key, resume_content, job_posting)
                detailed_scores[weight_key] = default_score
                logger.info(f"Generated intelligent score for {weight_key}: {default_score} (HR persona: {hr_persona})")
            else:
                logger.info(f"Using provided score for {weight_key}: {detailed_scores[weight_key]} (HR persona: {hr_persona})")
        
        # 重新计算总分（严格按照权重）
        weighted_score = 0
        total_weight = 0
        
        logger.info(f"计算加权分数，权重配置: {weights}")
        logger.info(f"详细分数: {detailed_scores}")
        
        for weight_key, weight_value in weights.items():
            raw_score = detailed_scores.get(weight_key, 60)
            
            # 确保分数是数字类型
            try:
                if isinstance(raw_score, dict):
                    # 如果是字典，尝试提取数字值
                    if 'score' in raw_score:
                        score = float(raw_score['score'])
                    elif 'value' in raw_score:
                        score = float(raw_score['value'])
                    else:
                        # 如果无法提取，使用默认值
                        logger.warning(f"Score for {weight_key} is a dict without 'score' or 'value' key: {raw_score}")
                        score = 60
                        detailed_scores[weight_key] = score  # 更新为数字值
                elif isinstance(raw_score, (int, float)):
                    score = float(raw_score)
                elif isinstance(raw_score, str):
                    # 尝试从字符串中提取数字
                    import re
                    number_match = re.search(r'\d+(?:\.\d+)?', raw_score)
                    if number_match:
                        score = float(number_match.group())
                    else:
                        score = 60
                        logger.warning(f"Could not extract number from string score for {weight_key}: {raw_score}")
                    detailed_scores[weight_key] = score  # 更新为数字值
                else:
                    score = 60
                    logger.warning(f"Unexpected score type for {weight_key}: {type(raw_score)} = {raw_score}")
                    detailed_scores[weight_key] = score  # 更新为数字值
                    
                # 确保分数在合理范围内
                score = max(0, min(100, score))
                detailed_scores[weight_key] = score  # 确保存储的是清理后的数字值
                
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting score for {weight_key}: {e}, using default score 60")
                score = 60
                detailed_scores[weight_key] = score
            
            contribution = score * weight_value
            weighted_score += contribution
            total_weight += weight_value
            logger.info(f"{weight_key}: 分数={score}, 权重={weight_value}, 贡献={contribution:.2f}")
        
        # 确保权重总和为1，如果不是则标准化
        if total_weight > 0:
            final_score = round(weighted_score / total_weight)
        else:
            final_score = 60
        
        logger.info(f"最终计算分数: {weighted_score:.2f} / {total_weight:.2f} = {final_score}")
        
        # 确保分数在有效范围内
        final_score = max(0, min(100, final_score))
        
        # 更新反馈内容
        feedback_content["detailed_scores"] = detailed_scores
        feedback_content["overall_score"] = final_score
        feedback_content["passes_initial_screening"] = final_score >= persona_config["pass_threshold"]
        
        # 最终验证：确保详细分数包含所有必需的字段
        missing_fields = []
        for weight_key in weights.keys():
            if weight_key not in feedback_content["detailed_scores"]:
                missing_fields.append(weight_key)
        
        if missing_fields:
            logger.warning(f"Final validation failed: missing detailed_scores fields {missing_fields} for HR persona {hr_persona}")
            # 补充缺失的字段
            for field in missing_fields:
                feedback_content["detailed_scores"][field] = Phase3HRAgent._generate_intelligent_score(field, resume_content, job_posting)
        
        logger.info(f"Final detailed_scores for {hr_persona}: {feedback_content['detailed_scores']}")
        
        # 确保关键字段存在并有实质内容
        if not feedback_content.get("strengths"):
            feedback_content["strengths"] = Phase3HRAgent._generate_strengths(resume_content, job_posting, hr_persona)
        
        if not feedback_content.get("weaknesses"):
            feedback_content["weaknesses"] = Phase3HRAgent._generate_weaknesses(resume_content, job_posting, hr_persona)
        
        if not feedback_content.get("detailed_analysis"):
            feedback_content["detailed_analysis"] = Phase3HRAgent._generate_detailed_analysis(
                detailed_scores, weights, resume_content, job_posting, hr_persona
            )
        
        if not feedback_content.get("improvement_suggestions"):
            feedback_content["improvement_suggestions"] = Phase3HRAgent._generate_improvement_suggestions(
                resume_content, job_posting, hr_persona
            )
        
        if not feedback_content.get("hr_comments"):
            feedback_content["hr_comments"] = Phase3HRAgent._generate_hr_comments(
                final_score, persona_config, resume_content, job_posting
            )
        
        return feedback_content

    @staticmethod
    def _generate_intelligent_score(metric: str, resume_content: Dict[str, Any], job_posting: Dict[str, Any]) -> int:
        """基于简历内容和职位要求生成智能评分"""
        base_score = 60
        
        # 确保输入参数是字典格式
        resume_content = ensure_dict(resume_content)
        job_posting = ensure_dict(job_posting)
        
        # 获取基础数据
        experience = safe_get(resume_content, "experience", [])
        skills = safe_get(resume_content, "skills", [])
        education = safe_get(resume_content, "education", [])
        projects = safe_get(resume_content, "projects", [])
        
        # 根据不同评估维度调整分数
        
        # === 经验丰富HR的字段 ===
        if metric == "experience_match":
            if len(experience) >= 3:
                base_score += 15
            elif len(experience) >= 1:
                base_score += 10
            
            # 检查经验相关性
            job_title = safe_get(job_posting, "job_title", "").lower()
            for exp in experience:
                exp_title = str(safe_get(exp, "position", "")).lower()
                if any(keyword in exp_title for keyword in ["开发", "工程师", "程序员", "技术"]):
                    base_score += 10
                    break
                    
        elif metric == "skills_proficiency":
            if len(skills) >= 8:
                base_score += 20
            elif len(skills) >= 5:
                base_score += 15
            elif len(skills) >= 3:
                base_score += 10
                
        elif metric == "performance_results":
            # 检查工作经验中是否有业绩描述
            for exp in experience:
                exp_desc = str(safe_get(exp, "description", "")).lower()
                if any(keyword in exp_desc for keyword in ["提升", "优化", "增长", "完成", "实现", "%"]):
                    base_score += 15
                    break
            
            # 检查项目经验
            if len(projects) >= 2:
                base_score += 10
                
        elif metric == "career_stability":
            # 职业稳定性评估
            if len(experience) >= 2:
                # 计算平均在职时长（简化评估）
                base_score += 10
            if len(experience) <= 3:  # 跳槽不频繁
                base_score += 10
                
        elif metric == "resume_professionalism":
            # 简历专业性评估
            if education and skills and experience:
                base_score += 15
            
        # === 保守型HR的字段 ===
        elif metric == "education_background":
            if education:
                edu_str = str(education).lower()
                if "硕士" in edu_str or "研究生" in edu_str:
                    base_score += 20
                elif "本科" in edu_str or "学士" in edu_str:
                    base_score += 15
                elif "专科" in edu_str:
                    base_score += 10
                    
        elif metric == "work_stability":
            # 工作稳定性（与career_stability类似）
            if len(experience) >= 2:
                base_score += 15
            if len(experience) <= 3:  # 跳槽不频繁
                base_score += 10
                
        elif metric == "culture_fit":
            # 企业文化匹配（基于经验和教育背景评估）
            if education:
                base_score += 10
            if len(experience) >= 2:
                base_score += 10
                
        elif metric == "basic_skills":
            # 基础技能
            if len(skills) >= 3:
                base_score += 15
            elif len(skills) >= 1:
                base_score += 10
                
        elif metric == "character_assessment":
            # 品格素养（基于整体简历完整性）
            if education and skills and experience:
                base_score += 15
            
        # === 开放型HR的字段 ===
        elif metric == "learning_potential":
            # 学习能力与潜力
            if len(skills) >= 5:  # 技能多样说明学习能力强
                base_score += 15
            if len(projects) >= 2:  # 项目经验多说明实践能力强
                base_score += 10
                
        elif metric == "innovation_thinking":
            # 创新思维
            if len(projects) >= 3:  # 项目经验丰富说明有创新实践
                base_score += 15
            # 检查是否有创新相关描述
            for proj in projects:
                proj_desc = str(safe_get(proj, "description", "")).lower()
                if any(keyword in proj_desc for keyword in ["创新", "优化", "改进", "设计", "架构"]):
                    base_score += 10
                    break
                    
        elif metric == "adaptability":
            # 适应性与灵活性
            if len(experience) >= 2:  # 多段经验说明适应性强
                base_score += 10
            if len(skills) >= 6:  # 技能多样说明适应性强
                base_score += 10
                
        elif metric == "soft_skills":
            # 软技能
            if len(experience) >= 2:  # 工作经验多说明软技能好
                base_score += 10
            if len(projects) >= 2:  # 项目经验说明协作能力
                base_score += 10
                
        elif metric == "current_skills_match":
            # 当前技能匹配度
            if len(skills) >= 5:
                base_score += 15
            elif len(skills) >= 3:
                base_score += 10
            
        # === 技术型HR的字段 ===
        elif metric == "technical_depth":
            # 技术深度与专业度
            tech_skills = [s for s in skills if any(keyword in str(s).lower() 
                          for keyword in ["java", "python", "javascript", "react", "vue", "spring", "mysql", "redis"])]
            if len(tech_skills) >= 5:
                base_score += 20
            elif len(tech_skills) >= 3:
                base_score += 15
                
        elif metric == "project_complexity":
            # 项目技术含量
            if len(projects) >= 3:
                base_score += 20
            elif len(projects) >= 2:
                base_score += 15
            elif len(projects) >= 1:
                base_score += 10
                
        elif metric == "technical_breadth":
            # 技术广度与学习能力
            if len(skills) >= 8:
                base_score += 20
            elif len(skills) >= 6:
                base_score += 15
                
        elif metric == "practical_experience":
            # 技术实践经验
            if len(experience) >= 2 and len(projects) >= 2:
                base_score += 20
            elif len(experience) >= 1 or len(projects) >= 1:
                base_score += 10
                
        elif metric == "technical_vision":
            # 技术前瞻性
            # 检查是否有新技术相关技能
            modern_tech = [s for s in skills if any(keyword in str(s).lower() 
                          for keyword in ["cloud", "docker", "kubernetes", "微服务", "分布式"])]
            if len(modern_tech) >= 2:
                base_score += 15
            elif len(modern_tech) >= 1:
                base_score += 10
                
        # === 通用字段处理（兼容其他可能的字段名） ===
        elif "experience" in metric.lower():
            # 工作经验相关的通用处理
            if len(experience) >= 3:
                base_score += 15
            elif len(experience) >= 1:
                base_score += 10
        
        elif "skill" in metric.lower():
            # 技能相关的通用处理
            if len(skills) >= 8:
                base_score += 20
            elif len(skills) >= 5:
                base_score += 15
            elif len(skills) >= 3:
                base_score += 10
        
        elif "education" in metric.lower():
            # 教育背景相关的通用处理
            if education:
                edu_str = str(education).lower()
                if "硕士" in edu_str or "研究生" in edu_str:
                    base_score += 20
                elif "本科" in edu_str or "学士" in edu_str:
                    base_score += 15
                elif "专科" in edu_str:
                    base_score += 10
        
        # 确保分数在合理范围内
        return min(95, max(40, base_score))

    @staticmethod
    def _generate_strengths(resume_content: Dict[str, Any], job_posting: Dict[str, Any], hr_persona: str) -> List[str]:
        """生成优势分析"""
        strengths = []
        
        # 基于工作经验
        experience = resume_content.get("experience", [])
        if len(experience) >= 2:
            strengths.append(f"拥有{len(experience)}段工作经验，展现了良好的职业发展轨迹")
        
        # 基于技能
        skills = resume_content.get("skills", [])
        if len(skills) >= 5:
            strengths.append(f"技能栈较为丰富，掌握{len(skills)}项专业技能")
        
        # 基于项目经验
        projects = resume_content.get("projects", [])
        if len(projects) >= 2:
            strengths.append(f"项目经验丰富，参与过{len(projects)}个项目的开发")
        
        # 基于教育背景
        education = resume_content.get("education", [])
        if education:
            strengths.append("具备良好的教育背景，专业基础扎实")
        
        # 如果没有找到优势，添加默认优势
        if not strengths:
            strengths = [
                "简历信息相对完整，基本符合岗位要求",
                "展现了一定的学习能力和工作热情",
                "具备进一步发展的潜力"
            ]
        
        return strengths[:3]  # 最多返回3个优势

    @staticmethod
    def _generate_weaknesses(resume_content: Dict[str, Any], job_posting: Dict[str, Any], hr_persona: str) -> List[str]:
        """生成不足分析"""
        weaknesses = []
        
        # 检查工作经验
        experience = resume_content.get("experience", [])
        if len(experience) < 2:
            weaknesses.append("工作经验相对较少，需要在实践中进一步积累")
        
        # 检查技能匹配度
        job_requirements = job_posting.get("requirements", "")
        resume_skills = resume_content.get("skills", [])
        if len(resume_skills) < 5:
            weaknesses.append("技能栈需要进一步扩充，特别是核心专业技能")
        
        # 检查项目经验
        projects = resume_content.get("projects", [])
        if len(projects) < 2:
            weaknesses.append("项目经验较少，建议补充更多实际项目案例")
        
        # HR人设特定的不足分析
        if hr_persona == "conservative":
            weaknesses.append("需要更明确地展示工作稳定性和长期职业规划")
        elif hr_persona == "technical":
            weaknesses.append("技术深度描述不够详细，建议补充具体的技术成果")
        
        # 如果没有找到明显不足，添加通用改进建议
        if not weaknesses:
            weaknesses = [
                "简历表述可以更加具体和量化",
                "建议补充更多具体的工作成果和数据支撑",
                "可以进一步优化简历格式和关键词"
            ]
        
        return weaknesses[:3]  # 最多返回3个不足

    @staticmethod
    def _generate_detailed_analysis(detailed_scores: Dict[str, int], weights: Dict[str, float], 
                                   resume_content: Dict[str, Any], job_posting: Dict[str, Any], hr_persona: str) -> Dict[str, str]:
        """生成详细分析（确保每项分析不少于100字）"""
        analysis = {}
        
        # 确保输入参数是字典格式
        resume_content = ensure_dict(resume_content)
        job_posting = ensure_dict(job_posting)
        
        # 安全地提取数字分数的辅助函数
        def safe_get_score(scores_dict, key, default=60):
            """安全地从scores字典中提取数字分数"""
            value = scores_dict.get(key, default)
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, dict):
                # 如果是字典，尝试提取数字值
                if 'score' in value:
                    return value['score'] if isinstance(value['score'], (int, float)) else default
                elif 'value' in value:
                    return value['value'] if isinstance(value['value'], (int, float)) else default
                else:
                    return default
            elif isinstance(value, str):
                # 尝试从字符串中提取数字
                import re
                number_match = re.search(r'\d+(?:\.\d+)?', value)
                return float(number_match.group()) if number_match else default
            else:
                return default
        
        # 工作经验分析（不少于100字）
        experience_score = safe_get_score(detailed_scores, "experience_match", 
                                        safe_get_score(detailed_scores, "work_experience", 60))
        experience_data = safe_get(resume_content, "experience", [])
        
        experience_analysis = f"""工作经验评估得分{experience_score}分。候选人拥有{len(experience_data)}段工作经历，"""
        
        if len(experience_data) >= 3:
            experience_analysis += """展现了丰富的职业发展历程和良好的工作稳定性。从工作经历来看，候选人在不同岗位上都积累了宝贵经验，具备了较强的适应能力和学习能力。工作轨迹显示出明确的职业发展方向，每一段经历都为下一步发展奠定了基础。特别是在核心技能和业务理解方面，通过多年的实践积累，已经形成了较为成熟的工作方法和解决问题的思路。"""
        elif len(experience_data) >= 1:
            experience_analysis += """虽然工作经验相对有限，但在已有的工作经历中表现出了一定的专业能力和成长潜力。从简历描述可以看出，候选人在工作中能够承担相应职责，完成既定目标，并在实践中不断学习和提升。虽然经验深度有待进一步积累，但展现出的学习态度和工作热情值得肯定。建议在后续工作中继续深化专业技能，扩大知识面。"""
        else:
            experience_analysis += """目前缺乏正式的工作经验，这在一定程度上限制了对其实际工作能力的评估。但从教育背景和其他经历来看，候选人具备了基本的理论基础和学习能力。建议通过实习、项目参与等方式积累实践经验，逐步建立职业技能体系。对于入门级岗位，重点关注其学习能力和发展潜力。"""
        
        analysis["experience_analysis"] = experience_analysis
        
        # 技能评价分析（不少于100字）
        skills_score = safe_get_score(detailed_scores, "skills_proficiency", 
                                    safe_get_score(detailed_scores, "technical_skills", 60))
        skills_data = safe_get(resume_content, "skills", [])
        
        skills_analysis = f"""技能评价得分{skills_score}分。候选人掌握了{len(skills_data)}项专业技能，"""
        
        if len(skills_data) >= 8:
            skills_analysis += """技能栈相当丰富，覆盖了从基础技术到高级应用的各个层面。从技能构成来看，既有扎实的基础技能，也有紧跟行业发展趋势的新兴技术，显示出持续学习和技术更新的能力。技能之间的搭配较为合理，能够形成完整的技术解决方案。在实际工作中，这样的技能结构能够很好地支撑复杂项目的开发和维护，具备了承担核心技术工作的能力基础。"""
        elif len(skills_data) >= 5:
            skills_analysis += """技能覆盖了主要的专业领域，基本满足岗位要求。从技能列表可以看出，候选人在核心技术方面有一定积累，具备了处理常规工作任务的能力。不过在技能深度和广度方面还有进一步提升的空间，特别是在一些前沿技术和高级应用方面。建议在现有技能基础上，继续深化核心技能的掌握程度，同时关注行业技术发展趋势。"""
        else:
            skills_analysis += """目前掌握的技能相对有限，可能难以完全满足岗位的技术要求。虽然具备了一些基础技能，但在技能的深度和广度方面都需要大幅提升。建议制定系统的学习计划，重点补强核心专业技能，同时扩展相关技术栈。可以通过在线课程、实践项目、技术社区参与等方式加快技能积累的步伐。"""
        
        analysis["skills_analysis"] = skills_analysis
        
        # 教育背景分析（不少于100字）
        education_score = safe_get_score(detailed_scores, "education_background", 
                                       safe_get_score(detailed_scores, "education", 60))
        education_data = safe_get(resume_content, "education", [])
        
        education_analysis = f"""教育背景评估得分{education_score}分。"""
        
        if education_data:
            education_str = str(education_data).lower()
            if "硕士" in education_str or "研究生" in education_str:
                education_analysis += """候选人具备硕士研究生学历，展现了较强的学习能力和理论基础。研究生阶段的学习经历不仅提供了扎实的专业知识基础，更重要的是培养了独立思考、问题分析和解决的能力。这样的教育背景为职业发展提供了良好的起点，在面对复杂工作任务时能够运用理论知识指导实践，具备了持续学习和自我提升的基础。高等教育经历也培养了良好的学习习惯和方法，这对于快速适应新环境和掌握新技能具有重要意义。"""
            elif "本科" in education_str or "学士" in education_str:
                education_analysis += """候选人具备本科学历，获得了完整的高等教育，建立了较为扎实的专业基础。大学四年的学习经历不仅传授了专业知识，也培养了系统性思维和解决问题的能力。从教育背景来看，候选人具备了胜任专业工作的基本理论基础，在学习能力和知识结构方面达到了一定水平。建议在实际工作中继续深化专业应用，将理论知识与实践相结合，形成更加完善的职业能力体系。"""
            else:
                education_analysis += """候选人完成了相应的教育阶段，获得了基本的专业知识和技能基础。虽然学历层次可能不是最高，但重要的是在学习过程中培养的学习能力和专业素养。在实际工作中，学历只是起点，更重要的是持续学习和实践能力。建议通过在职学习、专业培训等方式继续提升学历水平和专业能力，同时在实际工作中积累经验，弥补理论基础的不足。"""
        else:
            education_analysis += """简历中教育背景信息相对有限，这可能影响对候选人理论基础和学习能力的全面评估。建议候选人补充完整的教育经历信息，包括学历层次、专业背景、主修课程等。同时，如果有相关的职业培训、认证考试等学习经历，也应该在简历中体现，以便HR能够更全面地了解其知识结构和学习能力。"""
        
        analysis["education_analysis"] = education_analysis
        
        return analysis

    @staticmethod
    def _analyze_experience(resume_content: Dict[str, Any]) -> str:
        """分析工作经验"""
        experience = resume_content.get("experience", [])
        if not experience:
            return "暂无相关工作经验"
        elif len(experience) == 1:
            return "有一段工作经验，为职业发展奠定了基础"
        elif len(experience) <= 3:
            return "具有多段工作经验，展现了良好的职业发展轨迹"
        else:
            return "拥有丰富的工作经验，职业经历较为完整"

    @staticmethod
    def _analyze_skills(resume_content: Dict[str, Any]) -> str:
        """分析技能构成"""
        skills = resume_content.get("skills", [])
        if not skills:
            return "技能信息需要补充完善"
        elif len(skills) <= 3:
            return "掌握基本的专业技能"
        elif len(skills) <= 6:
            return "具备较为全面的技能体系"
        else:
            return "技能栈丰富，覆盖面较广"

    @staticmethod
    def _analyze_education(resume_content: Dict[str, Any]) -> str:
        """分析教育背景"""
        education = resume_content.get("education", [])
        if not education:
            return "教育背景信息需要补充"
        
        edu_text = str(education).lower()
        if "硕士" in edu_text or "研究生" in edu_text:
            return "具有研究生学历，专业基础扎实"
        elif "本科" in edu_text or "学士" in edu_text:
            return "具有本科学历，教育背景良好"
        else:
            return "具备相应的教育背景"

    @staticmethod
    def _analyze_projects(resume_content: Dict[str, Any]) -> str:
        """分析项目经验"""
        projects = resume_content.get("projects", [])
        if not projects:
            return "建议补充更多项目经验"
        elif len(projects) == 1:
            return "有一定的项目经验"
        elif len(projects) <= 3:
            return "项目经验较为丰富"
        else:
            return "拥有大量项目实践经验"

    @staticmethod
    def _evaluate_skill_structure(score: int) -> str:
        """评估技能结构"""
        if score >= 80:
            return "完整且有深度"
        elif score >= 70:
            return "较为完整"
        elif score >= 60:
            return "基本合理"
        else:
            return "需要进一步完善"

    @staticmethod
    def _get_performance_level(score: int) -> str:
        """获取表现水平描述"""
        if score >= 80:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 60:
            return "中等"
        else:
            return "有待提升"

    @staticmethod
    def _generate_improvement_suggestions(resume_content: Dict[str, Any], job_posting: Dict[str, Any], hr_persona: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于工作经验的建议
        experience = resume_content.get("experience", [])
        if len(experience) < 2:
            suggestions.append("建议补充更多工作经验描述，详细说明工作职责和取得的成果")
        
        # 基于技能的建议
        skills = resume_content.get("skills", [])
        if len(skills) < 5:
            suggestions.append("建议完善技能清单，补充与目标职位相关的核心技能")
        
        # 基于项目的建议
        projects = resume_content.get("projects", [])
        if len(projects) < 2:
            suggestions.append("建议补充项目经验，详细描述项目背景、个人贡献和技术难点")
        
        # 通用建议
        suggestions.append("优化简历格式，确保关键信息突出，表述清晰专业")
        
        return suggestions[:4]  # 最多返回4个建议

    @staticmethod
    def _generate_hr_comments(final_score: int, persona_config: Dict[str, Any], 
                            resume_content: Dict[str, Any], job_posting: Dict[str, Any]) -> str:
        """生成HR评价"""
        hr_name = persona_config["name"]
        
        # 基础评价
        performance = "优秀" if final_score >= 80 else "良好" if final_score >= 70 else "中等" if final_score >= 60 else "有待提升"
        
        # 具体分析
        experience_count = len(resume_content.get("experience", []))
        skills_count = len(resume_content.get("skills", []))
        projects_count = len(resume_content.get("projects", []))
        
        experience_desc = f"工作经验方面，候选人有{experience_count}段经历" if experience_count > 0 else "工作经验相对有限"
        skills_desc = f"技能方面掌握{skills_count}项专业技能" if skills_count > 0 else "技能信息需要完善"
        
        # 录用建议
        recommendation = "推荐录用" if final_score >= persona_config["pass_threshold"] else "建议在完善相关能力后重新申请"
        
        return f"作为{hr_name}，我对这位候选人的综合评估为{final_score}分，表现{performance}。{experience_desc}，{skills_desc}。综合考虑候选人的整体素质和发展潜力，我{recommendation}。建议在面试中重点关注实际工作能力和学习适应性的验证。"

    @staticmethod
    def _create_default_feedback(persona_config: Dict[str, Any], hr_persona: str, 
                                resume_content: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """创建智能默认反馈"""
        weights = persona_config["weights"]
        
        # 为每个权重键生成智能分数
        detailed_scores = {}
        for weight_key in weights.keys():
            score = Phase3HRAgent._generate_intelligent_score(weight_key, resume_content, job_posting)
            # 确保分数是数字类型
            if not isinstance(score, (int, float)):
                logger.warning(f"Generated score for {weight_key} is not a number: {score}, using 60")
                score = 60
            detailed_scores[weight_key] = score
        
        # 计算总分
        try:
            weighted_score = sum(score * weight for score, weight in zip(detailed_scores.values(), weights.values()))
            final_score = round(weighted_score)
        except (TypeError, ValueError) as e:
            logger.error(f"Error calculating weighted score in default feedback: {e}")
            final_score = 60
        
        return {
            "overall_score": final_score,
            "passes_initial_screening": final_score >= persona_config["pass_threshold"],
            "detailed_scores": detailed_scores,
            "strengths": Phase3HRAgent._generate_strengths(resume_content, job_posting, hr_persona),
            "weaknesses": Phase3HRAgent._generate_weaknesses(resume_content, job_posting, hr_persona),
            "detailed_analysis": Phase3HRAgent._generate_detailed_analysis(detailed_scores, weights, resume_content, job_posting, hr_persona),
            "comprehensive_feedback": Phase3HRAgent._generate_comprehensive_feedback(final_score, resume_content, job_posting, hr_persona, persona_config),
            "improvement_suggestions": Phase3HRAgent._generate_improvement_suggestions(resume_content, job_posting, hr_persona),
            "specific_recommendations": {
                "skills_to_add": ["与岗位需求匹配的核心技能", "行业前沿技术技能", "软技能和沟通能力"],
                "experience_highlight": "重点突出与目标职位最相关的工作经验和项目成果",
                "format_improvements": ["使用更清晰的时间线格式", "添加量化的工作成果", "优化关键词使用"],
                "keyword_optimization": ["补充行业关键词", "添加技能关键词", "优化职位匹配词汇"]
            },
            "interview_recommendation": {
                "should_interview": final_score >= persona_config["pass_threshold"],
                "interview_type": "综合面试（技能+行为+文化匹配）",
                "focus_areas": ["技能深度验证", "项目经验了解", "学习能力评估"],
                "estimated_success_rate": min(85, final_score + 10),
                "key_questions": [
                    "请详细介绍您最有成就感的一个项目经验",
                    "您如何保持技能的持续更新和学习",
                    "您对这个职位和我们公司的了解程度如何"
                ],
                "preparation_advice": [
                    "准备具体的项目案例和成果数据",
                    "了解公司业务和行业发展趋势",
                    "准备技能相关的深度问题回答"
                ]
            },
            "hr_comments": Phase3HRAgent._generate_hr_comments(final_score, persona_config, resume_content, job_posting),
            "risk_assessment": "中等风险" if final_score >= 65 else "较高风险，建议深入面试验证能力",
            "salary_negotiation_advice": f"基于评估结果，建议薪资谈判空间为{'15-20%' if final_score >= 80 else '10-15%' if final_score >= 70 else '5-10%'}",
            "development_potential": "具备良好的发展潜力，建议提供相应的培训和成长机会" if final_score >= 65 else "需要更多的指导和培养来达到岗位要求"
        }

    @staticmethod
    def _generate_comprehensive_feedback(final_score: int, resume_content: Dict[str, Any], 
                                        job_posting: Dict[str, Any], hr_persona: str, persona_config: Dict[str, Any]) -> Dict[str, str]:
        """生成综合评价（不少于300字）"""
        
        # 确保输入参数是字典格式
        resume_content = ensure_dict(resume_content)
        job_posting = ensure_dict(job_posting)
        
        company_name = safe_get(job_posting, 'company_name', '目标公司')
        job_title = safe_get(job_posting, 'job_title', '目标职位')
        
        # 根据分数区间生成不同的综合评价
        if final_score >= 80:
            description = f"""经过全面深入的评估分析，该候选人在各项评估维度上均表现出色，总体得分{final_score}分，属于优秀候选人行列。从工作经验来看，候选人具备了丰富的相关工作背景，其职业发展轨迹清晰合理，展现出良好的职业规划能力和执行力。在技能方面，候选人掌握的技能栈与{job_title}职位要求高度匹配，不仅具备扎实的核心技能基础，还紧跟行业发展趋势，展现出持续学习和自我提升的能力。教育背景为其专业能力提供了坚实的理论基础，良好的学习经历培养了其系统性思维和解决问题的能力。

从候选人的整体素质来看，其在专业能力、学习能力、适应能力等方面都达到了较高水平，具备了胜任{company_name}{job_title}职位的核心竞争力。特别值得关注的是，候选人在工作中展现出的责任心、团队协作能力和创新思维，这些软实力将为团队带来积极的影响。基于其优秀的综合表现和发展潜力，强烈建议公司考虑录用该候选人，相信其能够为公司创造显著价值，并在团队中发挥重要作用。同时，建议为其提供更具挑战性的工作任务和良好的发展平台，以充分发挥其潜力。"""
            
            recommendation = "强烈推荐录用，建议优先考虑，可以给予较高的薪资待遇和发展机会"
            
        elif final_score >= 70:
            description = f"""通过细致全面的评估，该候选人总体得分{final_score}分，各项能力指标基本达到{job_title}职位的要求标准。在工作经验方面，候选人具备了一定的相关工作背景，虽然可能在某些具体领域的深度经验上略有不足，但整体的工作能力和职业素养是值得肯定的。技能构成相对完整，核心技能基本满足岗位需求，展现了良好的专业基础和学习潜力。教育背景为其提供了必要的理论支撑，具备了解决复杂问题的基本能力。

从综合评估的角度来看，候选人在专业能力、学习态度、团队合作等方面表现良好，具备了在{company_name}发展的基本条件。虽然在个别维度上可能需要进一步提升，但其展现出的学习能力和发展潜力表明，通过适当的培训和指导，能够很好地适应新的工作环境并胜任{job_title}职位。建议公司考虑录用该候选人，同时制定相应的培养计划，帮助其在短期内补齐能力短板，发挥更大的价值。在薪资待遇方面可以按照标准水平执行，重点关注其后续的成长表现。"""
            
            recommendation = "推荐录用，建议安排面试深入了解，可提供标准薪资待遇和培训机会"
            
        else:
            description = f"""基于详细的评估分析，该候选人总体得分{final_score}分，在某些关键维度上与{job_title}职位要求存在一定差距。工作经验方面可能相对有限，或者与目标岗位的匹配度不够理想，需要通过额外的学习和实践来弥补经验不足。技能水平虽然具备一定基础，但在深度和广度上都需要进一步提升，特别是在核心专业技能方面需要加强学习和实践。教育背景提供了基本的理论基础，但可能需要通过继续教育或职业培训来补充专业知识。

尽管在某些方面存在不足，但候选人表现出的学习热情和发展意愿是值得认可的。如果公司愿意投入时间和资源进行培养，该候选人仍然具备一定的发展潜力。建议在考虑录用时，需要评估公司的培养能力和时间成本，同时制定详细的培训计划和考核机制。如果决定录用，建议给予较长的适应期和更多的指导支持，密切关注其学习进展和能力提升情况。在薪资方面可以考虑从较低水平开始，根据其能力提升情况进行调整。"""
            
            recommendation = "谨慎考虑，建议深度面试评估学习能力和发展潜力，如录用需提供充分的培训支持"
        
        return {
            "description": description,
            "recommendation": recommendation
        }

    @staticmethod
    def _generate_improvement_suggestions(resume_content: Dict[str, Any], job_posting: Dict[str, Any], hr_persona: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 确保输入参数是字典格式
        resume_content = ensure_dict(resume_content)
        job_posting = ensure_dict(job_posting)
        
        # 基于工作经验的建议
        experience = safe_get(resume_content, "experience", [])
        if len(experience) < 2:
            suggestions.append("增加相关工作经验，可以通过实习、项目参与、志愿工作等方式积累实践经验")
        elif len(experience) < 5:
            suggestions.append("继续积累工作经验，重点关注与目标职位相关的实践经历和技能提升")
        
        # 基于技能的建议
        skills = safe_get(resume_content, "skills", [])
        if len(skills) < 5:
            suggestions.append("扩充技能栈，学习与岗位要求高度匹配的核心技能和前沿技术")
        
        # 基于项目经验的建议
        projects = safe_get(resume_content, "projects", [])
        if len(projects) < 2:
            suggestions.append("增加项目经验，参与更多实际项目来展示技能应用能力和解决问题的能力")
        
        # 基于教育背景的建议
        education = safe_get(resume_content, "education", [])
        if not education:
            suggestions.append("补充教育背景信息，如有相关培训、认证等学习经历也应该体现在简历中")
        
        # HR人设特定建议
        if hr_persona == "conservative":
            suggestions.append("加强简历中工作稳定性和职业规划的描述，展现长期发展的决心")
        elif hr_persona == "progressive":
            suggestions.append("突出学习能力和适应性，展现面对新挑战的积极态度和创新思维")
        elif hr_persona == "technical":
            suggestions.append("详细描述技术项目经验，量化技术成果，展现技术深度和解决问题的能力")
        
        # 通用建议
        suggestions.extend([
            "优化简历格式和表述，使用更具体的量化指标来描述工作成果",
            "针对目标职位定制简历内容，突出最相关的经验和技能",
            "保持简历内容的及时更新，确保信息的准确性和完整性"
        ])
        
        return suggestions[:5]  # 返回最多5条建议

    @staticmethod
    def _generate_hr_comments(final_score: int, persona_config: Dict[str, Any], 
                             resume_content: Dict[str, Any], job_posting: Dict[str, Any]) -> str:
        """生成HR专业评价"""
        
        # 确保输入参数是字典格式
        resume_content = ensure_dict(resume_content)
        job_posting = ensure_dict(job_posting)
        
        persona_name = persona_config.get("name", "HR专家")
        company_name = safe_get(job_posting, 'company_name', '公司')
        job_title = safe_get(job_posting, 'job_title', '职位')
        
        if final_score >= 80:
            return f"作为{persona_name}，我对该候选人的综合表现非常满意，总评分{final_score}分。候选人在各个评估维度上都表现出色，特别是专业能力和发展潜力方面，完全符合我们{company_name}{job_title}的招聘标准。建议立即安排面试，优先考虑录用。这样的优秀候选人在市场上竞争激烈，建议尽快决策并给予有竞争力的薪资待遇。"
        
        elif final_score >= 70:
            return f"从{persona_name}的角度来看，该候选人总体表现良好，评分{final_score}分，基本达到了{job_title}职位的要求。虽然在个别方面还有提升空间，但其展现出的学习能力和专业素养是值得认可的。建议安排面试进一步了解，如果面试表现理想，可以考虑录用并提供相应的培训支持。"
        
        elif final_score >= 60:
            return f"以{persona_name}的专业判断，该候选人得分{final_score}分，虽然基本具备了一定的专业基础，但与{job_title}的理想要求还有一定差距。如果公司愿意投入时间进行培养，该候选人仍有发展潜力。建议谨慎考虑，如决定面试，需要重点评估其学习能力和发展意愿。"
        
        else:
            return f"根据{persona_name}的评估，该候选人当前得分{final_score}分，与{company_name}{job_title}的招聘要求存在较大差距。主要体现在专业技能、工作经验等核心维度上的不足。建议候选人进一步提升相关能力后再次申请，或者考虑其他更适合的职位机会。"
        
    
    @staticmethod
    def generate_self_introduction(strengths, weaknesses, min_length=300, resume_content=None, job_posting=None, hr_persona="experienced", hr_feedback=None):
        """
        根据HR反馈的优点与缺点，扬长避短，生成自我介绍（不少于min_length字）。
        """
        # 构建增强版prompt
        prompt = f"""
        你是一名求职者，请根据以下信息撰写一段不少于{min_length}字的个性化自我介绍：

        ## 基础信息：
        优点（可直接体现或强调）:
        {', '.join(strengths) if strengths else '无'}

        缺点（可转化为成长经历、改进方向或未来规划）:
        {', '.join(weaknesses) if weaknesses else '无'}

        ## 面试官类型：{hr_persona}
        """
        
        # 添加简历内容信息
        if resume_content:
            prompt += f"""
        ## 你的简历背景：
        {json.dumps(resume_content, ensure_ascii=False, indent=2)}
        """
        
        # 添加目标职位信息
        if job_posting:
            prompt += f"""
        ## 目标职位：
        {json.dumps(job_posting, ensure_ascii=False, indent=2)}
        """
        
        # 添加HR反馈信息
        if hr_feedback:
            prompt += f"""
        ## HR评估反馈：
        {json.dumps(hr_feedback, ensure_ascii=False, indent=2)}
        """
        
        prompt += f"""
        ## 要求：
        1. 结合优点和缺点，扬长避短，内容积极正面
        2. 体现自我认知、成长经历、职业目标和对岗位的热情
        3. 根据面试官类型调整表达风格和重点
        4. 如有简历和职位信息，要体现匹配度和针对性
        5. 语言流畅，结构完整，避免直接罗列优缺点
        6. 字数不少于{min_length}字

        请用第一人称中文输出一段自然流畅的自我介绍。
        """

        # 调用大模型生成
        result = llm_service.call_phase3_model(prompt)
        # 可根据实际情况做截断或后处理
        return result.strip()

    @staticmethod
    def generate_interview_questions(hr_persona, resume_content, job_posting, num_questions=3):
        """
        根据HR人设、简历内容和职位信息生成面试问题
        """
        try:
            logger.info(f"生成面试问题 - HR类型: {hr_persona}, 问题数量: {num_questions}")
            
            # 获取HR人设配置
            persona_config = Phase3HRAgent.HR_PERSONAS.get(hr_persona, Phase3HRAgent.HR_PERSONAS["experienced"])
            
            # 构建prompt
            prompt = f"""
            你是一位{persona_config['name']}，{persona_config['description']}
            
            现在需要为以下候选人准备{num_questions}个面试问题：
            
            ## 职位信息：
            {json.dumps(job_posting, ensure_ascii=False, indent=2)}
            
            ## 候选人简历：
            {json.dumps(resume_content, ensure_ascii=False, indent=2)}
            
            ## 要求：
            1. 根据你的HR人设特点，生成{num_questions}个具有针对性的面试问题
            2. 问题应该能够深入了解候选人的能力、经验和匹配度
            3. 问题类型要多样化：技能类、经验类、情境类、动机类等
            4. 每个问题都要有明确的考查目的
            
            请返回JSON格式：
            {{
                "questions": [
                    {{
                        "id": 1,
                        "question": "具体问题内容",
                        "type": "问题类型",
                        "purpose": "考查目的",
                        "focus_area": "重点考查领域",
                        "expected_duration": "预期回答时长（分钟）"
                    }}
                ]
            }}
            """
            
            # 调用大模型生成
            result = llm_service.call_phase3_model(prompt)
            
            # 解析JSON结果
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                try:
                    questions_data = json.loads(json_match.group())
                    questions = questions_data.get('questions', [])
                    
                    if not questions or len(questions) == 0:
                        raise ValueError("生成的问题列表为空")
                    
                    logger.info(f"成功生成 {len(questions)} 个面试问题")
                    
                    return {
                        "success": True,
                        "message": f"成功生成{len(questions)}个面试问题",
                        "data": {
                            "questions": questions,
                            "hr_persona": hr_persona,
                            "total_questions": len(questions)
                        }
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"原始结果: {result}")
                    
                    # 备用方案：简单文本解析
                    fallback_questions = Phase3HRAgent._parse_questions_fallback(result, num_questions)
                    
                    return {
                        "success": True,
                        "message": f"生成{len(fallback_questions)}个面试问题（使用备用解析）",
                        "data": {
                            "questions": fallback_questions,
                            "hr_persona": hr_persona,
                            "total_questions": len(fallback_questions)
                        }
                    }
            else:
                logger.error("未找到有效的JSON格式结果")
                logger.error(f"原始结果: {result}")
                
                # 备用方案
                fallback_questions = Phase3HRAgent._generate_fallback_questions(hr_persona, job_posting, num_questions)
                
                return {
                    "success": True,
                    "message": f"生成{len(fallback_questions)}个面试问题（使用备用模板）",
                    "data": {
                        "questions": fallback_questions,
                        "hr_persona": hr_persona,
                        "total_questions": len(fallback_questions)
                    }
                }
                
        except Exception as e:
            logger.error(f"生成面试问题失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"面试问题生成失败: {str(e)}",
                "data": {}
            }

    @staticmethod
    def evaluate_interview_answer(hr_persona, question, user_answer, resume_content, job_posting):
        """
        评估用户的面试回答并给出优化建议
        """
        try:
            logger.info(f"评估面试回答 - HR类型: {hr_persona}")
            
            # 获取HR人设配置
            persona_config = Phase3HRAgent.HR_PERSONAS.get(hr_persona, Phase3HRAgent.HR_PERSONAS["experienced"])
            
            # 构建prompt
            prompt = f"""
            你是一位{persona_config['name']}，{persona_config['description']}
            
            现在需要评估候选人对以下面试问题的回答：
            
            ## 面试问题：
            问题：{question.get('question', '未知问题')}
            考查目的：{question.get('purpose', '综合能力')}
            重点领域：{question.get('focus_area', '通用')}
            
            ## 候选人回答：
            {user_answer}
            
            ## 职位信息：
            {json.dumps(job_posting, ensure_ascii=False, indent=2)}
            
            ## 候选人简历：
            {json.dumps(resume_content, ensure_ascii=False, indent=2)}
            
            ## 评估要求：
            1. 根据你的HR人设特点，专业评估这个回答
            2. 给出具体的评分和详细分析
            3. 提供具体的改进建议
            4. 给出理想回答的要点
            
            请返回JSON格式：
            {{
                "overall_score": 75,
                "evaluation": {{
                    "content_relevance": 80,
                    "depth_of_answer": 70,
                    "communication_skill": 85,
                    "job_match": 75
                }},
                "strengths": ["回答的优点1", "回答的优点2"],
                "weaknesses": ["需要改进的地方1", "需要改进的地方2"],
                "improvement_suggestions": [
                    "具体改进建议1",
                    "具体改进建议2"
                ],
                "ideal_answer_points": [
                    "理想回答要点1",
                    "理想回答要点2"
                ],
                "hr_comment": "作为{persona_config['name']}的专业评价和建议"
            }}
            """
            
            # 调用大模型生成
            result = llm_service.call_phase3_model(prompt)
            
            # 解析JSON结果
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                try:
                    evaluation_data = json.loads(json_match.group())
                    
                    logger.info(f"面试回答评估完成，总分: {evaluation_data.get('overall_score', 0)}")
                    
                    return {
                        "success": True,
                        "message": "面试回答评估完成",
                        "data": {
                            "evaluation": evaluation_data,
                            "question": question,
                            "user_answer": user_answer,
                            "hr_persona": hr_persona
                        }
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"评估结果JSON解析失败: {e}")
                    logger.error(f"原始结果: {result}")
                    
                    # 备用方案：基本评估
                    fallback_evaluation = Phase3HRAgent._generate_fallback_evaluation(user_answer, question)
                    
                    return {
                        "success": True,
                        "message": "面试回答评估完成（使用备用评估）",
                        "data": {
                            "evaluation": fallback_evaluation,
                            "question": question,
                            "user_answer": user_answer,
                            "hr_persona": hr_persona
                        }
                    }
            else:
                logger.error("评估结果未找到有效的JSON格式")
                logger.error(f"原始结果: {result}")
                
                # 备用方案
                fallback_evaluation = Phase3HRAgent._generate_fallback_evaluation(user_answer, question)
                
                return {
                    "success": True,
                    "message": "面试回答评估完成（使用备用评估）",
                    "data": {
                        "evaluation": fallback_evaluation,
                        "question": question,
                        "user_answer": user_answer,
                        "hr_persona": hr_persona
                    }
                }
                
        except Exception as e:
            logger.error(f"评估面试回答失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"面试回答评估失败: {str(e)}",
                "data": {}
            }
        
    @staticmethod
    def _parse_questions_fallback(result_text, num_questions):
        """备用问题解析方法"""
        questions = []
        lines = result_text.split('\n')
        
        question_count = 0
        current_question = None
        
        for line in lines:
            line = line.strip()
            if '问题' in line and ('：' in line or ':' in line):
                if current_question:
                    questions.append(current_question)
                
                question_text = line.split('：')[-1] if '：' in line else line.split(':')[-1]
                current_question = {
                    "id": question_count + 1,
                    "question": question_text.strip(),
                    "type": "综合问题",
                    "purpose": "综合能力评估",
                    "focus_area": "通用能力",
                    "expected_duration": "3-5分钟"
                }
                question_count += 1
                
                if question_count >= num_questions:
                    break
        
        if current_question and current_question not in questions:
            questions.append(current_question)
        
        return questions[:num_questions]

    @staticmethod
    def _generate_fallback_questions(hr_persona, job_posting, num_questions):
        """生成备用面试问题"""
        job_title = job_posting.get('job_title', '未知职位')
        
        base_questions = [
            {
                "id": 1,
                "question": f"请简单介绍一下自己，并说明为什么对{job_title}这个职位感兴趣？",
                "type": "自我介绍类",
                "purpose": "了解候选人基本情况和求职动机",
                "focus_area": "个人背景",
                "expected_duration": "3-5分钟"
            },
            {
                "id": 2,
                "question": "请描述一个你在工作中遇到的挑战，以及你是如何解决的？",
                "type": "经验类",
                "purpose": "评估问题解决能力",
                "focus_area": "工作能力",
                "expected_duration": "4-6分钟"
            },
            {
                "id": 3,
                "question": "你认为自己的优势是什么？有哪些地方需要提升？",
                "type": "自我认知类",
                "purpose": "了解自我认知能力",
                "focus_area": "个人发展",
                "expected_duration": "3-5分钟"
            }
        ]
        
        return base_questions[:num_questions]

    @staticmethod
    def _generate_fallback_evaluation(user_answer, question):
        """生成备用评估结果"""
        answer_length = len(user_answer)
        
        # 基于回答长度的简单评分
        if answer_length > 200:
            base_score = 75
        elif answer_length > 100:
            base_score = 65
        else:
            base_score = 55
        
        return {
            "overall_score": base_score,
            "evaluation": {
                "content_relevance": base_score,
                "depth_of_answer": base_score - 5,
                "communication_skill": base_score + 5,
                "job_match": base_score
            },
            "strengths": ["回答态度积极", "表达较为清晰"],
            "weaknesses": ["可以更加详细", "建议提供更多具体例子"],
            "improvement_suggestions": [
                "建议在回答中提供更多具体的例子和数据",
                "可以更好地将个人经验与岗位要求结合",
                "表达可以更加结构化和逻辑清晰"
            ],
            "ideal_answer_points": [
                "结合具体工作经验回答",
                "展现与岗位相关的技能",
                "体现解决问题的思路和方法"
            ],
            "hr_comment": "候选人的回答基本符合要求，建议进一步提升回答的深度和针对性。"
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
search_agent = SearchAgent()
phase2_agent = Phase2ResumeAgent()
phase3_agent = Phase3HRAgent()
phase4_agent = Phase4Agent()  # 使用从Phase4ScheduleAgent.py导入的完整类