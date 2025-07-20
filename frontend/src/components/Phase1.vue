<template>
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
          v-for="(job, index) in store.searchResults.jobs" 
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
            <p>{{ job.description?.substring(0, 150) }}...</p>
          </div>
          
          <div class="job-skills" v-if="job.skills && job.skills.length > 0">
            <el-tag 
              v-for="skill in job.skills.slice(0, 3)" 
              :key="skill"
              size="small"
              effect="plain"
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
    <el-dialog v-model="showJobDialog" title="职位详情" width="60%">
      <div v-if="selectedJob">
        <h3>{{ selectedJob.job_title }}</h3>
        <p><strong>公司：</strong>{{ selectedJob.company_name }}</p>
        <p><strong>地点：</strong>{{ selectedJob.location }}</p>
        <p v-if="selectedJob.salary_range"><strong>薪资：</strong>{{ selectedJob.salary_range }}</p>
        
        <el-divider>职位描述</el-divider>
        <p>{{ selectedJob.description }}</p>
        
        <el-divider>任职要求</el-divider>
        <ul v-if="selectedJob.requirements">
          <li v-for="req in selectedJob.requirements" :key="req">{{ req }}</li>
        </ul>
        
        <el-divider>技能要求</el-divider>
        <div v-if="selectedJob.skills">
          <el-tag 
            v-for="skill in selectedJob.skills" 
            :key="skill"
            style="margin: 2px;"
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
</template>

<script>
import { ref, reactive } from 'vue'
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
      
      store.setSearchLoading(true)
      store.setSearchQuery(searchForm.searchQuery)
      
      try {
        const response = await apiService.searchJobs({
          search_query: searchForm.searchQuery,
          location: searchForm.location || null,
          max_results: searchForm.maxResults
        })
        
        if (response.success) {
          store.setSearchResults(response.data)
          ElMessage.success(`找到 ${response.data.jobs.length} 个职位`)
        } else {
          ElMessage.error(response.message || '搜索失败')
        }
      } catch (error) {
        console.error('Search error:', error)
        ElMessage.error('搜索过程中出现错误')
      } finally {
        store.setSearchLoading(false)
      }
    }
    
    const handleDemo = async () => {
      // Demo mode with mock data
      store.setSearchLoading(true)
      
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
      
      // 将选择的多个职位存储到localStorage，保持兼容性
      localStorage.setItem('selectedJobs', JSON.stringify(store.searchResults.selectedJobs))
      // 同时保存第一个职位作为默认选择，以兼容现有代码
      localStorage.setItem('selectedJob', JSON.stringify(store.searchResults.selectedJobs[0]))
      
      store.setCurrentPhase(2)
      router.push('/phase2')
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
      proceedToPhase2
    }
  }
}
</script>

<style scoped>
.phase1-container {
  max-width: 1200px;
  margin: 0 auto;
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

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.job-card {
  height: 280px;
  display: flex;
  flex-direction: column;
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
}

.job-description p {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.job-skills {
  margin-bottom: 12px;
}

.job-skills .el-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.job-actions {
  display: flex;
  gap: 8px;
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
</style>

