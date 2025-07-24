<template>
  <div class="phase4-container">
    <!-- 导航栏 -->
    <div class="navigation-bar">
      <div class="nav-steps">
        <el-steps :active="3" finish-status="success" simple>
          <el-step title="职位搜索" />
          <el-step title="简历生成" />
          <el-step title="HR评估" />
          <el-step title="面试安排" />
        </el-steps>
      </div>
      <div class="nav-buttons">
        <el-button @click="goToPhase(1)" type="default">Phase 1</el-button>
        <el-button @click="goToPhase(2)" type="default">Phase 2</el-button>
        <el-button @click="goToPhase(3)" type="default">Phase 3</el-button>
        <el-button type="primary" disabled>Phase 4</el-button>
      </div>
    </div>

    <el-card class="schedule-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Calendar /></el-icon> Phase 4: 智能面试安排</h2>
          <p>AI多维度分析，为您智能排序职位并安排面试时间</p>
        </div>
      </template>

      <!-- 个人信息展示 -->
      <div class="personal-info-section">
        <h4>🙋‍♂️ 个人信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ personalInfo.name || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ personalInfo.email || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ personalInfo.phone || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ personalInfo.location || '未填写' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 选择的职位展示 -->
      <div class="selected-jobs-section">
        <h4>📋 待安排面试的职位 ({{ selectedJobs.length }}个)</h4>
        <el-row :gutter="20">
          <el-col :span="8" v-for="(job, index) in selectedJobs" :key="index">
            <el-card class="job-card">
              <h5>{{ job.job_title }}</h5>
              <p class="company">{{ job.company_name }}</p>
              <el-tag type="info" size="small">{{ job.location }}</el-tag>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Step 1: 时间表生成 -->
      <div class="schedule-generation-section">
        <h4>⏰ Step 1: 生成可选面试时间表</h4>
        <el-button @click="generateTimeSlots" type="primary" :loading="generatingSlots" size="large">
          <el-icon><Timer /></el-icon>
          生成时间表
        </el-button>
        
        <!-- 时间表展示 -->
        <div v-if="timeSlots.length > 0" class="time-slots-display">
          <h5>📅 可选面试时间表（未来14天）</h5>
          <el-collapse v-model="activeTimeSlots">
            <el-collapse-item 
              v-for="(job, jobIndex) in timeSlots" 
              :key="jobIndex"
              :title="`${job.job_title} - ${job.company_name} (${job.available_slots.length}个可选时间)`"
              :name="jobIndex"
            >
              <div class="time-grid">
                <el-tag 
                  v-for="(slot, slotIndex) in job.available_slots" 
                  :key="slotIndex"
                  class="time-slot-tag"
                  type="success"
                >
                  {{ slot.date }} {{ slot.time_period }}
                </el-tag>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- Step 2: AI推荐排序 -->
      <div class="ranking-section" v-if="timeSlots.length > 0">
        <h4>🤖 Step 2: AI多维度职位推荐分析</h4>
        <el-button @click="startRecommendationRanking" type="primary" :loading="rankingLoading" size="large">
          <el-icon><Rank /></el-icon>
          开始AI分析排序
        </el-button>
        
        <!-- 三个LLM的分析结果 -->
        <div v-if="llmAnalysis.length > 0" class="llm-analysis-results">
          <h5>🧠 AI分析师独立评估</h5>
          <el-row :gutter="20">
            <el-col :span="8" v-for="(analysis, index) in llmAnalysis" :key="index">
              <el-card class="analysis-card">
                <h6>{{ analysis.llm_name }}</h6>
                <div class="analysis-content">
                  <div v-for="(item, jobIndex) in analysis.ranking" :key="jobIndex" class="rank-item">
                    <div class="rank-header">
                      <span class="rank-number">#{{ jobIndex + 1 }}</span>
                      <span class="job-title">{{ item.job_title }}</span>
                      <el-tag type="warning" size="small">{{ item.score }}分</el-tag>
                    </div>
                    <p class="rank-reason">{{ item.reason }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 最终综合排序 -->
        <div v-if="finalRanking.length > 0" class="final-ranking-results">
          <h5>🏆 AI综合推荐排序</h5>
          <el-card class="final-ranking-card">
            <div class="final-analysis">
              <h6>综合分析师评估</h6>
              <p class="final-summary">{{ finalAnalysisSummary }}</p>
            </div>
            <el-table :data="finalRanking" style="width: 100%" class="ranking-table">
              <el-table-column prop="rank" label="排名" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.rank <= 3 ? 'success' : 'info'" size="large">
                    #{{ row.rank }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="job_title" label="职位" />
              <el-table-column prop="company_name" label="公司" />
              <el-table-column prop="score" label="综合评分" width="100" align="center">
                <template #default="{ row }">
                  <el-progress 
                    type="circle" 
                    :percentage="row.score" 
                    :width="40"
                    :stroke-width="8"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="推荐理由" />
            </el-table>
          </el-card>
        </div>
      </div>

      <!-- Step 3: 最终面试日程安排 -->
      <div class="final-schedule-section" v-if="finalRanking.length > 0">
        <h4>📋 Step 3: 智能面试日程安排</h4>
        <el-button @click="generateFinalSchedule" type="success" :loading="schedulingLoading" size="large">
          <el-icon><Calendar /></el-icon>
          生成最终面试安排
        </el-button>
        
        <!-- 最终日程展示 -->
        <div v-if="finalSchedule.length > 0" class="final-schedule-display">
          <h5>📅 您的面试日程表</h5>
          <el-timeline>
            <el-timeline-item 
              v-for="(schedule, index) in finalSchedule" 
              :key="index"
              :timestamp="schedule.date"
              type="success"
            >
              <el-card class="schedule-item">
                <div class="schedule-header">
                  <h6>{{ schedule.job_title }}</h6>
                  <el-tag type="success">排名 #{{ schedule.rank }}</el-tag>
                </div>
                <p><strong>公司：</strong>{{ schedule.company_name }}</p>
                <p><strong>时间：</strong>{{ schedule.time_period }}</p>
                <p><strong>推荐理由：</strong>{{ schedule.reason }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          
          <div class="schedule-actions">
            <el-button @click="exportSchedule" type="primary" size="large">
              <el-icon><Download /></el-icon>
              导出日程表
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Calendar, Timer, Rank, Download
} from '@element-plus/icons-vue'
import { apiService } from '../api.js'

export default {
  name: 'Phase4',
  components: {
    Calendar, Timer, Rank, Download
  },
  setup() {
    const router = useRouter()
    
    // 状态管理
    const personalInfo = ref({})
    const selectedJobs = ref([])
    const timeSlots = ref([])
    const llmAnalysis = ref([])
    const finalRanking = ref([])
    const finalSchedule = ref([])
    const finalAnalysisSummary = ref('')
    
    // 加载状态
    const generatingSlots = ref(false)
    const rankingLoading = ref(false)
    const schedulingLoading = ref(false)
    
    // UI状态
    const activeTimeSlots = ref([])
    
    // 导航方法
    const goToPhase = (phase) => {
      const routes = {
        1: '/phase1',
        2: '/phase2',
        3: '/phase3',
        4: '/phase4'
      }
      if (routes[phase]) {
        router.push(routes[phase])
      }
    }
    
    // 从localStorage加载数据
    const loadDataFromPreviousPhases = () => {
      try {
        // 从Phase3获取选择的职位
        const phase3Jobs = localStorage.getItem('selectedResumesForPhase4')
        if (phase3Jobs) {
          const jobs = JSON.parse(phase3Jobs)
          selectedJobs.value = jobs.map(resume => resume.jobPosting || {
            job_title: '职位',
            company_name: '公司',
            location: '地点'
          })
        } else {
          // 回退方案：从其他地方获取职位信息
          const fallbackJobs = localStorage.getItem('selectedJobs')
          if (fallbackJobs) {
            selectedJobs.value = JSON.parse(fallbackJobs)
          }
        }
        
        // 从简历中提取个人信息
        const resumesData = localStorage.getItem('generatedResumes')
        if (resumesData) {
          const resumes = JSON.parse(resumesData)
          const firstResume = Object.values(resumes)[0]
          if (firstResume && firstResume.personal_info) {
            personalInfo.value = firstResume.personal_info
          } else {
            // 使用示例数据
            personalInfo.value = {
              name: '张小明',
              email: 'zhang.xiaoming@example.com',
              phone: '138-0000-0000',
              location: '北京市朝阳区'
            }
          }
        } else {
          // 使用示例数据
          personalInfo.value = {
            name: '张小明',
            email: 'zhang.xiaoming@example.com',
            phone: '138-0000-0000',
            location: '北京市朝阳区'
          }
        }
        
        console.log('Loaded personal info:', personalInfo.value)
        console.log('Loaded selected jobs:', selectedJobs.value)
        
      } catch (error) {
        console.error('Error loading data:', error)
        ElMessage.error('数据加载失败')
      }
    }
    
    // 生成时间表
    const generateTimeSlots = () => {
      generatingSlots.value = true
      
      try {
        const timePeriods = ['上午 9:00-11:00', '下午 2:00-4:00', '下午 4:30-6:30']
        const startDate = new Date()
        const slots = []
        
        selectedJobs.value.forEach(job => {
          const jobSlots = []
          const slotsCount = Math.floor(Math.random() * 3) + 3 // 3-5个时间段
          
          for (let i = 0; i < slotsCount; i++) {
            const randomDay = Math.floor(Math.random() * 14) // 未来14天
            const randomPeriod = Math.floor(Math.random() * timePeriods.length)
            const date = new Date(startDate)
            date.setDate(date.getDate() + randomDay)
            
            jobSlots.push({
              date: date.toLocaleDateString('zh-CN'),
              time_period: timePeriods[randomPeriod],
              day_offset: randomDay,
              period_index: randomPeriod
            })
          }
          
          // 按日期排序
          jobSlots.sort((a, b) => a.day_offset - b.day_offset)
          
          slots.push({
            job_title: job.job_title,
            company_name: job.company_name,
            available_slots: jobSlots
          })
        })
        
        timeSlots.value = slots
        ElMessage.success('时间表生成完成！')
        
      } catch (error) {
        console.error('Error generating time slots:', error)
        ElMessage.error('时间表生成失败')
      } finally {
        generatingSlots.value = false
      }
    }
    
    // 开始AI推荐排序
    const startRecommendationRanking = async () => {
      rankingLoading.value = true
      
      try {
        const requestData = {
          personal_info: personalInfo.value,
          jobs: selectedJobs.value
        }
        
        const response = await apiService.multiLLMRecommendation(requestData)
        
        if (response.success) {
          llmAnalysis.value = response.data.llm_analysis || []
          finalRanking.value = response.data.final_ranking || []
          finalAnalysisSummary.value = response.data.final_summary || '综合分析完成'
          
          ElMessage.success('AI分析完成！')
        } else {
          ElMessage.error('AI分析失败：' + response.message)
        }
        
      } catch (error) {
        console.error('Error in AI ranking:', error)
        ElMessage.error('AI分析过程中出现错误')
      } finally {
        rankingLoading.value = false
      }
    }
    
    // 生成最终面试安排
    const generateFinalSchedule = () => {
      schedulingLoading.value = true
      
      try {
        const schedule = []
        let currentDate = new Date()
        
        finalRanking.value.forEach((job, index) => {
          // 找到对应的时间表
          const jobTimeSlots = timeSlots.value.find(ts => 
            ts.job_title === job.job_title && ts.company_name === job.company_name
          )
          
          if (jobTimeSlots && jobTimeSlots.available_slots.length > 0) {
            // 选择第一个可用时间
            const selectedSlot = jobTimeSlots.available_slots[0]
            
            schedule.push({
              rank: index + 1,
              job_title: job.job_title,
              company_name: job.company_name,
              date: selectedSlot.date,
              time_period: selectedSlot.time_period,
              score: job.score,
              reason: job.reason
            })
          }
        })
        
        finalSchedule.value = schedule
        ElMessage.success('面试日程安排完成！')
        
      } catch (error) {
        console.error('Error generating final schedule:', error)
        ElMessage.error('日程安排失败')
      } finally {
        schedulingLoading.value = false
      }
    }
    
    // 导出日程表
    const exportSchedule = () => {
      try {
        const scheduleText = finalSchedule.value.map(item => 
          `${item.date} ${item.time_period} - ${item.job_title} (${item.company_name}) - 排名#${item.rank}`
        ).join('\n')
        
        const blob = new Blob([scheduleText], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `面试日程表_${new Date().toLocaleDateString()}.txt`
        a.click()
        URL.revokeObjectURL(url)
        
        ElMessage.success('日程表已导出！')
      } catch (error) {
        console.error('Error exporting schedule:', error)
        ElMessage.error('导出失败')
      }
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadDataFromPreviousPhases()
    })
    
    return {
      // 状态
      personalInfo,
      selectedJobs,
      timeSlots,
      llmAnalysis,
      finalRanking,
      finalSchedule,
      finalAnalysisSummary,
      
      // 加载状态
      generatingSlots,
      rankingLoading,
      schedulingLoading,
      
      // UI状态
      activeTimeSlots,
      
      // 方法
      goToPhase,
      generateTimeSlots,
      startRecommendationRanking,
      generateFinalSchedule,
      exportSchedule
    }
  }
}
</script>

<style scoped>
.phase4-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 导航栏样式 */
.navigation-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  color: white;
}

