# 求职规划助手 - Job Planner Assistant

基于多Agent系统的智能求职规划助手，从招聘信息收集到简历制作，从HR模拟到面试安排，为求职者提供全流程的智能化支持。

## 🚀 项目特色

- **多Agent协作**: 四个专业Agent分工协作，各司其职
- **智能化流程**: 从搜索到安排，全程AI辅助决策
- **个性化定制**: 根据用户背景和目标职位生成定制化简历
- **HR模拟**: 多角度HR评估，提供专业反馈
- **智能调度**: 多Agent讨论，优化面试时间安排

## 📋 功能概览

### Phase 1: 职位搜索Agent
- 🔍 智能搜索招聘信息
- 📊 结构化存储职位数据
- 🎯 基于用户画像推荐匹配职位
- 💾 向量数据库存储，支持相似度搜索

### Phase 2: 简历制作Agent
- 📝 个性化简历生成
- 🎨 针对不同职位定制内容
- 🔄 基于反馈迭代优化
- 📋 结构化数据存储，前端友好展示

### Phase 3: HR模拟Agent
- 👥 多种HR人格模拟
- 📈 专业评分和反馈
- 🔄 迭代优化建议
- 📅 面试邀请生成

### Phase 4: 面试安排Agent
- 🤖 多Agent讨论决策
- 📊 公司匹配度排序
- ⏰ 智能时间冲突解决
- 📅 最优面试日程安排

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **ChromaDB**: 向量数据库
- **OpenAI API**: 多模型LLM调用
- **Serper API**: 网络搜索服务
- **Pydantic**: 数据验证

### 前端技术栈
- **Vue 3**: 现代前端框架
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Axios**: HTTP客户端
- **Vite**: 构建工具

### 部署技术
- **Docker**: 容器化部署
- **Docker Compose**: 多服务编排
- **Nginx**: 反向代理(可选)

## 📁 项目结构

```
job_planner_assistant/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI应用入口
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库模型和操作
│   ├── services.py         # 外部服务集成
│   ├── agents.py           # 核心Agent实现
│   ├── api.py              # API路由
│   └── Dockerfile          # 后端容器配置
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   │   ├── Layout.vue  # 布局组件
│   │   │   ├── Phase1.vue  # 职位搜索
│   │   │   ├── Phase2.vue  # 简历制作
│   │   │   ├── Phase3.vue  # HR模拟
│   │   │   └── Phase4.vue  # 面试安排
│   │   ├── main.js         # 应用入口
│   │   ├── App.vue         # 根组件
│   │   ├── router.js       # 路由配置
│   │   ├── store.js        # 状态管理
│   │   └── api.js          # API调用
│   ├── package.json        # 依赖配置
│   ├── vite.config.js      # 构建配置
│   └── Dockerfile          # 前端容器配置
├── data/                   # 数据目录
│   ├── logs/              # 日志文件
│   └── chromadb/          # 向量数据库
├── requirements.txt        # Python依赖
├── docker-compose.yml      # Docker编排
├── start.sh               # 启动脚本
├── .env.example           # 环境变量模板
└── README.md              # 项目文档
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (可选)

### 1. 克隆项目
```bash
git clone <repository-url>
cd job_planner_assistant
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的API密钥
```

### 3. 启动服务

#### 方式一：使用启动脚本(推荐)
```bash
chmod +x start.sh
./start.sh
```

#### 方式二：Docker Compose
```bash
docker-compose up --build
```

#### 方式三：手动启动

**启动后端:**
```bash
cd backend
pip install -r ../requirements.txt
python main.py
```

**启动前端:**
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🔧 配置说明

### 必需的API密钥
```env
# OpenAI API (必需)
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Serper搜索API (必需)
SERPER_API_KEY=your_serper_api_key

# 数据库配置
DATABASE_URL=sqlite:///./data/job_planner.db

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 支持的LLM模型
- chatgpt-4o-latest
- claude-3-haiku
- claude-sonnet-4-20250514
- deepseek-r1-250528
- deepseek-v3
- doubao-1-5-vision-pro-32k-250115
- doubao-1.5-pro-256k
- gemini-2.5-flash-lite
- gemini-2.5-pro
- glm-4-32b-0414
- gpt-3.5-turbo
- grok-3-mini
- o1
- qwen2.5-14b-instruct
- qwen3-14b

