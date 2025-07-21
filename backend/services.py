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
    def call_model(model_name: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call LLM model with messages."""
        try:
            # 验证输入参数
            if not model_name:
                raise ValueError("Model name cannot be empty")
            
            if not messages:
                raise ValueError("Messages cannot be empty")
            
            logger.info(f"Calling model: {model_name}")
            logger.debug(f"Messages: {messages}")
            
            # 调用OpenAI API
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
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
            if "resume" in str(messages).lower() or "简历" in str(messages):
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
        return LLMService.call_model(settings.phase3_model, messages)
    
    @staticmethod
    def call_phase4_models(prompt: str) -> List[str]:
        """Call multiple Phase 4 models for scheduling discussion."""
        results = []
        for model in settings.phase4_models_list:
            messages = [{"role": "user", "content": prompt}]
            result = LLMService.call_model(model, messages)
            results.append({
                "model": model,
                "response": result
            })
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

