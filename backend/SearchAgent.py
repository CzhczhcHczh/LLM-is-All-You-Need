
# import json
# import time
# from datetime import datetime, timedelta
# from typing import List, Dict, Any, Optional
# from sqlalchemy.orm import Session
# from loguru import logger

# from services import llm_service, serper_service, chromadb_service, text_service
# from database import (
#     get_db, create_job_posting, create_resume, create_hr_feedback, 
#     create_interview, create_schedule, JobPostingCreate, ResumeCreate,
#     HRFeedbackCreate, InterviewCreate, ScheduleCreate
# )

import json
import time
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from openai import OpenAI
import os
import httpx

from services import chromadb_service

client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        # api_key="sk-t54PdgqlpcLAjZlEVrVWg0wPCXgei5xPNGmWq6PyqKSvr6W0",
        api_key="sk-HSLz7AUMoMfPm4desz0tRbehJrpdU1uSXUz7l3bLWFb2pYEE",
        base_url="https://api.chatanywhere.tech/v1"
        # base_url="https://api.chatanywhere.org/v1"
    )
class SearchAgent:
    """Job search agent using OpenAI gpt-4o-search-preview for web search."""
       
    @staticmethod
    def search_jobs(search_query: str, location: str = None, max_results: int = 20) -> Dict[str, Any]:
        logger.info(f"Starting GPT-4o web search for: {search_query}")

        prompt = f"""
请使用网络搜索功能，从58同城和Boss直聘等主流招聘网站查询“{search_query}”相关的招聘信息，工作地点是"{location}"并提取前{max_results}条有效结果，整理为如下JSON数组：

[
  {{
    "job_title": "职位名称",
    "company_name": "公司名称",
    "location": "工作地点",
    "salary_range": "薪资范围",
    "requirements": ["要求1", "要求2"],
    "skills": ["技能1", "技能2"],
    "description": "职位描述",
    "source_url": "来源链接"
  }},
  ...
]

要求输出内容为严格 JSON 格式。
"""

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[
                    {"role": "user", "content": prompt}
                ],
                # response_format={ "type": "json_object" }
            )

            raw_output = completion.choices[0].message.content
            print(raw_output)

            # 尝试提取 JSON
            import re
            json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in GPT response.")

            job_list = json.loads(json_match.group())
            jobs = []
            companies = {}

            for i, job in enumerate(job_list[:max_results]):
                job['search_query'] = search_query
                job['extracted_at'] = datetime.utcnow().isoformat()
                jobs.append(job)

                comp = job.get("company_name")
                if comp:
                    if comp not in companies:
                        companies[comp] = {
                            "name": comp,
                            "jobs_count": 1,
                            "locations": [job.get("location", "")]
                        }
                    else:
                        companies[comp]["jobs_count"] += 1
                        loc = job.get("location", "")
                        if loc not in companies[comp]["locations"]:
                            companies[comp]["locations"].append(loc)

                # 存入向量数据库
                job_text = f"{job['job_title']} {job['company_name']} {job['description']}"
                chromadb_service.add_job_posting(
                    job_id=f"gptweb_{int(time.time())}_{i}",
                    job_text=job_text,
                    metadata=job
                )

            return {
                "success": True,
                "message": f"提取了 {len(jobs)} 条职位信息",
                "data": {
                    "jobs": jobs,
                    "companies": list(companies.values()),
                    "search_query": search_query
                }
            }

        except Exception as e:
            logger.error(f"[GPT Web Search] Error: {e}")
            return {
                "success": False,
                "message": f"搜索失败：{str(e)}",
                "data": {"jobs": [], "companies": []}
            }

if __name__ == "__main__":

    agent = SearchAgent()
    print(agent.search_jobs("Python Developer", "Beijing", 10))


# class SearchAgent:
#     """Job search and data collection agent."""
    
#     @staticmethod
#     def search_jobs(search_query: str, location: str = None, max_results: int = 20) -> Dict[str, Any]:
#         """Search for job postings and extract structured data."""
#         try:
#             logger.info(f"Starting job search for: {search_query}")
            