## 👥 团队分工建议

### 开发人员A - 后端架构师
**负责模块:**
- `backend/main.py` - FastAPI应用配置
- `backend/config.py` - 配置管理
- `backend/database.py` - 数据库设计
- `backend/services.py` - 外部服务集成

**主要职责:**
- 设计和实现后端架构
- 配置数据库和外部服务
- 确保API接口规范
- 性能优化和错误处理

### 开发人员B - Agent专家
**负责模块:**
- `backend/agents.py` - 所有Agent实现
- `backend/api.py` - Agent相关API

**主要职责:**
- 实现四个核心Agent
- 优化LLM调用策略
- 设计Agent间协作机制
- 提升AI响应质量

### 开发人员C - 前端工程师
**负责模块:**
- `frontend/src/components/` - 所有Vue组件
- `frontend/src/store.js` - 状态管理
- `frontend/src/router.js` - 路由配置

**主要职责:**
- 实现用户界面
- 优化用户体验
- 响应式设计
- 前端状态管理

### 开发人员D - 全栈工程师
**负责模块:**
- `frontend/src/api.js` - API调用封装
- 部署配置文件
- 测试和集成

**主要职责:**
- 前后端接口对接
- 部署和运维配置
- 系统集成测试
- 文档维护

## 🔄 开发流程

### 1. 接口设计阶段
- 确定API接口规范
- 定义数据结构
- 约定错误处理机制

### 2. 并行开发阶段
- 后端开发API接口
- 前端开发UI组件
- Agent实现核心逻辑

### 3. 集成测试阶段
- 前后端联调
- Agent功能测试
- 用户体验优化

### 4. 部署上线阶段
- 容器化配置
- 生产环境部署
- 监控和维护

## 🧪 测试说明

### 后端测试
```bash
cd backend
python -m pytest tests/
```

### 前端测试
```bash
cd frontend
npm run test
```

### API测试
访问 http://localhost:8000/docs 使用Swagger UI进行API测试

### 演示模式
项目内置演示数据，可以在没有真实API密钥的情况下体验完整流程。

## 📝 API文档

### 核心接口

#### Phase 1 - 职位搜索
- `POST /api/phase1/search` - 搜索职位
- `POST /api/phase1/similar` - 相似职位推荐

#### Phase 2 - 简历生成
- `POST /api/phase2/generate` - 生成简历
- `POST /api/phase2/optimize` - 优化简历

#### Phase 3 - HR模拟
- `POST /api/phase3/review` - HR评估
- `POST /api/phase3/iterative` - 迭代反馈

#### Phase 4 - 面试安排
- `POST /api/phase4/discuss` - 多Agent讨论
- `POST /api/phase4/optimize` - 优化调度

#### 用户管理
- `POST /api/users` - 创建用户
- `GET /api/users/{id}` - 获取用户信息

#### 工具接口
- `GET /api/health` - 健康检查
- `GET /api/models` - 可用模型列表
- `POST /api/demo/full-workflow` - 完整流程演示

## 🚨 注意事项

### 开发注意事项
1. **API密钥安全**: 不要将API密钥提交到版本控制
2. **错误处理**: 确保所有API调用都有适当的错误处理
3. **数据验证**: 使用Pydantic进行数据验证
4. **日志记录**: 重要操作需要记录日志

### 部署注意事项
1. **环境变量**: 生产环境必须设置所有必需的环境变量
2. **数据持久化**: 确保数据目录正确挂载
3. **网络配置**: 确保服务间网络连通
4. **资源限制**: 根据实际需求配置容器资源

### 性能优化
1. **缓存策略**: 对频繁查询的数据进行缓存
2. **异步处理**: 长时间运行的任务使用异步处理
3. **数据库优化**: 合理设计索引和查询
4. **前端优化**: 组件懒加载和代码分割

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请通过以下方式联系:
- 提交 Issue
- 发送邮件
- 项目讨论区

---

**祝您求职顺利！** 🎉

