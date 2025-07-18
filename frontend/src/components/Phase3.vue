<template>
  <div class="phase3-container">
    <el-card class="hr-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><User /></el-icon> Phase 3: HR模拟</h2>
          <p>AI将模拟不同类型的HR对您的简历进行评估和反馈</p>
        </div>
      </template>

      <!-- HR Persona Selection -->
      <div class="hr-selection">
        <h4>选择HR类型</h4>
        <el-radio-group v-model="selectedHRPersona" @change="handlePersonaChange">
          <el-radio-button label="experienced">经验丰富的HR</el-radio-button>
          <el-radio-button label="conservative">保守的HR</el-radio-button>
          <el-radio-button label="progressive">开放的HR</el-radio-button>
          <el-radio-button label="technical">技术背景HR</el-radio-button>
        </el-radio-group>
      </div>

      <!-- Submit to HR -->
      <div class="submit-section">
        <el-button 
          type="primary" 
          @click="submitToHR"
          :loading="store.hrFeedback.loading"
          size="large"
        >
          <el-icon><Send /></el-icon>
          提交给HR评估
        </el-button>
        
        <el-button @click="startIterativeFeedback" type="success" size="large">
          <el-icon><Refresh /></el-icon>
          开始迭代优化
        </el-button>
      </div>
    </el-card>

    <!-- HR Feedback Results -->
    <el-card v-if="hrFeedback" class="feedback-card">
      <template #header>
        <div class="feedback-header">
          <h3>HR评估结果</h3>
          <el-tag 
            :type="hrFeedback.passes_initial_screening ? 'success' : 'danger'"
            size="large"
          >
            {{ hrFeedback.passes_initial_screening ? '通过初筛' : '未通过初筛' }}
          </el-tag>
        </div>
      </template>

      <div class="feedback-content">
        <!-- Overall Score -->
        <div class="score-section">
          <h4>总体评分</h4>
          <el-progress 
            :percentage="hrFeedback.overall_score" 
            :color="getScoreColor(hrFeedback.overall_score)"
            :stroke-width="20"
            text-inside
          />
        </div>

        <!-- Strengths and Weaknesses -->
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="feedback-section">
              <h4><el-icon><Check /></el-icon> 优势</h4>
              <ul v-if="hrFeedback.strengths">
                <li v-for="strength in hrFeedback.strengths" :key="strength">
                  {{ strength }}
                </li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="feedback-section">
              <h4><el-icon><Close /></el-icon> 不足</h4>
              <ul v-if="hrFeedback.weaknesses">
                <li v-for="weakness in hrFeedback.weaknesses" :key="weakness">
                  {{ weakness }}
                </li>
              </ul>
            </div>
          </el-col>
        </el-row>

        <!-- Detailed Feedback -->
        <div class="detailed-feedback">
          <el-tabs>
            <el-tab-pane label="工作经验" name="experience">
              <p>{{ hrFeedback.experience_feedback }}</p>
            </el-tab-pane>
            <el-tab-pane label="技能评价" name="skills">
              <p>{{ hrFeedback.skills_feedback }}</p>
            </el-tab-pane>
            <el-tab-pane label="教育背景" name="education">
              <p>{{ hrFeedback.education_feedback }}</p>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Missing Keywords -->
        <div class="missing-keywords" v-if="hrFeedback.missing_keywords">
          <h4>缺失关键词</h4>
          <el-tag 
            v-for="keyword in hrFeedback.missing_keywords" 
            :key="keyword"
            type="warning"
            style="margin: 2px 4px;"
          >
            {{ keyword }}
          </el-tag>
        </div>

        <!-- Suggestions -->
        <div class="suggestions" v-if="hrFeedback.suggestions">
          <h4>改进建议</h4>
          <ol>
            <li v-for="suggestion in hrFeedback.suggestions" :key="suggestion">
              {{ suggestion }}
            </li>
          </ol>
        </div>

        <!-- Interview Invitation -->
        <div v-if="hrFeedback.interview_invitation" class="interview-invitation">
          <h4><el-icon><Calendar /></el-icon> 面试邀请</h4>
          <div v-if="hrFeedback.interview_invitation.invited" class="invitation-details">
            <p><strong>面试类型：</strong>{{ hrFeedback.interview_invitation.interview_type }}</p>
            <p><strong>面试时长：</strong>{{ hrFeedback.interview_invitation.duration }}分钟</p>
            <p><strong>面试地点：</strong>{{ hrFeedback.interview_invitation.location }}</p>
            <p><strong>面试官：</strong>{{ hrFeedback.interview_invitation.interviewer }}</p>
            
            <div class="time-slots">
              <h5>可选时间段：</h5>
              <el-tag 
                v-for="time in hrFeedback.interview_invitation.proposed_times" 
                :key="time"
                type="primary"
                style="margin: 2px 4px;"
              >
                {{ time }}
              </el-tag>
            </div>
            
            <div class="preparation-notes">
              <h5>准备要点：</h5>
              <p>{{ hrFeedback.interview_invitation.preparation_notes }}</p>
            </div>
          </div>
          <div v-else class="no-invitation">
            <p>很遗憾，暂时没有收到面试邀请。建议根据反馈意见优化简历后重新提交。</p>
          </div>
        </div>

        <!-- HR Comments -->
        <div class="hr-comments">
          <h4>HR评价</h4>
          <el-card class="comment-card">
            <p>{{ hrFeedback.hr_comments }}</p>
          </el-card>
        </div>
      </div>

      <!-- Actions -->
      <div class="feedback-actions">
        <el-button @click="optimizeResume" type="warning">
          <el-icon><Edit /></el-icon>
          根据反馈优化简历
        </el-button>
        
        <el-button 
          v-if="hrFeedback.passes_initial_screening" 
          @click="proceedToPhase4" 
          type="success"
        >
          <el-icon><ArrowRight /></el-icon>
          进入面试安排
        </el-button>
      </div>
    </el-card>

    <!-- Loading State -->
    <el-card v-if="store.hrFeedback.loading" class="loading-card">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <h3>HR正在评估您的简历...</h3>
        <p>请稍候，AI正在模拟HR对您的简历进行专业评估</p>
      </div>
    </el-card>

    <!-- Iterative Feedback History -->
    <el-card v-if="feedbackHistory.length > 0" class="history-card">
      <template #header>
        <h3>反馈历史</h3>
      </template>
      
      <el-timeline>
        <el-timeline-item 
          v-for="(feedback, index) in feedbackHistory" 
          :key="index"
          :timestamp="feedback.timestamp"
        >
          <div class="history-item">
            <h5>第{{ index + 1 }}轮反馈 - {{ feedback.hr_persona }}</h5>
            <p>评分: {{ feedback.overall_score }}/100</p>
            <p>{{ feedback.passes_initial_screening ? '✅ 通过初筛' : '❌ 未通过初筛' }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Promotion, Refresh, Check, Close, Calendar, 
  Edit, ArrowRight, Loading 
} from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'

