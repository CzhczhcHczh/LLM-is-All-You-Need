<template>
  <div class="phase4-container">
    <el-card class="schedule-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Calendar /></el-icon> Phase 4: 面试安排</h2>
          <p>AI将帮您智能安排面试时间，优化面试顺序</p>
        </div>
      </template>

      <!-- User Preferences -->
      <div class="preferences-section">
        <h4>设置您的偏好</h4>
        <el-form :model="userPreferences" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="偏好时间">
                <el-select v-model="userPreferences.preferred_time" placeholder="选择偏好时间">
                  <el-option label="上午" value="morning" />
                  <el-option label="下午" value="afternoon" />
                  <el-option label="全天" value="all_day" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="每天最多面试">
                <el-input-number 
                  v-model="userPreferences.max_interviews_per_day" 
                  :min="1" 
                  :max="5" 
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="面试间隔">
                <el-select v-model="userPreferences.interview_gap" placeholder="面试间隔时间">
                  <el-option label="1小时" value="1h" />
                  <el-option label="2小时" value="2h" />
                  <el-option label="半天" value="half_day" />
                  <el-option label="1天" value="1_day" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="优先级排序">
                <el-select v-model="userPreferences.priority_criteria" placeholder="排序标准">
                  <el-option label="公司知名度" value="company_reputation" />
                  <el-option label="薪资水平" value="salary" />
                  <el-option label="匹配度" value="match_score" />
                  <el-option label="发展前景" value="growth_potential" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- Mock Interviews Setup -->
      <div class="interviews-setup">
        <h4>模拟面试邀请</h4>
        <el-button @click="generateMockInterviews" type="primary">
          <el-icon><Plus /></el-icon>
          生成模拟面试
        </el-button>
        <el-button @click="startScheduling" type="success" :disabled="mockInterviews.length === 0">
          <el-icon><Clock /></el-icon>
          开始智能调度
        </el-button>
      </div>

      <!-- Mock Interviews List -->
      <div v-if="mockInterviews.length > 0" class="interviews-list">
        <h4>待安排的面试 ({{ mockInterviews.length }}个)</h4>
        <el-table :data="mockInterviews" style="width: 100%">
          <el-table-column prop="company_name" label="公司" width="150" />
          <el-table-column prop="position" label="职位" width="200" />
          <el-table-column prop="match_score" label="匹配度" width="100">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.match_score" 
                :stroke-width="8"
                :show-text="false"
              />
              <span style="margin-left: 8px;">{{ scope.row.match_score }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="proposed_times" label="可选时间" min-width="200">
            <template #default="scope">
              <el-tag 
                v-for="time in scope.row.proposed_times" 
                :key="time"
                size="small"
                style="margin: 2px;"
              >
                {{ time }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button size="small" @click="editInterview(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- Scheduling Results -->
    <el-card v-if="schedulingResult" class="result-card">
      <template #header>
        <div class="result-header">
          <h3>智能调度结果</h3>
          <el-button @click="approveSchedule" type="success">
            <el-icon><Check /></el-icon>
            确认安排
          </el-button>
        </div>
      </template>

      <!-- Company Ranking -->
      <div class="ranking-section">
        <h4><el-icon><Trophy /></el-icon> 公司匹配度排序</h4>
        <el-table :data="schedulingResult.recommended_schedule" style="width: 100%">
          <el-table-column prop="priority_rank" label="排名" width="80" />
          <el-table-column prop="company_name" label="公司" width="150" />
          <el-table-column prop="position" label="职位" width="200" />
          <el-table-column prop="match_score" label="匹配度" width="120">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.match_score" 
                :stroke-width="8"
                :color="getScoreColor(scope.row.match_score)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="scheduled_time" label="安排时间" width="180" />
          <el-table-column prop="reasoning" label="安排理由" min-width="200" />
        </el-table>
      </div>

      <!-- Conflict Resolutions -->
      <div v-if="schedulingResult.conflict_resolutions" class="conflicts-section">
        <h4><el-icon><Warning /></el-icon> 冲突解决方案</h4>
        <el-timeline>
          <el-timeline-item 
            v-for="(conflict, index) in schedulingResult.conflict_resolutions" 
            :key="index"
            type="warning"
          >
            <div class="conflict-item">
              <h5>{{ conflict.conflict }}</h5>
              <p>解决方案：{{ conflict.resolution }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- AI Discussion Summary -->
      <div class="discussion-section">
        <h4><el-icon><ChatDotRound /></el-icon> AI讨论过程</h4>
        <el-collapse>
          <el-collapse-item 
            v-for="(discussion, index) in agentDiscussions" 
            :key="index"
            :title="`${discussion.model} 的分析`"
          >
            <p>{{ discussion.response }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- Final Reasoning -->
      <div class="reasoning-section">
        <h4><el-icon><Lightbulb /></el-icon> 最终决策理由</h4>
        <el-card class="reasoning-card">
          <p>{{ schedulingResult.final_reasoning }}</p>
        </el-card>
      </div>
    </el-card>

    <!-- Loading State -->
    <el-card v-if="store.interviews.loading" class="loading-card">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <h3>AI正在进行多角度分析...</h3>
        <p>多个AI助手正在讨论最优的面试安排方案</p>
      </div>
    </el-card>

    <!-- Final Schedule Calendar -->
    <el-card v-if="finalSchedule" class="calendar-card">
      <template #header>
        <h3><el-icon><Calendar /></el-icon> 最终面试日程</h3>
      </template>
      
      <div class="schedule-summary">
        <el-statistic-group direction="horizontal">
          <el-statistic title="总面试数" :value="finalSchedule.length" />
          <el-statistic title="预计天数" :value="getScheduleDays()" />
          <el-statistic title="平均匹配度" :value="getAverageScore()" suffix="%" />
        </el-statistic-group>
      </div>

      <el-timeline class="schedule-timeline">
        <el-timeline-item 
          v-for="interview in finalSchedule" 
          :key="interview.id"
          :timestamp="interview.scheduled_time"
          type="primary"
        >
          <div class="timeline-item">
            <h5>{{ interview.company_name }} - {{ interview.position }}</h5>
            <p>匹配度: {{ interview.match_score }}% | 优先级: 第{{ interview.priority_rank }}位</p>
            <el-tag type="info">{{ interview.duration }}分钟</el-tag>
            <el-tag v-if="interview.location" type="success">{{ interview.location }}</el-tag>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Calendar, Plus, Clock, Check, Trophy, Warning, 
  ChatDotRound, Sunny, Loading 
} from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'

export default {
  name: 'Phase4',
  components: {
    Calendar, Plus, Clock, Check, Trophy, Warning,
    ChatDotRound, Sunny, Loading
  },
  setup() {
    const store = useAppStore()
    
    const userPreferences = reactive({
      preferred_time: 'afternoon',
      max_interviews_per_day: 2,
      interview_gap: '2h',
      priority_criteria: 'match_score'
    })
    
    const mockInterviews = ref([])
    const schedulingResult = ref(null)
    const agentDiscussions = ref([])
    const finalSchedule = ref(null)
    
    const generateMockInterviews = () => {
      // Generate mock interview data based on previous phases
      const jobStr = localStorage.getItem('selectedJob')
      const interviewStr = localStorage.getItem('interviewInvitation')
      
      if (!jobStr) {
        ElMessage.warning('请先完成前面的步骤')
        return
      }
      
      const job = JSON.parse(jobStr)
      const invitation = interviewStr ? JSON.parse(interviewStr) : null
      
      // Create mock interviews for demo
      mockInterviews.value = [
        {
          id: 1,
          company_name: job.company_name || '阿里巴巴',
          position: job.job_title || '前端开发工程师',
          match_score: 85,
          proposed_times: ['2024-01-20 14:00', '2024-01-21 10:00', '2024-01-22 15:00'],
          duration: 60,
          location: '线上面试'
        },
        {
          id: 2,
          company_name: '腾讯',
          position: 'Web前端工程师',
          match_score: 78,
          proposed_times: ['2024-01-20 16:00', '2024-01-21 14:00', '2024-01-23 10:00'],
          duration: 90,
          location: '深圳总部'
        },
        {
          id: 3,
          company_name: '字节跳动',
          position: '前端开发专家',
          match_score: 92,
          proposed_times: ['2024-01-21 16:00', '2024-01-22 10:00', '2024-01-23 14:00'],
          duration: 75,
          location: '北京总部'
        },
        {
          id: 4,
          company_name: '美团',
          position: '高级前端工程师',
          match_score: 72,
          proposed_times: ['2024-01-22 14:00', '2024-01-23 16:00', '2024-01-24 10:00'],
          duration: 60,
          location: '线上面试'
        }
      ]
      
      ElMessage.success(`生成了 ${mockInterviews.value.length} 个模拟面试`)
    }
    
    const startScheduling = async () => {
      if (mockInterviews.value.length === 0) {
        ElMessage.warning('请先生成模拟面试')
        return
      }
      
      store.setInterviewLoading(true)
      
      try {
        const response = await apiService.multiAgentDiscussion({
          interviews: mockInterviews.value,
          user_preferences: userPreferences,
          constraints: {
            max_interviews_per_day: userPreferences.max_interviews_per_day,
            preferred_time: userPreferences.preferred_time
          }
        })
        
        if (response.success) {
          schedulingResult.value = response.data.schedule
          agentDiscussions.value = response.data.agent_discussions || []
          ElMessage.success('智能调度完成')
        } else {
          ElMessage.error(response.message || '调度失败')
        }
      } catch (error) {
        console.error('Scheduling error:', error)
        ElMessage.error('调度过程中出现错误')
      } finally {
        store.setInterviewLoading(false)
      }
    }
    
    const editInterview = (interview) => {
      ElMessage.info('面试编辑功能开发中...')
    }
    
    const approveSchedule = () => {
      if (!schedulingResult.value) {
        ElMessage.warning('没有可确认的调度结果')
        return
      }
      
      finalSchedule.value = schedulingResult.value.recommended_schedule
      store.setSchedule({
        id: Date.now(),
        schedule: finalSchedule.value,
        approved: true,
        created_at: new Date().toISOString()
      })
      
      ElMessage.success('面试安排已确认！')
    }
    
    const getScoreColor = (score) => {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    const getScheduleDays = () => {
      if (!finalSchedule.value) return 0
      
      const dates = new Set()
      finalSchedule.value.forEach(interview => {
        const date = interview.scheduled_time?.split(' ')[0]
        if (date) dates.add(date)
      })
      return dates.size
    }
    
    const getAverageScore = () => {
      if (!finalSchedule.value || finalSchedule.value.length === 0) return 0
      
      const total = finalSchedule.value.reduce((sum, interview) => sum + interview.match_score, 0)
      return Math.round(total / finalSchedule.value.length)
    }
    
    return {
      store,
      userPreferences,
      mockInterviews,
      schedulingResult,
      agentDiscussions,
      finalSchedule,
      generateMockInterviews,
      startScheduling,
      editInterview,
      approveSchedule,
      getScoreColor,
      getScheduleDays,
      getAverageScore
    }
  }
}
</script>

<style scoped>
.phase4-container {
  max-width: 1200px;
  margin: 0 auto;
}

.schedule-card, .result-card, .calendar-card {
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

.preferences-section, .interviews-setup, .interviews-list {
  margin-bottom: 24px;
}

.preferences-section h4, .interviews-setup h4, .interviews-list h4 {
  margin-bottom: 16px;
  color: #409EFF;
}

.interviews-setup {
  text-align: center;
}

.interviews-setup .el-button {
  margin: 0 8px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking-section, .conflicts-section, .discussion-section, .reasoning-section {
  margin-bottom: 24px;
}

.ranking-section h4, .conflicts-section h4, .discussion-section h4, .reasoning-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #409EFF;
}

.conflict-item h5 {
  margin: 0 0 8px 0;
  color: #e6a23c;
}

.conflict-item p {
  margin: 0;
  color: #666;
}

.reasoning-card {
  background: #f0f9ff;
  border-left: 4px solid #409EFF;
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

.schedule-summary {
  margin-bottom: 24px;
  text-align: center;
}

.schedule-timeline {
  margin-top: 20px;
}

.timeline-item h5 {
  margin: 0 0 8px 0;
  color: #303133;
}

.timeline-item p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.timeline-item .el-tag {
  margin-right: 8px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

:deep(.el-statistic__content) {
  font-size: 24px;
}

:deep(.el-statistic__title) {
  font-size: 14px;
  color: #666;
}
</style>

