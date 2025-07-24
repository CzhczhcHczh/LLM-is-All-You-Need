#!/usr/bin/env python3
"""
Phase4 API测试脚本
用于测试多LLM推荐分析功能
"""

import json
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Phase4ScheduleAgent import Phase4ScheduleAgent

def test_multi_llm_recommendation():
    """测试多LLM推荐分析功能"""
    
    # 模拟个人信息
    personal_info = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "skills": ["Python", "Vue.js", "JavaScript", "React"],
        "experience": "3年前端开发经验",
        "target_position": "前端开发工程师"
    }
    
    # 模拟职位列表
    jobs = [
        {
            "job_title": "前端开发工程师",
            "company_name": "腾讯科技",
            "location": "深圳",
            "salary_range": "20-30K",
            "skills": ["Vue.js", "React", "JavaScript", "TypeScript"],
            "requirements": ["3年以上前端开发经验", "熟悉Vue/React框架"]
        },
        {
            "job_title": "Web前端开发",
            "company_name": "阿里巴巴",
            "location": "杭州", 
            "salary_range": "25-35K",
            "skills": ["React", "JavaScript", "Node.js"],
            "requirements": ["熟悉React生态", "有大型项目经验"]
        },
        {
            "job_title": "前端工程师",
            "company_name": "字节跳动",
            "location": "北京",
            "salary_range": "22-32K",
            "skills": ["Vue.js", "JavaScript", "Webpack"],
            "requirements": ["前端框架开发经验", "性能优化经验"]
        }
    ]
    
    print("🚀 开始测试多LLM推荐分析...")
    print(f"候选人: {personal_info['name']}")
    print(f"职位数量: {len(jobs)}")
    print("-" * 50)
    
    try:
        # 调用多LLM推荐分析
        result = Phase4ScheduleAgent.multi_llm_recommendation(personal_info, jobs)
        
        if result.get("success"):
            print("✅ 分析成功完成!")
            print(f"📊 分析师数量: {result.get('total_analysts', 0)}")
            print(f"💼 分析职位数: {result.get('total_jobs', 0)}")
            print(f"📝 综合总结: {result.get('final_summary', '')}")
            print()
            
            # 显示各分析师的评估
            print("🧠 各分析师评估结果:")
            for i, analysis in enumerate(result.get('llm_analysis', []), 1):
                print(f"\n{i}. {analysis.get('analyst_name', 'Unknown')}")
                print(f"   视角: {analysis.get('perspective', '')}")
                print(f"   关注: {analysis.get('focus', '')}")
                print(f"   权重: {analysis.get('weight', 1.0)}")
                
                # 显示前3个排序结果
                rankings = analysis.get('rankings', [])[:3]
                for rank in rankings:
                    print(f"   - {rank.get('job_title', '')} ({rank.get('company', '')}) - {rank.get('score', 0)}分")
            
            print("\n🏆 最终推荐排序:")
            for rank in result.get('final_ranking', []):
                print(f"  #{rank.get('rank', 0)} {rank.get('job_title', '')} - {rank.get('company', '')} "
                      f"(综合评分: {rank.get('score', 0)}分, 共识度: {rank.get('consensus', '未知')})")
                
        else:
            print("❌ 分析失败:")
            print(f"错误信息: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()

def test_json_format():
    """测试JSON格式的数据处理"""
    print("\n🔧 测试JSON格式处理...")
    
    # 测试mock数据生成
    test_jobs = [
        {"job_title": "测试职位1", "company_name": "测试公司1", "skills": ["Python", "Vue"]},
        {"job_title": "测试职位2", "company_name": "测试公司2", "skills": ["React", "Node.js"]}
    ]
    
    try:
        mock_result = Phase4ScheduleAgent._generate_mock_ranking_response(
            test_jobs, "技术专家视角", 42
        )
        
        print("✅ Mock数据生成成功")
        print(f"分析视角: {mock_result.get('analysis_perspective', '')}")
        print(f"职位数量: {len(mock_result.get('rankings', []))}")
        
        # 验证JSON序列化
        json_str = json.dumps(mock_result, ensure_ascii=False, indent=2)
        parsed_back = json.loads(json_str)
        print("✅ JSON序列化/反序列化成功")
        
    except Exception as e:
        print(f"❌ JSON格式测试失败: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Phase4 多LLM推荐分析 - 功能测试")
    print("=" * 60)
    
    # 运行测试
    test_multi_llm_recommendation()
    test_json_format()
    
    print("\n" + "=" * 60)
    print("测试完成! 🎉")
    print("=" * 60)
