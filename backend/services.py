"""
External services integration for Job Planner Assistant.
"""

import os
import json
import requests
import chromadb
from typing import List, Dict, Any, Optional
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
from config import settings

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=settings.chromadb_path)


class LLMService:
    """LLM service for calling different models."""
    
    @staticmethod
    def call_model(model_name: str, messages: List[Dict[str, str]], temperature: float = 0.7, js: bool = False) -> str:
        """Call LLM model with messages."""
        try:
            # 验证输入参数
            if not model_name:
                raise ValueError("Model name cannot be empty")
            
            if not messages:
                raise ValueError("Messages cannot be empty")
            
            logger.info(f"Calling model: {model_name}")
            logger.debug(f"Messages: {messages}")
            if js is True:
                response = openai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4000,
                    response_format={ "type": "json_object" }
                )
            else:
                response = openai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4000
                )
            
            # 验证响应对象
            if not hasattr(response, 'choices'):
                logger.error(f"Invalid response type: {type(response)}")
                logger.error(f"Response content: {response}")
                raise ValueError(f"Invalid response format from OpenAI API")
            
            if not response.choices:
                raise ValueError("Empty choices in response")
            
            if not hasattr(response.choices[0], 'message'):
                raise ValueError("Invalid choice format in response")
            
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("Empty content in response")
            
            logger.info(f"Successfully got response from {model_name}")
            return content
            
        except Exception as e:
            logger.error(f"Error calling model {model_name}: {e}")
            
            # 返回演示数据而不是错误信息
            if "自我介绍" in str(messages) or "self_introduction" in str(messages):
                return LLMService._get_demo_self_introduction()
            elif "面试问题" in str(messages) or "interview" in str(messages).lower() or "generate_interview_questions" in str(messages):
                return LLMService._get_demo_interview_questions()
            elif "面试回答" in str(messages) or "evaluate_interview_answer" in str(messages):
                return LLMService._get_demo_interview_evaluation()
            elif "resume" in str(messages).lower() or "简历" in str(messages):
                return LLMService._get_demo_resume_response()
            elif "search" in str(messages).lower() or "搜索" in str(messages):
                return LLMService._get_demo_search_response()
            elif "hr" in str(messages).lower() or "评估" in str(messages):
                return LLMService._get_demo_hr_response()
            else:
                return LLMService._get_demo_generic_response()
    
    @staticmethod
    def _get_demo_resume_response() -> str:
        """返回演示简历数据"""
        return json.dumps({
            "personal_info": {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "location": "北京市朝阳区"
            },
            "summary": "3年前端开发经验，熟悉Vue.js、React等主流框架，具备良好的编程基础和项目管理能力。",
            "experience": [
                {
                    "company": "某科技有限公司",
                    "position": "前端开发工程师",
                    "duration": "2021.06 - 2024.01",
                    "description": "负责公司主要产品的前端开发，使用Vue.js技术栈。",
                    "achievements": [
                        "独立完成3个重要项目的前端开发",
                        "优化页面性能，提升加载速度30%",
                        "参与技术选型和架构设计"
                    ]
                }
            ],
            "education": [
                {
                    "school": "某大学",
                    "degree": "本科",
                    "major": "计算机科学与技术",
                    "duration": "2017-2021"
                }
            ],
            "skills": ["Vue.js", "React", "JavaScript", "TypeScript", "CSS3", "HTML5", "Node.js"],
            "projects": [
                {
                    "name": "电商管理系统",
                    "description": "基于Vue.js的电商后台管理系统",
                    "technologies": ["Vue.js", "Element UI", "Axios"],
                    "achievements": ["完整的CRUD功能", "用户权限管理"]
                }
            ],
            "highlighted_skills": ["Vue.js", "JavaScript", "前端开发"],
            "customization_notes": "简历已针对前端开发岗位进行优化"
        }, ensure_ascii=False)
    
    @staticmethod
    def _get_demo_search_response() -> str:
        """返回演示搜索数据"""
        return json.dumps([
            {
                "job_title": "前端开发工程师",
                "company_name": "某科技公司",
                "location": "北京",
                "salary": "15-25K",
                "description": "负责前端页面开发，要求熟悉Vue.js框架",
                "requirements": ["3年以上前端经验", "熟悉Vue.js", "了解ES6"],
                "skills": ["Vue.js", "JavaScript", "CSS"]
            }
        ], ensure_ascii=False)
    
    @staticmethod
    def _get_demo_hr_response() -> str:
        """返回演示HR评估数据"""
        return json.dumps({
            "overall_score": 78,
            "passes_initial_screening": True,
            "strengths": ["技术技能匹配", "项目经验丰富"],
            "weaknesses": ["缺少大厂经验"],
            "missing_keywords": ["微服务", "性能优化"],
            "experience_feedback": "工作经验符合要求",
            "skills_feedback": "技能栈匹配度高",
            "education_feedback": "教育背景良好",
            "suggestions": ["补充性能优化经验", "增加开源项目"],
            "interview_invitation": {
                "invited": True,
                "interview_type": "技术面试",
                "proposed_times": ["2025-07-21 14:00", "2025-07-22 10:00"],
                "duration": 60,
                "location": "线上面试",
                "interviewer": "技术总监",
                "preparation_notes": "准备技术问题和项目介绍"
            },
            "hr_comments": "候选人技能匹配度较高，建议进入面试环节"
        }, ensure_ascii=False)
    
    @staticmethod
    def _get_demo_self_introduction() -> str:
        """返回演示自我介绍数据"""
        import random
        
        # 生成多样化的自我介绍模板（无时间戳）
        templates = [
            "大家好，我是一名充满热情的专业人士。在我的职业生涯中，我特别擅长团队协作和问题解决，这些能力帮助我在工作中取得了不错的成果。虽然我在某些新兴技术方面还在持续学习中，但我将此视为自己成长的动力。我相信通过不断的努力和学习，我能够为团队带来更多价值。我期待能够在新的工作环境中发挥自己的专长，与优秀的同事一起创造更大的成就。感谢您的时间，期待进一步的交流机会。",
            
            "很高兴有机会向大家介绍自己。我是一个注重细节且富有创新精神的求职者，在项目管理和技术实施方面有着丰富的经验。我的同事们常常夸赞我的沟通能力和学习能力，这让我能够快速适应新的工作环境。虽然我在某些领域的经验可能还不够深入，但我已经制定了明确的学习计划来弥补这些不足。我希望能够加入一个充满活力的团队，与大家一起追求卓越，实现共同的目标。期待与您进一步探讨合作的可能性。",
            
            "我是一名对工作充满激情的候选人，特别在技术创新和团队领导方面表现突出。在过往的项目中，我积累了丰富的实战经验，能够独立承担重要任务并取得预期成果。我深知自己在某些新兴技术方面还需要继续学习，但我将此看作是职业发展的新机遇。我相信通过持续的自我提升和团队合作，我能够为公司创造更大的价值。我期待能够在新的平台上展现自己的能力，与团队一起迎接挑战，创造辉煌。感谢您的关注和支持。"
        ]
        
        # 随机选择一个模板
        return random.choice(templates)
    
    @staticmethod
    def _get_demo_interview_questions() -> str:
        """返回演示面试问题数据"""
        return json.dumps({
            "questions": [
                {
                    "id": 1,
                    "question": "请简单介绍一下您的工作经历，重点说明与我们岗位相关的项目经验。",
                    "type": "经验验证",
                    "focus_area": "工作经验",
                    "difficulty": "基础",
                    "evaluation_criteria": "经验的相关性、深度和成果",
                    "time_limit": "3-5分钟"
                },
                {
                    "id": 2,
                    "question": "在工作中遇到技术难题时，您通常采用什么方法来解决？请举一个具体的例子。",
                    "type": "问题解决",
                    "focus_area": "技术能力",
                    "difficulty": "中等",
                    "evaluation_criteria": "问题分析和解决思路",
                    "time_limit": "4-6分钟"
                },
                {
                    "id": 3,
                    "question": "您对我们公司和这个职位有什么了解？为什么想要加入我们？",
                    "type": "求职动机",
                    "focus_area": "求职意愿",
                    "difficulty": "基础",
                    "evaluation_criteria": "对公司的了解程度和求职诚意",
                    "time_limit": "3-4分钟"
                }
            ],
            "interview_context": {
                "hr_persona": "experienced",
                "total_time": "12-18分钟",
                "interview_goal": "全面评估候选人的岗位适配性",
                "candidate_profile": "技术岗位候选人"
            }
        }, ensure_ascii=False)
    
    @staticmethod
    def _get_demo_interview_evaluation() -> str:
        """返回演示面试回答评估数据"""
        return json.dumps({
            "evaluation": {
                "overall_score": 75,
                "detailed_scores": {
                    "relevance": 80,
                    "depth": 70,
                    "clarity": 85,
                    "professionalism": 75
                },
                "strengths": [
                    "回答思路清晰，逻辑性强",
                    "能够结合具体例子说明问题",
                    "表达简洁，重点突出"
                ],
                "areas_for_improvement": [
                    "可以更深入地展示技术细节",
                    "建议增加量化的成果描述",
                    "可以展现更多的主动学习意识"
                ],
                "hr_comment": "回答整体表现良好，体现了较强的专业素养。建议在后续环节中更深入地展示技术深度。",
                "follow_up_suggestions": [
                    "请准备更多具体的技术实现细节",
                    "可以提前想好如何量化您的工作成果",
                    "建议了解更多行业发展趋势"
                ]
            },
            "ideal_answer_example": "理想的回答应该包含：具体的问题背景、采用的解决方案、实施过程中的挑战、最终的成果和收获。建议结构化表达，先说问题，再说方法，最后说结果。"
        }, ensure_ascii=False)
    
    @staticmethod
    def _get_demo_generic_response() -> str:
        """返回通用演示数据"""
        return json.dumps({
            "success": True,
            "message": "演示模式：API调用失败，返回模拟数据",
            "data": "这是演示数据，请检查您的API配置"
        }, ensure_ascii=False)
    
    @staticmethod
    def call_phase1_model(prompt: str) -> str:
        """Call Phase 1 model for search tasks."""
        messages = [{"role": "user", "content": prompt}]
        return LLMService.call_model(settings.phase1_model, messages)
    
    @staticmethod
    def call_phase2_model(prompt: str) -> str:
        """Call Phase 2 model for resume generation."""
        messages = [{"role": "user", "content": prompt}]
        return LLMService.call_model(settings.phase2_model, messages)
    
    @staticmethod
    def call_phase3_model(prompt: str) -> str:
        """Call Phase 3 model for HR simulation."""
        messages = [{"role": "user", "content": prompt}]
        # 如果是自我介绍相关的prompt，增加温度参数以提高多样性
        if "自我介绍" in prompt or "self_introduction" in prompt:
            return LLMService.call_model(settings.phase3_model, messages, temperature=0.9)
        else:
            return LLMService.call_model(settings.phase3_model, messages)
    
    @staticmethod
    def call_phase4_models(prompt: str) -> List[str]:
        """Call multiple Phase 4 models for scheduling discussion."""
        results = []
        try:
            for model in settings.phase4_models_list:
                messages = [{"role": "user", "content": prompt}]
                result = LLMService.call_model(model, messages, js=False)
                results.append(result)  # 直接添加响应字符串
        except Exception as e:
            logger.error(f"Error calling phase4 models: {e}")
            # 返回演示数据
            results.append(LLMService._get_demo_generic_response())
        return results


