<template>
  <div class="phase3-container">
    <el-card class="hr-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><User /></el-icon> Phase 3: HR模拟</h2>
          <p>AI将模拟不同类型的HR对您的简历进行评估和反馈</p>
        </div>
      </template>

      <!-- 多份简历列表 -->
      <div class="resumes-section">
        <h4>简历列表 ({{ resumeList.length }} 份)</h4>
        <div v-if="resumeList.length === 0" class="no-resumes">
          <el-empty description="暂无简历数据，请先完成Phase2简历生成"></el-empty>
        </div>
        
        <div v-else class="resume-cards">
          <el-card 
            v-for="(resume, index) in resumeList" 
            :key="index"
            class="resume-item-card"
            :class="{ 'evaluated': resume.hrFeedback }"
          >
            <template #header>
              <div class="resume-header">
                <h5>简历 {{ index + 1 }}: {{ resume.data.personal_info?.name || '未命名简历' }}</h5>
                <el-tag v-if="resume.hrFeedback" :type="resume.hrFeedback.passes_initial_screening ? 'success' : 'danger'">
                  {{ resume.hrFeedback.passes_initial_screening ? '已通过' : '未通过' }}
                </el-tag>
              </div>
            </template>

            <!-- HR类型选择 -->
            <div class="hr-selection">
              <label>选择HR类型：</label>
              <el-select 
                v-model="resume.selectedHRPersona" 
                placeholder="请选择HR类型"
                style="width: 200px;"
              >
                <el-option label="经验丰富的HR" value="experienced"></el-option>
                <el-option label="保守的HR" value="conservative"></el-option>
                <el-option label="开放的HR" value="progressive"></el-option>
                <el-option label="技术背景HR" value="technical"></el-option>
              </el-select>
            </div>

            <!-- 评估按钮 -->
            <div class="resume-actions">
              <el-button 
                type="primary" 
                @click="submitSingleResumeToHR(index)"
                :loading="resume.isEvaluating"
                :disabled="!resume.selectedHRPersona"
                size="small"
              >
                <el-icon><Promotion /></el-icon>
                {{ resume.hrFeedback ? '重新评估' : '提交评估' }}
              </el-button>
              
              <el-button 
                v-if="resume.hrFeedback" 
                @click="viewFeedback(index)"
                type="info" 
                size="small"
              >
                <el-icon><View /></el-icon>
                查看反馈
              </el-button>
            </div>

            <!-- 评估结果预览 -->
            <div v-if="resume.hrFeedback" class="feedback-preview">
              <div class="score-preview">
                <span>评分: {{ resume.hrFeedback.overall_score }}/100</span>
                <el-progress 
                  :percentage="resume.hrFeedback.overall_score" 
                  :color="getScoreColor(resume.hrFeedback.overall_score)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
              <div class="hr-info">
                <el-tag size="small">{{ getHRPersonaName(resume.evaluatedPersona) }}</el-tag>
                <span class="eval-time">{{ resume.evaluationTime }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 批量操作 -->
      <div class="batch-section" v-if="resumeList.length > 0">
        <h4>批量操作</h4>
        <div class="batch-controls">
          <!-- 使用各自选择的HR类型进行批量评估 -->
          <div class="batch-option">
            <el-button 
              type="primary" 
              @click="submitAllResumesToHR"
              :loading="isBatchEvaluating"
              size="default"
            >
              <el-icon><Promotion /></el-icon>
              评估所有简历（使用各自HR类型）
            </el-button>
            <p class="batch-desc">每份简历将使用其单独选择的HR类型进行评估</p>
          </div>
          
          <!-- 使用统一HR类型进行批量评估 -->
          <div class="batch-option">
            <div class="unified-hr-controls">
              <el-select v-model="batchHRPersona" placeholder="选择统一HR类型" style="width: 200px;">
                <el-option label="经验丰富的HR" value="experienced"></el-option>
                <el-option label="保守的HR" value="conservative"></el-option>
                <el-option label="开放的HR" value="progressive"></el-option>
                <el-option label="技术背景HR" value="technical"></el-option>
              </el-select>
              
              <el-button 
                type="warning" 
                @click="submitAllResumesWithSameHR"
                :loading="isBatchEvaluating"
                :disabled="!batchHRPersona"
              >
                <el-icon><Promotion /></el-icon>
                使用统一HR类型评估
              </el-button>
            </div>
            <p class="batch-desc">所有简历将使用相同的HR类型进行评估</p>
          </div>
          
          <!-- 多HR对比评估 -->
          <div class="batch-option">
            <el-button @click="startMultiHRFeedback" type="success">
              <el-icon><Refresh /></el-icon>
              多HR对比评估
            </el-button>
            <p class="batch-desc">选择一份简历，由4种不同类型的HR进行评估对比</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 新增：评估进度条 -->
    <el-card v-if="evaluationProgress.show" class="progress-card">
      <template #header>
        <div class="progress-header">
          <h3>
            <el-icon class="loading-icon"><Loading /></el-icon>
            {{ evaluationProgress.message }}
          </h3>
        </div>
      </template>
      
      <div class="progress-content">
        <el-progress 
          :percentage="Math.round((evaluationProgress.current / evaluationProgress.total) * 100)"
          :stroke-width="20"
          text-inside
        />
        <p class="progress-text">
          正在处理第 {{ evaluationProgress.current }} / {{ evaluationProgress.total }} 项
        </p>
      </div>
    </el-card>

    <!-- HR Feedback Results -->
    <el-card v-if="selectedFeedback" class="feedback-card">
      <template #header>
        <div class="feedback-header">
          <h3>HR评估结果 - {{ selectedFeedback.resumeName }}</h3>
          <div class="header-actions">
            <el-tag 
              :type="selectedFeedback.feedback.passes_initial_screening ? 'success' : 'danger'"
              size="large"
            >
              {{ selectedFeedback.feedback.passes_initial_screening ? '通过初筛' : '未通过初筛' }}
            </el-tag>
            <el-button @click="selectedFeedback = null" type="text" size="small">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <div class="feedback-content">
        <!-- Overall Score -->
        <div class="score-section">
          <h4>总体评分</h4>
          <el-progress 
            :percentage="selectedFeedback.feedback.overall_score" 
            :color="getScoreColor(selectedFeedback.feedback.overall_score)"
            :stroke-width="20"
            text-inside
          />
          
          <!-- 评分详细计算 -->
          <div v-if="selectedFeedback.feedback.score_breakdown" class="score-breakdown">
            <h5>评分计算详情：</h5>
            <div class="calculation-details">
              <div 
                v-for="(breakdown, key) in selectedFeedback.feedback.score_breakdown" 
                :key="key"
                class="score-detail-item"
              >
                <div class="score-line">
                  <span class="dimension">{{ getDimensionName(key) }}</span>
                  <span class="calculation">
                    {{ breakdown.score }}分 × {{ (breakdown.weight * 100).toFixed(1) }}% = {{ breakdown.contribution }}分
                  </span>
                </div>
                <el-progress 
                  :percentage="breakdown.score" 
                  :color="getScoreColor(breakdown.score)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
              <div class="total-calculation">
                <strong>总分：{{ calculateTotalScore(selectedFeedback.feedback.score_breakdown) }}分</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Strengths and Weaknesses -->
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="feedback-section">
              <h4><el-icon><Check /></el-icon> 优势</h4>
              <ul v-if="selectedFeedback.feedback.strengths">
                <li v-for="strength in selectedFeedback.feedback.strengths" :key="strength">
                  {{ strength }}
                </li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="feedback-section">
              <h4><el-icon><Close /></el-icon> 不足</h4>
              <ul v-if="selectedFeedback.feedback.weaknesses">
                <li v-for="weakness in selectedFeedback.feedback.weaknesses" :key="weakness">
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
              <div v-if="selectedFeedback.feedback.detailed_analysis && selectedFeedback.feedback.detailed_analysis.experience_analysis">
                <p>{{ selectedFeedback.feedback.detailed_analysis.experience_analysis }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.comprehensive_feedback && selectedFeedback.feedback.comprehensive_feedback.experience_feedback">
                <p>{{ selectedFeedback.feedback.comprehensive_feedback.experience_feedback }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.experience_feedback">
                <p>{{ selectedFeedback.feedback.experience_feedback }}</p>
              </div>
              <div v-else>
                <p>工作经验评估：基于简历中的工作经历，HR对候选人的工作经验进行了综合评估。</p>
              </div>
              
              <!-- 详细分数显示 -->
              <div v-if="selectedFeedback.feedback.detailed_scores" class="score-breakdown">
                <h5>详细评分：</h5>
                <template v-for="(score, key) in selectedFeedback.feedback.detailed_scores" :key="key">
                  <div v-if="key && key.toLowerCase().includes('experience')" class="score-item">
                    <span>{{ getDimensionName(key) }}：</span>
                    <el-progress 
                      :percentage="score" 
                      :color="getScoreColor(score)"
                      :stroke-width="12"
                      text-inside
                      style="width: 300px; margin-left: 10px;"
                    />
                  </div>
                </template>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="技能评价" name="skills">
              <div v-if="selectedFeedback.feedback.detailed_analysis && selectedFeedback.feedback.detailed_analysis.skills_analysis">
                <p>{{ selectedFeedback.feedback.detailed_analysis.skills_analysis }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.comprehensive_feedback && selectedFeedback.feedback.comprehensive_feedback.skills_feedback">
                <p>{{ selectedFeedback.feedback.comprehensive_feedback.skills_feedback }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.skills_feedback">
                <p>{{ selectedFeedback.feedback.skills_feedback }}</p>
              </div>
              <div v-else>
                <p>技能评估：HR对候选人的技能构成和专业能力进行了详细分析。</p>
              </div>
              
              <!-- 详细分数显示 -->
              <div v-if="selectedFeedback.feedback.detailed_scores" class="score-breakdown">
                <h5>详细评分：</h5>
                <template v-for="(score, key) in selectedFeedback.feedback.detailed_scores" :key="key">
                  <div v-if="key && key.toLowerCase().includes('skill')" class="score-item">
                    <span>{{ getDimensionName(key) }}：</span>
                    <el-progress 
                      :percentage="score" 
                      :color="getScoreColor(score)"
                      :stroke-width="12"
                      text-inside
                      style="width: 300px; margin-left: 10px;"
                    />
                  </div>
                </template>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="教育背景" name="education">
              <div v-if="selectedFeedback.feedback.detailed_analysis && selectedFeedback.feedback.detailed_analysis.education_analysis">
                <p>{{ selectedFeedback.feedback.detailed_analysis.education_analysis }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.comprehensive_feedback && selectedFeedback.feedback.comprehensive_feedback.education_feedback">
                <p>{{ selectedFeedback.feedback.comprehensive_feedback.education_feedback }}</p>
              </div>
              <div v-else-if="selectedFeedback.feedback.education_feedback">
                <p>{{ selectedFeedback.feedback.education_feedback }}</p>
              </div>
              <div v-else>
                <p>教育背景评估：HR对候选人的学历和教育经历进行了专业评估。</p>
              </div>
              
              <!-- 详细分数显示 -->
              <div v-if="selectedFeedback.feedback.detailed_scores" class="score-breakdown">
                <h5>详细评分：</h5>
                <template v-for="(score, key) in selectedFeedback.feedback.detailed_scores" :key="key">
                  <div v-if="key && key.toLowerCase().includes('education')" class="score-item">
                    <span>{{ getDimensionName(key) }}：</span>
                    <el-progress 
                      :percentage="score" 
                      :color="getScoreColor(score)"
                      :stroke-width="12"
                      text-inside
                      style="width: 300px; margin-left: 10px;"
                    />
                  </div>
                </template>
              </div>
            </el-tab-pane>
            
            <!-- 新增：全部评分标签页 -->
            <el-tab-pane label="全部评分" name="all_scores">
              <div v-if="selectedFeedback.feedback.detailed_scores" class="all-scores">
                <h5>详细评分明细：</h5>
                <div v-for="(score, key) in selectedFeedback.feedback.detailed_scores" :key="key" class="score-item">
                  <div class="score-label">{{ getDimensionName(key) }}：</div>
                  <el-progress 
                    :percentage="score" 
                    :color="getScoreColor(score)"
                    :stroke-width="18"
                    text-inside
                    style="width: 450px; margin: 5px 0;"
                  />
                  <span class="score-value">{{ score }}分</span>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Missing Keywords -->
        <div class="missing-keywords" v-if="selectedFeedback.feedback.missing_keywords">
          <h4>缺失关键词</h4>
          <el-tag 
            v-for="keyword in selectedFeedback.feedback.missing_keywords" 
            :key="keyword"
            type="warning"
            style="margin: 2px 4px;"
          >
            {{ keyword }}
          </el-tag>
        </div>

        <!-- Suggestions -->
        <div class="suggestions" v-if="selectedFeedback.feedback.suggestions">
          <h4>改进建议</h4>
          <ol>
            <li v-for="suggestion in selectedFeedback.feedback.suggestions" :key="suggestion">
              {{ suggestion }}
            </li>
          </ol>
        </div>

        <!-- Interview Invitation -->
        <div v-if="selectedFeedback.feedback.interview_invitation" class="interview-invitation">
          <h4><el-icon><Calendar /></el-icon> 面试邀请</h4>
          <div v-if="selectedFeedback.feedback.interview_invitation.invited" class="invitation-details">
            <p><strong>面试类型：</strong>{{ selectedFeedback.feedback.interview_invitation.interview_type }}</p>
            <p><strong>面试时长：</strong>{{ selectedFeedback.feedback.interview_invitation.duration }}分钟</p>
            <p><strong>面试地点：</strong>{{ selectedFeedback.feedback.interview_invitation.location }}</p>
            <p><strong>面试官：</strong>{{ selectedFeedback.feedback.interview_invitation.interviewer }}</p>
            
            <div class="time-slots">
              <h5>可选时间段：</h5>
              <el-tag 
                v-for="time in selectedFeedback.feedback.interview_invitation.proposed_times" 
                :key="time"
                type="primary"
                style="margin: 2px 4px;"
              >
                {{ time }}
              </el-tag>
            </div>
            
            <div class="preparation-notes">
              <h5>准备要点：</h5>
              <p>{{ selectedFeedback.feedback.interview_invitation.preparation_notes }}</p>
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
            <p>{{ selectedFeedback.feedback.hr_comments }}</p>
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
          v-if="selectedFeedback.feedback.passes_initial_screening" 
          @click="proceedToPhase4" 
          type="success"
        >
          <el-icon><ArrowRight /></el-icon>
          进入面试安排
        </el-button>
      </div>
      
      <!-- 新增：反馈翻页控件 -->
      <div v-if="feedbackPagination.totalCount > 1" class="feedback-pagination">
        <div class="pagination-info">
          <span>第 {{ feedbackPagination.currentIndex + 1 }} / {{ feedbackPagination.totalCount }} 个反馈</span>
        </div>
        <div class="pagination-controls">
          <el-button 
            @click="previousFeedback" 
            :disabled="feedbackPagination.currentIndex === 0"
            size="small"
            icon="ArrowLeft"
          >
            上一个
          </el-button>
          
          <el-button 
            @click="nextFeedback" 
            :disabled="feedbackPagination.currentIndex === feedbackPagination.totalCount - 1"
            size="small"
            icon="ArrowRight"
          >
            下一个
          </el-button>
        </div>
        
        <!-- 反馈类型标签 -->
        <div class="feedback-type-tags">
          <el-tag 
            v-for="(feedback, index) in feedbackPagination.availableFeedbacks" 
            :key="index"
            :type="index === feedbackPagination.currentIndex ? 'primary' : 'info'"
            :effect="index === feedbackPagination.currentIndex ? 'dark' : 'light'"
            @click="selectFeedbackByIndex(index)"
            class="feedback-tag"
          >
            {{ getHRPersonaName(feedback.persona) }}
            <span class="tag-score">{{ feedback.score }}分</span>
          </el-tag>
        </div>
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
            <h5>第{{ index + 1 }}轮反馈 - {{ feedback.persona_name }}</h5>
            <p>评分: {{ feedback.score }}/100</p>
            <p>{{ feedback.passes_screening ? '✅ 通过初筛' : '❌ 未通过初筛' }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Promotion, Refresh, Check, Close, Calendar, 
  Edit, ArrowRight, Loading, View, ArrowLeft
} from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'

export default {
  name: 'Phase3',
  components: {
    User, Promotion, Refresh, Check, Close, Calendar,
    Edit, ArrowRight, Loading, View, ArrowLeft
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    
    // 状态管理
    const resumeList = ref([])
    const selectedFeedback = ref(null)
    const feedbackHistory = ref([])
    const batchHRPersona = ref('experienced')
    const isBatchEvaluating = ref(false)
    
    // 新增：进度条相关状态
    const evaluationProgress = ref({
      show: false,
      current: 0,
      total: 0,
      message: '',
      type: 'single' // single, batch, multi-hr
    })
    
    // 新增：反馈翻页相关状态
    const feedbackPagination = ref({
      currentIndex: 0,
      availableFeedbacks: [],
      totalCount: 0
    })
    
    // HR类型描述
    const hrPersonaDescriptions = {
      experienced: '经验丰富的HR，注重技能匹配和工作经验',
      conservative: '保守的HR，重视教育背景和稳定性',
      progressive: '开放的HR，看重潜力和学习能力',
      technical: '技术背景的HR，专注技术技能和项目经验'
    }
    
    // 初始化简历列表
    const initializeResumeList = () => {
      try {
        // 尝试多种可能的localStorage键名
        const resumesStr = localStorage.getItem('generatedResumes') || localStorage.getItem('batchResumes')
        const jobsStr = localStorage.getItem('selectedJobsForPhase3') || localStorage.getItem('selectedJobs') || localStorage.getItem('selectedJob')
        
        console.log('localStorage检查:')
        console.log('generatedResumes:', localStorage.getItem('generatedResumes'))
        console.log('batchResumes:', localStorage.getItem('batchResumes'))
        console.log('selectedJobsForPhase3:', localStorage.getItem('selectedJobsForPhase3'))
        console.log('selectedJobs:', localStorage.getItem('selectedJobs'))
        console.log('selectedJob:', localStorage.getItem('selectedJob'))
        
        if (resumesStr) {
          const resumes = JSON.parse(resumesStr)
          let jobs = []
          
          // 处理职位数据
          if (jobsStr) {
            try {
              const parsedJobs = JSON.parse(jobsStr)
              if (Array.isArray(parsedJobs)) {
                jobs = parsedJobs
              } else {
                jobs = [parsedJobs] // 单个职位转换为数组
              }
            } catch (e) {
              console.warn('职位数据解析失败:', e)
            }
          }
          
          // 处理简历数据
          let resumeEntries = []
          if (Array.isArray(resumes)) {
            // 如果resumes是数组
            resumeEntries = resumes.map((resume, index) => ([`resume_${index}`, resume]))
          } else if (typeof resumes === 'object') {
            // 如果resumes是对象
            resumeEntries = Object.entries(resumes)
          } else {
            // 单个简历
            resumeEntries = [['resume_0', resumes]]
          }
          
          resumeList.value = resumeEntries.map(([key, resumeData], index) => ({
            id: key,
            data: resumeData,
            jobPosting: jobs[index] || jobs[0] || {
              job_title: '未指定职位',
              company_name: '未知公司',
              description: '暂无描述'
            }, // 使用对应职位、第一个职位或默认职位
            selectedHRPersona: 'experienced',
            isEvaluating: false,
            hrFeedback: null,
            evaluatedPersona: null,
            evaluationTime: null
          }))
          
          console.log('初始化简历列表:', resumeList.value.length, '份简历')
          console.log('简历数据:', resumeList.value)
        } else {
          console.log('未找到简历数据，检查所有可能的键名')
          ElMessage.warning('未找到简历数据，请先完成Phase2简历生成')
        }
      } catch (error) {
        console.error('初始化简历列表失败:', error)
        ElMessage.error('加载简历数据失败: ' + error.message)
      }
    }
    
    // 提交单份简历给HR评估
    const submitSingleResumeToHR = async (resumeIndex) => {
      const resume = resumeList.value[resumeIndex]
      if (!resume) {
        ElMessage.error('简历不存在')
        return false
      }
      
      if (!resume.selectedHRPersona) {
        ElMessage.warning('请先选择HR类型')
        return false
      }
      
      resume.isEvaluating = true
      
      // 显示进度条
      showProgress('single', 1, `正在评估简历${resumeIndex + 1}`)
      
      try {
        console.log(`提交简历 ${resumeIndex + 1} 给 ${resume.selectedHRPersona} HR评估`)
        
        updateProgress(0.5) // 50% 进度
        
        const response = await apiService.submitHRReview({
          resume_content: resume.data,
          job_posting: resume.jobPosting,
          hr_persona: resume.selectedHRPersona
        })
        
        updateProgress(1) // 100% 进度
        
        if (response.success !== false) {
          resume.hrFeedback = response.data.feedback
          resume.evaluatedPersona = resume.selectedHRPersona
          resume.evaluationTime = new Date().toLocaleString()
          
          // 添加到历史记录
          feedbackHistory.value.unshift({
            id: Date.now() + resumeIndex,
            resumeIndex: resumeIndex,
            resumeName: `简历${resumeIndex + 1}`,
            persona: resume.selectedHRPersona,
            persona_name: hrPersonaDescriptions[resume.selectedHRPersona],
            score: response.data.feedback.overall_score,
            timestamp: resume.evaluationTime,
            passes_screening: response.data.feedback.passes_initial_screening,
            feedback: response.data.feedback
          })
          
          ElMessage.success(`简历${resumeIndex + 1}评估完成！评分：${response.data.feedback.overall_score}/100`)
          return true
        } else {
          ElMessage.error(`简历${resumeIndex + 1}评估失败：` + (response.message || '未知错误'))
          return false
        }
      } catch (error) {
        console.error('HR评估错误:', error)
        ElMessage.error(`简历${resumeIndex + 1}评估过程中出现错误`)
        return false
      } finally {
        resume.isEvaluating = false
        hideProgress() // 隐藏进度条
      }
    }
    
    // 批量提交所有简历 - 每份简历使用各自选择的HR类型
    const submitAllResumesToHR = async () => {
      // 检查是否有未选择HR类型的简历
      const unselectedResumes = resumeList.value.filter(resume => !resume.selectedHRPersona)
      if (unselectedResumes.length > 0) {
        ElMessage.warning(`有${unselectedResumes.length}份简历未选择HR类型，请先完成选择`)
        return
      }
      
      isBatchEvaluating.value = true
      
      // 显示批量进度条
      showProgress('batch', resumeList.value.length, '批量评估进行中')
      
      try {
        ElMessage.info('开始批量评估，这可能需要一些时间...')
        
        // 准备评估请求数据
        const evaluationRequests = resumeList.value.map((resume, index) => ({
          resume_content: resume.data,
          job_posting: resume.jobPosting,
          hr_persona: resume.selectedHRPersona
        }))
        
        // 设置所有简历为评估中状态
        resumeList.value.forEach(resume => {
          resume.isEvaluating = true
        })
        
        updateProgress(1) // 开始处理
        
        // 使用改进的逐个评估方式来提供准确的进度反馈
        let successCount = 0
        const results = []
        
        for (let i = 0; i < evaluationRequests.length; i++) {
          const request = evaluationRequests[i]
          const resume = resumeList.value[i]
          
          try {
            updateProgress(i + 1) // 更新进度
            
            const response = await apiService.submitHRReview(request)
            
            if (response.success !== false) {
              // 评估成功
              resume.hrFeedback = response.data.feedback
              resume.evaluatedPersona = resume.selectedHRPersona
              resume.evaluationTime = new Date().toLocaleString()
              
              // 添加到历史记录
              feedbackHistory.value.unshift({
                id: Date.now() + i * 1000,
                resumeIndex: i,
                resumeName: `简历${i + 1}`,
                persona: resume.selectedHRPersona,
                persona_name: hrPersonaDescriptions[resume.selectedHRPersona],
                score: response.data.feedback.overall_score,
                timestamp: resume.evaluationTime,
                passes_screening: response.data.feedback.passes_initial_screening,
                feedback: response.data.feedback,
                isBatch: true
              })
              
              successCount++
              results.push({ index: i, success: true, data: response })
            } else {
              // 评估失败
              console.error(`简历${i + 1}评估失败:`, response.message)
              ElMessage.error(`简历${i + 1}评估失败: ${response.message}`)
              results.push({ index: i, success: false, error: response.message })
            }
            
            resume.isEvaluating = false
          } catch (error) {
            console.error(`简历${i + 1}评估异常:`, error)
            ElMessage.error(`简历${i + 1}评估异常: ${error.message}`)
            resume.isEvaluating = false
            results.push({ index: i, success: false, error: error.message })
          }
        }
        
        ElMessage.success(`批量评估完成！成功评估 ${successCount}/${resumeList.value.length} 份简历`)
        
      } catch (error) {
        console.error('批量评估错误:', error)
        ElMessage.error('批量评估过程中出现错误')
      } finally {
        // 确保所有简历状态重置
        resumeList.value.forEach(resume => {
          resume.isEvaluating = false
        })
        isBatchEvaluating.value = false
        hideProgress() // 隐藏进度条
      }
    }
    
    // 使用统一HR类型批量评估
    const submitAllResumesWithSameHR = async () => {
      if (!batchHRPersona.value) {
        ElMessage.warning('请选择HR类型')
        return
      }
      
      // 临时设置所有简历使用相同的HR类型
      const originalPersonas = resumeList.value.map(r => r.selectedHRPersona)
      resumeList.value.forEach(resume => {
        resume.selectedHRPersona = batchHRPersona.value
      })
      
      try {
        await submitAllResumesToHR()
      } catch (error) {
        // 如果出错，恢复原来的HR选择
        resumeList.value.forEach((resume, index) => {
          resume.selectedHRPersona = originalPersonas[index]
        })
        throw error
      }
    }
    
    // 多HR对比评估
    const startMultiHRFeedback = async () => {
      if (resumeList.value.length === 0) {
        ElMessage.warning('没有可评估的简历')
        return
      }
      
      const { value: selectedResumeIndex } = await ElMessageBox.prompt(
        '请输入要进行多HR评估的简历编号（1-' + resumeList.value.length + '）',
        '多HR对比评估',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^[1-9]\d*$/,
          inputErrorMessage: '请输入有效的简历编号'
        }
      )
      
      const resumeIndex = parseInt(selectedResumeIndex) - 1
      if (resumeIndex < 0 || resumeIndex >= resumeList.value.length) {
        ElMessage.error('简历编号无效')
        return
      }
      
      const resume = resumeList.value[resumeIndex]
      const personas = ['experienced', 'conservative', 'progressive', 'technical']
      
      try {
        // 显示进度条
        showProgress('multiHR', personas.length, '多HR对比评估中')
        
        ElMessage.info('开始多HR评估，这可能需要一些时间...')
        
        const results = []
        
        // 逐个进行HR评估以提供准确的进度反馈
        for (let i = 0; i < personas.length; i++) {
          const persona = personas[i]
          updateProgress(i + 1) // 更新进度
          
          try {
            const response = await apiService.submitHRReview({
              resume_content: resume.data,
              job_posting: resume.jobPosting,
              hr_persona: persona
            })
            
            results.push({
              persona,
              success: response.success !== false,
              feedback: response.success !== false ? response.data.feedback : null,
              error: response.success !== false ? null : response.message
            })
          } catch (error) {
            results.push({
              persona,
              success: false,
              feedback: null,
              error: error.message
            })
          }
        }
        
        // 添加所有成功的评估到历史记录
        results.forEach(result => {
          if (result.success && result.feedback) {
            feedbackHistory.value.unshift({
              id: Date.now() + Math.random(),
              resumeIndex: resumeIndex,
              resumeName: `简历${resumeIndex + 1}`,
              persona: result.persona,
              persona_name: hrPersonaDescriptions[result.persona],
              score: result.feedback.overall_score,
              timestamp: new Date().toLocaleString(),
              passes_screening: result.feedback.passes_initial_screening,
              feedback: result.feedback,
              isMultiHR: true
            })
          }
        })
        
        const successCount = results.filter(r => r.success).length
        ElMessage.success(`多HR评估完成！获得了 ${successCount}/4 个HR的评估反馈`)
        
      } catch (error) {
        console.error('多HR评估错误:', error)
        ElMessage.error('多HR评估过程中出现错误')
      } finally {
        hideProgress() // 隐藏进度条
      }
    }
    
    // 进度条控制函数
    const showProgress = (type, total, message) => {
      evaluationProgress.value = {
        show: true,
        current: 0,
        total: total,
        message: message,
        type: type
      }
    }
    
    const updateProgress = (current) => {
      evaluationProgress.value.current = current
    }
    
    const hideProgress = () => {
      evaluationProgress.value.show = false
    }
    
    // 反馈翻页控制函数
    const initializeFeedbackPagination = (resumeIndex) => {
      // 获取指定简历的所有反馈
      const allFeedbacks = feedbackHistory.value.filter(f => f.resumeIndex === resumeIndex)
      
      feedbackPagination.value = {
        currentIndex: 0,
        availableFeedbacks: allFeedbacks,
        totalCount: allFeedbacks.length
      }
      
      if (allFeedbacks.length > 0) {
        selectedFeedback.value = {
          resumeIndex: resumeIndex,
          resumeName: `简历${resumeIndex + 1}`,
          feedback: allFeedbacks[0].feedback,
          persona: allFeedbacks[0].persona
        }
      }
    }
    
    const previousFeedback = () => {
      if (feedbackPagination.value.currentIndex > 0) {
        feedbackPagination.value.currentIndex--
        updateSelectedFeedback()
      }
    }
    
    const nextFeedback = () => {
      if (feedbackPagination.value.currentIndex < feedbackPagination.value.totalCount - 1) {
        feedbackPagination.value.currentIndex++
        updateSelectedFeedback()
      }
    }
    
    const selectFeedbackByIndex = (index) => {
      if (index >= 0 && index < feedbackPagination.value.totalCount) {
        feedbackPagination.value.currentIndex = index
        updateSelectedFeedback()
      }
    }
    
    const updateSelectedFeedback = () => {
      const currentFeedback = feedbackPagination.value.availableFeedbacks[feedbackPagination.value.currentIndex]
      if (currentFeedback) {
        selectedFeedback.value = {
          resumeIndex: currentFeedback.resumeIndex,
          resumeName: currentFeedback.resumeName,
          feedback: currentFeedback.feedback,
          persona: currentFeedback.persona
        }
      }
    }
    
    // 查看反馈详情（修改后的版本）
    const viewFeedback = (resumeIndex) => {
      // 初始化反馈翻页
      initializeFeedbackPagination(resumeIndex)
      
      // 如果没有历史反馈，但有当前简历的反馈，则显示当前反馈
      if (feedbackPagination.value.totalCount === 0) {
        const resume = resumeList.value[resumeIndex]
        if (resume && resume.hrFeedback) {
          selectedFeedback.value = {
            resumeIndex,
            resumeName: `简历${resumeIndex + 1}`,
            feedback: resume.hrFeedback,
            persona: resume.evaluatedPersona
          }
          
          // 重置翻页状态
          feedbackPagination.value = {
            currentIndex: 0,
            availableFeedbacks: [],
            totalCount: 1
          }
        }
      }
    }
    
    // 计算总分
    const calculateTotalScore = (scoreBreakdown) => {
      if (!scoreBreakdown) return 0
      
      const total = Object.values(scoreBreakdown)
        .reduce((sum, item) => sum + item.contribution, 0)
      
      return total.toFixed(2)
    }
    
    // 获取维度中文名称
    const getDimensionName = (key) => {
      const nameMap = {
        'experience_match': '工作经验匹配度',
        'skills_proficiency': '技能专业程度',
        'performance_results': '业绩表现',
        'career_stability': '职业稳定性',
        'resume_professionalism': '简历专业性',
        'education_background': '教育背景',
        'work_stability': '工作稳定性',
        'culture_fit': '企业文化匹配',
        'basic_skills': '技能基础',
        'character_assessment': '品格素养',
        'learning_potential': '学习能力与潜力',
        'innovation_thinking': '创新思维',
        'adaptability': '适应性与灵活性',
        'soft_skills': '软技能',
        'current_skills_match': '技能匹配度',
        'technical_depth': '技术深度与专业度',
        'project_complexity': '项目技术含量',
        'technical_breadth': '技术广度与学习能力',
        'practical_experience': '技术实践经验',
        'technical_vision': '技术前瞻性'
      }
      return nameMap[key] || key
    }
    
    // 获取HR类型名称
    const getHRPersonaName = (persona) => {
      const nameMap = {
        'experienced': '经验丰富的HR',
        'conservative': '保守的HR',
        'progressive': '开放的HR',
        'technical': '技术背景HR'
      }
      return nameMap[persona] || persona
    }
    
    // 其他辅助方法保持不变
    const getScoreColor = (score) => {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    const proceedToPhase4 = () => {
      const passedResumes = resumeList.value.filter(r => 
        r.hrFeedback && r.hrFeedback.passes_initial_screening
      )
      
      if (passedResumes.length === 0) {
        ElMessage.warning('暂无通过HR初筛的简历')
        return
      }
      
      // 存储通过的简历和面试邀请
      const interviewData = passedResumes.map((resume, index) => ({
        resumeId: resume.id,
        resumeData: resume.data,
        hrFeedback: resume.hrFeedback,
        interviewInvitation: resume.hrFeedback.interview_invitation
      }))
      
      localStorage.setItem('passedResumes', JSON.stringify(interviewData))
      
      store.setCurrentPhase(4)
      router.push('/phase4')
    }
    
    // 优化简历方法
    const optimizeResume = async () => {
      if (!selectedFeedback.value) {
        ElMessage.warning('请先选择一个反馈结果')
        return
      }
      
      try {
        ElMessage.info('正在根据HR反馈优化简历...')
        
        const resumeIndex = selectedFeedback.value.resumeIndex
        const resume = resumeList.value[resumeIndex]
        
        const response = await apiService.optimizeResume(
          resume.data,
          selectedFeedback.value.feedback
        )
        
        if (response.success !== false) {
          // 更新简历数据
          resume.data = response.data.content || response.optimized_resume
          
          // 更新localStorage
          const resumesStr = localStorage.getItem('generatedResumes')
          if (resumesStr) {
            const resumes = JSON.parse(resumesStr)
            resumes[resume.id] = resume.data
            localStorage.setItem('generatedResumes', JSON.stringify(resumes))
          }
          
          ElMessage.success('简历已根据HR反馈进行优化')
          
          // 清除当前的HR反馈，建议重新评估
          resume.hrFeedback = null
          resume.evaluatedPersona = null
          resume.evaluationTime = null
          selectedFeedback.value = null
          
        } else {
          ElMessage.error('简历优化失败：' + (response.message || '未知错误'))
        }
      } catch (error) {
        console.error('简历优化错误:', error)
        ElMessage.error('简历优化过程中出现错误')
      }
    }
    
    // 组件挂载时初始化
    onMounted(() => {
      initializeResumeList()
    })
    
    return {
      // 响应式数据
      resumeList,
      selectedFeedback,
      feedbackHistory,
      batchHRPersona,
      isBatchEvaluating,
      evaluationProgress,           // 新增：进度条状态
      feedbackPagination,          // 新增：反馈分页状态
      
      // HR类型描述
      hrPersonaDescriptions,
      
      // 评估函数
      submitSingleResumeToHR,
      submitAllResumesToHR,
      submitAllResumesWithSameHR,
      startMultiHRFeedback,
      
      // 进度条控制函数
      showProgress,                // 新增：显示进度条
      updateProgress,              // 新增：更新进度
      hideProgress,                // 新增：隐藏进度条
      
      // 反馈分页函数
      initializeFeedbackPagination, // 新增：初始化分页
      previousFeedback,            // 新增：上一个反馈
      nextFeedback,                // 新增：下一个反馈
      selectFeedbackByIndex,       // 新增：选择指定反馈
      updateSelectedFeedback,      // 新增：更新选中反馈
      
      // 其他函数
      viewFeedback,
      optimizeResume,
      calculateTotalScore,
      getDimensionName,
      getHRPersonaName,
      getScoreColor,
      proceedToPhase4,
      store
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

/* 多简历布局样式 */
.resumes-section {
  margin-bottom: 30px;
}

.resumes-section h4 {
  margin-bottom: 16px;
  color: #303133;
  font-weight: 600;
}

.no-resumes {
  text-align: center;
  padding: 40px 0;
}

.resume-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.resume-item-card {
  border: 1px solid #EBEEF5;
  transition: all 0.3s ease;
}

.resume-item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.resume-item-card.evaluated {
  border-color: #67C23A;
  background-color: #F0F9FF;
}

.resume-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-header h5 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.hr-selection {
  margin-bottom: 16px;
}

.hr-selection label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.resume-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.feedback-preview {
  border-top: 1px solid #EBEEF5;
  padding-top: 12px;
}

.score-preview {
  margin-bottom: 8px;
}

.score-preview span {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: block;
}

.hr-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.eval-time {
  color: #909399;
  font-size: 12px;
}

/* 批量操作样式 */
.batch-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #F5F7FA;
  border-radius: 8px;
}

.batch-section h4 {
  margin-bottom: 16px;
  color: #303133;
  font-weight: 600;
}

.batch-controls {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.batch-option {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.unified-hr-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.batch-desc {
  margin: 0;
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.batch-controls .el-select {
  min-width: 200px;
}

.multi-hr-section {
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.multi-hr-section h4 {
  margin-bottom: 12px;
  color: white;
}

.multi-hr-section .el-button {
  border-color: white;
  color: white;
}

.multi-hr-section .el-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
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

/* 新增样式 */
.score-breakdown {
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.score-breakdown h5 {
  margin: 0 0 12px 0;
  color: #409EFF;
  font-size: 14px;
}

.score-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.score-item span {
  min-width: 120px;
  font-size: 14px;
  color: #606266;
}

.all-scores .score-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.all-scores .score-label {
  min-width: 150px;
  font-weight: 500;
  color: #303133;
}

.all-scores .score-value {
  margin-left: 10px;
  font-weight: bold;
  color: #409EFF;
}

.detailed-feedback .el-tabs__content {
  padding-top: 16px;
}

/* 进度条样式 */
.progress-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  min-width: 400px;
  z-index: 2000;
  text-align: center;
}

.progress-content h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
}

.progress-text {
  margin-top: 15px;
  color: #606266;
  font-size: 14px;
}

.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1999;
}

/* 反馈分页样式 */
.feedback-pagination {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.feedback-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.feedback-nav .nav-buttons {
  display: flex;
  gap: 8px;
}

.feedback-nav .nav-buttons .el-button {
  padding: 5px 12px;
  font-size: 12px;
}

.feedback-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  color: #606266;
  font-size: 13px;
}

.feedback-info .info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.feedback-info .hr-tag {
  display: inline-block;
  padding: 2px 8px;
  background-color: #409eff;
  color: white;
  border-radius: 4px;
  font-size: 11px;
}

.feedback-info .score-badge {
  display: inline-block;
  padding: 2px 6px;
  background-color: #67c23a;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
}

.detailed-feedback .el-tab-pane {
  line-height: 1.6;
  color: #606266;
}
</style>