.nav-steps {
  margin-bottom: 15px;
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-buttons .el-button {
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

/* 卡片样式 */
.schedule-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header h2 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 各个部分样式 */
.personal-info-section,
.selected-jobs-section,
.schedule-generation-section,
.ranking-section,
.final-schedule-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.job-card {
  text-align: center;
  margin-bottom: 15px;
}

.job-card h5 {
  margin: 0 0 10px 0;
  color: #1f2937;
}

.job-card .company {
  color: #6b7280;
  margin: 5px 0;
}

/* 时间表样式 */
.time-slots-display {
  margin-top: 20px;
}

.time-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.time-slot-tag {
  margin: 5px;
  padding: 8px 12px;
}

/* LLM分析结果样式 */
.llm-analysis-results {
  margin-top: 20px;
}

.analysis-card {
  height: 400px;
  overflow-y: auto;
}

.analysis-card h6 {
  margin: 0 0 15px 0;
  color: #1f2937;
  text-align: center;
  font-size: 16px;
  font-weight: bold;
}

.rank-item {
  margin-bottom: 15px;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
}

.rank-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.rank-number {
  font-weight: bold;
  color: #dc2626;
}

.job-title {
  flex: 1;
  font-weight: 500;
}

.rank-reason {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

/* 最终排序样式 */
.final-ranking-card {
  margin-top: 20px;
}

.final-analysis {
  margin-bottom: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
}

.final-analysis h6 {
  margin: 0 0 10px 0;
  color: #1e40af;
}

.final-summary {
  margin: 0;
  color: #374151;
}

/* 最终日程样式 */
.final-schedule-display {
  margin-top: 20px;
}

.schedule-item {
  margin-bottom: 10px;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.schedule-header h6 {
  margin: 0;
  color: #1f2937;
}

.schedule-actions {
  text-align: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .phase4-container {
    padding: 10px;
  }
}
</style>
