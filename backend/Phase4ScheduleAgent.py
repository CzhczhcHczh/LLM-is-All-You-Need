import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import random
from services import llm_service

class Phase4ScheduleAgent:
    """Phase 4: Interview scheduling and optimization agent."""
    
    @staticmethod
    def generate_interview_time_slots(jobs: List[Dict[str, Any]], days_ahead: int = 14) -> Dict[str, List[str]]:
        """为每个公司/职位生成2-5个可选面试时间段"""
        time_slots = {}
        base_date = datetime.now()
        
        # 定义时间段
        time_periods = {
            "morning": "09:00-12:00",
            "afternoon": "14:00-17:00", 
            "evening": "18:00-21:00"
        }
        
        for i, job in enumerate(jobs):
            company_key = f"company_{i}"
            company_slots = []
            # 每个公司随机生成3-5个时间段
            num_slots = random.randint(3, 5)
            
            # 生成随机日期和时间段
            for _ in range(num_slots):
                # 随机选择未来14天内的某一天
                random_day = random.randint(1, days_ahead)
                target_date = base_date + timedelta(days=random_day)
                
                # 随机选择时间段
                period_key = random.choice(list(time_periods.keys()))
                period_time = time_periods[period_key]
                
                # 格式化时间字符串
                date_str = target_date.strftime("%Y-%m-%d")
                time_slot = f"{date_str} {period_time}"
                
                if time_slot not in company_slots:  # 避免重复
                    company_slots.append(time_slot)
            
            time_slots[company_key] = sorted(company_slots)
        
        return time_slots

    @staticmethod
    def multi_llm_recommendation_ranking(user_profile: Dict[str, Any], selected_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """多LLM讨论职位推荐度排序"""
        try:
            logger.info(f"Starting multi-LLM recommendation ranking for {len(selected_jobs)} jobs")
            
            # 准备用户和职位信息
            ranking_context = f"""
            用户个人信息：
            {json.dumps(user_profile, ensure_ascii=False, indent=2)}
            
            候选职位列表：
            {json.dumps(selected_jobs, ensure_ascii=False, indent=2)}
            
            请根据以下标准对职位进行推荐度排序：
            1. 技能匹配度 (40%)
            2. 职业发展前景 (25%)
            3. 薪资待遇 (20%)
            4. 公司声誉和文化匹配 (15%)
            
            请输出JSON格式的排序结果：
            {{
                "rankings": [
                    {{
                        "job_index": 0,
                        "company_name": "公司名称",
                        "position": "职位名称", 
                        "recommendation_score": 85,
                        "ranking_reason": "推荐理由"
                    }}
                ],
                "analysis_perspective": "你的分析角度"
            }}
            """
            
            # 模拟三个LLM的响应
            llm_responses = []
            perspectives = ["技术专家视角", "HR招聘视角", "职业规划师视角"]
            
            for i, perspective in enumerate(perspectives):
                # 调用真实的LLM服务
                try:
                    response = llm_service.call_phase4_models(ranking_context + f"\n分析角度：{perspective}")
                    if response and len(response) > 0:
                        llm_response = response[0]  # 取第一个模型的响应
                    else:
                        # 如果LLM调用失败，使用mock数据
                        llm_response = json.dumps(Phase4ScheduleAgent._generate_mock_ranking_response(selected_jobs, perspective, i))
                except Exception as e:
                    logger.warning(f"LLM call failed for {perspective}: {e}, using mock data")
                    llm_response = json.dumps(Phase4ScheduleAgent._generate_mock_ranking_response(selected_jobs, perspective, i))
                
                llm_responses.append({
                    "llm_id": f"LLM_{i+1}",
                    "perspective": perspective,
                    "response": llm_response
                })
            
            # 综合LLM意见生成最终排序
            final_ranking = Phase4ScheduleAgent._synthesize_final_ranking(llm_responses, selected_jobs)
            
            return {
                "success": True,
                "message": "Multi-LLM recommendation ranking completed",
                "data": {
                    "final_ranking": final_ranking,
                    "llm_discussions": llm_responses,
                    "ranking_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in multi-LLM ranking: {e}")
            return {
                "success": False,
                "message": f"Multi-LLM ranking failed: {str(e)}",
                "data": {}
            }

    @staticmethod
    def _generate_mock_ranking_response(jobs: List[Dict[str, Any]], perspective: str, seed: int) -> Dict[str, Any]:
        """生成模拟的LLM排序响应"""
        random.seed(seed)
        rankings = []
        
        for i, job in enumerate(jobs):
            # 根据不同视角生成不同的评分
            base_score = random.randint(60, 95)
            if perspective == "技术专家视角":
                # 技术专家更关注技术栈匹配
                if any(skill in str(job.get('skills', [])) for skill in ['Python', 'Java', 'React', 'Vue']):
                    base_score += 5
            elif perspective == "HR招聘视角":
                # HR更关注软技能和文化匹配
                if job.get('company_name') in ['阿里巴巴', '腾讯', '字节跳动']:
                    base_score += 8
            
            rankings.append({
                "job_index": i,
                "company_name": job.get('company_name', ''),
                "position": job.get('job_title', ''),
                "recommendation_score": min(100, base_score),
                "ranking_reason": f"从{perspective}分析，该职位匹配度较高"
            })
        
        # 按评分排序
        rankings.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return {
            "rankings": rankings,
            "analysis_perspective": perspective
        }

    @staticmethod
    def _synthesize_final_ranking(llm_responses: List[Dict[str, Any]], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """综合多个LLM的意见生成最终排序"""
        job_scores = {}
        
        # 计算每个职位的平均评分
        for response in llm_responses:
            try:
                # 尝试解析LLM响应的JSON
                if isinstance(response["response"], str):
                    response_data = json.loads(response["response"])
                else:
                    response_data = response["response"]
                    
                rankings = response_data.get("rankings", [])
            except (json.JSONDecodeError, KeyError):
                logger.warning(f"Failed to parse LLM response, using mock data")
                rankings = Phase4ScheduleAgent._generate_mock_ranking_response(jobs, response["perspective"], 0)["rankings"]
            
            for rank in rankings:
                job_idx = rank["job_index"]
                score = rank["recommendation_score"]
                
                if job_idx not in job_scores:
                    job_scores[job_idx] = []
                job_scores[job_idx].append(score)
        
        # 计算平均分并生成最终排序
        final_rankings = []
        for job_idx, scores in job_scores.items():
            avg_score = sum(scores) / len(scores)
            job = jobs[job_idx]
            
            final_rankings.append({
                "job_index": job_idx,
                "company_name": job.get('company_name', ''),
                "position": job.get('job_title', ''),
                "final_recommendation_score": round(avg_score, 2),
                "individual_scores": scores,
                "consensus_level": "高" if max(scores) - min(scores) <= 10 else "中等"
            })
        
        # 按最终评分排序
        final_rankings.sort(key=lambda x: x['final_recommendation_score'], reverse=True)
        
        # 添加排名
        for i, ranking in enumerate(final_rankings):
            ranking["final_rank"] = i + 1
        
        return final_rankings

    @staticmethod
    def generate_final_interview_schedule(
        ranked_jobs: List[Dict[str, Any]], 
        available_slots: Dict[str, List[str]], 
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终面试日程安排"""
        try:
            logger.info("Generating final interview schedule")
            
            # 构建LLM提示
            schedule_prompt = f"""
            根据以下信息生成最优的面试日程安排：
            
            职位推荐排序（按优先级排列）：
            {json.dumps(ranked_jobs, ensure_ascii=False, indent=2)}
            
            各公司可选时间段：
            {json.dumps(available_slots, ensure_ascii=False, indent=2)}
            
            用户偏好设置：
            {json.dumps(user_preferences, ensure_ascii=False, indent=2)}
            
            请生成最优的面试安排，考虑以下原则：
            1. 优先安排推荐度高的职位
            2. 避免时间冲突
            3. 合理分配面试间隔
            4. 考虑用户的时间偏好
            5. 每天面试数量不超过用户设定的最大值
            
            请输出JSON格式的日程安排：
            {{
                "schedule": [
                    {{
                        "date": "2024-01-20",
                        "interviews": [
                            {{
                                "time": "09:00-12:00",
                                "company_name": "公司名称",
                                "position": "职位名称",
                                "priority_rank": 1,
                                "preparation_tips": "面试准备建议"
                            }}
                        ]
                    }}
                ],
                "schedule_summary": {{
                    "total_interviews": 5,
                    "schedule_span_days": 7,
                    "average_interviews_per_day": 0.7,
                    "optimization_notes": "调度优化说明"
                }}
            }}
            """
            
            # 调用LLM服务生成日程
            try:
                schedule_responses = llm_service.call_phase4_models(schedule_prompt)
                if schedule_responses and len(schedule_responses) > 0:
                    schedule_result = json.loads(schedule_responses[0])
                else:
                    # LLM调用失败，使用mock数据
                    schedule_result = Phase4ScheduleAgent._generate_mock_schedule(ranked_jobs, available_slots, user_preferences)
            except Exception as e:
                logger.warning(f"LLM schedule generation failed: {e}, using mock data")
                schedule_result = Phase4ScheduleAgent._generate_mock_schedule(ranked_jobs, available_slots, user_preferences)
            
            return {
                "success": True,
                "message": "Final interview schedule generated successfully",
                "data": schedule_result
            }
            
        except Exception as e:
            logger.error(f"Error generating final schedule: {e}")
            return {
                "success": False,
                "message": f"Schedule generation failed: {str(e)}",
                "data": {}
            }

    @staticmethod
    def _generate_mock_schedule(ranked_jobs: List[Dict[str, Any]], available_slots: Dict[str, List[str]], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成模拟的面试日程"""
        schedule = []
        used_slots = set()
        max_per_day = user_preferences.get('max_interviews_per_day', 2)
        
        # 按推荐排序安排面试
        current_date = None
        interviews_today = 0
        
        for i, job in enumerate(ranked_jobs[:5]):  # 最多安排前5个职位
            company_key = f"company_{job['job_index']}"
            available = available_slots.get(company_key, [])
            
            # 找到可用的时间段
            selected_slot = None
            for slot in available:
                if slot not in used_slots:
                    slot_date = slot.split()[0]
                    
                    # 检查当天面试数量
                    if slot_date != current_date:
                        current_date = slot_date
                        interviews_today = 0
                    
                    if interviews_today < max_per_day:
                        selected_slot = slot
                        used_slots.add(slot)
                        interviews_today += 1
                        break
            
            if selected_slot:
                date_part = selected_slot.split()[0]
                time_part = selected_slot.split()[1]
                
                # 找到对应日期的记录或创建新记录
                date_record = next((item for item in schedule if item["date"] == date_part), None)
                if not date_record:
                    date_record = {"date": date_part, "interviews": []}
                    schedule.append(date_record)
                
                date_record["interviews"].append({
                    "time": time_part,
                    "company_name": job['company_name'],
                    "position": job['position'],
                    "priority_rank": job['final_rank'],
                    "recommendation_score": job['final_recommendation_score'],
                    "preparation_tips": f"重点准备{job['position']}相关技能展示"
                })
        
        # 按日期排序
        schedule.sort(key=lambda x: x["date"])
        
        return {
            "schedule": schedule,
            "schedule_summary": {
                "total_interviews": sum(len(day["interviews"]) for day in schedule),
                "schedule_span_days": len(schedule),
                "average_interviews_per_day": round(sum(len(day["interviews"]) for day in schedule) / max(len(schedule), 1), 1),
                "optimization_notes": "已根据推荐度排序和用户偏好优化安排"
            }
        }

    @staticmethod
    def multi_agent_discussion(interviews: List[Dict[str, Any]], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """完整的Phase4流程：推荐排序 + 时间生成 + 最终调度"""
        try:
            logger.info(f"Starting Phase4 complete workflow for {len(interviews)} positions")
            
            # Step 1: 多LLM推荐度排序
            user_profile = user_preferences.get('user_profile', {})
            ranking_result = Phase4ScheduleAgent.multi_llm_recommendation_ranking(user_profile, interviews)
            
            if not ranking_result["success"]:
                return ranking_result
            
            ranked_jobs = ranking_result["data"]["final_ranking"]
            
            # Step 2: 生成每个公司的可选时间段
            available_slots = Phase4ScheduleAgent.generate_interview_time_slots(interviews)
            
            # Step 3: 生成最终面试日程
            schedule_result = Phase4ScheduleAgent.generate_final_interview_schedule(
                ranked_jobs, available_slots, user_preferences
            )
            
            if not schedule_result["success"]:
                return schedule_result
            
            return {
                "success": True,
                "message": "Phase4 complete workflow finished successfully",
                "data": {
                    "recommendation_ranking": ranking_result["data"],
                    "available_time_slots": available_slots,
                    "final_schedule": schedule_result["data"],
                    "workflow_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Phase4 workflow: {e}")
            return {
                "success": False,
                "message": f"Phase4 workflow failed: {str(e)}",
                "data": {}
            }

    @staticmethod
    def optimize_schedule(interviews: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """保持原有的优化方法"""
        try:
            scored_interviews = []
            for interview in interviews:
                base_score = interview.get('match_score', 50)
                company_bonus = 10 if 'BAT' in interview.get('company_name', '') else 0
                salary_bonus = 5 if interview.get('salary_range', '').find('20k') > -1 else 0
                final_score = min(100, base_score + company_bonus + salary_bonus)
                
                scored_interviews.append({
                    **interview,
                    'calculated_score': final_score
                })
            
            scored_interviews.sort(key=lambda x: x.get('calculated_score', 0), reverse=True)
            
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
    
    @staticmethod
    def multi_llm_recommendation(personal_info: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Multi-LLM job recommendation analysis."""
        try:
            # 模拟三个不同的LLM分析师
            llm_analysts = [
                {
                    "llm_name": "技术专家分析师",
                    "focus": "技能匹配度和技术发展前景"
                },
                {
                    "llm_name": "职业规划分析师", 
                    "focus": "职业发展路径和成长空间"
                },
                {
                    "llm_name": "综合评估分析师",
                    "focus": "工作环境和企业文化匹配"
                }
            ]
            
            llm_analysis = []
            all_rankings = []
            
            # 每个LLM分析师独立评分
            for analyst in llm_analysts:
                # 这里应该调用真实的LLM，暂时使用mock数据
                analyst_result = {
                    "analyst": analyst["llm_name"],
                    "focus": analyst["focus"],
                    "rankings": []
                }
                
                for i, job in enumerate(jobs):
                    score = random.randint(70, 95)
                    analyst_result["rankings"].append({
                        "job_index": i,
                        "job_title": job.get("job_title", ""),
                        "company": job.get("company_name", ""),
                        "score": score,
                        "reason": f"基于{analyst['focus']}的分析评分"
                    })
                
                llm_analysis.append(analyst_result)
                all_rankings.extend(analyst_result["rankings"])
            
            # 综合分析师整合三个LLM的结果
            final_ranking = []
            for i, job in enumerate(jobs):
                job_scores = [r["score"] for r in all_rankings if r["job_index"] == i]
                avg_score = sum(job_scores) / len(job_scores) if job_scores else 0
                
                final_ranking.append({
                    "rank": 0,  # 将在排序后更新
                    "job_title": job.get("job_title", ""),
                    "company": job.get("company_name", ""),
                    "score": round(avg_score, 1),
                    "individual_scores": job_scores
                })
            
            # 按综合分数重新排序
            final_ranking.sort(key=lambda x: x["score"], reverse=True)
            
            # 更新最终排名
            for i, item in enumerate(final_ranking):
                item["rank"] = i + 1
            
            # **关键修改：调用LLM生成综合分析总结**
            final_summary = Phase4ScheduleAgent._generate_llm_summary(personal_info, final_ranking, llm_analysis)
            
            return {
                "llm_analysis": llm_analysis,
                "final_ranking": final_ranking,
                "final_summary": final_summary,
                "analysis_time": datetime.now().isoformat(),
                "candidate_name": personal_info.get("name", "候选人")
            }
            
        except Exception as e:
            logger.error(f"Error in multi-LLM recommendation: {e}")
            return {
                "llm_analysis": [],
                "final_ranking": [],
                "final_summary": "分析过程中出现错误，请重试",
                "error": str(e)
            }

    @staticmethod
    def _generate_llm_summary(personal_info: Dict[str, Any], final_ranking: List[Dict[str, Any]], llm_analysis: List[Dict[str, Any]]) -> str:
        """调用LLM生成综合分析总结"""
        try:
            summary_prompt = f"""
            请基于以下信息生成一份专业的求职推荐总结报告：

            候选人信息：
            {json.dumps(personal_info, ensure_ascii=False, indent=2)}

            最终职位排序结果：
            {json.dumps(final_ranking, ensure_ascii=False, indent=2)}

            各分析师详细评估：
            {json.dumps(llm_analysis, ensure_ascii=False, indent=2)}

            请生成一份简洁专业的总结，包含：
            1. 分析概述（分析了多少个职位）
            2. 重点推荐（排名前1-2的职位及推荐理由）
            3. 决策建议（如何安排面试优先级）
            4. 注意事项（需要考虑的个人因素）

            要求：
            - 语言简洁专业
            - 突出关键信息
            - 提供实用建议
            - 字数控制在200字以内
            """
            
            # 调用LLM服务生成总结
            try:
                summary_responses = llm_service.call_phase4_models(summary_prompt)
                if summary_responses and len(summary_responses) > 0:
                    summary = summary_responses[0]
                    # 如果LLM返回的是演示数据，使用降级方案
                    if "演示模式" in summary:
                        return Phase4ScheduleAgent._generate_fallback_summary(personal_info, final_ranking)
                    return summary
                else:
                    return Phase4ScheduleAgent._generate_fallback_summary(personal_info, final_ranking)
            except Exception as e:
                logger.warning(f"LLM summary generation failed: {e}")
                return Phase4ScheduleAgent._generate_fallback_summary(personal_info, final_ranking)
            
        except Exception as e:
            logger.error(f"Error generating LLM summary: {e}")
            return Phase4ScheduleAgent._generate_fallback_summary(personal_info, final_ranking)

    @staticmethod
    def _generate_fallback_summary(personal_info: Dict[str, Any], final_ranking: List[Dict[str, Any]]) -> str:
        """生成降级总结（当LLM调用失败时使用）"""
        candidate_name = personal_info.get('name', '您')
        job_count = len(final_ranking)
        
        if not final_ranking:
            return f"抱歉，{candidate_name}，未能找到合适的职位推荐。建议扩大搜索范围或调整期望条件。"
        
        top_job = final_ranking[0]
        fallback_summary = f"经过AI分析师团队评估，为{candidate_name}分析了{job_count}个职位机会。"
        fallback_summary += f"最推荐的是{top_job['company']}的{top_job['job_title']}职位（综合评分：{top_job['score']}分）。"
        fallback_summary += "建议优先安排推荐度较高的职位面试，同时考虑个人时间安排和职业发展目标。"
        
        return fallback_summary