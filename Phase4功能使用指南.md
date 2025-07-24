# Phase4 面试安排功能使用指南

## 功能概述
Phase4是求职规划助手的第四阶段，主要负责：
1. **职位推荐度排序**：使用多个LLM对候选职位进行智能评分和排序
2. **面试时间安排**：为每个职位生成可选的面试时间段
3. **智能日程规划**：根据推荐度和用户偏好自动安排最优面试日程

## 数据流向
```
Phase1(职位搜索) → Phase2(简历生成) → Phase3(HR筛选) → Phase4(面试安排)
```

- **输入数据**：
  - 从Phase3传递：通过HR筛选的职位和简历
  - 从Phase2传递：用户个人信息和偏好设置
  
- **输出数据**：
  - 职位推荐度排序结果
  - 各公司可选面试时间段
  - 最终优化的面试日程安排

## 核心功能

### 1. 多LLM推荐排序
- **技术实现**：3个不同角色的LLM（技术专家、HR招聘师、职业规划师）分别评分
- **评分标准**：
  - 技能匹配度 (40%)
  - 职业发展前景 (25%)
  - 薪资待遇 (20%)
  - 公司文化匹配 (15%)
- **共识度**：计算多个LLM评分的一致性

### 2. 时间段生成
- **生成规则**：每个公司提供3-5个可选时间段
- **时间类型**：
  - 上午：09:00-12:00
  - 下午：14:00-17:00
  - 晚上：18:00-21:00
- **时间跨度**：未来14天内的工作日

### 3. 智能日程安排
- **优化原则**：
  - 优先安排推荐度高的职位
  - 避免时间冲突
  - 考虑用户时间偏好
  - 控制每日面试数量
  - 合理安排面试间隔

## 前端使用流程

### Step 1: 设置偏好
```javascript
userPreferences = {
  preferred_time: 'morning',      // 偏好时间：morning/afternoon/evening/all_day
  max_interviews_per_day: 2,      // 每天最多面试数：1-3
  interview_gap: '2h',            // 面试间隔
  priority_criteria: 'match_score' // 优先级标准
}
```

### Step 2: 开始推荐排序
- 点击"开始推荐度分析"按钮
- 系统调用`/api/phase4/discuss`接口
- 显示推荐排序结果和可选时间段

### Step 3: 生成最终日程
- 点击"生成最终日程"按钮
- 显示日历视图和日程详情
- 提供日程统计信息

## 后端API接口

### 主要接口
```
POST /api/phase4/discuss
```

**请求格式：**
```json
{
  "interviews": [
    {
      "job_title": "职位名称",
      "company_name": "公司名称",
      "skills": ["技能1", "技能2"],
      "salary_range": "薪资范围",
      // ... 其他职位信息
    }
  ],
  "user_preferences": {
    "user_profile": {
      "full_name": "用户姓名",
      "skills": ["技能1", "技能2"],
      // ... 用户信息
    },
    "preferred_time": "morning",
    "max_interviews_per_day": 2
  }
}
```

**响应格式：**
```json
{
  "success": true,
  "message": "处理成功",
  "data": {
    "recommendation_ranking": {
      "final_ranking": [...]  // 推荐排序结果
    },
    "available_time_slots": {
      "company_0": ["2025-07-25 09:00-12:00", ...]
    },
    "final_schedule": {
      "schedule": [
        {
          "date": "2025-07-25",
          "interviews": [...]
        }
      ],
      "schedule_summary": {
        "total_interviews": 5,
        "schedule_span_days": 3,
        "average_interviews_per_day": 1.7
      }
    }
  }
}
```

## 测试方法

### 1. 后端功能测试
```bash
python test_phase4.py
```

### 2. API集成测试
```bash
# 启动后端服务
python backend/main.py

# 运行集成测试
python test_phase4_integration.py
```

### 3. 前端测试
1. 确保前面三个阶段已完成
2. 进入Phase4页面
3. 检查数据加载是否正确
4. 测试推荐排序和日程生成功能

## 故障排除

### 常见问题

1. **数据加载失败**
   - 检查localStorage中是否有`selectedJobs`或`selectedJobsForPhase4`
   - 确认前面阶段是否正确完成

2. **API调用失败**
   - 检查后端服务是否启动（默认端口8000）
   - 查看浏览器控制台的网络请求错误

3. **推荐排序结果异常**
   - 检查用户信息是否完整
   - 确认职位数据格式是否正确

4. **日程显示问题**
   - 检查日期格式是否为YYYY-MM-DD
   - 确认时间段格式是否正确

### 调试建议
- 打开浏览器开发者工具查看控制台日志
- 检查Network标签页的API请求和响应
- 查看localStorage中存储的数据格式
- 检查后端日志文件`./data/logs/app.log`

## 扩展功能

### 可能的改进方向
1. **更智能的时间冲突解决**
2. **面试准备建议个性化**
3. **面试结果跟踪**
4. **日程导出功能（iCal格式）**
5. **邮件提醒功能**
6. **面试录音和笔记**

## 技术架构

### 后端组件
- `Phase4ScheduleAgent.py`：核心业务逻辑
- `api.py`：API路由和请求处理
- `database.py`：数据模型和存储

### 前端组件
- `Phase4.vue`：主要UI组件
- `api.js`：API调用封装
- `store.js`：状态管理

### 数据存储
- SQLite数据库：持久化存储
- localStorage：前端临时存储
- ChromaDB：向量数据库（用于相似度搜索）
