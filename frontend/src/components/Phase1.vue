<template>
  <div class="phase1-page">
    <!-- 粒子背景动画 -->
    <div class="particles-background">
      <div class="particle" v-for="n in 100" :key="n" :style="getParticleStyle()"></div>
    </div>
    
    <div class="phase1-container">
      <el-card class="search-card">
        <template #header>
          <div class="card-header">
            <h2><el-icon><Search /></el-icon> Phase 1: 职位搜索</h2>
            <p>输入您的求职意向，我们将为您搜索相关职位</p>
          </div>
        </template>

      <!-- Search Form -->
      <el-form :model="searchForm" label-width="100px" @submit.prevent="handleSearch">
        <el-form-item label="职位关键词">
          <el-input
            v-model="searchForm.searchQuery"
            placeholder="例如：前端开发、Python工程师、产品经理"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="工作地点">
          <el-input
            v-model="searchForm.location"
            placeholder="例如：北京、上海、深圳"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="搜索数量">
          <el-slider
            v-model="searchForm.maxResults"
            :min="5"
            :max="50"
            :step="5"
            show-stops
            show-input
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleSearch"
            :loading="store.searchResults.loading"
            size="large"
          >
            <el-icon><Search /></el-icon>
            开始搜索
          </el-button>
          
          <el-button @click="handleDemo" type="success" size="large">
            <el-icon><Promotion /></el-icon>
            演示模式
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Search Results -->
    <el-card v-if="store.searchResults.jobs.length > 0" class="results-card">
      <template #header>
        <div class="results-header">
          <h3>搜索结果 ({{ store.searchResults.jobs.length }} 个职位)</h3>
          <div class="selected-jobs-info">
            <span v-if="store.searchResults.selectedJobs.length > 0" class="selected-count">
              已选择 {{ store.searchResults.selectedJobs.length }} 个职位
            </span>
            <el-button @click="proceedToPhase2" type="primary" :disabled="store.searchResults.selectedJobs.length === 0">
              进入下一阶段 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 已选职位列表 -->
      <div v-if="store.searchResults.selectedJobs.length > 0" class="selected-jobs">
        <h4>已选择的职位：</h4>
        <el-tag
          v-for="(job, index) in store.searchResults.selectedJobs"
          :key="index"
          closable
          @close="removeSelectedJob(index)"
          class="selected-job-tag"
        >
          {{ job.job_title }} - {{ job.company_name }}
        </el-tag>
        <div class="selected-jobs-actions">
          <el-button size="small" type="danger" @click="clearSelectedJobs">清空所选职位</el-button>
        </div>
      </div>

      <div class="jobs-grid">
        <el-card 
          v-for="(job, index) in paginatedJobs" 
          :key="index"
          class="job-card"
          shadow="hover"
        >
          <div class="job-header">
            <h4>{{ job.job_title }}</h4>
            <el-tag type="primary">{{ job.company_name }}</el-tag>
          </div>
          
          <div class="job-details">
            <p><el-icon><Location /></el-icon> {{ job.location }}</p>
            <p v-if="job.salary_range"><el-icon><Money /></el-icon> {{ job.salary_range }}</p>
          </div>
          
          <div class="job-description">
            <p>{{ formatDescription(job.description) }}</p>
          </div>
          
          <div class="job-skills" v-if="job.skills">
            <el-tag 
              v-for="(skill, idx) in formatSkills(job.skills)" 
              :key="idx"
              size="small"
              effect="plain"
              class="skill-tag"
            >
              {{ skill }}
            </el-tag>
          </div>
          
          <div class="job-actions">
            <el-button size="small" @click="viewJobDetails(job)">
              查看详情
            </el-button>
            <el-button size="small" type="primary" @click="selectJob(job)">
              选择此职位
            </el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 底部分页 -->
      <div class="pagination-container bottom">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="store.searchResults.jobs.length"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Loading State -->
    <el-card v-if="store.searchResults.loading" class="loading-card">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <h3>正在搜索职位...</h3>
        <p>请稍候，我们正在为您收集最新的招聘信息</p>
      </div>
    </el-card>

    <!-- Job Details Dialog -->
    <el-dialog v-model="showJobDialog" title="职位详情" width="70%">
      <div v-if="selectedJob" class="job-detail-content">
        <h3 class="job-detail-title">{{ selectedJob.job_title }}</h3>
        <p class="job-detail-company"><strong>公司：</strong>{{ selectedJob.company_name }}</p>
        <p class="job-detail-location"><strong>地点：</strong>{{ selectedJob.location }}</p>
        <p v-if="selectedJob.salary_range" class="job-detail-salary"><strong>薪资：</strong>{{ selectedJob.salary_range }}</p>
        
        <el-divider>职位描述</el-divider>
        <p class="job-detail-description">{{ selectedJob.description }}</p>
        
        <el-divider>任职要求</el-divider>
        <ul v-if="selectedJob.requirements" class="job-detail-requirements">
          <li v-for="(req, idx) in formatRequirements(selectedJob.requirements)" :key="idx">{{ req }}</li>
        </ul>
        
        <el-divider>技能要求</el-divider>
        <div v-if="selectedJob.skills" class="job-detail-skills">
          <el-tag 
            v-for="(skill, idx) in formatSkills(selectedJob.skills)" 
            :key="idx"
            style="margin: 5px;"
          >
            {{ skill }}
          </el-tag>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showJobDialog = false">关闭</el-button>
        <el-button type="primary" @click="selectJob(selectedJob)">选择此职位</el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Location, Money, ArrowRight, Loading, Promotion } from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'