#             # Search using Serper API
#             search_results = serper_service.search_jobs(
#                 query=search_query,
#                 location=location,
#                 num_results=max_results
#             )
            
#             if not search_results:
#                 return {
#                     "success": False,
#                     "message": "No search results found",
#                     "data": {"jobs": [], "companies": []}
#                 }
            
#             # Process search results with LLM
#             jobs = []
#             companies = {}
            
#             for result in search_results:
#                 # Extract job information using LLM
#                 extraction_prompt = f"""
#                 请从以下搜索结果中提取招聘信息，返回JSON格式：
                
#                 标题: {result.get('title', '')}
#                 链接: {result.get('link', '')}
#                 描述: {result.get('snippet', '')}
                
#                 请提取以下信息并返回JSON格式：
#                 {{
#                     "job_title": "职位名称",
#                     "company_name": "公司名称",
#                     "location": "工作地点",
#                     "salary_range": "薪资范围",
#                     "requirements": ["要求1", "要求2"],
#                     "skills": ["技能1", "技能2"],
#                     "description": "职位描述",
#                     "is_valid_job": true/false
#                 }}
                
#                 如果这不是一个有效的招聘信息，请设置 is_valid_job 为 false。
#                 """
                
#                 try:
#                     extraction_result = llm_service.call_phase1_model(extraction_prompt)
                    
#                     # Parse JSON result
#                     import re
#                     json_match = re.search(r'\{.*\}', extraction_result, re.DOTALL)
#                     if json_match:
#                         job_data = json.loads(json_match.group())
                        
#                         if job_data.get('is_valid_job', False):
#                             # Add source information
#                             job_data.update({
#                                 'source_url': result.get('link', ''),
#                                 'search_query': search_query,
#                                 'extracted_at': datetime.now().isoformat()
#                             })
                            
#                             jobs.append(job_data)
                            
#                             # Collect company information
#                             company_name = job_data.get('company_name', '')
#                             if company_name and company_name not in companies:
#                                 companies[company_name] = {
#                                     'name': company_name,
#                                     'jobs_count': 1,
#                                     'locations': [job_data.get('location', '')],
#                                     'search_query': search_query
#                                 }
#                             elif company_name:
#                                 companies[company_name]['jobs_count'] += 1
#                                 if job_data.get('location') not in companies[company_name]['locations']:
#                                     companies[company_name]['locations'].append(job_data.get('location', ''))
                
#                 except Exception as e:
#                     logger.error(f"Error processing search result: {e}")
#                     continue
            
#             # Store in vector database for similarity search
#             for i, job in enumerate(jobs):
#                 job_text = f"{job.get('job_title', '')} {job.get('company_name', '')} {job.get('description', '')}"
#                 chromadb_service.add_job_posting(
#                     job_id=f"search_{int(time.time())}_{i}",
#                     job_text=job_text,
#                     metadata=job
#                 )
            
#             logger.info(f"Successfully processed {len(jobs)} jobs from {len(companies)} companies")
            
#             return {
#                 "success": True,
#                 "message": f"Found {len(jobs)} job postings",
#                 "data": {
#                     "jobs": jobs,
#                     "companies": list(companies.values()),
#                     "search_query": search_query,
#                     "total_results": len(jobs)
#                 }
#             }
            
#         except Exception as e:
#             logger.error(f"Error in job search: {e}")
#             return {
#                 "success": False,
#                 "message": f"Search failed: {str(e)}",
#                 "data": {"jobs": [], "companies": []}
#             }
    
#     @staticmethod
#     def get_similar_jobs(user_profile: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
#         """Find similar jobs based on user profile."""
#         try:
#             # Create search query from user profile
#             profile_text = f"{user_profile.get('target_position', '')} {' '.join(user_profile.get('skills', []))}"
            
#             # Search similar jobs in vector database
#             similar_jobs = chromadb_service.search_similar_jobs(profile_text, n_results)
            
#             return similar_jobs
            
#         except Exception as e:
#             logger.error(f"Error finding similar jobs: {e}")
#             return []

