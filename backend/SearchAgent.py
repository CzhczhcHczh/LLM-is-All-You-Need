
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
            # print(raw_output)

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

                # 存入向量数据库（ChromaDBService会自动处理列表类型字段）
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

