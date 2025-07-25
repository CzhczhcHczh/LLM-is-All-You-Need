<template>
  <div class="phase4-page">
    <!-- 粒子背景动画 -->
    <div class="particles-background">
      <div class="particle" v-for="n in 100" :key="n" :style="getParticleStyle()"></div>
    </div>
    
    <div class="phase4-container">
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
                <template #header>
                  <div class="analyst-header">
                    <h6>{{ analysis.analyst_name || analysis.analyst }}</h6>
                    <el-tag type="primary" size="small">{{ analysis.perspective }}</el-tag>
                  </div>
                </template>
                <div class="analysis-content">
                  <p class="focus-area"><strong>关注点:</strong> {{ analysis.focus }}</p>
                  <div class="rankings-list">
                    <div v-for="(item, jobIndex) in analysis.rankings" :key="jobIndex" class="rank-item">
                      <div class="rank-header">
                        <span class="rank-number">#{{ jobIndex + 1 }}</span>
                        <span class="job-title">{{ item.job_title }}</span>
                        <el-tag :type="getScoreType(item.score)" size="small">{{ item.score }}分</el-tag>
                      </div>
                      <p class="rank-reason">{{ item.reason }}</p>
                      <div v-if="item.detailed_scores" class="detailed-scores">
                        <el-tag 
                          v-for="(score, dimension) in item.detailed_scores" 
                          :key="dimension"
                          type="info" 
                          size="mini"
                          class="score-tag"
                        >
                          {{ dimension }}: {{ score }}分
                        </el-tag>
                      </div>
                    </div>
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
              <el-table-column prop="job_title" label="职位" min-width="150" />
              <el-table-column prop="company" label="公司" min-width="120" />
              <el-table-column prop="score" label="综合评分" width="120" align="center">
                <template #default="{ row }">
                  <el-progress 
                    type="circle" 
                    :percentage="row.score" 
                    :width="50"
                    :stroke-width="6"
                    :color="getProgressColor(row.score)"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="consensus" label="共识度" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.consensus === '高' ? 'success' : 'warning'" size="small">
                    {{ row.consensus }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="analysis_summary" label="推荐理由" min-width="200">
                <template #default="{ row }">
                  <el-tooltip :content="row.analysis_summary" placement="top">
                    <span class="reason-text">{{ truncateText(row.analysis_summary, 50) }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="showJobDetails(row)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
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
          
          <!-- 日程详情列表 -->
          <div class="schedule-details">
            <h6>📋 面试详情列表</h6>
            <el-table :data="finalSchedule" style="width: 100%" class="schedule-table">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="time_period" label="时间" width="150" />
              <el-table-column prop="rank" label="排名" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="getRankTagType(row.rank)" size="small">
                    #{{ row.rank }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="job_title" label="职位" />
              <el-table-column prop="company_name" label="公司" />
              <el-table-column prop="reason" label="推荐理由" show-overflow-tooltip />
            </el-table>
          </div>
        </div>
      </div>
    </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Calendar, Timer, Rank, Download, Tickets, Trophy, MagicStick
} from '@element-plus/icons-vue'
import { apiService } from '../api.js'

export default {
  name: 'Phase4',
  components: {
    Calendar, Timer, Rank, Download, Tickets, Trophy, MagicStick
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
    
    // 从localStorage加载数据
    const loadDataFromPreviousPhases = () => {
      try {
        console.log('开始加载Phase4数据...')
        
        // 从Phase3获取选择的职位
        const phase3Jobs = localStorage.getItem('selectedResumesForPhase4')
        if (phase3Jobs) {
          const jobs = JSON.parse(phase3Jobs)
          selectedJobs.value = jobs.map(resume => resume.jobPosting || {
            job_title: '职位',
            company_name: '公司',
            location: '地点'
          })
          console.log('从Phase3加载的职位:', selectedJobs.value)
        } else {
          // 回退方案：从其他地方获取职位信息
          const fallbackJobs = localStorage.getItem('selectedJobs')
          if (fallbackJobs) {
            selectedJobs.value = JSON.parse(fallbackJobs)
            console.log('从fallback加载的职位:', selectedJobs.value)
          } else {
            // 使用默认示例数据
            selectedJobs.value = [
              {
                job_title: 'Python后端开发工程师',
                company_name: '阿里巴巴',
                location: '杭州',
                salary_range: '20-35K'
              },
              {
                job_title: 'Vue前端开发工程师', 
                company_name: '腾讯',
                location: '深圳',
                salary_range: '18-30K'
              }
            ]
            console.log('使用默认示例职位数据:', selectedJobs.value)
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
        
        console.log('加载的个人信息:', personalInfo.value)
        console.log('Phase4数据加载完成')
        
      } catch (error) {
        console.error('Phase4数据加载失败:', error)
        ElMessage.error('数据加载失败，使用默认数据')
        
        // 错误时使用默认数据
        personalInfo.value = {
          name: '张小明',
          email: 'zhang.xiaoming@example.com', 
          phone: '138-0000-0000',
          location: '北京市朝阳区'
        }
        
        selectedJobs.value = [
          {
            job_title: 'Python后端开发工程师',
            company_name: '阿里巴巴',
            location: '杭州',
            salary_range: '20-35K'
          }
        ]
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
        console.log('开始AI多维度分析...')
        console.log('个人信息:', personalInfo.value)
        console.log('职位列表:', selectedJobs.value)
        
        const response = await apiService.multiLLMRecommendation(
          personalInfo.value,
          selectedJobs.value
        )
        
        console.log('API响应:', response)
        
        if (response.success) {
          llmAnalysis.value = response.data.llm_analysis || []
          finalRanking.value = response.data.final_ranking || []
          finalAnalysisSummary.value = response.data.final_summary || '综合分析完成'
          
          console.log('LLM分析结果:', llmAnalysis.value)
          console.log('最终排序:', finalRanking.value)
          
          ElMessage.success('AI多维度分析完成！')
        } else {
          console.error('分析失败:', response.message || response)
          ElMessage.error('AI分析失败：' + (response.message || '未知错误'))
        }
        
      } catch (error) {
        console.error('Error in AI ranking:', error)
        ElMessage.error('AI分析过程中出现错误：' + error.message)
      } finally {
        rankingLoading.value = false
      }
    }
    
    // 生成最终面试安排（调用后端LLM智能安排）
    const generateFinalSchedule = async () => {
      if (finalRanking.value.length === 0) {
        ElMessage.warning('请先完成AI推荐排序')
        return
      }
      
      schedulingLoading.value = true
      
      try {
        console.log('开始生成LLM智能面试安排...')
        console.log('最终排序结果:', finalRanking.value)
        
        // 构建用户偏好设置
        const userPreferences = {
          user_profile: personalInfo.value,
          max_interviews_per_day: 2,
          preferred_time: 'afternoon',
          interview_gap: '2h',
          priority_criteria: 'match_score'
        }
        
        // 调用后端多Agent讨论接口，包含完整的推荐+调度流程
        const response = await apiService.multiAgentDiscussion({
          interviews: selectedJobs.value,
          user_preferences: userPreferences
        })
        
        console.log('LLM调度响应:', response)
        
        if (response.success) {
          const scheduleData = response.data.final_schedule
          console.log('Schedule data:', scheduleData)
          
          // 解析后端返回的schedule数据
          if (scheduleData && scheduleData.flat_interviews) {
            // 使用扁平化的interviews列表
            finalSchedule.value = scheduleData.flat_interviews.map((interview, index) => ({
              rank: interview.priority_rank || (index + 1),
              job_title: interview.position || interview.job_title,
              company_name: interview.company_name,
              date: interview.date,
              time_period: interview.time,
              score: interview.recommendation_score || 80,
              reason: interview.preparation_tips || '推荐面试',
              preparation_tips: interview.preparation_tips
            }))
          } else if (scheduleData && scheduleData.schedule) {
            // 解析标准的schedule结构
            const flattenedSchedule = []
            scheduleData.schedule.forEach(day => {
              day.interviews.forEach((interview, index) => {
                flattenedSchedule.push({
                  rank: interview.priority_rank || (index + 1),
                  job_title: interview.position || interview.job_title,
                  company_name: interview.company_name,
                  date: day.date,
                  time_period: interview.time,
                  score: interview.recommendation_score || 80,
                  reason: interview.preparation_tips || '推荐面试',
                  preparation_tips: interview.preparation_tips
                })
              })
            })
            finalSchedule.value = flattenedSchedule
          } else {
            console.warn('未找到有效的schedule数据，使用降级方案')
            // 降级方案：基于排序结果生成简单的日程
            generateFallbackSchedule()
          }
          
          console.log('最终日程:', finalSchedule.value)
          ElMessage.success('LLM智能面试安排完成！')
          
        } else {
          console.error('LLM调度失败:', response.message)
          ElMessage.error('LLM智能安排失败：' + (response.message || '未知错误'))
          // 使用降级方案
          generateFallbackSchedule()
        }
        
      } catch (error) {
        console.error('Error in LLM scheduling:', error)
        ElMessage.error('LLM调度过程中出现错误：' + error.message)
        // 使用降级方案
        generateFallbackSchedule()
      } finally {
        schedulingLoading.value = false
      }
    }
    
    // 降级方案：生成简单的面试安排
    const generateFallbackSchedule = () => {
      try {
        const schedule = []
        let currentDateOffset = 1
        
        finalRanking.value.forEach((job, index) => {
          const jobTimeSlots = timeSlots.value.find(ts => 
            ts.job_title === job.job_title && ts.company_name === job.company
          )
          
          let selectedSlot = null
          if (jobTimeSlots && jobTimeSlots.available_slots.length > 0) {
            const targetDateOffset = currentDateOffset + Math.floor(index / 2)
            selectedSlot = jobTimeSlots.available_slots.find(slot => slot.day_offset >= targetDateOffset) ||
                          jobTimeSlots.available_slots[0]
          }
          
          const scheduleDate = new Date()
          if (selectedSlot) {
            scheduleDate.setDate(scheduleDate.getDate() + selectedSlot.day_offset)
          } else {
            scheduleDate.setDate(scheduleDate.getDate() + currentDateOffset + index)
          }
          
          schedule.push({
            rank: job.rank || (index + 1),
            job_title: job.job_title,
            company_name: job.company,
            date: scheduleDate.toLocaleDateString('zh-CN'),
            time_period: selectedSlot ? selectedSlot.time_period : '上午 9:00-11:00',
            score: job.score,
            reason: '基于AI推荐排序安排',
            preparation_tips: `重点准备${job.job_title}相关技能展示`
          })
        })
        
        finalSchedule.value = schedule.sort((a, b) => new Date(a.date) - new Date(b.date))
        ElMessage.success('面试日程安排完成（降级方案）')
        
      } catch (error) {
        console.error('Error in fallback schedule:', error)
        ElMessage.error('日程安排失败')
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
    
    const getRankTagType = (rank) => {
      if (rank === 1) return 'danger'  // 红色 - 最高优先级
      if (rank === 2) return 'warning' // 橙色 - 高优先级
      if (rank === 3) return 'success' // 绿色 - 中等优先级
      return 'info' // 蓝色 - 较低优先级
    }

    // 新增方法：根据分数获取标签类型
    const getScoreType = (score) => {
      if (score >= 90) return 'success'
      if (score >= 80) return 'warning' 
      if (score >= 70) return 'info'
      return 'danger'
    }

    // 新增方法：根据分数获取进度条颜色
    const getProgressColor = (score) => {
      if (score >= 90) return '#67c23a'  // 绿色
      if (score >= 80) return '#e6a23c'  // 橙色
      if (score >= 70) return '#409eff'  // 蓝色
      return '#f56c6c'  // 红色
    }

    // 新增方法：截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    // 新增方法：显示职位详情
    const showJobDetails = (job) => {
      ElMessageBox.alert(
        `职位：${job.job_title}\n公司：${job.company}\n综合评分：${job.score}分\n共识度：${job.consensus}\n\n详细分析：${job.analysis_summary}`,
        '职位详细信息',
        {
          confirmButtonText: '确定',
          type: 'info'
        }
      )
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
      generateTimeSlots,
      startRecommendationRanking,
      generateFinalSchedule,
      exportSchedule,
      getRankTagType,
      getScoreType,
      getProgressColor,
      truncateText,
      showJobDetails
    }
  }
}
</script>

<style scoped>
.phase4-page {
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
.phase4-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  z-index: 1;
}

/* 卡片样式 */
.schedule-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header h2 {
  margin: 0;
  color: #409EFF;
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

/* 新增样式 */
.analyst-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.analyst-header h6 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: bold;
}

.focus-area {
  margin-bottom: 15px;
  padding: 10px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 14px;
  color: #4b5563;
}

.rankings-list {
  max-height: 280px;
  overflow-y: auto;
}

.detailed-scores {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.score-tag {
  margin-right: 0 !important;
}

.reason-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

/* 日程详情表格 */
.schedule-details {
  margin-top: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.schedule-details h6 {
  margin: 0 0 15px 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: bold;
}

.schedule-table {
  border-radius: 8px;
  overflow: hidden;
}

.schedule-table :deep(.el-table__header) {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}

.schedule-table :deep(.el-table__row:hover > td) {
  background: #f0f9ff !important;
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
