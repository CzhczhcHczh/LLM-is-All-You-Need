<template>
  <el-container class="app-container">
  <!-- Header -->
  <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <el-icon><Briefcase /></el-icon>
          求职规划助手 - Job Planner Assistant
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
          
          <el-divider />
          
          <el-menu-item index="/admin">
            <el-icon><Setting /></el-icon>
            <span>管理控制台</span>
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
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../store.js'
import { Briefcase, Search, Document, User, Calendar, Setting } from '@element-plus/icons-vue'

export default {
  name: 'Layout',
  components: {
    Briefcase,
    Search,
    Document,
    User,
    Calendar,
    Setting
  },
  setup() {
    const route = useRoute()
    const store = useAppStore()
    
    const currentRoute = computed(() => route.path)
    
    // 初始化时检查数据一致性
    const initializeAppState = () => {
      // 如果 store 中没有搜索结果但 currentPhase > 1，重置为 Phase 1
      if (store.currentPhase > 1 && store.searchResults.jobs.length === 0) {
        console.log('检测到数据不一致，重置应用状态到 Phase 1')
        store.setCurrentPhase(1)
        
        // 清理可能存在的过时 localStorage 数据
        const itemsToCheck = [
          'selectedJobsForPhase4',
          'phase3HRFeedback',
          'generatedResumes',
          'selectedJob',
          'selectedJobs'
        ]
        
        itemsToCheck.forEach(item => {
          if (localStorage.getItem(item)) {
            console.log(`清理过时的 localStorage 数据: ${item}`)
            localStorage.removeItem(item)
          }
        })
      }
      
      // 如果有搜索结果但没有选择职位，且 currentPhase > 2，重置到可访问的最高阶段
      if (store.currentPhase > 2 && store.searchResults.selectedJobs.length === 0) {
        store.setCurrentPhase(1)
      }
    }
    
    const canAccessPhase = (phase) => {
      // Phase 1 is always accessible
      if (phase === 1) return true
      
      // For other phases, check if previous phases have been completed in the current session
      switch (phase) {
        case 2:
          // Phase 2: 需要先完成Phase 1（有搜索结果且选择了职位）
          return store.searchResults.jobs.length > 0 && store.searchResults.selectedJobs.length > 0
        case 3:
          // Phase 3: 需要先完成Phase 2（有生成的简历）并且当前进度至少到Phase 3
          const hasResumes = store.resumes.list.length > 0 || 
                            (localStorage.getItem('generatedResumes') && 
                             JSON.parse(localStorage.getItem('generatedResumes')).length > 0)
          return hasResumes && store.currentPhase >= 3
        case 4:
          // Phase 4: 需要先完成Phase 3（有HR反馈）并且当前进度到达Phase 4
          // 必须通过正常流程从Phase 3进入，不允许直接跳转
          const hasPhase3Completed = store.currentPhase >= 4
          const hasPassedJobs = localStorage.getItem('selectedJobsForPhase4')
          
          if (hasPhase3Completed && hasPassedJobs) {
            try {
              const passedJobs = JSON.parse(hasPassedJobs)
              return passedJobs.length > 0
            } catch (e) {
              return false
            }
          }
          
          return false
        default:
          return false
      }
    }
    
    // 组件挂载时初始化应用状态
    onMounted(() => {
      initializeAppState()
    })
    
    return {
      store,
      currentRoute,
      canAccessPhase
    }
  }
}
</script>

<style scoped>
/* 添加容器背景渐变效果 */
.app-container {
  height: 100vh;
  background: linear-gradient(135deg, #304156 0%, #2c3a4a 100%);
}

.app-header {
  background: #304156;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  height: 64px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 28px;
  font-weight: bold;
  color: #fff;
}

.user-info {
  font-size: 14px;
  opacity: 0.9;
  color: #fff;
}

.app-sidebar {
  background: linear-gradient(180deg, #304156 0%, #2c3a4a 100%);
  box-shadow: 2px 0 6px rgba(0,0,0,0.1);
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 120px);
  background: transparent;
}

.progress-section {
  padding: 20px;
  color: #bfcbd9;
  background: linear-gradient(135deg, rgba(48, 65, 86, 0.8) 0%, rgba(44, 58, 74, 0.8) 100%);
  margin: 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.progress-section h4 {
  margin-bottom: 15px;
  color: #66b3ff;
  font-weight: bold;
}

.app-main {
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4fd 25%, #f0f8ff 50%, #e6f3ff 75%, #f8fafc 100%);
  padding: 20px;
  position: relative;
}

.main-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-height: calc(100vh - 140px);
}

:deep(.el-menu-item.is-disabled) {
  opacity: 0.4;
}

:deep(.el-menu-item) {
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.3s ease;
}

:deep(.el-menu-item:hover) {
  background: rgba(64, 158, 255, 0.1);
  color: #66b3ff;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%);
  color: #66b3ff;
  font-weight: bold;
}

:deep(.el-steps--vertical .el-step__main) {
  padding-left: 10px;
}

:deep(.el-step__title) {
  font-size: 12px;
  line-height: 1.2;
  color: #bfcbd9;
  font-weight: 500;
}

:deep(.el-step__description) {
  font-size: 11px;
  margin-top: 2px;
  color: #8fa3b8;
}

:deep(.el-step__icon) {
  border-color: #66b3ff;
}

:deep(.el-step__icon.is-process) {
  background: #66b3ff;
  border-color: #66b3ff;
}

:deep(.el-step__icon.is-finish) {
  background: #67c23a;
  border-color: #67c23a;
}

:deep(.el-divider) {
  border-color: rgba(191, 203, 217, 0.3);
  margin: 16px 0;
}
</style>

