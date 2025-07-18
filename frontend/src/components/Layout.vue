<template>
  <el-container class="app-container">
    <!-- Header -->
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <el-icon><Briefcase /></el-icon>
          求职规划助手
        </h1>
        <div class="user-info" v-if="store.isUserLoggedIn">
          <span>欢迎，{{ store.user.full_name || store.user.username }}</span>
        </div>
      </div>
    </el-header>

    <el-container>
      <!-- Sidebar Navigation -->
      <el-aside width="250px" class="app-sidebar">
        <el-menu
          :default-active="currentRoute"
          router
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/phase1" :disabled="!canAccessPhase(1)">
            <el-icon><Search /></el-icon>
            <span>Phase 1: 职位搜索</span>
          </el-menu-item>
          
          <el-menu-item index="/phase2" :disabled="!canAccessPhase(2)">
            <el-icon><Document /></el-icon>
            <span>Phase 2: 简历制作</span>
          </el-menu-item>
          
          <el-menu-item index="/phase3" :disabled="!canAccessPhase(3)">
            <el-icon><User /></el-icon>
            <span>Phase 3: HR模拟</span>
          </el-menu-item>
          
          <el-menu-item index="/phase4" :disabled="!canAccessPhase(4)">
            <el-icon><Calendar /></el-icon>
            <span>Phase 4: 面试安排</span>
          </el-menu-item>
        </el-menu>
        
        <!-- Progress Indicator -->
        <div class="progress-section">
          <h4>进度</h4>
          <el-steps direction="vertical" :active="store.currentPhase - 1" finish-status="success">
            <el-step title="职位搜索" description="搜索并收集招聘信息"></el-step>
            <el-step title="简历制作" description="生成个性化简历"></el-step>
            <el-step title="HR模拟" description="获取HR反馈"></el-step>
            <el-step title="面试安排" description="智能安排面试时间"></el-step>
          </el-steps>
        </div>
      </el-aside>

      <!-- Main Content -->
      <el-main class="app-main">
        <div class="main-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../store.js'
import { Briefcase, Search, Document, User, Calendar } from '@element-plus/icons-vue'

export default {
  name: 'Layout',
  components: {
    Briefcase,
    Search,
    Document,
    User,
    Calendar
  },
  setup() {
    const route = useRoute()
    const store = useAppStore()
    
    const currentRoute = computed(() => route.path)
    
    const canAccessPhase = (phase) => {
      // Phase 1 is always accessible
      if (phase === 1) return true
      
      // For other phases, check if previous phases have data
      switch (phase) {
        case 2:
          return store.searchResults.jobs.length > 0
        case 3:
          return store.resumes.list.length > 0
        case 4:
          return store.hrFeedback.list.some(f => f.passes_screening)
        default:
          return false
      }
    }
    
    return {
      store,
      currentRoute,
      canAccessPhase
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.user-info {
  font-size: 14px;
  opacity: 0.9;
}

.app-sidebar {
  background-color: #304156;
  box-shadow: 2px 0 6px rgba(0,0,0,0.1);
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 120px);
}

.progress-section {
  padding: 20px;
  color: #bfcbd9;
}

.progress-section h4 {
  margin-bottom: 15px;
  color: #409EFF;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
}

.main-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  min-height: calc(100vh - 140px);
}

:deep(.el-menu-item.is-disabled) {
  opacity: 0.5;
}

:deep(.el-steps--vertical .el-step__main) {
  padding-left: 10px;
}

:deep(.el-step__title) {
  font-size: 12px;
  line-height: 1.2;
}

:deep(.el-step__description) {
  font-size: 11px;
  margin-top: 2px;
}
</style>

