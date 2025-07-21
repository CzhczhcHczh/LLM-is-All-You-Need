
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
import re

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
        
        # 限制每次查询的职位数量为5条
        batch_size = 10
        # 计算需要进行的查询次数
        num_batches = (max_results + batch_size - 1) // batch_size
        
        jobs = []
        companies = {}
        excluded_jobs = set()  # 用于跟踪已获取的职位，避免重复
        
        try:
            for batch in range(num_batches):
                remaining = min(batch_size, max_results - len(jobs))
                if remaining <= 0:
                    break
                    
                # 构建排除已获取职位的提示
                exclusion_text = ""
                if excluded_jobs:
                    excluded_list = list(excluded_jobs)
                    # 只展示前5个已排除的职位，避免提示过长
                    display_exclusions = excluded_list[:5]
                    if len(excluded_list) > 5:
                        display_exclusions.append(f"...等{len(excluded_list)}个职位")
                    exclusion_text = f"\n请不要提供以下已获取的职位: {', '.join(display_exclusions)}，确保返回全新不同的职位信息。"
                
                logger.info(f"Requesting batch {batch+1}/{num_batches}, remaining: {remaining}")
                
                prompt = f"""
请使用网络搜索功能，从智联招聘、前程无忧(51job)、BOSS直聘、猎聘网、拉勾网、58同城、LinkedIn等主流招聘网站查询"{search_query}"相关的招聘信息，工作地点是"{location}"并提取{remaining}条有效结果，整理为如下JSON数组：

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

{exclusion_text}
请确保输出内容为严格 JSON 格式，且职位信息完整详细。
"""

                completion = client.chat.completions.create(
                    model="gpt-4o-search-preview",
                    web_search_options={},
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    timeout=60
                    # response_format={ "type": "json_object" }
                )

                raw_output = completion.choices[0].message.content
                # print(raw_output)

                json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
                if not json_match:
                    logger.warning(f"No JSON found in GPT response for batch {batch+1}. Continuing to next batch.")
                    continue

                batch_jobs = json.loads(json_match.group())
                
                # 处理本批次获取的职位
                for job in batch_jobs:
                    # 创建职位的唯一标识
                    job_key = f"{job.get('job_title', '未知职位')}_{job.get('company_name', '未知公司')}".lower()
                    
                    # 如果是重复职位，跳过
                    if job_key in excluded_jobs:
                        continue
                        
                    # 添加到已处理列表
                    excluded_jobs.add(job_key)
                    
                    # 添加元数据
                    job['search_query'] = search_query
                    job['extracted_at'] = datetime.utcnow().isoformat()
                    jobs.append(job)
                    
                    # 处理公司信息
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

                    # 添加到向量数据库
                    job_text = f"{job['job_title']} {job['company_name']} {job['description']}"
                    chromadb_service.add_job_posting(
                        job_id=f"gptweb_{int(time.time())}_{len(jobs)}",
                        job_text=job_text,
                        metadata=job
                    )
                
                logger.info(f"Batch {batch+1} completed. Total jobs so far: {len(jobs)}")
                
                # 如果已经获取足够的职位，提前结束
                if len(jobs) >= max_results:
                    break

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