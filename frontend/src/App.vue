<template>
  <div id="app">
    <!-- 如果在首页，显示简化版内容 -->
    <div v-if="$route.path === '/' || $route.path === '/home'" class="home-page">
      <h1>求职规划助手 - Job Planner Assistant</h1>
      <p>欢迎使用求职规划助手！</p>
      
      <div class="phases">
        <div class="phase-card" v-for="phase in phases" :key="phase.id">
          <h3>{{ phase.title }}</h3>
          <p>{{ phase.description }}</p>
          <button @click="goToPhase(phase.route)">{{ phase.buttonText }}</button>
        </div>
      </div>
      
      <div v-if="currentDemo" class="demo-section">
        <h2>{{ currentDemo }} 演示</h2>
        <p>这里是 {{ currentDemo }} 的演示内容</p>
        <button @click="currentDemo = null">关闭演示</button>
      </div>
    </div>
    
    <!-- 如果在其他页面，显示完整布局 -->
    <Layout v-else />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Layout from './components/Layout.vue'

export default {
  name: 'App',
  components: {
    Layout
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const currentDemo = ref(null)
    
    const phases = [
      {
        id: 1,
        title: 'Phase 1: 职位搜索',
        description: '智能搜索招聘信息，结构化存储数据',
        buttonText: '开始搜索',
        route: '/phase1'
      },
      {
        id: 2,
        title: 'Phase 2: 简历制作',
        description: '个性化简历生成，针对不同职位定制',
        buttonText: '制作简历',
        route: '/phase2'
      },
      {
        id: 3,
        title: 'Phase 3: HR模拟',
        description: '多种HR人格模拟，专业评分反馈',
        buttonText: 'HR评估',
        route: '/phase3'
      },
      {
        id: 4,
        title: 'Phase 4: 面试安排',
        description: '多Agent讨论，智能时间安排',
        buttonText: '安排面试',
        route: '/phase4'
      }
    ]
    
    const goToPhase = (routePath) => {
      router.push(routePath)
    }
    
    return {
      currentDemo,
      phases,
      goToPhase
    }
  }
}
</script>

<style>
/* 保留原有样式 + 添加响应式 */
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 保留原有的所有样式... */
</style>