export default {
  name: 'Phase1',
  components: {
    Search,
    Location,
    Money,
    ArrowRight,
    Loading,
    Promotion
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    
    // 添加分页相关变量
    const currentPage = ref(1)
    const pageSize = ref(6)  // 修改为每页显示6个职位
    
    // 分页后的职位数据
    const paginatedJobs = computed(() => {
      const startIndex = (currentPage.value - 1) * pageSize.value
      const endIndex = startIndex + pageSize.value
      return store.searchResults.jobs.slice(startIndex, endIndex)
    })
    
    // 处理页码变化
    const handlePageChange = (page) => {
      currentPage.value = page
    }
    
    // 格式化职位描述，截断长文本
    const formatDescription = (description) => {
      if (!description) return ''
      return description.length > 150 ? `${description.substring(0, 150)}...` : description
    }
    
    // 格式化技能，处理可能是字符串或数组的情况
    const formatSkills = (skills) => {
      if (!skills) return []
      if (Array.isArray(skills)) return skills
      if (typeof skills === 'string') return skills.split(',').map(s => s.trim())
      return []
    }
    
    // 格式化职位要求，处理可能是字符串或数组的情况
    const formatRequirements = (requirements) => {
      if (!requirements) return []
      if (Array.isArray(requirements)) return requirements
      if (typeof requirements === 'string') return requirements.split(',').map(r => r.trim())
      return []
    }
    
    const searchForm = reactive({
      searchQuery: '',
      location: '',
      maxResults: 20
    })
    
    const showJobDialog = ref(false)
    const selectedJob = ref(null)
    
    const handleSearch = async () => {
      if (!searchForm.searchQuery.trim()) {
        ElMessage.warning('请输入职位关键词')
        return
      }
      
      // 重置分页到第一页
      currentPage.value = 1
      
      // 显示加载状态
      store.setSearchLoading(true)
      store.setSearchQuery(searchForm.searchQuery)
      
      try {
        const response = await apiService.searchJobs({
          search_query: searchForm.searchQuery,
          location: searchForm.location || null,
          max_results: searchForm.maxResults
        })
        
        if (response.success) {
          // 验证返回的数据格式
          if (!response.data || !Array.isArray(response.data.jobs)) {
            throw new Error('搜索返回的数据格式不正确')
          }
          
          // 处理职位数据中的字段格式
          const processedJobs = (response.data.jobs || []).map(job => {
            return {
              ...job,
              // 确保这些字段即使是字符串也能被正确处理
              requirements: formatRequirements(job.requirements),
              skills: formatSkills(job.skills)
            }
          })
          
          // 设置处理后的结果
          store.setSearchResults({
            jobs: processedJobs,
            companies: response.data.companies || [],
            search_query: response.data.search_query
          })
          
          ElMessage.success(`找到 ${processedJobs.length} 个职位`)
        } else {
          ElMessage.error(response.message || '搜索失败')
        }
      } catch (error) {
        console.error('Search error:', error)
        ElMessage.error(`搜索过程中出现错误: ${error.message || '未知错误'}`)
        // 重置搜索结果，避免显示错误数据
        store.setSearchResults({ jobs: [], companies: [] })
      } finally {
        store.setSearchLoading(false)
      }
    }
    
    const handleDemo = async () => {
      // Demo mode with mock data
      store.setSearchLoading(true)
      
      // 重置分页到第一页
      currentPage.value = 1
      
      // Simulate API delay
      setTimeout(() => {
        const mockJobs = [
          {
            job_title: "前端开发工程师",
            company_name: "阿里巴巴",
            location: "杭州",
            salary_range: "20k-35k",
            description: "负责前端页面开发，使用Vue.js、React等技术栈，参与产品功能设计和优化。",
            requirements: ["3年以上前端开发经验", "熟练掌握Vue.js/React", "熟悉ES6+语法"],
            skills: ["Vue.js", "React", "JavaScript", "CSS3", "Webpack"]
          },
          {
            job_title: "Python后端工程师",
            company_name: "腾讯",
            location: "深圳",
            salary_range: "25k-40k",
            description: "负责后端服务开发，使用Python Django/Flask框架，设计和实现高并发系统。",
            requirements: ["5年以上Python开发经验", "熟悉Django/Flask", "了解微服务架构"],
            skills: ["Python", "Django", "Flask", "MySQL", "Redis"]
          },
          {
            job_title: "产品经理",
            company_name: "字节跳动",
            location: "北京",
            salary_range: "30k-50k",
            description: "负责产品规划和设计，与技术团队协作，推动产品功能迭代和优化。",
            requirements: ["3年以上产品经验", "有互联网产品经验", "良好的沟通能力"],
            skills: ["产品设计", "用户研究", "数据分析", "项目管理"]
          }
        ]
        
        store.setSearchResults({
          jobs: mockJobs,
          companies: [
            { name: "阿里巴巴", jobs_count: 1 },
            { name: "腾讯", jobs_count: 1 },
            { name: "字节跳动", jobs_count: 1 }
          ]
        })
        
        store.setSearchLoading(false)
        ElMessage.success('演示数据加载完成')
      }, 2000)
    }
    
    const viewJobDetails = (job) => {
      selectedJob.value = job
      showJobDialog.value = true
    }
    
    const selectJob = (job) => {
      // 将职位添加到选中列表中
      store.addSelectedJob(job)
      showJobDialog.value = false
      ElMessage.success(`已选择职位：${job.job_title}`)
    }
    
    const removeSelectedJob = (index) => {
      store.removeSelectedJob(index)
      ElMessage.info('已移除所选职位')
    }
    
    const clearSelectedJobs = () => {
      store.clearSelectedJobs()
      ElMessage.info('已清空所有选择的职位')
    }
    
    const proceedToPhase2 = () => {
      if (store.searchResults.jobs.length === 0) {
        ElMessage.warning('请先搜索职位')
        return
      }
      
      if (store.searchResults.selectedJobs.length === 0) {
        ElMessage.warning('请至少选择一个职位')
        return
      }
      
      // 🔥 清除Phase3返回标识，确保从Phase1进入Phase2时清空历史数据
      localStorage.removeItem('fromPhase3Optimization')
      
      // 将选择的多个职位存储到localStorage，保持兼容性
      localStorage.setItem('selectedJobs', JSON.stringify(store.searchResults.selectedJobs))
      // 同时保存第一个职位作为默认选择，以兼容现有代码
      localStorage.setItem('selectedJob', JSON.stringify(store.searchResults.selectedJobs[0]))
      
      console.log('从Phase1进入Phase2，已选择', store.searchResults.selectedJobs.length, '个职位')
      
      store.setCurrentPhase(2)
      router.push('/phase2')
    }
    
    // 粒子动画样式生成
    const getParticleStyle = () => {
      return {
        left: Math.random() * 100 + '%',
        animationDelay: Math.random() * 20 + 's',
        animationDuration: (Math.random() * 10 + 10) + 's',
        opacity: Math.random() * 0.6 + 0.2
      }
    }
    
    return {
      store,
      searchForm,
      showJobDialog,
      selectedJob,
      handleSearch,
      handleDemo,
      viewJobDetails,
      selectJob,
      removeSelectedJob,
      clearSelectedJobs,
      proceedToPhase2,
      // 添加分页相关函数和变量
      currentPage,
      pageSize,
      paginatedJobs,
      handlePageChange,
      // 添加格式化函数
      formatDescription,
      formatSkills,
      formatRequirements,
      // 粒子动画
      getParticleStyle
    }
  }
}
</script>