export default {
  name: 'Phase3',
  components: {
    User, Promotion, Refresh, Check, Close, Calendar,
    Edit, ArrowRight, Loading
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    
    const selectedHRPersona = ref('experienced')
    const hrFeedback = ref(null)
    const feedbackHistory = ref([])
    
    const hrPersonaDescriptions = {
      experienced: '经验丰富的HR，注重技能匹配和工作经验',
      conservative: '保守的HR，重视教育背景和稳定性',
      progressive: '开放的HR，看重潜力和学习能力',
      technical: '技术背景的HR，专注技术技能和项目经验'
    }
    
    const handlePersonaChange = (value) => {
      ElMessage.info(`已选择：${hrPersonaDescriptions[value]}`)
    }
    
    const submitToHR = async () => {
      // Get generated resume from Phase 2
      const resumeStr = localStorage.getItem('generatedResume')
      const jobStr = localStorage.getItem('selectedJob')
      
      if (!resumeStr || !jobStr) {
        ElMessage.warning('请先完成前面的步骤')
        return
      }
      
      const resume = JSON.parse(resumeStr)
      const job = JSON.parse(jobStr)
      
      store.setHRFeedbackLoading(true)
      
      try {
        const response = await apiService.hrReview({
          resume_content: resume,
          job_posting: job,
          hr_persona: selectedHRPersona.value
        })
        
        if (response.success) {
          hrFeedback.value = response.data.feedback
          
          // Add to history
          feedbackHistory.value.push({
            ...response.data.feedback,
            hr_persona: hrPersonaDescriptions[selectedHRPersona.value],
            timestamp: new Date().toLocaleString()
          })
          
          store.addHRFeedback({
            id: Date.now(),
            feedback: response.data.feedback,
            hr_persona: selectedHRPersona.value,
            created_at: new Date().toISOString()
          })
          
          ElMessage.success('HR评估完成')
        } else {
          ElMessage.error(response.message || 'HR评估失败')
        }
      } catch (error) {
        console.error('HR review error:', error)
        ElMessage.error('HR评估过程中出现错误')
      } finally {
        store.setHRFeedbackLoading(false)
      }
    }
    
    const startIterativeFeedback = async () => {
      const resumeStr = localStorage.getItem('generatedResume')
      const jobStr = localStorage.getItem('selectedJob')
      
      if (!resumeStr || !jobStr) {
        ElMessage.warning('请先完成前面的步骤')
        return
      }
      
      const resume = JSON.parse(resumeStr)
      const job = JSON.parse(jobStr)
      
      store.setHRFeedbackLoading(true)
      
      try {
        const response = await apiService.iterativeFeedback(resume, job, 3)
        
        if (response.success) {
          hrFeedback.value = response.data.final_feedback
          ElMessage.success(`迭代反馈完成，共进行了${response.data.rounds_completed}轮`)
        } else {
          ElMessage.error(response.message || '迭代反馈失败')
        }
      } catch (error) {
        console.error('Iterative feedback error:', error)
        ElMessage.error('迭代反馈过程中出现错误')
      } finally {
        store.setHRFeedbackLoading(false)
      }
    }
    
    const optimizeResume = async () => {
      if (!hrFeedback.value) {
        ElMessage.warning('请先获取HR反馈')
        return
      }
      
      const resumeStr = localStorage.getItem('generatedResume')
      if (!resumeStr) {
        ElMessage.warning('未找到简历数据')
        return
      }
      
      const resume = JSON.parse(resumeStr)
      
      try {
        const response = await apiService.optimizeResume(resume, hrFeedback.value)
        
        if (response.success) {
          // Update stored resume
          localStorage.setItem('generatedResume', JSON.stringify(response.data.content))
          ElMessage.success('简历已根据反馈进行优化')
        } else {
          ElMessage.error(response.message || '简历优化失败')
        }
      } catch (error) {
        console.error('Resume optimization error:', error)
        ElMessage.error('简历优化过程中出现错误')
      }
    }
    
    const getScoreColor = (score) => {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    const proceedToPhase4 = () => {
      if (!hrFeedback.value || !hrFeedback.value.passes_initial_screening) {
        ElMessage.warning('请先通过HR初筛')
        return
      }
      
      // Store interview invitation for next phase
      if (hrFeedback.value.interview_invitation) {
        localStorage.setItem('interviewInvitation', JSON.stringify(hrFeedback.value.interview_invitation))
      }
      
      store.setCurrentPhase(4)
      router.push('/phase4')
    }
    
    return {
      store,
      selectedHRPersona,
      hrFeedback,
      feedbackHistory,
      hrPersonaDescriptions,
      handlePersonaChange,
      submitToHR,
      startIterativeFeedback,
      optimizeResume,
      getScoreColor,
      proceedToPhase4
    }
  }
}
</script>

<style scoped>
.phase3-container {
  max-width: 1200px;
  margin: 0 auto;
}

.hr-card, .feedback-card, .history-card {
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

.hr-selection {
  margin-bottom: 20px;
}

.hr-selection h4 {
  margin-bottom: 12px;
  color: #303133;
}

.submit-section {
  text-align: center;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feedback-content {
  max-height: 800px;
  overflow-y: auto;
}

.score-section {
  margin-bottom: 24px;
}

.score-section h4 {
  margin-bottom: 12px;
  color: #409EFF;
}

.feedback-section {
  margin-bottom: 20px;
}

.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #409EFF;
}

.feedback-section ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-section li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.detailed-feedback {
  margin: 24px 0;
}

.missing-keywords, .suggestions {
  margin: 24px 0;
}

.missing-keywords h4, .suggestions h4 {
  margin-bottom: 12px;
  color: #409EFF;
}

.suggestions ol {
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.interview-invitation {
  margin: 24px 0;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.interview-invitation h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #409EFF;
}

.invitation-details p {
  margin: 8px 0;
}

.time-slots, .preparation-notes {
  margin: 12px 0;
}

.time-slots h5, .preparation-notes h5 {
  margin-bottom: 8px;
  color: #303133;
}

.no-invitation {
  color: #f56c6c;
  font-style: italic;
}

.hr-comments {
  margin: 24px 0;
}

.hr-comments h4 {
  margin-bottom: 12px;
  color: #409EFF;
}

.comment-card {
  background: #fafafa;
}

.feedback-actions {
  margin-top: 24px;
  text-align: center;
}

.feedback-actions .el-button {
  margin: 0 8px;
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

.history-item h5 {
  margin: 0 0 8px 0;
  color: #303133;
}

.history-item p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

