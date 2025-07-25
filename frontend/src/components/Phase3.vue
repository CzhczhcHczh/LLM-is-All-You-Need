<template>
  <div class="phase3-page">
    <!-- 粒子背景动画 -->
    <div class="particles-background">
      <div class="particle" v-for="n in 100" :key="n" :style="getParticleStyle()"></div>
    </div>
    
    <div class="phase3-container">
      <!-- 优化进度指示器 -->
      <div v-if="progressInfo.show" class="optimization-progress-overlay">
        <el-card class="progress-card">
          <div class="progress-content">
            <h3><el-icon><Loading /></el-icon> 简历优化中...</h3>
            <el-progress 
              :percentage="Math.floor(progressInfo.value * 100)" 
              :color="progressInfo.color"
              :stroke-width="8"
            />
            <p class="progress-text">{{ progressInfo.text }}</p>
            <div class="progress-steps">
              <el-tag :type="progressInfo.value >= 0.2 ? 'success' : 'info'">解析简历数据</el-tag>
              <el-tag :type="progressInfo.value >= 0.5 ? 'success' : 'info'">分析HR反馈</el-tag>
              <el-tag :type="progressInfo.value >= 0.8 ? 'success' : 'info'">生成优化版本</el-tag>
              <el-tag :type="progressInfo.value >= 1.0 ? 'success' : 'info'">完成优化</el-tag>
            </div>
          </div>
        </el-card>
      </div>

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

      <!-- 新增：进入Phase4入口区域 -->
      <div class="phase4-entry-section" v-if="resumeList.length > 0">
        <h4>下一阶段 - 面试安排</h4>
        
        <!-- 职位选择区域 -->
        <div class="job-selection-area">
          <h5>选择要进入面试安排的职位：</h5>
          <div class="selection-hint">
            <el-alert
              title="灵活选择"
              type="info"
              show-icon
              :closable="false"
            >
              您可以选择任何职位进入面试阶段，无论是否通过HR初筛。未通过初筛的职位也可能在面试中有出色表现！
            </el-alert>
          </div>
          <div class="job-selection-grid">
            <el-card 
              v-for="(resume, index) in resumeList" 
              :key="resume.id"
              class="job-selection-card"
              :class="{ 
                'selected': selectedJobsForPhase4.includes(index),
                'passed': resume.hrFeedback && resume.hrFeedback.passes_initial_screening,
                'failed': resume.hrFeedback && !resume.hrFeedback.passes_initial_screening,
                'not-evaluated': !resume.hrFeedback
              }"
              @click="toggleJobSelection(index)"
            >
              <div class="job-card-content">
                <div class="job-header">
                  <h6>{{ resume.jobPosting.job_title || '职位' + (index + 1) }}</h6>
                  <div class="job-status">
                    <el-checkbox 
                      :model-value="selectedJobsForPhase4.includes(index)"
                      @change="toggleJobSelection(index)"
                      @click.stop
                    />
                  </div>
                </div>
                <div class="job-details">
                  <p class="company">{{ resume.jobPosting.company_name || '公司' + (index + 1) }}</p>
                  <div class="job-tags">
                    <el-tag v-if="resume.hrFeedback" 
                           :type="resume.hrFeedback.passes_initial_screening ? 'success' : 'danger'" 
                           size="small">
                      {{ resume.hrFeedback.passes_initial_screening ? '通过初筛' : '未通过初筛' }}
                      ({{ resume.hrFeedback.overall_score }}分)
                    </el-tag>
                    <el-tag v-else type="info" size="small">未评估</el-tag>
                    
                    <el-tag v-if="resume.evaluatedPersona" type="warning" size="small">
                      {{ getHRPersonaName(resume.evaluatedPersona) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 快速选择按钮 -->
          <div class="quick-selection">
            <el-button @click="selectAllJobs" size="small">全选</el-button>
            <el-button @click="selectPassedJobs" size="small" type="success">只选通过初筛</el-button>
            <el-button @click="selectFailedJobs" size="small" type="warning">只选未通过初筛</el-button>
            <el-button @click="clearJobSelection" size="small">清空</el-button>
          </div>
        </div>
        
        <!-- 统计信息和操作按钮 -->
        <div class="phase4-entry-content">
          <div class="entry-info">
            <h5>Phase 4 - 面试安排</h5>
            <p>系统将为您智能安排面试时间，优化面试顺序</p>
            <div class="entry-stats">
              <el-statistic title="总职位数" :value="resumeList.length" />
              <el-statistic title="已选择" :value="selectedJobsForPhase4.length" />
              <el-statistic title="通过初筛" :value="getPassedCount()" />
              <el-statistic title="已评估" :value="getEvaluatedCount()" />
            </div>
          </div>
          <div class="entry-actions">
            <el-button 
              v-if="selectedJobsForPhase4.length > 0"
              @click="proceedToPhase4WithSelected" 
              type="success"
              size="large"
            >
              <el-icon><ArrowRight /></el-icon>
              进入面试安排 ({{ selectedJobsForPhase4.length }}个职位)
            </el-button>
            <el-button 
              v-else
              disabled
              size="large"
            >
              <el-icon><ArrowRight /></el-icon>
              请先选择职位
            </el-button>
          </div>
        </div>
      </div>

    </el-card>

    <!-- 新增：评估进度条 -->
    <el-card v-if="evaluationProgress.show" class="evaluation-progress-card">
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
          
          <!-- 新增：能力雷达图 -->
          <RadarChart v-if="selectedFeedback.feedback.detailed_scores"
            :scores="selectedFeedback.feedback.detailed_scores"
            style="margin: 30px 0;" />
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
                  <div v-if="isExperienceRelatedScore(key)" class="score-item">
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
                  <div v-if="isSkillRelatedScore(key)" class="score-item">
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
                  <div v-if="isEducationRelatedScore(key)" class="score-item">
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

        <!-- Suggestions
        <div class="suggestions" v-if="selectedFeedback.feedback.suggestions">
          <h4>改进建议</h4>
          <ol>
            <li v-for="suggestion in selectedFeedback.feedback.suggestions" :key="suggestion">
              {{ suggestion }}
            </li>
          </ol>
        </div> -->

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
        
        <div class="action-group proceed-group">
          <h5>进入下一阶段</h5>
          <el-button 
            v-if="selectedFeedback.feedback.passes_initial_screening" 
            @click="proceedToPhase4" 
            type="success"
            size="large"
          >
            <el-icon><ArrowRight /></el-icon>
            直接进入面试安排
          </el-button>
          
          <el-button 
            v-else
            @click="proceedToPhase4" 
            type="primary"
            size="large"
          >
            <el-icon><ArrowRight /></el-icon>
            仍要进入面试安排
          </el-button>
          
          <p class="action-hint" v-if="!selectedFeedback.feedback.passes_initial_screening">
            虽然未通过初筛，但您仍可选择进入面试阶段
          </p>
          <p class="action-hint" v-else>
            恭喜！您已通过HR初筛，可直接进入面试安排
          </p>
        </div>
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
          v-for="(feedback, index) in  [...feedbackHistory].reverse()" 
          :key="index"
          :timestamp="feedback.timestamp"
        >
          <div class="history-item">
            <h5>第{{ feedbackHistory.length - index }}轮反馈 - {{ feedback.persona_name }}</h5>
            <p>评分: {{ feedback.score }}/100</p>
            <p>{{ feedback.passes_screening ? '✅ 通过初筛' : '❌ 未通过初筛' }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    <!-- 自我介绍生成区域 -->
    <div class="self-intro-section" style="margin: 32px 0;">
      <el-button 
        type="primary" 
        :loading="isGeneratingIntro" 
        @click="generateSelfIntroduction"
        size="large"
      >
        <el-icon><Edit /></el-icon>
        根据反馈生成自我介绍
      </el-button>
      <el-card v-if="selfIntroduction" style="margin-top: 20px; background: #f8fafc;">
        <h4>自我介绍示例</h4>
        <p style="white-space: pre-line;">{{ selfIntroduction }}</p>
      </el-card>
    </div>

    <!-- 面试模拟区域 -->
    <el-card class="interview-simulation-card" style="margin: 32px 0;">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Calendar /></el-icon> AI面试模拟</h2>
          <p>根据HR类型和简历内容，模拟真实面试场景</p>
        </div>
      </template>

      <div v-if="!selectedFeedback" class="no-feedback-hint">
        <el-alert type="info" :closable="false">
          <template #title>
            <span>请先选择一个HR评估结果，然后开始面试模拟</span>
          </template>
        </el-alert>
      </div>

      <div v-else class="interview-content">
        <!-- 面试设置 -->
        <div class="interview-settings" v-if="!interviewStarted">
          <h4>面试设置</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <label>HR类型：</label>
              <el-tag :type="getHRTypeColor(selectedFeedback.hrPersona)" size="large">
                {{ getHRTypeName(selectedFeedback.hrPersona) }}
              </el-tag>
            </el-col>
            <el-col :span="12">
              <label>问题数量：</label>
              <el-select v-model="interviewSettings.numQuestions" style="width: 120px;">
                <el-option label="3题" :value="3"></el-option>
                <el-option label="5题" :value="5"></el-option>
                <el-option label="8题" :value="8"></el-option>
              </el-select>
            </el-col>
          </el-row>
          
          <div class="start-interview-section" style="margin-top: 20px; text-align: center;">
            <el-button 
              type="primary" 
              size="large"
              :loading="isGeneratingQuestions"
              @click="startInterview"
            >
              <el-icon><Promotion /></el-icon>
              开始面试模拟
            </el-button>
          </div>
        </div>

        <!-- 面试进行中 -->
        <div class="interview-in-progress" v-if="interviewStarted && interviewQuestions.length > 0">
          <div class="interview-header">
            <h4>面试进行中</h4>
            <div class="progress-info">
              <span>问题 {{ currentQuestionIndex + 1 }} / {{ interviewQuestions.length }}</span>
              <el-progress 
                :percentage="((currentQuestionIndex + 1) / interviewQuestions.length) * 100"
                :stroke-width="16"
                text-inside
                style="width: 200px; margin-left: 20px;"
              />
            </div>
          </div>

          <!-- 当前问题 -->
          <el-card class="current-question-card" v-if="currentQuestion">
            <template #header>
              <div class="question-header">
                <h5>{{ getHRTypeName(selectedFeedback.hrPersona) }} 向您提问：</h5>
                <div class="question-meta">
                  <el-tag size="small">{{ currentQuestion.type }}</el-tag>
                  <el-tag size="small" type="info">{{ currentQuestion.difficulty }}</el-tag>
                  <el-tag size="small" type="warning">{{ currentQuestion.time_limit }}</el-tag>
                </div>
              </div>
            </template>

            <div class="question-content">
              <p class="question-text">{{ currentQuestion.question }}</p>
              <p class="question-focus">
                <strong>考察重点：</strong>{{ currentQuestion.focus_area }}
              </p>
            </div>

            <!-- 用户回答输入 -->
            <div class="answer-input-section" style="margin-top: 20px;">
              <label>您的回答：</label>
              <el-input
                v-model="currentAnswer"
                type="textarea"
                :rows="6"
                placeholder="请输入您的回答..."
                :disabled="isEvaluatingAnswer"
              />
              
              <div class="answer-actions" style="margin-top: 15px; text-align: right;">
                <el-button @click="currentAnswer = ''" :disabled="isEvaluatingAnswer">
                  清空
                </el-button>
                <el-button 
                  type="primary"
                  @click="submitAnswer"
                  :loading="isEvaluatingAnswer"
                  :disabled="!currentAnswer.trim()"
                >
                  提交回答
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- 回答评估结果 -->
          <el-card class="answer-evaluation-card" v-if="currentEvaluation">
            <template #header>
              <h5>回答评估与建议</h5>
            </template>

            <div class="evaluation-content">
              <!-- 评分 -->
              <div class="score-section">
                <h6>评分</h6>
                <el-progress 
                  :percentage="currentEvaluation.evaluation?.overall_score || currentEvaluation.overall_score || 0"
                  :color="getScoreColor(currentEvaluation.evaluation?.overall_score || currentEvaluation.overall_score || 0)"
                  :stroke-width="12"
                  text-inside
                />
              </div>

              <!-- 优缺点分析 -->
              <el-row :gutter="20" style="margin-top: 20px;">
                <el-col :span="12">
                  <h6>回答优点</h6>
                  <ul class="evaluation-list">
                    <li v-for="strength in (currentEvaluation.evaluation?.strengths || currentEvaluation.strengths || [])" :key="strength">
                      <el-icon color="green"><Check /></el-icon>
                      {{ strength }}
                    </li>
                  </ul>
                </el-col>
                <el-col :span="12">
                  <h6>需要改进</h6>
                  <ul class="evaluation-list">
                    <li v-for="weakness in (currentEvaluation.evaluation?.weaknesses || currentEvaluation.weaknesses || [])" :key="weakness">
                      <el-icon color="red"><Close /></el-icon>
                      {{ weakness }}
                    </li>
                  </ul>
                </el-col>
              </el-row>

              <!-- HR点评 -->
              <div class="hr-feedback-section" style="margin-top: 20px;">
                <h6>HR点评</h6>
                <el-card class="hr-comment-card">
                  <p>{{ currentEvaluation.evaluation?.hr_comment || currentEvaluation.hr_comment || '暂无HR评价' }}</p>
                </el-card>
              </div>

              <!-- 优化建议 -->
              <div class="optimization-section" style="margin-top: 20px;">
                <h6>优化建议</h6>
                <el-tabs v-if="currentEvaluation.evaluation && currentEvaluation.evaluation.improvement_suggestions">
                  <el-tab-pane label="改进建议" name="improvements">
                    <ul>
                      <li v-for="improvement in currentEvaluation.evaluation.improvement_suggestions" :key="improvement">
                        {{ improvement }}
                      </li>
                    </ul>
                  </el-tab-pane>
                  <el-tab-pane label="HR评价" name="comment">
                    <p>{{ currentEvaluation.evaluation.hr_comment }}</p>
                  </el-tab-pane>
                </el-tabs>
                <div v-else-if="currentEvaluation.improvement_suggestions">
                  <ul>
                    <li v-for="improvement in currentEvaluation.improvement_suggestions" :key="improvement">
                      {{ improvement }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- 理想回答示例 -->
              <div class="ideal-answer-section" style="margin-top: 20px;">
                <el-collapse>
                  <el-collapse-item title="查看理想回答示例" name="ideal-answer">
                    <div class="ideal-answer-content">
                      <h6 style="font-size: 1.5em; font-weight: bold; margin-bottom: 20px;">推荐回答要点</h6>
                      <el-card class="ideal-answer-card">
                        <ul v-if="currentEvaluation.evaluation && currentEvaluation.evaluation.ideal_answer_points">
                          <li v-for="point in currentEvaluation.evaluation.ideal_answer_points" :key="point">
                            {{ point }}
                          </li>
                        </ul>
                        <ul v-else-if="currentEvaluation.ideal_answer_points">
                          <li v-for="point in currentEvaluation.ideal_answer_points" :key="point">
                            {{ point }}
                          </li>
                        </ul>
                        <p v-else>暂无理想回答示例</p>
                      </el-card>
                      
                      <h6 style="font-size: 1.5em; font-weight: bold; margin-top: 25px; margin-bottom: 15px;">HR专业评价</h6>
                      <p v-if="currentEvaluation.evaluation && currentEvaluation.evaluation.hr_comment">
                        {{ currentEvaluation.evaluation.hr_comment }}
                      </p>
                      <p v-else-if="currentEvaluation.hr_comment">
                        {{ currentEvaluation.hr_comment }}
                      </p>
                      <p v-else>暂无HR评价</p>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <!-- 继续下一题 -->
              <div class="next-question-section" style="margin-top: 20px; text-align: center;">
                <el-button 
                  v-if="currentQuestionIndex < interviewQuestions.length - 1"
                  type="primary"
                  @click="nextQuestion"
                  size="large"
                >
                  下一题
                </el-button>
                <el-button 
                  v-else
                  type="success"
                  @click="finishInterview"
                  size="large"
                >
                  <el-icon><Check /></el-icon>
                  完成面试
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 面试完成总结 -->
        <div class="interview-summary" v-if="interviewFinished">
          <el-result icon="success" title="面试完成！">
            <template #sub-title>
              <p>恭喜您完成了与{{ getHRTypeName(selectedFeedback.hrPersona) }}的面试模拟</p>
            </template>
            <template #extra>
              <el-button type="primary" @click="restartInterview">重新开始面试</el-button>
              <el-button @click="resetInterview">返回设置</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Promotion, Refresh, Check, Close, Calendar, 
  Edit, ArrowRight, Loading, View, ArrowLeft, Download
} from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'
import ResumeDisplay from './ResumeDisplay.vue'
import RadarChart from './RadarChart.vue'
export default {
  name: 'Phase3',
  components: {
    User, Promotion, Refresh, Check, Close, Calendar,
    Edit, ArrowRight, Loading, View, ArrowLeft, Download,
    ResumeDisplay,
    RadarChart
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    

    //自我介绍
    const selfIntroduction = ref('')
    const isGeneratingIntro = ref(false)

    // 面试模拟相关状态
    const interviewSettings = reactive({
      numQuestions: 3
    })
    const interviewStarted = ref(false)
    const interviewFinished = ref(false)
    const isGeneratingQuestions = ref(false)
    const isEvaluatingAnswer = ref(false)
    const interviewQuestions = ref([])
    const currentQuestionIndex = ref(0)
    const currentAnswer = ref('')
    const currentEvaluation = ref(null)
    const interviewHistory = ref([]) // 存储所有问题和回答的历史

    // 状态管理
    const resumeList = ref([])
    const selectedFeedback = ref(null)
    const feedbackHistory = ref([])
    const batchHRPersona = ref('experienced')
    const isBatchEvaluating = ref(false)
    

        // 新增：职位选择相关状态
    const selectedJobsForPhase4 = ref([])
    const selectedJobs = ref([]) // 在职位选择界面选中的简历ID
    
    // 新增：简历展示相关状态
    const optimizedResumeDialogVisible = ref(false)
    const optimizedResumeData = ref(null)
    const currentJobPosting = ref(null)

    // 新增：进度条相关状态
    const evaluationProgress = ref({
      show: false,
      current: 0,
      total: 0,
      message: '',
      type: 'single' // single, batch, multi-hr
    })
    
    // 新增：优化进度指示器状态
    const progressInfo = ref({
      show: false,
      value: 0,
      text: '正在优化简历...',
      color: '#409EFF'
    })
    
    // 新增：反馈翻页相关状态
    const feedbackPagination = ref({
      currentIndex: 0,
      availableFeedbacks: [],
      totalCount: 0
    })
    
    // 新增：计算属性 - 是否可以导航到Phase4
    const canNavigateToPhase4 = computed(() => {
      return resumeList.value.length > 0 && (getEvaluatedCount() > 0 || selectedJobsForPhase4.value.length > 0)
    })
    
    // 新增：计算属性 - 是否有优化后的简历
    const hasOptimizedResume = computed(() => {
      if (!selectedFeedback.value) return false
      const resumeIndex = selectedFeedback.value.resumeIndex
      const resume = resumeList.value[resumeIndex]
      return resume && resume.data && resume.optimizedAt
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
          feedbackHistory.value.push({
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
                    // 新增：保存评估结果到localStorage
          saveHRFeedbackToStorage()
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
              feedbackHistory.value.push({
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
        

        // 保存评估结果
        saveHRFeedbackToStorage()
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
    
    // 新增：保存HR反馈结果到localStorage
    const saveHRFeedbackToStorage = () => {
      try {
        const feedbackData = {
          resumeList: resumeList.value.map(resume => ({
            id: resume.id,
            hrFeedback: resume.hrFeedback,
            evaluatedPersona: resume.evaluatedPersona,
            evaluationTime: resume.evaluationTime,
            selectedHRPersona: resume.selectedHRPersona
          })),
          feedbackHistory: feedbackHistory.value,
          timestamp: new Date().toISOString()
        }
        
        localStorage.setItem('phase3HRFeedback', JSON.stringify(feedbackData))
        console.log('HR反馈数据已保存到localStorage')
      } catch (error) {
        console.error('保存HR反馈数据失败:', error)
      }
    }

    // 新增：从localStorage加载HR反馈结果
    const loadHRFeedbackFromStorage = () => {
      try {
        const savedData = localStorage.getItem('phase3HRFeedback')
        if (savedData) {
          const feedbackData = JSON.parse(savedData)
          
          // 恢复HR反馈数据
          if (feedbackData.resumeList) {
            feedbackData.resumeList.forEach(savedResume => {
              const currentResume = resumeList.value.find(r => r.id === savedResume.id)
              if (currentResume) {
                currentResume.hrFeedback = savedResume.hrFeedback
                currentResume.evaluatedPersona = savedResume.evaluatedPersona
                currentResume.evaluationTime = savedResume.evaluationTime
                currentResume.selectedHRPersona = savedResume.selectedHRPersona || 'experienced'
              }
            })
          }
          
          // 恢复历史记录
          if (feedbackData.feedbackHistory) {
            feedbackHistory.value = feedbackData.feedbackHistory
          }
          
          console.log('HR反馈数据已从localStorage恢复')
          ElMessage.success('已恢复之前的HR评估结果')
          return true
        }
      } catch (error) {
        console.error('加载HR反馈数据失败:', error)
      }
      return false
    }

    // 新增：导航方法
    const navigateToPhase = (phase) => {
      try {
        store.setCurrentPhase(phase)
        router.push(`/phase${phase}`)
      } catch (error) {
        console.error('导航失败:', error)
        ElMessage.error('页面跳转失败')
      }
    }

    // 新增：职位选择方法
    const toggleJobSelection = (index) => {
      const currentIndex = selectedJobsForPhase4.value.indexOf(index)
      if (currentIndex > -1) {
        selectedJobsForPhase4.value.splice(currentIndex, 1)
      } else {
        selectedJobsForPhase4.value.push(index)
      }
    }

    const selectAllJobs = () => {
      selectedJobsForPhase4.value = resumeList.value.map((_, index) => index)
    }

    const selectPassedJobs = () => {
      selectedJobsForPhase4.value = resumeList.value
        .map((resume, index) => ({ resume, index }))
        .filter(({ resume }) => resume.hrFeedback && resume.hrFeedback.passes_initial_screening)
        .map(({ index }) => index)
        
      if (selectedJobsForPhase4.value.length === 0) {
        ElMessage.warning('没有通过初筛的职位')
      }
    }

    const selectFailedJobs = () => {
      selectedJobsForPhase4.value = resumeList.value
        .map((resume, index) => ({ resume, index }))
        .filter(({ resume }) => resume.hrFeedback && !resume.hrFeedback.passes_initial_screening)
        .map(({ index }) => index)
        
      if (selectedJobsForPhase4.value.length === 0) {
        ElMessage.warning('没有未通过初筛的职位')
      }
    }

    const clearJobSelection = () => {
      selectedJobsForPhase4.value = []
    }

    // 新增：导航到指定阶段
    const goToPhase = (phase) => {
      const routes = {
        1: '/phase1',
        2: '/phase2', 
        3: '/phase3',
        4: '/phase4'
      };
      
      if (routes[phase]) {
        router.push(routes[phase]);
      }
    }

    // 新增：获取HR决策信息
    const getHrDecision = (resume) => {
      if (!resume.hrFeedback) {
        return { decision: 'not-evaluated', score: 0 };
      }
      
      const decision = resume.hrFeedback.passes_initial_screening ? 'pass' : 'fail';
      const score = resume.hrFeedback.overall_score || 0;
      
      return { decision, score };
    }

    // 新增：使用选择的职位进入Phase4
    const proceedToPhase4WithSelected = () => {
      if (selectedJobsForPhase4.value.length === 0) {
        ElMessage.warning('请先选择要进入面试安排的职位')
        return
      }

      try {
        // 获取原始选择的职位数据
        const selectedJobs = JSON.parse(localStorage.getItem('selectedJobs') || '[]')
        
        // 根据选择的索引获取对应的简历和职位数据
        const selectedInterviewData = selectedJobsForPhase4.value.map(index => {
          const resume = resumeList.value[index]
          const originalJob = selectedJobs.find(job => 
            job.job_title === resume.jobPosting.job_title || 
            job.company_name === resume.jobPosting.company_name
          ) || resume.jobPosting

          return {
            resumeId: resume.id,
            resumeData: resume.data,
            hrFeedback: resume.hrFeedback || null,
            interviewInvitation: resume.hrFeedback?.interview_invitation || null,
            // 保留完整的职位信息供Phase4使用
            job_title: originalJob.job_title || resume.jobPosting.job_title,
            company_name: originalJob.company_name || resume.jobPosting.company_name,
            location: originalJob.location,
            salary_range: originalJob.salary_range,
            requirements: originalJob.requirements || [],
            skills: originalJob.skills || [],
            description: originalJob.description,
            experience_level: originalJob.experience_level,
            // 添加选择状态
            isSelected: true,
            selectionIndex: index
          }
        })

        // 存储数据供Phase4使用
        localStorage.setItem('selectedJobsForPhase4', JSON.stringify(selectedInterviewData))
        
        const passedCount = selectedInterviewData.filter(job => 
          job.hrFeedback && job.hrFeedback.passes_initial_screening
        ).length
        
        ElMessage.success(
          `已选择${selectedInterviewData.length}个职位进入面试安排` +
          (passedCount > 0 ? `，其中${passedCount}个通过HR初筛` : '')
        )
        
        store.setCurrentPhase(4)
        router.push('/phase4')
      } catch (error) {
        console.error('进入Phase4失败:', error)
        ElMessage.error('进入面试安排阶段失败')
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
            feedbackHistory.value.push({
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
      if (type === 'optimization') {
        // 优化进度条
        progressInfo.value = {
          show: true,
          value: 0,
          text: message || '正在优化简历...',
          color: '#409EFF'
        }
      } else {
        // 评估进度条
        evaluationProgress.value = {
          show: true,
          current: 0,
          total: total,
          message: message,
          type: type
        }
      }
    }
    
    const updateProgress = (current) => {
      if (typeof current === 'number' && current <= 1) {
        // 优化进度 (0-1)
        progressInfo.value.value = current
        
        // 根据进度更新文本，与界面显示的四个步骤保持一致
        if (current < 0.2) {
          progressInfo.value.text = '正在解析简历数据...'
        } else if (current < 0.5) {
          progressInfo.value.text = '正在分析HR反馈...'
        } else if (current < 0.8) {
          progressInfo.value.text = '正在生成优化版本...'
        } else if (current < 1.0) {
          progressInfo.value.text = '正在完成优化...'
        } else {
          progressInfo.value.text = '完成优化！'
        }
      } else {
        // 评估进度 (整数)
        evaluationProgress.value.current = current
      }
    }
    
    const hideProgress = () => {
      evaluationProgress.value.show = false
      progressInfo.value.show = false
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
          persona: allFeedbacks[0].persona,
          hrPersona: allFeedbacks[0].persona, // 添加这个字段用于面试模拟
          resumeContent: resumeList.value[resumeIndex]?.data,
          jobPosting: resumeList.value[resumeIndex]?.jobPosting
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
          persona: currentFeedback.persona,
          hrPersona: currentFeedback.persona, // 添加这个字段用于面试模拟
          resumeContent: resumeList.value[currentFeedback.resumeIndex]?.data,
          jobPosting: resumeList.value[currentFeedback.resumeIndex]?.jobPosting
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
            persona: resume.evaluatedPersona,
            hrPersona: resume.evaluatedPersona, // 添加这个字段用于面试模拟
            resumeContent: resume.data,
            jobPosting: resume.jobPosting
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
        'technical_vision': '技术前瞻性',
        
        // 通用维度（备用）
        'education': '教育背景',
        'work_experience': '工作经验',
        'technical_skills': '技术技能',
        'communication_skills': '沟通能力',
        'leadership_potential': '领导力潜质'
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
    
    // 智能识别不同HR类型的评分字段
    const isExperienceRelatedScore = (key) => {
      const experienceKeys = [
        'experience_match', 'work_experience', 'career_stability', 
        'work_stability', 'practical_experience', 'performance_results'
      ]
      return experienceKeys.includes(key) || key.toLowerCase().includes('experience') || key.toLowerCase().includes('stability')
    }
    
    const isSkillRelatedScore = (key) => {
      const skillKeys = [
        'skills_proficiency', 'technical_skills', 'basic_skills', 
        'current_skills_match', 'technical_depth', 'technical_breadth',
        'project_complexity', 'technical_vision', 'innovation_thinking'
      ]
      return skillKeys.includes(key) || key.toLowerCase().includes('skill') || key.toLowerCase().includes('technical')
    }
    
    const isEducationRelatedScore = (key) => {
      const educationKeys = [
        'education_background', 'education', 'learning_potential',
        'adaptability', 'soft_skills', 'character_assessment', 
        'culture_fit', 'resume_professionalism'
      ]
      return educationKeys.includes(key) || key.toLowerCase().includes('education') || key.toLowerCase().includes('learning')
    }
    
    const proceedToPhase4 = () => {
      const passedResumes = resumeList.value.filter(r => 
        r.hrFeedback && r.hrFeedback.passes_initial_screening
      )
      
      if (passedResumes.length === 0) {
        ElMessage.warning('暂无通过HR初筛的简历')
        return
      }
      
      // 获取原始选择的职位数据
      const selectedJobs = JSON.parse(localStorage.getItem('selectedJobs') || '[]')
      
      // 存储通过的简历和面试邀请，同时保留完整的职位信息
      const interviewData = passedResumes.map((resume, index) => {
        // 找到对应的原始职位数据
        const originalJob = selectedJobs.find(job => 
          job.job_title === resume.jobTitle || job.company_name === resume.companyName
        ) || {}
        
        return {
          resumeId: resume.id,
          resumeData: resume.data,
          hrFeedback: resume.hrFeedback,
          interviewInvitation: resume.hrFeedback.interview_invitation,
          // 保留完整的职位信息供Phase4使用
          job_title: originalJob.job_title || resume.jobTitle,
          company_name: originalJob.company_name || resume.companyName,
          location: originalJob.location,
          salary_range: originalJob.salary_range,
          requirements: originalJob.requirements || [],
          skills: originalJob.skills || [],
          description: originalJob.description,
          experience_level: originalJob.experience_level
        }
      })
      
      // 存储数据供Phase4使用
      localStorage.setItem('passedResumes', JSON.stringify(interviewData))
      localStorage.setItem('selectedJobsForPhase4', JSON.stringify(interviewData))
      
      ElMessage.success(`已有${passedResumes.length}份简历通过HR初筛，准备进入面试安排阶段`)
      
      localStorage.setItem('passedResumes', JSON.stringify(interviewData))
      
      store.setCurrentPhase(4)
      router.push('/phase4')
    }
    
    // 优化简历方法 - 跳转到Phase2进行优化
    const optimizeResume = async () => {
      if (!selectedFeedback.value) {
        ElMessage.warning('请先选择一个反馈结果')
        return
      }
      
      try {
        // 显示优化进度条
        showProgress('optimization', 1, '正在根据HR反馈优化简历...')
        updateProgress(0)
        
        const resumeIndex = selectedFeedback.value.resumeIndex
        const resume = resumeList.value[resumeIndex]
        
        console.log('开始优化简历:', {
          resumeIndex,
          resume: resume ? 'exists' : 'not found',
          feedback: selectedFeedback.value ? 'exists' : 'not found'
        })
        
        if (!resume || !resume.data) {
          throw new Error('简历数据不存在或格式错误')
        }
        
        // 第1步：解析简历数据 (0% -> 20%)
        await new Promise(resolve => setTimeout(resolve, 800)) // 模拟解析时间
        updateProgress(0.2)
        
        // 第2步：分析HR反馈 (20% -> 50%)
        await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟分析时间
        updateProgress(0.5)
        
        // 第3步：生成优化版本 (50% -> 80%)
        

        // 调用API优化简历
        console.log('调用API优化简历...')
        const response = await apiService.optimizeResume(
          resume.data,
          selectedFeedback.value
        )
        
        console.log('API响应:', response)
        updateProgress(0.8)
        
        // 检查响应是否成功
        if (response && response.success !== false) {
          console.log('优化成功，处理响应数据...')
          
          // 第4步：完成优化 (80% -> 100%)
          await new Promise(resolve => setTimeout(resolve, 600)) // 模拟处理时间
          
          // 保存原简历到localStorage供对比
          const originalResumeKey = `original_resume_${resume.id}`
          localStorage.setItem(originalResumeKey, JSON.stringify({
            content: resume.data,
            feedback: selectedFeedback.value,
            optimizationTime: new Date().toISOString()
          }))
          
          // 保存优化后的简历
          const optimizedResume = response.data?.content || response.data?.optimized_resume || response.data
          
          if (!optimizedResume) {
            throw new Error('优化后的简历数据为空')
          }
          
          // 确保store.phase2结构存在
          if (!store.phase2) {
            console.log('初始化store.phase2结构')
            store.phase2 = {
              generatedResumes: {},
              optimizationHistory: [],
              userProfile: null,
              selectedJobs: []
            }
          }
          if (!store.phase2.generatedResumes) {
            store.phase2.generatedResumes = {}
          }
          if (!store.phase2.optimizationHistory) {
            store.phase2.optimizationHistory = []
          }
          
          // 更新store中的简历数据
          store.phase2.generatedResumes[resume.id] = optimizedResume
          console.log('已更新store中的简历数据')
          
          // 更新localStorage中的简历
          const resumesStr = localStorage.getItem('generatedResumes')
          if (resumesStr) {
            try {
              const resumes = JSON.parse(resumesStr)
              resumes[resume.id] = optimizedResume
              localStorage.setItem('generatedResumes', JSON.stringify(resumes))
              console.log('已更新localStorage中的简历')
            } catch (e) {
              console.warn('更新localStorage失败:', e)
            }
          }
          
          // 保存优化信息到store
          const optimizationRecord = {
            resumeId: resume.id,
            originalResume: resume.data,
            optimizedResume: optimizedResume,
            feedback: selectedFeedback.value,
            optimizationSummary: response.data?.optimization_summary || {},
            timestamp: new Date().toISOString()
          }
          
          store.phase2.optimizationHistory.push(optimizationRecord)
          console.log('已保存优化历史记录')
          
          // 更新进度到完成
          updateProgress(1)
          
          // 延迟一下显示完成状态，让用户看到100%进度
          setTimeout(() => {
            hideProgress()
            ElMessage.success('简历优化完成，正在跳转到Phase2查看结果...')
            
            // 设置跳转标识，告诉Phase2这是从优化过来的
            localStorage.setItem('fromPhase3Optimization', JSON.stringify({
              resumeId: resume.id,
              feedback: selectedFeedback.value,
              optimizationData: response.data || {}
            }))
            
            // 跳转到Phase2
            setTimeout(() => {
              router.push('/phase2')
            }, 1000)
          }, 1500)
          
        } else {
          const errorMessage = response?.message || response?.detail || '未知错误'
          console.error('优化失败:', errorMessage)
          ElMessage.error('简历优化失败：' + errorMessage)
        }
      } catch (error) {
        console.error('简历优化错误:', error)
        
        let errorMessage = '简历优化过程中出现错误'
        if (error.response?.data?.detail) {
          errorMessage += ': ' + error.response.data.detail
        } else if (error.message) {
          errorMessage += ': ' + error.message
        }
        
        ElMessage.error(errorMessage)
      } finally {
        // 确保进度条关闭
        hideProgress()
      }
    }
    // 新增：获取评估数量的方法
    const getEvaluatedCount = () => {
      return resumeList.value.filter(r => r.hrFeedback).length
    }

    // 新增：获取通过初筛数量的方法
    const getPassedCount = () => {
      return resumeList.value.filter(r => 
        r.hrFeedback && r.hrFeedback.passes_initial_screening
      ).length
    }

    // 新增：强制进入Phase4（包含所有职位）的方法
    const proceedToPhase4ForceAll = async () => {
      try {
        const result = await ElMessageBox.confirm(
          '当前没有简历通过HR初筛，是否要强制进入面试安排阶段？这将包含所有职位。',
          '确认进入Phase4',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )

        if (result === 'confirm') {
          // 获取原始选择的职位数据
          const selectedJobs = JSON.parse(localStorage.getItem('selectedJobs') || '[]')
          
          // 包含所有简历，不论是否通过初筛
          const allInterviewData = resumeList.value.map((resume, index) => {
            // 找到对应的原始职位数据
            const originalJob = selectedJobs.find(job => 
              job.job_title === resume.jobTitle || job.company_name === resume.companyName
            ) || {}
            
            return {
              resumeId: resume.id,
              resumeData: resume.data,
              hrFeedback: resume.hrFeedback || null,
              interviewInvitation: resume.hrFeedback?.interview_invitation || null,
              // 保留完整的职位信息供Phase4使用
              job_title: originalJob.job_title || resume.jobTitle,
              company_name: originalJob.company_name || resume.companyName,
              location: originalJob.location,
              salary_range: originalJob.salary_range,
              requirements: originalJob.requirements || [],
              skills: originalJob.skills || [],
              description: originalJob.description,
              experience_level: originalJob.experience_level
            }
          })
          
          // 存储数据供Phase4使用
          localStorage.setItem('passedResumes', JSON.stringify(allInterviewData))
          localStorage.setItem('selectedJobsForPhase4', JSON.stringify(allInterviewData))
          
          ElMessage.success(`已将所有${resumeList.value.length}个职位包含在面试安排中`)
          
          store.setCurrentPhase(4)
          router.push('/phase4')
        }
      } catch (error) {
        // 用户取消操作
      }
    }

    //自我介绍方法（增强版）
    const generateSelfIntroduction = async () => {
      if (!selectedFeedback.value) {
        ElMessage.warning('请先选择一个反馈结果')
        return
      }
      
      const strengths = selectedFeedback.value.feedback.strengths || []
      const weaknesses = selectedFeedback.value.feedback.weaknesses || []
      
      isGeneratingIntro.value = true
      selfIntroduction.value = ''
      
      try {
        // 准备增强的参数
        const options = {
          resumeContent: selectedFeedback.value.resumeContent || null,
          jobPosting: selectedFeedback.value.jobPosting || null,
          hrPersona: selectedFeedback.value.hrPersona || 'experienced',
          hrFeedback: selectedFeedback.value.feedback || null
        }
        
        console.log('生成个性化自我介绍，参数：', {
          strengths,
          weaknesses,
          hrPersona: options.hrPersona,
          hasResume: !!options.resumeContent,
          hasJob: !!options.jobPosting
        })
        
        const res = await apiService.generateSelfIntroduction(strengths, weaknesses, 300, options)
        
        if (res.success) {
          selfIntroduction.value = res.data.self_introduction
          
          // 显示个性化信息
          if (res.data.personalization) {
            const personInfo = res.data.personalization
            let message = '个性化自我介绍生成成功'
            if (personInfo.based_on_resume || personInfo.based_on_job) {
              message += `（已针对${personInfo.hr_persona}类型HR优化）`
            }
            ElMessage.success(message)
          } else {
            ElMessage.success('自我介绍生成成功')
          }
        } else {
          ElMessage.error(res.message || '自我介绍生成失败')
        }
      } catch (e) {
        console.error('生成自我介绍失败:', e)
        ElMessage.error('自我介绍生成失败')
      } finally {
        isGeneratingIntro.value = false
      }
    }

    // 面试模拟相关方法
    const currentQuestion = computed(() => {
      if (interviewQuestions.value.length > 0 && currentQuestionIndex.value < interviewQuestions.value.length) {
        return interviewQuestions.value[currentQuestionIndex.value]
      }
      return null
    })

    const getHRTypeName = (hrPersona) => {
      const hrTypes = {
        'conservative': '传统稳重型HR',
        'progressive': '创新开放型HR',
        'experienced': '资深专业型HR'
      }
      return hrTypes[hrPersona] || '专业HR'
    }


    const getHRTypeColor = (hrPersona) => {
      const colors = {
        'conservative': 'info',
        'progressive': 'success',
        'experienced': 'warning'
      }
      return colors[hrPersona] || 'primary'
    }

    const startInterview = async () => {
      if (!selectedFeedback.value) {
        ElMessage.warning('请先选择一个HR评估结果')
        return
      }

      // 调试：检查selectedFeedback的数据
      console.log('开始面试模拟 - selectedFeedback:', selectedFeedback.value)
      console.log('HR类型:', selectedFeedback.value.hrPersona)
      console.log('简历内容:', selectedFeedback.value.resumeContent)
      console.log('职位信息:', selectedFeedback.value.jobPosting)

      isGeneratingQuestions.value = true
      try {
        const res = await apiService.generateInterviewQuestions(
          selectedFeedback.value.hrPersona,
          selectedFeedback.value.resumeContent,
          selectedFeedback.value.jobPosting,
          interviewSettings.numQuestions
        )

        console.log('API返回结果:', res)
        
        if (res && res.success) {
          const questions = res.data?.questions || []
          console.log('解析的问题数组:', questions)
          if (!Array.isArray(questions) || questions.length === 0) {
            console.error('问题数组无效:', questions)
            ElMessage.error('未能生成有效的面试问题，请重试')
            return
          }
          interviewQuestions.value = questions
          currentQuestionIndex.value = 0
          currentAnswer.value = ''
          currentEvaluation.value = null
          interviewHistory.value = []
          interviewStarted.value = true
          interviewFinished.value = false

          console.log('面试状态设置完成:', {
            interviewStarted: interviewStarted.value,
            questionsCount: interviewQuestions.value.length,
            currentQuestion: currentQuestion.value,
            firstQuestion: questions[0] // 直接输出第一个问题
          })
          ElMessage.success('面试问题生成成功，开始面试！')
        } else {
          console.error('API返回失败:', res)
          const errorMessage = res?.message || '面试问题生成失败'
          ElMessage.error('面试问题生成失败：' + errorMessage)
        }
      } catch (e) {
        console.error('生成面试问题失败:', e)
        console.error('错误详情:', {
          message: e.message,
          response: e.response?.data,
          status: e.response?.status
        })
        
        let errorMessage = '面试问题生成失败'
        if (e.response?.data?.detail) {
          errorMessage += '：' + e.response.data.detail
        } else if (e.message) {
          errorMessage += '：' + e.message
        } else {
          errorMessage += '，请检查网络连接或联系管理员'
        }
        
        ElMessage.error(errorMessage)
      } finally {
        isGeneratingQuestions.value = false
      }
    }


    const submitAnswer = async () => {
      if (!currentAnswer.value.trim()) {
        ElMessage.warning('请输入您的回答')
        return
      }

      // 验证当前问题是否存在
      if (!currentQuestion.value) {
        ElMessage.error('当前问题无效，请重新开始面试')
        return
      }

      console.log('提交回答 - 开始评估:', {
        hrPersona: selectedFeedback.value.hrPersona,
        currentQuestion: currentQuestion.value,
        userAnswer: currentAnswer.value,
        resumeContent: selectedFeedback.value.resumeContent ? '已提供' : '未提供',
        jobPosting: selectedFeedback.value.jobPosting ? '已提供' : '未提供'
      })

      isEvaluatingAnswer.value = true
      try {
        const res = await apiService.evaluateInterviewAnswer(
          selectedFeedback.value.hrPersona,
          currentQuestion.value, // 使用 .value 访问计算属性
          currentAnswer.value,
          selectedFeedback.value.resumeContent,
          selectedFeedback.value.jobPosting
        )

        console.log('评估API返回结果:', res)

        if (res && res.success) {
          currentEvaluation.value = res.data
          
          // 保存问题和回答到历史记录
          interviewHistory.value.push({
            question: currentQuestion.value, // 使用 .value
            answer: currentAnswer.value,
            evaluation: res.data
          })

          console.log('回答评估成功，数据已保存')
          ElMessage.success('回答评估完成')
        } else {
          console.error('评估失败，API返回:', res)
          const errorMessage = res?.message || '未知错误'
          ElMessage.error('回答评估失败：' + errorMessage)
        }
        } catch (e) {
        console.error('评估回答失败:', e)
        console.error('错误详情:', {
          message: e.message,
          response: e.response?.data,
          status: e.response?.status,
          stack: e.stack
        })
        let errorMessage = '回答评估失败'
        if (e.response?.data?.detail) {
          errorMessage += '：' + e.response.data.detail
        } else if (e.message) {
          errorMessage += '：' + e.message
        } else {
          errorMessage += '，请检查网络连接或联系管理员'
        }
        
        ElMessage.error(errorMessage)
      } finally {
        isEvaluatingAnswer.value = false
      }
    }

    const nextQuestion = () => {
      currentQuestionIndex.value++
      currentAnswer.value = ''
      currentEvaluation.value = null
    }

    const finishInterview = () => {
      interviewFinished.value = true
      ElMessage.success('恭喜您完成面试！您可以查看所有问题的评估结果。')
    }

    const restartInterview = () => {
      currentQuestionIndex.value = 0
      currentAnswer.value = ''
      currentEvaluation.value = null
      interviewHistory.value = []
      interviewStarted.value = true
      interviewFinished.value = false
    }

    const resetInterview = () => {
      interviewStarted.value = false
      interviewFinished.value = false
      interviewQuestions.value = []
      currentQuestionIndex.value = 0
      currentAnswer.value = ''
      currentEvaluation.value = null
      interviewHistory.value = []
      interviewSettings.numQuestions = 3
    }

    // 组件挂载时初始化
    onMounted(() => {
      initializeResumeList()
    })
    
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
      // 响应式数据
      resumeList,
      selectedFeedback,
      feedbackHistory,
      batchHRPersona,
      isBatchEvaluating,
      evaluationProgress,           // 评估进度条状态
      progressInfo,                 // 优化进度条状态
      feedbackPagination,          // 反馈分页状态
      selectedJobsForPhase4,       // 新增：选择的职位
      selectedJobs,                // 新增：职位选择状态
      // 新增：简历展示相关状态
      optimizedResumeDialogVisible,
      optimizedResumeData,
      currentJobPosting,
      
      // 计算属性
      canNavigateToPhase4,         // 新增：是否可以导航到Phase4
      hasOptimizedResume,          // 新增：是否有优化后的简历
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
      // 新增：智能评分过滤函数
      isExperienceRelatedScore,
      isSkillRelatedScore,
      isEducationRelatedScore,
      proceedToPhase4,
      // 新增：导航方法
      navigateToPhase,
      
      // 新增：职位选择方法
      toggleJobSelection,
      selectAllJobs,
      selectPassedJobs,
      clearJobSelection,
      proceedToPhase4WithSelected,
      
      // 新增：导航方法
      goToPhase,
      
      // 辅助函数
      getHrDecision,

      // 新增：Phase4入口相关函数
      getEvaluatedCount,
      getPassedCount,
      proceedToPhase4ForceAll,
      
      // 新增：数据持久化函数
      saveHRFeedbackToStorage,
      loadHRFeedbackFromStorage,
      
      // 新增：自我介绍相关状态和方法
      selfIntroduction,
      isGeneratingIntro,
      generateSelfIntroduction,

      // 新增：面试模拟相关
      interviewSettings,
      interviewStarted,
      interviewFinished,
      isGeneratingQuestions,
      isEvaluatingAnswer,
      interviewQuestions,
      currentQuestionIndex,
      currentAnswer,
      currentEvaluation,
      interviewHistory,
      currentQuestion,
      getHRTypeName,
      getHRTypeColor,
      getScoreColor,
      startInterview,
      submitAnswer,
      nextQuestion,
      finishInterview,
      restartInterview,
      resetInterview,
      store,
      // 粒子动画
      getParticleStyle
    }
  }
}
</script>

<style scoped>
.phase3-page {
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

.phase3-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  padding: 20px 16px;
}

/* 优化进度指示器样式 */
.optimization-progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 2000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.progress-card {
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 职位选择区域样式 */
.job-selection-area {
  margin-bottom: 25px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.job-selection-area h5 {
  margin: 0 0 15px 0;
  color: #1e40af;
  font-weight: 600;
}

.selection-hint {
  margin-bottom: 20px;
}

.selection-hint .el-alert {
  border-radius: 8px;
}

.job-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.job-selection-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
}

.job-selection-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.job-selection-card.selected {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.job-selection-card.passed {
  border-left: 4px solid #10b981;
}

.job-selection-card.failed {
  border-left: 4px solid #ef4444;
}

.job-selection-card.not-evaluated {
  border-left: 4px solid #6b7280;
}

.job-card-content {
  padding: 15px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.job-header h6 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.job-status {
  margin-left: 10px;
}

.job-details .company {
  color: #6b7280;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.job-tags .el-tag {
  font-size: 12px;
}

.quick-selection {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding: 15px 0;
  border-top: 1px solid #e2e8f0;
}

.quick-selection .el-button {
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navigation-bar {
    padding: 15px;
  }
  
  .nav-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .job-selection-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-selection {
    flex-wrap: wrap;
    justify-content: center;
  }
}

/* 评估进度卡片样式 */
.evaluation-progress-card {
  margin-bottom: 20px;
  /* 与其他主要卡片保持一致的宽度 */
}

.evaluation-progress-content {
  text-align: center;
  padding: 20px;
}

.progress-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.progress-header h3 {
  margin: 0;
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.progress-header .loading-icon {
  font-size: 20px;
  color: #409EFF;
  animation: spin 1s linear infinite;
}

.progress-content {
  text-align: center;
  padding: 24px;
}

.progress-content h3 {
  margin: 0 0 20px 0;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.progress-text {
  margin: 20px 0 0 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.progress-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 20px;
}

.progress-steps .el-tag {
  font-size: 12px;
}


/* 优化反馈操作区域样式 */
.feedback-actions {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  border: 1px solid #cbd5e1;
}

.dialog-actions {
  text-align: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.dialog-actions .el-button {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: 600;
}



.action-group {
  flex: 1;
  min-width: 280px;
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-group h5 {
  margin: 0 0 15px 0;
  color: #374151;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

.optimization-group h5 {
  border-bottom-color: #f59e0b;
}

.proceed-group h5 {
  border-bottom-color: #10b981;
}

.action-group .el-button {
  margin: 8px;
  padding: 12px 24px;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.3s ease;
  min-width: 160px;
}

.action-group .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-hint {
  margin: 15px 0 0 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
  font-style: italic;
}

@media (max-width: 768px) {
  .feedback-actions {
    flex-direction: column;
    gap: 20px;
  }
  
  .action-group {
    min-width: auto;
  }
}

.hr-card, .feedback-card, .history-card, .evaluation-progress-card {
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

/* 新增：Phase4入口区域样式 */
.phase4-entry-section {
  margin-top: 30px;
  padding: 20px 0;
  border-top: 2px solid #E4E7ED;
}

.phase4-entry-section h4 {
  color: #409EFF;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.phase4-entry-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid #bfdbfe;
}

.entry-info h5 {
  color: #1e40af;
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: bold;
}

.entry-info p {
  color: #64748b;
  margin: 0 0 15px 0;
  font-size: 14px;
  line-height: 1.5;
}

.entry-stats {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.entry-stats .el-statistic {
  text-align: center;
}

.entry-actions {
  flex-shrink: 0;
}

.entry-actions .el-button {
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.entry-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.entry-actions .el-button--warning {
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.entry-actions .el-button--warning:hover {
  box-shadow: 0 6px 16px rgba(245, 108, 108, 0.4);
}

@media (max-width: 768px) {
  .phase4-entry-content {
    flex-direction: column;
    text-align: center;
  }
  
  .entry-stats {
    justify-content: center;
  }
}

/* 面试模拟相关样式 */
.interview-simulation-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 1px solid #cbd5e1;
}

.interview-simulation-card .card-header h2 {
  color: #1e40af;
}

.no-feedback-hint {
  text-align: center;
  padding: 40px 0;
}

.interview-settings {
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

.interview-settings h4 {
  margin-bottom: 16px;
  color: #374151;
  font-weight: 600;
}

.interview-settings label {
  display: inline-block;
  min-width: 80px;
  font-weight: 500;
  color: #4b5563;
  margin-right: 10px;
}

.start-interview-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
}

.interview-in-progress {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.interview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e5e7eb;
}

.interview-header h4 {
  margin: 0;
  color: #374151;
  font-weight: 600;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
  color: #6b7280;
}

.current-question-card {
  margin-bottom: 20px;
  border: 2px solid #3b82f6;
  background: #eff6ff;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-header h5 {
  margin: 0;
  color: #1e40af;
  font-weight: 600;
}

.question-meta {
  display: flex;
  gap: 8px;
}

.question-content .question-text {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 12px;
}

.question-content .question-focus {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.answer-input-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.answer-evaluation-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.evaluation-content .score-section h6,
.evaluation-content h6 {
  color: #374151;
  font-weight: 600;
  margin-bottom: 12px;
}

.evaluation-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.evaluation-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.hr-comment-card, .ideal-answer-card {
  background: #fafbfc;
  border: 1px solid #e1e5e9;
  margin-top: 8px;
}

.hr-comment-card p, .ideal-answer-card p {
  margin: 0;
  line-height: 1.6;
  color: #374151;
}

.ideal-answer-content h6 {
  color: #059669;
  font-weight: 600;
  margin-bottom: 8px;
}

.next-question-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
}

.interview-summary {
  text-align: center;
  padding: 40px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .interview-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .progress-info {
    flex-direction: column;
    gap: 10px;
  }
  
  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .question-meta {
    align-self: stretch;
    justify-content: space-between;
  }
}
</style>