<style scoped>
.phase1-page {
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

.phase1-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  padding: 20px 16px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px 0;
  color: #409EFF;
}

.card-header p {
  margin: 0;
  color: #666;
}

.results-card {
  margin-bottom: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-jobs-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-count {
  font-weight: bold;
  color: #67c23a;
}

.selected-jobs {
  background-color: #f8f9fa;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.selected-job-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.selected-jobs-actions {
  margin-top: 10px;
}

/* 分页容器样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}

.pagination-container.bottom {
  margin-top: 24px;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); /* 增加卡片宽度 */
  gap: 20px;
  margin-top: 16px;
}

.job-card {
  height: 320px; /* 增加卡片高度 */
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  transition: all 0.3s;
  overflow: hidden;
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.job-header h4 {
  margin: 0;
  color: #303133;
  flex: 1;
  margin-right: 8px;
  font-size: 18px; /* 增加标题大小 */
}

.job-details {
  margin-bottom: 12px;
}

.job-details p {
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
}

.job-description {
  flex: 1;
  margin-bottom: 12px;
  overflow: hidden;
}

.job-description p {
  color: #666;
  font-size: 14px;
  line-height: 1.6; /* 增加行高 */
}

.job-skills {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
}

.skill-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.job-actions {
  display: flex;
  gap: 8px;
  margin-top: auto; /* 保证按钮在底部 */
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

/* 职位详情样式 */
.job-detail-content {
  padding: 10px;
}

.job-detail-title {
  font-size: 22px;
  color: #303133;
  margin-bottom: 15px;
}

.job-detail-company,
.job-detail-location,
.job-detail-salary {
  margin: 8px 0;
}

.job-detail-description {
  white-space: pre-line; /* 保留换行符 */
  line-height: 1.6;
}

.job-detail-requirements li {
  margin: 5px 0;
}

.job-detail-skills {
  display: flex;
  flex-wrap: wrap;
}

.loading-card {
  text-align: center;
  padding: 40px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  font-size: 48px;
  color: #409EFF;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

:deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-pagination {
  display: inline-block;
}
</style>