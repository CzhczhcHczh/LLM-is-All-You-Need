<template>
  <div id="app">
    <!-- 首页美化版 -->
    <div v-if="$route.path === '/' || $route.path === '/home'" class="home-page">
      <!-- 粒子背景动画 -->
      <div class="particles-background">
        <div class="particle" v-for="n in 100" :key="n" :style="getParticleStyle()"></div>
      </div>
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
          <el-row :gutter="32">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(phase, index) in phases.slice(0, 4)" :key="phase.id">
              <el-card class="phase-card" :class="`phase-card-${index + 1}`" shadow="hover">
                <div class="card-icon">
                  <el-icon size="28">
                    <Search v-if="phase.id === 1" />
                    <Document v-else-if="phase.id === 2" />
                    <UserFilled v-else-if="phase.id === 3" />
                    <Calendar v-else-if="phase.id === 4" />
                  </el-icon>
                </div>
                <h3>
                  <div class="phase-number">Phase {{ phase.id }}</div>
                  <div class="phase-name">{{ phase.title.split(': ')[1] }}</div>
                </h3>
                <p>{{ phase.description }}</p>
                <el-button type="primary" size="large" @click="goToPhase(phase.route)">{{ phase.buttonText }}</el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 管理控制台单独卡片 -->
        <div class="admin-section">
          <el-card class="admin-card" shadow="hover">
            <div class="admin-content">
              <div class="admin-icon">
                <el-icon size="24">
                  <Setting />
                </el-icon>
              </div>
              <div class="admin-info">
                <h3>{{ phases[4].title }}</h3>
                <p>{{ phases[4].description }}</p>
              </div>
              <el-button type="primary" size="large" @click="goToPhase(phases[4].route)">{{ phases[4].buttonText }}</el-button>
            </div>
          </el-card>
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
import { Briefcase, Search, Document, UserFilled, Calendar, Setting } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Layout,
    Briefcase,
    Search,
    Document,
    UserFilled,
    Calendar,
    Setting
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const currentDemo = ref(null)
    const phases = [
      { id: 1, title: 'Phase 1: 职位搜索', description: '智能搜索招聘信息，结构化存储数据', buttonText: '开始搜索', route: '/phase1' },
      { id: 2, title: 'Phase 2: 简历制作', description: '个性化简历生成，针对不同职位定制', buttonText: '制作简历', route: '/phase2' },
      { id: 3, title: 'Phase 3: HR 模拟', description: '多种HR人格模拟，专业评分反馈', buttonText: 'HR评估', route: '/phase3' },
      { id: 4, title: 'Phase 4: 面试安排', description: '多Agent讨论，智能时间安排', buttonText: '安排面试', route: '/phase4' },
      { id: 5, title: '管理控制台', description: '查看与管理向量数据库中的职位信息', buttonText: '进入管理', route: '/admin' }
    ]
    const goToPhase = (routePath) => { router.push(routePath) }
    
    // 粒子动画样式生成
    const getParticleStyle = () => {
      return {
        left: Math.random() * 100 + '%',
        animationDelay: Math.random() * 20 + 's',
        animationDuration: (Math.random() * 10 + 10) + 's',
        opacity: Math.random() * 0.6 + 0.2
      }
    }
    
    return { currentDemo, phases, goToPhase, getParticleStyle }
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
  background: #f8fafc;
}

.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4fd 25%, #f0f8ff 50%, #e6f3ff 75%, #f8fafc 100%);
  position: relative;
  overflow: hidden;
}

/* 粒子背景动画 */
.particles-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, rgba(64, 158, 255, 1) 0%, rgba(64, 158, 255, 0.4) 50%, transparent 100%);
  border-radius: 50%;
  animation: float linear infinite;
}

.particle:nth-child(2n) {
  background: radial-gradient(circle, rgba(103, 194, 58, 1) 0%, rgba(103, 194, 58, 0.4) 50%, transparent 100%);
  width: 5px;
  height: 5px;
}

.particle:nth-child(3n) {
  background: radial-gradient(circle, rgba(255, 193, 7, 1) 0%, rgba(255, 193, 7, 0.4) 50%, transparent 100%);
  width: 7px;
  height: 7px;
}

.particle:nth-child(4n) {
  background: radial-gradient(circle, rgba(245, 108, 108, 1) 0%, rgba(245, 108, 108, 0.4) 50%, transparent 100%);
  width: 4px;
  height: 4px;
}

@keyframes float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

/* 为元素添加相对定位以确保在粒子之上 */
.app-header,
.home-main {
  position: relative;
  z-index: 1;
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
  margin-bottom: 40px;
  border-radius: 20px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  color: #fff;
  box-shadow: 0 20px 40px rgba(102,126,234,0.3);
  border: 0;
  position: relative;
  overflow: hidden;
  padding: 40px 24px;
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.welcome-card h2 {
  font-size: 36px;
  margin-bottom: 12px;
  font-weight: bold;
  position: relative;
  z-index: 1;
}
.welcome-desc {
  font-size: 20px;
  opacity: 0.95;
  position: relative;
  z-index: 1;
}
.phases {
  margin-top: 24px;
}

.phase-card {
  border-radius: 16px;
  margin-bottom: 32px;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 0;
  padding: 24px;
}

.phase-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.phase-card-1 {
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b95 100%);
  color: #fff;
}

.phase-card-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.phase-card-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #fff;
}

.phase-card-4 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #fff;
}

.phase-card-5 {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #fff;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px auto;
  backdrop-filter: blur(10px);
}

.phase-card h3 {
  margin: 0 0 12px 0;
  font-size: 22px;
  font-weight: bold;
  line-height: 1.3;
  text-align: center;
}

.phase-number {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
  opacity: 0.9;
}

.phase-name {
  font-size: 28px;
  font-weight: bold;
}

.phase-card p {
  flex: 1;
  margin-bottom: 20px;
  opacity: 0.9;
  font-size: 15px;
  line-height: 1.5;
}

.phase-card .el-button {
  align-self: stretch;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-weight: bold;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.phase-card .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* 管理控制台单独样式 */
.admin-section {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.admin-card {
  max-width: 500px;
  width: 100%;
  border-radius: 16px;
  background: linear-gradient(135deg, #8e44ad 0%, #e74c3c 100%);
  color: #fff;
  border: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.admin-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(142,68,173,0.25);
}

.admin-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.admin-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
}

.admin-info {
  flex: 1;
}

.admin-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: bold;
}

.admin-info p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
  line-height: 1.4;
}

.admin-card .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-weight: bold;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.admin-card .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}
.demo-section {
  margin-top: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
</style>
