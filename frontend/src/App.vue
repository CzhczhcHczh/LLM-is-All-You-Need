<template>
  <div id="app">
    <!-- 首页美化版 -->
    <div v-if="$route.path === '/' || $route.path === '/home'" class="home-page">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon><Briefcase /></el-icon>
            求职规划助手 - Job Planner Assistant
          </h1>
        </div>
      </el-header>
      <el-main class="home-main">
        <el-card class="welcome-card" shadow="hover">
          <h2>欢迎使用求职规划助手！</h2>
          <p class="welcome-desc">一站式智能求职全流程体验</p>
        </el-card>
        <div class="phases">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="phase in phases" :key="phase.id">
              <el-card class="phase-card" shadow="hover">
                <h3>{{ phase.title }}</h3>
                <p>{{ phase.description }}</p>
                <el-button type="primary" size="large" @click="goToPhase(phase.route)">{{ phase.buttonText }}</el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <div v-if="currentDemo" class="demo-section">
          <el-card shadow="hover">
            <h2>{{ currentDemo }} 演示</h2>
            <p>这里是 {{ currentDemo }} 的演示内容</p>
            <el-button @click="currentDemo = null">关闭演示</el-button>
          </el-card>
        </div>
      </el-main>
    </div>
    <!-- 其他页面 -->
    <Layout v-else />
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Layout from './components/Layout.vue'
import { Briefcase } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Layout,
    Briefcase
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const currentDemo = ref(null)
    const phases = [
      { id: 1, title: 'Phase 1: 职位搜索', description: '智能搜索招聘信息，结构化存储数据', buttonText: '开始搜索', route: '/phase1' },
      { id: 2, title: 'Phase 2: 简历制作', description: '个性化简历生成，针对不同职位定制', buttonText: '制作简历', route: '/phase2' },
      { id: 3, title: 'Phase 3: HR模拟', description: '多种HR人格模拟，专业评分反馈', buttonText: 'HR评估', route: '/phase3' },
      { id: 4, title: 'Phase 4: 面试安排', description: '多Agent讨论，智能时间安排', buttonText: '安排面试', route: '/phase4' },
      { id: 5, title: '管理控制台', description: '查看与管理向量数据库中的职位信息', buttonText: '进入管理', route: '/admin' }
    ]
    const goToPhase = (routePath) => { router.push(routePath) }
    return { currentDemo, phases, goToPhase }
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background: #f5f7fa;
}
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
}
.app-header {
  background: #304156;
  color: #fff;
  padding: 0 0 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}
.app-title {
  font-size: 28px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  margin: 0;
}
.home-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 16px 0 16px;
}
.welcome-card {
  margin-bottom: 32px;
  border-radius: 12px;
  text-align: center;
  background: linear-gradient(90deg, #409EFF 0%, #67c23a 100%);
  color: #fff;
  box-shadow: 0 4px 24px rgba(64,158,255,0.08);
}
.welcome-card h2 {
  font-size: 32px;
  margin-bottom: 8px;
}
.welcome-desc {
  font-size: 18px;
  opacity: 0.95;
}
.phases {
  margin-top: 16px;
}
.phase-card {
  border-radius: 10px;
  margin-bottom: 24px;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: #fff;
}
.phase-card h3 {
  margin: 0 0 8px 0;
  color: #409EFF;
  font-size: 20px;
}
.phase-card p {
  flex: 1;
  color: #666;
  margin-bottom: 16px;
}
.phase-card .el-button {
  align-self: flex-end;
}
.demo-section {
  margin-top: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
</style>
