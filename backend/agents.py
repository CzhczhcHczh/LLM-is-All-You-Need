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
        """优化简历内容"""
        try:
            if optimization_focus is None:
                optimization_focus = []
                
            # 根据反馈优化简历
            optimized_resume = resume_content.copy()
            
            # 这里可以添加具体的优化逻辑
            # 例如根据HR反馈调整内容重点
            
            return {
                "optimized_resume": optimized_resume,
                "optimization_notes": "已根据反馈进行优化",
                "focus_areas": optimization_focus
            }
            
        except Exception as e:
            logger.error(f"Error optimizing resume: {e}")
            return {"error": str(e)}

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
            improved_resume = Phase2ResumeAgent.optimize_resume_content(resume_content, feedback_data)
            
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
search_agent = SearchAgent()
phase2_agent = Phase2ResumeAgent()
phase3_agent = Phase3HRAgent()
phase4_agent = Phase4ScheduleAgent()

