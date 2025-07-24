# Phase4 功能测试指南

## 修改后的Phase4功能

### 数据流程
1. **Phase2** → 保存个人信息到 `userProfile`
2. **Phase3** → 选择职位，传递到Phase4，不保留HR评估结果
3. **Phase4** → 使用个人信息 + 职位信息进行AI分析和时间安排

### Phase4 三步流程

#### Step 1: 生成时间表
- 点击"生成时间表"按钮
- 系统为每个职位随机生成3-5个可选时间段
- 时间范围：未来14天，每天3个时间段

#### Step 2: AI多维度分析
- 点击"开始AI分析排序"按钮
- 调用 `/phase4/multi-llm-recommendation` API
- 展示3个LLM的独立分析结果
- 展示1个综合LLM的最终排序

#### Step 3: 生成最终日程
- 根据AI排序安排面试时间
- 展示时间线格式的最终日程
- 支持导出为文本文件

### 需要后端实现的API

```
POST /phase4/multi-llm-recommendation
{
  "personal_info": {
    "name": "张小明",
    "email": "zhang.xiaoming@example.com", 
    "phone": "138-0000-0000",
    "location": "北京市朝阳区"
  },
  "jobs": [
    {
      "job_title": "前端开发工程师",
      "company_name": "腾讯",
      "location": "深圳"
    }
  ]
}
```

**期望返回**：
```json
{
  "success": true,
  "data": {
    "llm_analysis": [
      {
        "llm_name": "技术专家分析师",
        "ranking": [
          {
            "job_title": "前端开发工程师",
            "company_name": "腾讯", 
            "score": 85,
            "reason": "该职位与候选人技能高度匹配..."
          }
        ]
      }
    ],
    "final_ranking": [
      {
        "job_title": "前端开发工程师",
        "company_name": "腾讯",
        "rank": 1,
        "score": 87,
        "reason": "综合考虑技能匹配度、发展前景..."
      }
    ],
    "final_summary": "综合三位AI分析师的评估..."
  }
}
```

### 测试要点

1. **个人信息正确显示**：进入Phase4后应该能看到正确的个人信息
2. **职位信息传递正确**：从Phase3选择的职位应该正确传递到Phase4
3. **不保留HR评估**：重新进入Phase3应该没有之前的HR评估结果
4. **时间表生成**：每个职位生成合理的时间段选择
5. **AI分析界面**：正确展示多个LLM的分析结果
6. **最终日程**：根据排序生成合理的面试时间安排

### 预期用户体验

用户现在可以：
- 在Phase2填写/生成个人信息
- 在Phase3进行HR评估（每次重新开始）
- 选择性地优化简历或直接进入Phase4
- 在Phase4看到完整的AI分析和智能日程安排
- 获得专业的面试时间规划