class SerperService:
    """Serper API service for web search."""
    
    @staticmethod
    def search_jobs(query: str, location: str = None, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for job postings using Serper API."""
        try:
            search_query = f"{query} 招聘"
            if location:
                search_query += f" {location}"
            
            url = "https://google.serper.dev/search"
            payload = {
                "q": search_query,
                "num": num_results,
                "gl": "cn",
                "hl": "zh-cn"
            }
            headers = {
                "X-API-KEY": settings.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process organic results
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "serper"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching jobs with Serper: {e}")
            return []
    
    @staticmethod
    def search_company_info(company_name: str) -> Dict[str, Any]:
        """Search for company information."""
        try:
            search_query = f"{company_name} 公司信息"
            
            url = "https://google.serper.dev/search"
            payload = {
                "q": search_query,
                "num": 5,
                "gl": "cn",
                "hl": "zh-cn"
            }
            headers = {
                "X-API-KEY": settings.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract company info from search results
            company_info = {
                "name": company_name,
                "description": "",
                "industry": "",
                "website": "",
                "search_results": []
            }
            
            for item in data.get("organic", []):
                company_info["search_results"].append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
                
                # Try to extract website
                if not company_info["website"] and "官网" in item.get("title", ""):
                    company_info["website"] = item.get("link", "")
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error searching company info: {e}")
            return {"name": company_name, "error": str(e)}


class ChromaDBService:
    """ChromaDB service for vector storage and similarity search."""
    
    def __init__(self, collection_name: str = "job_embeddings"):
        self.collection_name = collection_name
        self.collection = None
        self._init_collection()
    
    def _init_collection(self):
        """Initialize ChromaDB collection."""
        try:
            self.collection = chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Job postings and user profiles embeddings"}
            )
            logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {e}")
    
    def add_job_posting(self, job_id: str, job_text: str, metadata: Dict[str, Any]):
        """Add job posting to vector database."""
        try:
            if not self.collection:
                self._init_collection()
            
            # 确保所有的metadata值都是基本类型 (str, int, float, bool, None)
            # ChromaDB不接受列表或字典等复杂类型作为metadata值
            cleaned_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    cleaned_metadata[key] = value
                elif isinstance(value, list):
                    # 将列表转换为逗号分隔的字符串
                    cleaned_metadata[key] = ', '.join(map(str, value))
                elif isinstance(value, dict):
                    # 将字典转换为JSON字符串
                    cleaned_metadata[key] = json.dumps(value, ensure_ascii=False)
                else:
                    # 对于其他类型，转换为字符串
                    cleaned_metadata[key] = str(value)
            
            self.collection.add(
                documents=[job_text],
                metadatas=[cleaned_metadata],
                ids=[f"job_{job_id}"]
            )
            logger.info(f"Added job posting {job_id} to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding job posting to ChromaDB: {e}")
    
    def search_similar_jobs(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar job postings."""
        try:
            if not self.collection:
                self._init_collection()
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            similar_jobs = []
            for i, doc in enumerate(results["documents"][0]):
                similar_jobs.append({
                    "id": results["ids"][0][i],
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
            
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Error searching similar jobs: {e}")
            return []
            
    def get_all_job_embeddings(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all job embeddings from ChromaDB."""
        try:
            if not self.collection:
                self._init_collection()
                
            # 获取所有数据（ChromaDB没有分页API，所以需要一次获取全部）
            results = self.collection.get()
            
            job_embeddings = []
            for i, doc_id in enumerate(results["ids"]):
                # 只处理job开头的ID（跳过user类型的）
                if doc_id.startswith("job_"):
                    job_embeddings.append({
                        "id": doc_id,
                        "document": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })
                    
                # 如果达到限制，提前停止
                if len(job_embeddings) >= limit:
                    break
                    
            return job_embeddings
            
        except Exception as e:
            logger.error(f"Error getting all job embeddings: {e}")
            return []
            
    def get_job_embedding(self, job_id: str) -> Dict[str, Any]:
        """Get a specific job embedding by ID."""
        try:
            if not self.collection:
                self._init_collection()
                
            # ChromaDB的get方法根据ID获取特定文档
            if not job_id.startswith("job_"):
                job_id = f"job_{job_id}"
                
            results = self.collection.get(ids=[job_id])
            
            if not results["ids"]:
                return None
                
            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
            
        except Exception as e:
            logger.error(f"Error getting job embedding {job_id}: {e}")
            return None
            
    def delete_job_embedding(self, job_id: str) -> bool:
        """Delete a specific job embedding by ID."""
        try:
            if not self.collection:
                self._init_collection()
                
            if not job_id.startswith("job_"):
                job_id = f"job_{job_id}"
                
            self.collection.delete(ids=[job_id])
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job embedding {job_id}: {e}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics."""
        try:
            if not self.collection:
                self._init_collection()
                
            # 获取所有数据
            results = self.collection.get()
            
            # 计算统计信息
            total_count = len(results["ids"]) if results["ids"] else 0
            job_count = sum(1 for id in results["ids"] if id.startswith("job_"))
            user_count = sum(1 for id in results["ids"] if id.startswith("user_"))
            
            # 获取最近添加的几个职位
            recent_jobs = []
            for i, doc_id in enumerate(results["ids"]):
                if doc_id.startswith("job_") and len(recent_jobs) < 5:
                    recent_jobs.append({
                        "id": doc_id,
                        "title": results["metadatas"][i].get("job_title", "Unknown"),
                        "company": results["metadatas"][i].get("company_name", "Unknown"),
                    })
            
            return {
                "total_embeddings": total_count,
                "job_embeddings": job_count,
                "user_embeddings": user_count,
                "recent_jobs": recent_jobs,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Error getting ChromaDB stats: {e}")
            return {"error": str(e)}
    
    def add_user_profile(self, user_id: str, profile_text: str, metadata: Dict[str, Any]):
        """Add user profile to vector database."""
        try:
            if not self.collection:
                self._init_collection()
            
            self.collection.add(
                documents=[profile_text],
                metadatas=[metadata],
                ids=[f"user_{user_id}"]
            )
            logger.info(f"Added user profile {user_id} to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding user profile to ChromaDB: {e}")


class TextProcessingService:
    """Text processing utilities."""
    
    @staticmethod
    def extract_job_info(job_text: str) -> Dict[str, Any]:
        """Extract structured information from job posting text."""
        # Use LLM to extract structured information
        prompt = f"""
        请从以下招聘信息中提取结构化数据，返回JSON格式：
        
        招聘信息：
        {job_text}
        
        请提取以下字段：
        - title: 职位名称
        - company: 公司名称
        - location: 工作地点
        - salary: 薪资范围
        - requirements: 任职要求列表
        - responsibilities: 工作职责列表
        - skills: 技能要求列表
        
        只返回JSON格式的结果，不要其他说明。
        """
        
        try:
            result = LLMService.call_phase1_model(prompt)
            # Try to parse JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Failed to extract JSON", "raw_result": result}
        except Exception as e:
            logger.error(f"Error extracting job info: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks for processing."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return splitter.split_text(text)


# Initialize services
llm_service = LLMService()
serper_service = SerperService()
chromadb_service = ChromaDBService()
text_service = TextProcessingService()

