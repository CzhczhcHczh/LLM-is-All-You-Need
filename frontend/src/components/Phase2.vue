<template>
  <div class="phase2-page">
    <!-- 粒子背景动画 -->
    <div class="particles-background">
      <div class="particle" v-for="n in 100" :key="n" :style="getParticleStyle()"></div>
    </div>
    
    <div class="phase2-container">
      <!-- 个人信息表单 - 保持不变 -->
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <h2><el-icon><Document /></el-icon> Phase 2: 简历制作</h2>
            <p>填写您的详细信息，我们将为您生成个性化简历</p>
          </div>
        </template>

      <!-- 原有的用户信息表单保持不变 -->
      <el-form :model="userProfile" label-width="120px" ref="profileForm" :rules="formRules">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="姓名" prop="full_name" required>
              <el-input v-model="userProfile.full_name" placeholder="请输入您的姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="邮箱" prop="email" required>
              <el-input v-model="userProfile.email" placeholder="请输入邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="userProfile.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="居住地址">
              <el-input v-model="userProfile.location" placeholder="如：北京市朝阳区" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标职位">
              <el-input v-model="userProfile.target_position" placeholder="期望的职位" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 个人简介 -->
        <el-divider content-position="left">个人简介</el-divider>
        <el-form-item label="个人简介">
          <el-input 
            v-model="userProfile.summary" 
            type="textarea" 
            :rows="4"
            placeholder="请简要介绍您的专业背景、工作经验和核心优势（建议100-200字）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 技能特长 -->
        <el-divider content-position="left">技能特长</el-divider>
        <el-form-item label="专业技能">
          <div class="skills-section">
            <el-tag
              v-for="skill in userProfile.skills"
              :key="skill"
              closable
              @close="removeSkill(skill)"
              style="margin-right: 8px; margin-bottom: 8px;"
              :type="getSkillType(skill)"
            >
              {{ skill }}
            </el-tag>
            <el-input
              v-if="inputVisible"
              ref="skillInput"
              v-model="inputValue"
              size="small"
              style="width: 120px;"
              @keyup.enter="handleInputConfirm"
              @blur="handleInputConfirm"
            />
            <el-button v-else size="small" @click="showInput">+ 添加技能</el-button>
          </div>
        </el-form-item>

        <!-- 工作经验 -->
        <el-divider content-position="left">工作经验</el-divider>
        <el-form-item label="工作经验">
          <div v-for="(exp, index) in userProfile.experience" :key="index" class="experience-item">
            <el-row :gutter="10">
              <el-col :span="6">
                <el-input v-model="exp.company" placeholder="公司名称" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="exp.position" placeholder="职位名称" />
              </el-col>
              <el-col :span="8">
                <el-date-picker
                  v-model="exp.duration_dates"
                  type="monthrange"
                  range-separator="至"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  format="YYYY-MM"
                  value-format="YYYY-MM"
                  @change="updateDuration(index)"
                />
              </el-col>
              <el-col :span="2">
                <el-checkbox v-model="exp.is_current" @change="updateDuration(index)">至今</el-checkbox>
              </el-col>
              <el-col :span="2">
                <el-button type="danger" size="small" @click="removeExperience(index)">删除</el-button>
              </el-col>
            </el-row>
            
            <el-input
              v-model="exp.description"
              type="textarea"
              placeholder="详细描述工作内容、职责和主要成果"
              style="margin-top: 8px; margin-bottom: 8px;"
              :rows="3"
            />
            
            <!-- 工作成就 -->
            <div class="achievements-section">
              <el-text size="small" style="margin-bottom: 8px; display: block;">主要成就：</el-text>
              <div v-for="(achievement, achIndex) in exp.achievements" :key="achIndex" class="achievement-item">
                <el-input
                  v-model="exp.achievements[achIndex]"
                  placeholder="具体成就或亮点"
                  style="margin-bottom: 4px;"
                >
                  <template #append>
                    <el-button @click="removeAchievement(index, achIndex)" size="small">删除</el-button>
                  </template>
                </el-input>
              </div>
              <el-button @click="addAchievement(index)" size="small" type="primary">添加成就</el-button>
            </div>
          </div>
          <el-button @click="addExperience" type="primary" size="small">添加工作经验</el-button>
        </el-form-item>

        <!-- 教育背景 -->
        <el-divider content-position="left">教育背景</el-divider>
        <el-form-item label="教育经历">
          <div v-for="(edu, index) in userProfile.education" :key="index" class="education-item">
            <el-row :gutter="10">
              <el-col :span="6">
                <el-input v-model="edu.school" placeholder="学校名称" />
              </el-col>
              <el-col :span="4">
                <el-select v-model="edu.degree" placeholder="学历">
                  <el-option label="专科" value="专科" />
                  <el-option label="本科" value="本科" />
                  <el-option label="硕士" value="硕士" />
                  <el-option label="博士" value="博士" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-input v-model="edu.major" placeholder="专业名称" />
              </el-col>
              <el-col :span="4">
                <el-input v-model="edu.gpa" placeholder="GPA(可选)" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" size="small" @click="removeEducation(index)">删除</el-button>
              </el-col>
            </el-row>
            <el-row :gutter="10" style="margin-top: 8px;">
              <el-col :span="8">
                <el-date-picker
                  v-model="edu.duration_dates"
                  type="monthrange"
                  range-separator="至"
                  start-placeholder="入学时间"
                  end-placeholder="毕业时间"
                  format="YYYY-MM"
                  value-format="YYYY-MM"
                  @change="updateEducationDuration(index)"
                />
              </el-col>
            </el-row>
          </div>
          <el-button @click="addEducation" type="primary" size="small">添加教育经历</el-button>
        </el-form-item>

        <!-- 项目经验 -->
        <el-divider content-position="left">项目经验</el-divider>
        <el-form-item label="项目经历">
          <div v-for="(project, index) in userProfile.projects" :key="index" class="project-item">
            <el-row :gutter="10">
              <el-col :span="12">
                <el-input v-model="project.name" placeholder="项目名称" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="project.duration" placeholder="项目周期 如：2023.06-2023.12" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" size="small" @click="removeProject(index)">删除</el-button>
              </el-col>
            </el-row>
            
            <el-input
              v-model="project.description"
              type="textarea"
              placeholder="项目描述、您的角色和主要贡献"
              style="margin: 8px 0;"
              :rows="2"
            />
            
            <!-- 项目技术栈 -->
            <div class="project-tech-section">
              <el-text size="small" style="margin-bottom: 8px; display: block;">技术栈：</el-text>
              <el-tag
                v-for="tech in project.technologies"
                :key="tech"
                closable
                @close="removeProjectTech(index, tech)"
                style="margin-right: 8px; margin-bottom: 4px;"
                size="small"
              >
                {{ tech }}
              </el-tag>
              <el-input
                v-if="project.techInputVisible"
                :ref="`projectTechInput${index}`"
                v-model="project.techInputValue"
                size="small"
                style="width: 100px;"
                @keyup.enter="handleProjectTechConfirm(index)"
                @blur="handleProjectTechConfirm(index)"
              />
              <el-button v-else size="small" @click="showProjectTechInput(index)">+ 技术</el-button>
            </div>

            <!-- 项目成果 -->
            <div class="project-achievements-section" style="margin-top: 8px;">
              <el-text size="small" style="margin-bottom: 8px; display: block;">项目成果：</el-text>
              <div v-for="(achievement, achIndex) in project.achievements" :key="achIndex">
                <el-input
                  v-model="project.achievements[achIndex]"
                  placeholder="项目成果或亮点"
                  size="small"
                  style="margin-bottom: 4px;"
                >
                  <template #append>
                    <el-button @click="removeProjectAchievement(index, achIndex)" size="small">删除</el-button>
                  </template>
                </el-input>
              </div>
              <el-button @click="addProjectAchievement(index)" size="small" type="primary">添加成果</el-button>
            </div>
          </div>
          <el-button @click="addProject" type="primary" size="small">添加项目经验</el-button>
        </el-form-item>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="语言能力">
              <el-input v-model="userProfile.languages" placeholder="如：英语CET-6，日语N2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职业证书">
              <el-input v-model="userProfile.certifications" placeholder="如：PMP，AWS认证等" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="特殊要求">
          <el-input 
            v-model="userProfile.special_requirements" 
            type="textarea" 
            placeholder="针对此职位的特殊说明或定制要求"
            :rows="2"
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            @click="generateAllResumes"
            :loading="isGeneratingAll"
            size="large"
          >
            <el-icon><Star /></el-icon>
            生成所有简历 ({{ selectedJobs.length }})
          </el-button>
          
          <el-button 
            @click="generateSingleResume"
            :loading="isGeneratingSingle"
            :disabled="activeJobIndex === -1"
            size="large"
          >
            生成当前职位简历
          </el-button>
          
          <el-button @click="loadDemoProfile" type="success" size="large">
            <el-icon><User /></el-icon>
            加载示例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 显示选择的职位 -->
    <el-card v-if="selectedJobs.length > 0" class="selected-jobs-card">
      <template #header>
        <h3>选择的职位 ({{ selectedJobs.length }} 个)</h3>
      </template>
      
      <div class="jobs-overview">
        <div 
          v-for="(job, index) in selectedJobs" 
          :key="index"
          class="job-overview-item"
          :class="{ 'active': activeJobIndex === index }"
          @click="setActiveJob(index)"
        >
          <h5>{{ job.job_title }}</h5>
          <p>{{ job.company_name }}</p>
          <el-tag 
            :type="getResumeStatus(index) === 'generated' ? 'success' : 
                   getResumeStatus(index) === 'generating' ? 'warning' : 'info'"
            size="small"
          >
            {{ getResumeStatusText(index) }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 生成进度显示 -->
    <el-card v-if="isGeneratingAll || isGeneratingSingle" class="generation-progress-card">
      <div class="generation-progress">
        <h4>正在生成简历...</h4>
        <el-progress 
          :percentage="generationProgress" 
          :status="generationProgress === 100 ? 'success' : 'active'"
        />
        <p>{{ currentGeneratingJob }}</p>
      </div>
    </el-card>

    <!-- 修复后的简历显示区 -->
    <div v-if="Object.keys(generatedResumes).length > 0" class="resumes-container">
      <h3>生成的简历 ({{ Object.keys(generatedResumes).length }} 份)</h3>
      
      <!-- 操作提示 -->
      <el-alert
        title="简历已生成"
        description="您可以查看下方生成的简历，下载专业Word文档或进行优化操作"
        type="success"
        show-icon
        :closable="false"
        style="margin-bottom: 16px;"
      />
      

      
      <!-- 简历展示区域 - 折叠面板模式 -->
      <div class="resumes-collapse-display">
        <!-- 显示提示信息 -->
        <el-alert
          title="📋 简历折叠面板"
          :description="`共生成 ${Object.keys(generatedResumes).length} 份简历，点击标题展开查看内容`"
          type="success"
          style="margin-bottom: 20px;"
        />
        
        <!-- 折叠面板操作按钮 -->
        <div style="margin-bottom: 16px; text-align: center;">
          <el-button-group>
            <el-button 
              size="small" 
              type="primary"
              @click="expandAllResumes"
              :icon="View"
            >
              展开全部
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="collapseAllResumes"
              :icon="Loading"
            >
              收起全部
            </el-button>
          </el-button-group>
        </div>
        
        <!-- 简历折叠面板 -->
        <el-collapse v-model="activeResumeKeys" accordion>
          <el-collapse-item 
            v-for="(job, index) in selectedJobs" 
            :key="index"
            :name="index.toString()"
            v-show="generatedResumes[index]"
          >
            <!-- 折叠面板标题 -->
            <template #title>
              <div class="resume-collapse-title">
                <div class="job-info">
                  <h3>{{ job.job_title }} - {{ job.company_name }}</h3>
                  <p>{{ job.location || '位置未知' }} | {{ job.salary_range || '薪资面议' }}</p>
                </div>
                <div class="resume-meta">
                  <el-tag type="success" size="small" style="margin-right: 8px;">
                    匹配度: {{ getMatchScore(index) }}%
                  </el-tag>
                  <el-tag :type="getResumeStatus(index) === 'generated' ? 'success' : 'info'" size="small">
                    {{ getResumeStatusText(index) }}
                  </el-tag>
                  <!-- 优化标识 -->
                  <el-tag v-if="getOptimizationCount(index) > 0" type="warning" size="small" style="margin-left: 8px;">
                    已优化 {{ getOptimizationCount(index) }} 次
                  </el-tag>
                </div>
              </div>
            </template>
            
            <!-- 折叠面板内容 -->
            <div class="resume-collapse-content">
              <!-- 操作按钮 -->
              <div class="resume-actions-bar" style="margin-bottom: 16px; text-align: right;">
                <el-button-group>
                  <el-button 
                    size="small" 
                    type="primary"
                    @click="downloadResume(index)"
                    :icon="Document"
                  >
                    下载Word简历
                  </el-button>
                  <el-button 
                    size="small" 
                    type="info"
                    @click="editResume(index)"
                    :icon="User"
                  >
                    编辑简历
                  </el-button>
                  <!-- 新增：查看优化历史按钮 -->
                  <el-button 
                    v-if="getOptimizationCount(index) > 0"
                    size="small" 
                    type="success"
                    @click="showOptimizationHistory(index)"
                    :icon="View"
                  >
                    优化历史 ({{ getOptimizationCount(index) }})
                  </el-button>
                </el-button-group>
              </div>
              
              <!-- 优化历史标签页 -->
              <div v-if="getOptimizationCount(index) > 0" class="optimization-tabs">
                <el-tabs v-model="activeOptimizationTab[index]" type="card" style="margin-bottom: 20px;">
                  <el-tab-pane label="当前简历" name="current">
                    <div class="resume-content-wrapper" :data-resume-index="index">
                      <ResumeDisplay 
                        :resume-data="generatedResumes[index]" 
                        :job-info="job"
                        @edit="editResume(index)"
                        @optimize="optimizeResume(index)"
                      />
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="原始简历" name="original">
                    <div class="resume-content-wrapper">
                      <ResumeDisplay 
                        :resume-data="getOriginalResume(index)" 
                        :job-info="job"
                        :is-readonly="true"
                      />
                    </div>
                  </el-tab-pane>
                  <el-tab-pane 
                    v-for="(optimization, optIndex) in getOptimizationHistoryForJob(index)" 
                    :key="`opt-${optIndex}`"
                    :label="`第${optIndex + 1}次优化`" 
                    :name="`optimization-${optIndex}`"
                  >
                    <div class="optimization-info">
                      <el-alert
                        :title="`优化时间：${new Date(optimization.timestamp).toLocaleString()}`"
                        :description="`基于HR评分 ${optimization.feedback?.feedback?.overall_score || 'N/A'} 分的反馈进行优化`"
                        type="info"
                        :closable="false"
                        style="margin-bottom: 16px;"
                      />
                      
                      <!-- 优化详细信息 -->
                      <div class="optimization-details" style="margin-bottom: 20px;">
                        <el-collapse>
                          <el-collapse-item title="📝 本次优化的具体修改内容，可点击展开查看" name="modifications">
                            <div class="optimization-summary">
                              <!-- 优化重点 -->
                              <div v-if="optimization.optimizationSummary?.optimization_focus" class="optimization-section">
                                <h4>🎯 优化重点</h4>
                                <ul>
                                  <li v-for="focus in optimization.optimizationSummary.optimization_focus" :key="focus">
                                    {{ focus }}
                                  </li>
                                </ul>
                              </div>
                              
                              <!-- 主要改进 -->
                              <div v-if="optimization.optimizationSummary?.expected_improvements" class="optimization-section">
                                <h4>✨ 主要改进</h4>
                                <ul>
                                  <li v-for="improvement in optimization.optimizationSummary.expected_improvements" :key="improvement">
                                    {{ improvement }}
                                  </li>
                                </ul>
                              </div>
                              
                              <!-- 目标改进要点 -->
                              <div v-if="optimization.optimizationSummary?.target_improvements" class="optimization-section">
                                <h4>📈 目标改进要点</h4>
                                <ul>
                                  <li v-for="target in optimization.optimizationSummary.target_improvements" :key="target">
                                    {{ target }}
                                  </li>
                                </ul>
                              </div>
                              
                              <!-- 优化评分信息 -->
                              <div v-if="optimization.optimizationSummary?.original_score" class="optimization-section">
                                <h4>📊 优化评分信息</h4>
                                <div class="stats-grid">
                                  <div class="stat-item">
                                    <span class="stat-label">优化前评分：</span>
                                    <span class="stat-value">{{ optimization.optimizationSummary.original_score }}分</span>
                                  </div>
                                  <div v-if="optimization.feedback?.feedback?.overall_score" class="stat-item">
                                    <span class="stat-label">HR反馈评分：</span>
                                    <span class="stat-value">{{ optimization.feedback.feedback.overall_score }}分</span>
                                  </div>
                                  <div class="stat-item">
                                    <span class="stat-label">优化类型：</span>
                                    <span class="stat-value">{{ getOptimizationTypeName(optimization.optimizationSummary) }}</span>
                                  </div>
                                </div>
                              </div>
                              
                              <!-- HR反馈要点 -->
                              <div v-if="optimization.feedback?.feedback" class="optimization-section">
                                <h4>💬 基于的HR反馈要点</h4>
                                <div class="hr-feedback-summary">
                                  <div v-if="optimization.feedback.feedback.improvement_suggestions" class="feedback-item">
                                    <span class="feedback-label">改进建议：</span>
                                    <ul>
                                      <li v-for="suggestion in optimization.feedback.feedback.improvement_suggestions" :key="suggestion">
                                        {{ suggestion }}
                                      </li>
                                    </ul>
                                  </div>
                                  <div v-if="optimization.feedback.feedback.missing_keywords" class="feedback-item">
                                    <span class="feedback-label">缺失关键词：</span>
                                    <el-tag 
                                      v-for="keyword in optimization.feedback.feedback.missing_keywords" 
                                      :key="keyword" 
                                      size="small" 
                                      type="warning"
                                      style="margin: 2px;"
                                    >
                                      {{ keyword }}
                                    </el-tag>
                                  </div>
                                  <div v-if="optimization.feedback.feedback.strengths" class="feedback-item">
                                    <span class="feedback-label">简历优势：</span>
                                    <ul>
                                      <li v-for="strength in optimization.feedback.feedback.strengths" :key="strength">
                                        {{ strength }}
                                      </li>
                                    </ul>
                                  </div>
                                </div>
                              </div>
                              
                              <!-- 无详细信息时的提示 -->
                              <div v-if="!optimization.optimizationSummary" class="optimization-section">
                                <el-alert
                                  title="优化信息不完整"
                                  description="此版本的优化记录缺少详细信息，但简历内容已根据HR反馈进行了相应调整。"
                                  type="info"
                                  :closable="false"
                                />
                              </div>
                            </div>
                          </el-collapse-item>
                        </el-collapse>
                      </div>
                    </div>
                    <div class="resume-content-wrapper">
                      <ResumeDisplay 
                        :resume-data="optimization.optimizedResume" 
                        :job-info="job"
                        :is-readonly="true"
                      />
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
              
              <!-- 简历内容显示（无优化历史时） -->
              <div v-else-if="generatedResumes[index]" class="resume-content-wrapper" :data-resume-index="index">
                <ResumeDisplay 
                  :resume-data="generatedResumes[index]" 
                  :job-info="job"
                  @edit="editResume(index)"
                  @optimize="optimizeResume(index)"
                />
              </div>
              
              <!-- 数据不存在时的提示 -->
              <el-empty 
                v-else
                description="简历数据加载中或不存在"
                :image-size="100"
              />
            </div>
          </el-collapse-item>
        </el-collapse>
        
        <!-- 没有生成简历时的提示 -->
        <el-empty 
          v-if="Object.keys(generatedResumes).length === 0"
          description="还没有生成简历，请先填写个人信息并选择职位生成简历"
          :image-size="200"
        />
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <el-card v-if="Object.keys(generatedResumes).length > 0" class="actions-card">
      <div class="bottom-actions">
        <el-button 
          type="warning" 
          size="large"
          @click="proceedToPhase3"
        >
          进入HR评估 ({{ Object.keys(generatedResumes).length }} 份简历)
        </el-button>
      </div>
    </el-card>
    
    <!-- 简历编辑模态框 -->
    <el-dialog
      v-model="showEditMode"
      title="编辑简历"
      width="85%"
      :close-on-click-modal="false"
      class="resume-edit-modal"
    >
      <div v-if="editingResume && Object.keys(editingResume).length > 0" class="edit-content">
        <el-tabs v-model="activeEditTab" class="edit-tabs">
          <!-- 个人信息编辑 -->
          <el-tab-pane label="个人信息" name="personal">
            <el-card>
              <el-form label-width="100px">
                <el-row :gutter="20" v-if="editingResume.personal_info">
                  <el-col :span="8">
                    <el-form-item label="姓名">
                      <el-input v-model="editingResume.personal_info.name" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="邮箱">
                      <el-input v-model="editingResume.personal_info.email" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="电话">
                      <el-input v-model="editingResume.personal_info.phone" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="地址" v-if="editingResume.personal_info">
                  <el-input v-model="editingResume.personal_info.location" />
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <!-- 个人简介编辑 -->
          <el-tab-pane label="个人简介" name="summary">
            <el-card v-if="editingResume.professional_summary">
              <el-input
                v-model="editingResume.professional_summary"
                type="textarea"
                :rows="6"
                placeholder="请输入个人简介"
              />
            </el-card>
          </el-tab-pane>
          
          <!-- 核心竞争力编辑 -->
          <el-tab-pane label="核心竞争力" name="competencies">
            <el-card v-if="editingResume.core_competencies">
              <div class="edit-tags-section">
                <el-tag
                  v-for="(competency, index) in editingResume.core_competencies"
                  :key="index"
                  closable
                  @close="editingResume.core_competencies.splice(index, 1)"
                  style="margin-right: 8px; margin-bottom: 8px;"
                  size="large"
                >
                  {{ competency }}
                </el-tag>
                <el-input
                  v-if="newCompetencyVisible"
                  ref="newCompetencyInput"
                  v-model="newCompetencyValue"
                  size="small"
                  style="width: 150px;"
                  @keyup.enter="addNewCompetency"
                  @blur="addNewCompetency"
                />
                <el-button v-else size="small" @click="showNewCompetencyInput">+ 添加竞争力</el-button>
              </div>
            </el-card>
          </el-tab-pane>
          
          <!-- 技能编辑 -->
          <el-tab-pane label="技能" name="skills">
            <el-card v-if="editingResume.highlighted_skills">
              <!-- 技术技能 -->
              <div v-if="editingResume.highlighted_skills.technical_skills" class="skill-edit-section">
                <h4>技术技能</h4>
                <div class="edit-tags-section">
                  <el-tag
                    v-for="(skill, index) in editingResume.highlighted_skills.technical_skills"
                    :key="index"
                    closable
                    @close="editingResume.highlighted_skills.technical_skills.splice(index, 1)"
                    style="margin-right: 8px; margin-bottom: 8px;"
                    type="primary"
                  >
                    {{ skill }}
                  </el-tag>
                  <el-input
                    v-if="newTechSkillVisible"
                    ref="newTechSkillInput"
                    v-model="newTechSkillValue"
                    size="small"
                    style="width: 120px;"
                    @keyup.enter="addNewTechSkill"
                    @blur="addNewTechSkill"
                  />
                  <el-button v-else size="small" @click="showNewTechSkillInput">+ 添加技术技能</el-button>
                </div>
              </div>
              
              <!-- 框架和工具 -->
              <div v-if="editingResume.highlighted_skills.frameworks_and_tools" class="skill-edit-section">
                <h4>框架和工具</h4>
                <div class="edit-tags-section">
                  <el-tag
                    v-for="(tool, index) in editingResume.highlighted_skills.frameworks_and_tools"
                    :key="index"
                    closable
                    @close="editingResume.highlighted_skills.frameworks_and_tools.splice(index, 1)"
                    style="margin-right: 8px; margin-bottom: 8px;"
                    type="warning"
                  >
                    {{ tool }}
                  </el-tag>
                  <el-input
                    v-if="newToolVisible"
                    ref="newToolInput"
                    v-model="newToolValue"
                    size="small"
                    style="width: 120px;"
                    @keyup.enter="addNewTool"
                    @blur="addNewTool"
                  />
                  <el-button v-else size="small" @click="showNewToolInput">+ 添加工具</el-button>
                </div>
              </div>
              
              <!-- 软技能 -->
              <div v-if="editingResume.highlighted_skills.soft_skills" class="skill-edit-section">
                <h4>软技能</h4>
                <div class="edit-tags-section">
                  <el-tag
                    v-for="(skill, index) in editingResume.highlighted_skills.soft_skills"
                    :key="index"
                    closable
                    @close="editingResume.highlighted_skills.soft_skills.splice(index, 1)"
                    style="margin-right: 8px; margin-bottom: 8px;"
                    type="success"
                  >
                    {{ skill }}
                  </el-tag>
                  <el-input
                    v-if="newSoftSkillVisible"
                    ref="newSoftSkillInput"
                    v-model="newSoftSkillValue"
                    size="small"
                    style="width: 120px;"
                    @keyup.enter="addNewSoftSkill"
                    @blur="addNewSoftSkill"
                  />
                  <el-button v-else size="small" @click="showNewSoftSkillInput">+ 添加软技能</el-button>
                </div>
              </div>
            </el-card>
          </el-tab-pane>
          
          <!-- 教育背景编辑 -->
          <el-tab-pane label="教育背景" name="education">
            <el-card v-if="editingResume.education">
              <div v-for="(edu, index) in editingResume.education" :key="index" class="edit-experience-item">
                <el-divider>教育经历 {{ index + 1 }}</el-divider>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="学校名称">
                      <el-input v-model="edu.institution" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="学历">
                      <el-select v-model="edu.degree" placeholder="选择学历">
                        <el-option label="专科" value="专科" />
                        <el-option label="本科" value="本科" />
                        <el-option label="硕士" value="硕士" />
                        <el-option label="博士" value="博士" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="专业">
                      <el-input v-model="edu.major" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item label="就读时间">
                      <el-input v-model="edu.duration" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item label="GPA">
                      <el-input v-model="edu.gpa" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="地点">
                  <el-input v-model="edu.location" />
                </el-form-item>
                <el-button type="danger" size="small" @click="removeEducationFromResume(index)">删除这条教育经历</el-button>
              </div>
              <el-button type="primary" @click="addEducationToResume">+ 添加教育经历</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 工作经验编辑 -->
          <el-tab-pane label="工作经验" name="experience">
            <el-card v-if="editingResume.professional_experience">
              <div v-for="(exp, index) in editingResume.professional_experience" :key="index" class="edit-experience-item">
                <el-divider>工作经验 {{ index + 1 }}</el-divider>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="公司名称">
                      <el-input v-model="exp.company" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="职位">
                      <el-input v-model="exp.position" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="工作时间">
                      <el-input v-model="exp.duration" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="地点">
                      <el-input v-model="exp.location" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="工作描述">
                  <el-input v-model="exp.description" type="textarea" :rows="3" />
                </el-form-item>
                
                <!-- 工作职责 -->
                <div v-if="exp.responsibilities" class="responsibilities-edit">
                  <h5>工作职责</h5>
                  <div v-for="(resp, respIndex) in exp.responsibilities" :key="respIndex" class="list-item-edit">
                    <el-input v-model="exp.responsibilities[respIndex]" style="margin-bottom: 8px;">
                      <template #append>
                        <el-button @click="exp.responsibilities.splice(respIndex, 1)" size="small" type="danger">删除</el-button>
                      </template>
                    </el-input>
                  </div>
                  <el-button size="small" @click="exp.responsibilities.push('')">+ 添加职责</el-button>
                </div>
                
                <!-- 关键成就 -->
                <div v-if="exp.achievements" class="achievements-edit">
                  <h5>关键成就</h5>
                  <div v-for="(ach, achIndex) in exp.achievements" :key="achIndex" class="list-item-edit">
                    <el-input v-model="exp.achievements[achIndex]" style="margin-bottom: 8px;">
                      <template #append>
                        <el-button @click="exp.achievements.splice(achIndex, 1)" size="small" type="danger">删除</el-button>
                      </template>
                    </el-input>
                  </div>
                  <el-button size="small" @click="exp.achievements.push('')">+ 添加成就</el-button>
                </div>
                
                <el-button type="danger" size="small" @click="removeWorkExperience(index)">删除这条工作经验</el-button>
              </div>
              <el-button type="primary" @click="addWorkExperience">+ 添加工作经验</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 项目经验编辑 -->
          <el-tab-pane label="项目经验" name="projects">
            <el-card v-if="editingResume.key_projects">
              <div v-for="(project, index) in editingResume.key_projects" :key="index" class="edit-experience-item">
                <el-divider>项目经验 {{ index + 1 }}</el-divider>
                <el-row :gutter="10">
                  <el-col :span="16">
                    <el-form-item label="项目名称">
                      <el-input v-model="project.name" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="项目时间">
                      <el-input v-model="project.duration" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="项目描述">
                  <el-input v-model="project.description" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item label="我的角色">
                  <el-input v-model="project.role" />
                </el-form-item>
                
                <!-- 技术栈 -->
                <div v-if="project.technologies_used" class="tech-edit-section">
                  <h5>技术栈</h5>
                  <div class="edit-tags-section">
                    <el-tag
                      v-for="(tech, techIndex) in project.technologies_used"
                      :key="techIndex"
                      closable
                      @close="project.technologies_used.splice(techIndex, 1)"
                      style="margin-right: 8px; margin-bottom: 8px;"
                      type="info"
                    >
                      {{ tech }}
                    </el-tag>
                    <el-input
                      v-if="project.newTechVisible"
                      v-model="project.newTechValue"
                      size="small"
                      style="width: 120px;"
                      @keyup.enter="addProjectTechToResume(index)"
                      @blur="addProjectTechToResume(index)"
                    />
                    <el-button v-else size="small" @click="showProjectTechInputInResume(index)">+ 添加技术</el-button>
                  </div>
                </div>
                
                <!-- 项目成果 -->
                <div v-if="project.outcomes" class="outcomes-edit">
                  <h5>项目成果</h5>
                  <div v-for="(outcome, outIndex) in project.outcomes" :key="outIndex" class="list-item-edit">
                    <el-input v-model="project.outcomes[outIndex]" style="margin-bottom: 8px;">
                      <template #append>
                        <el-button @click="project.outcomes.splice(outIndex, 1)" size="small" type="danger">删除</el-button>
                      </template>
                    </el-input>
                  </div>
                  <el-button size="small" @click="project.outcomes.push('')">+ 添加成果</el-button>
                </div>
                
                <el-button type="danger" size="small" @click="removeProjectFromResume(index)">删除这个项目</el-button>
              </div>
              <el-button type="primary" @click="addProjectToResume">+ 添加项目经验</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 认证证书编辑 -->
          <el-tab-pane label="认证证书" name="certifications">
            <el-card v-if="editingResume.certifications">
              <div v-for="(cert, index) in editingResume.certifications" :key="index" class="edit-experience-item">
                <el-divider>证书 {{ index + 1 }}</el-divider>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="证书名称">
                      <el-input v-model="cert.name" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="颁发机构">
                      <el-input v-model="cert.issuer" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="获得日期">
                      <el-input v-model="cert.date" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="有效期">
                      <el-input v-model="cert.validity" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="证书ID">
                  <el-input v-model="cert.credential_id" />
                </el-form-item>
                <el-button type="danger" size="small" @click="removeCertification(index)">删除证书</el-button>
              </div>
              <el-button type="primary" @click="addCertification">+ 添加证书</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 语言能力编辑 -->
          <el-tab-pane label="语言能力" name="languages">
            <el-card v-if="editingResume.languages">
              <div v-for="(lang, index) in editingResume.languages" :key="index" class="edit-experience-item">
                <el-divider>语言 {{ index + 1 }}</el-divider>
                <el-row :gutter="10">
                  <el-col :span="8">
                    <el-form-item label="语言">
                      <el-input v-model="lang.language" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="熟练程度">
                      <el-select v-model="lang.proficiency" placeholder="选择熟练程度">
                        <el-option label="母语" value="母语" />
                        <el-option label="精通" value="精通" />
                        <el-option label="流利" value="流利" />
                        <el-option label="良好" value="良好" />
                        <el-option label="基础" value="基础" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="证书">
                      <el-input v-model="lang.certification" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-button type="danger" size="small" @click="removeLanguage(index)">删除语言</el-button>
              </div>
              <el-button type="primary" @click="addLanguage">+ 添加语言</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 职业发展编辑 -->
          <el-tab-pane label="职业发展" name="development">
            <el-card v-if="editingResume.professional_development">
              <div v-for="(dev, index) in editingResume.professional_development" :key="index" class="list-item-edit">
                <el-input v-model="editingResume.professional_development[index]" style="margin-bottom: 8px;">
                  <template #append>
                    <el-button @click="editingResume.professional_development.splice(index, 1)" size="small" type="danger">删除</el-button>
                  </template>
                </el-input>
              </div>
              <el-button type="primary" @click="editingResume.professional_development.push('')">+ 添加发展项目</el-button>
            </el-card>
          </el-tab-pane>
          
          <!-- 附加信息编辑 -->
          <el-tab-pane label="附加信息" name="additional">
            <el-card v-if="editingResume.additional_information">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="到岗时间">
                    <el-input v-model="editingResume.additional_information.availability" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="期望薪资">
                    <el-input v-model="editingResume.additional_information.salary_expectation" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="工作偏好">
                    <el-input v-model="editingResume.additional_information.work_preference" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="搬迁意愿">
                    <el-input v-model="editingResume.additional_information.relocation_willingness" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="出差安排">
                <el-input v-model="editingResume.additional_information.travel_availability" />
              </el-form-item>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="saveEditedResume">保存修改</el-button>
        </span>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, User, View, Loading, Star } from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'
import ResumeDisplay from './ResumeDisplay.vue'

export default {
  name: 'Phase2',
  components: {
    Document,
    Star,
    User,
    View,
    Loading,
    ResumeDisplay
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    
    // 原有的用户信息相关状态
    const userProfile = reactive({
      full_name: '',
      email: '',
      phone: '',
      location: '',
      target_position: '',
      summary: '',
      skills: [],
      experience: [],
      education: [],
      projects: [],
      languages: '',
      certifications: '',
      special_requirements: ''
    })
    
    // 新增的多职位简历相关状态
    const selectedJobs = ref([])
    const activeJobIndex = ref(-1)
    const generatedResumes = ref({}) // 存储生成的简历 {jobIndex: resumeData}
    const resumeStatus = ref({}) // 存储简历状态 {jobIndex: 'pending'|'generating'|'generated'|'error'}
    const activeResumeKeys = ref([]) // 控制折叠面板展开状态
    
    // 新增：优化历史相关状态
    const optimizationHistory = ref({}) // 存储每个职位的优化历史 {jobIndex: [optimizations]}
    const activeOptimizationTab = ref({}) // 控制每个职位的优化标签页 {jobIndex: 'current'|'original'|'optimization-0'}
    const originalResumes = ref({}) // 存储原始简历 {jobIndex: resumeData}
    
    // 编辑相关状态
    const showEditMode = ref(false)
    const editingIndex = ref(-1)
    const editingResume = ref({})
    const activeEditTab = ref('personal')
    
    // 各种编辑状态
    const newCompetencyVisible = ref(false)
    const newCompetencyValue = ref('')
    const newCompetencyInput = ref(null)
    
    const newTechSkillVisible = ref(false)
    const newTechSkillValue = ref('')
    const newTechSkillInput = ref(null)
    
    const newToolVisible = ref(false)
    const newToolValue = ref('')
    const newToolInput = ref(null)
    
    const newSoftSkillVisible = ref(false)
    const newSoftSkillValue = ref('')
    const newSoftSkillInput = ref(null)
    
    // 生成相关状态
    const isGeneratingAll = ref(false)
    const isGeneratingSingle = ref(false)
    const generationProgress = ref(0)
    const currentGeneratingJob = ref('')
    
    // 原有状态
    const inputVisible = ref(false)
    const inputValue = ref('')
    const skillInput = ref(null)
    
    // 表单验证规则
    const formRules = {
      full_name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 页面加载时获取选择的职位并检查是否从Phase3优化过来
    onMounted(() => {
      // 检查是否从Phase3优化过来
      const fromOptimization = localStorage.getItem('fromPhase3Optimization')
      if (fromOptimization) {
        console.log('检测到从Phase3优化返回，加载完整历史数据')
        
        // 加载用户信息
        const savedProfile = localStorage.getItem('userProfile')
        if (savedProfile) {
          try {
            const profileData = JSON.parse(savedProfile)
            Object.assign(userProfile, profileData)
            console.log('已加载保存的用户信息')
          } catch (e) {
            console.warn('加载用户信息失败:', e)
          }
        }
        
        // 处理优化数据
        const optimizationData = JSON.parse(fromOptimization)
        handleOptimizationFromPhase3(optimizationData)
        
        // 加载已生成的简历
        loadExistingResumes()
        
        // 清除标识
        localStorage.removeItem('fromPhase3Optimization')
        return
      }
      
      // 检查是否从Phase1进入（正常流程）
      console.log('检测到从Phase1进入，清空历史数据开始新流程')
      
      // 清空用户表单数据（从Phase1进入时重新开始）
      Object.assign(userProfile, {
        full_name: '',
        email: '',
        phone: '',
        location: '',
        target_position: '',
        summary: '',
        skills: [],
        experience: [],
        education: [],
        projects: [],
        languages: '',
        certifications: '',
        special_requirements: ''
      })
      
      // 清空简历相关数据
      generatedResumes.value = {}
      resumeStatus.value = {}
      optimizationHistory.value = {}
      originalResumes.value = {}
      activeResumeKeys.value = []
      
      console.log('已清空表单和简历数据')
      
      // 加载选择的职位（从Phase1传来的）
      const selectedJobsStr = localStorage.getItem('selectedJobs')
      if (selectedJobsStr) {
        selectedJobs.value = JSON.parse(selectedJobsStr)
        console.log('已加载从Phase1选择的职位:', selectedJobs.value.length, '个')
        
        // 初始化简历状态为待生成
        selectedJobs.value.forEach((_, index) => {
          resumeStatus.value[index] = 'pending'
        })
        
        if (selectedJobs.value.length > 0) {
          activeJobIndex.value = 0
        }
      }
      
      // 设置自动保存机制（仅在用户开始编辑后保存）
      const saveUserProfile = () => {
        // 只有在用户有输入内容时才保存
        if (userProfile.full_name || userProfile.email) {
          localStorage.setItem('userProfile', JSON.stringify(userProfile))
        }
      }
      
      // 定时保存用户信息（每5秒保存一次）
      setInterval(saveUserProfile, 5000)
      
      // 监听beforeunload事件确保离开页面时保存
      window.addEventListener('beforeunload', saveUserProfile)
    })
    
    // 处理从Phase3优化过来的情况
    const handleOptimizationFromPhase3 = (optimizationData) => {
      try {
        const { resumeId, feedback, optimizationData: data } = optimizationData
        
        // 显示优化成功信息
        ElMessage.success('简历优化完成！可以对比查看原简历和优化后的简历')
        
        // 加载对应的职位信息
        const selectedJobsStr = localStorage.getItem('selectedJobs')
        if (selectedJobsStr) {
          selectedJobs.value = JSON.parse(selectedJobsStr)
        }
        
        // 加载原始简历
        const originalResumeKey = `original_resume_${resumeId}`
        const originalResumeStr = localStorage.getItem(originalResumeKey)
        if (originalResumeStr) {
          const originalData = JSON.parse(originalResumeStr)
          
          // 找到对应的简历索引
          const resumeIndex = Object.keys(selectedJobs.value).find(index => 
            selectedJobs.value[index].id === resumeId || index === resumeId
          ) || resumeId
          
          // 保存原始简历
          originalResumes.value[resumeIndex] = originalData.content
          localStorage.setItem('originalResumes', JSON.stringify(originalResumes.value))
          
          // 保存优化历史
          const optimizationRecord = {
            timestamp: originalData.optimizationTime || new Date().toISOString(),
            feedback: feedback,
            optimizedResume: data.content,
            optimizationSummary: data.optimization_summary || {},
            originalScore: feedback.feedback?.overall_score || 0
          }
          
          saveOptimizationHistory(resumeIndex, optimizationRecord)
        }
        
        // 加载优化后的简历
        const resumesStr = localStorage.getItem('generatedResumes')
        if (resumesStr) {
          const resumes = JSON.parse(resumesStr)
          generatedResumes.value = resumes
          
          // 找到对应的简历索引
          const resumeIndex = Object.keys(resumes).indexOf(resumeId)
          if (resumeIndex >= 0) {
            activeJobIndex.value = resumeIndex
            
            // 初始化优化标签页为当前简历
            activeOptimizationTab.value[resumeIndex] = 'current'
            
            // 自动展开对应的简历
            setTimeout(() => {
              activeResumeKeys.value = [resumeIndex.toString()]
            }, 500)
          }
        }
        
        // 加载优化历史
        loadOptimizationHistory()
        
        // 加载原简历供对比 - 使用前面已声明的 originalResumeKey
        const originalResumeStr2 = localStorage.getItem(originalResumeKey)
        if (originalResumeStr2) {
          const originalData2 = JSON.parse(originalResumeStr2)
          
          // 显示对比提示
          setTimeout(() => {
            ElMessageBox.confirm(
              `简历已根据HR反馈进行优化。HR评分：${feedback.feedback?.overall_score || 'N/A'}分\n\n主要改进：\n${data.optimization_summary?.optimization_focus?.join('\n') || '多项优化'}\n\n是否要查看优化前后的对比？`,
              '简历优化完成',
              {
                confirmButtonText: '查看对比',
                cancelButtonText: '稍后再看',
                type: 'success'
              }
            ).then(() => {
              showOptimizationComparison(originalData2.content, generatedResumes.value[resumeId], data)
            }).catch(() => {
              // 用户选择稍后再看
            })
          }, 1000)
        }
        
      } catch (error) {
        console.error('处理Phase3优化数据失败:', error)
        ElMessage.error('加载优化数据失败')
      }
    }
    
    // 显示优化对比的方法
    const showOptimizationComparison = (originalResume, optimizedResume, optimizationData) => {
      // 可以在这里实现对比界面，或者简单地显示优化信息
      ElMessageBox.alert(
        `优化完成！\n\n预期改进：\n${optimizationData.optimization_summary?.expected_improvements?.join('\n') || '多项改进'}\n\n您可以在简历列表中查看优化后的结果，并可随时重新提交给HR评估。`,
        '优化详情',
        {
          confirmButtonText: '知道了',
          type: 'success'
        }
      )
    }
    
    // 加载已存在的简历
    const loadExistingResumes = () => {
      const resumesStr = localStorage.getItem('generatedResumes')
      if (resumesStr) {
        try {
          const resumes = JSON.parse(resumesStr)
          generatedResumes.value = resumes
          
          // 更新简历状态
          Object.keys(resumes).forEach((key, index) => {
            resumeStatus.value[index] = 'generated'
          })
          
          // 如果有简历，自动展开第一个
          if (Object.keys(resumes).length > 0) {
            setTimeout(() => {
              expandFirstResume()
            }, 500)
          }
        } catch (error) {
          console.error('加载简历数据失败:', error)
        }
      }
      
      // 加载优化历史
      loadOptimizationHistory()
    }
    
    // ============ 添加缺失的工作经验管理方法 ============

    const addExperience = () => {
      userProfile.experience.push({
        company: '',
        position: '',
        duration: '',
        duration_dates: [],
        is_current: false,
        description: '',
        achievements: ['']
      })
    }
    
    const removeExperience = (index) => {
      userProfile.experience.splice(index, 1)
    }
    
    const updateDuration = (index) => {
      const exp = userProfile.experience[index]
      if (exp.duration_dates && exp.duration_dates.length === 2) {
        const startDate = exp.duration_dates[0]
        const endDate = exp.is_current ? '至今' : exp.duration_dates[1]
        exp.duration = `${startDate} - ${endDate}`
      }
    }
    
    const addAchievement = (expIndex) => {
      userProfile.experience[expIndex].achievements.push('')
    }
    
    const removeAchievement = (expIndex, achIndex) => {
      userProfile.experience[expIndex].achievements.splice(achIndex, 1)
    }
    
    // ============ 添加缺失的教育经历管理方法 ============

    const addEducation = () => {
      userProfile.education.push({
        school: '',
        degree: '',
        major: '',
        gpa: '',
        duration: '',
        duration_dates: []
      })
    }
    
    const removeEducation = (index) => {
      userProfile.education.splice(index, 1)
    }
    
    const updateEducationDuration = (index) => {
      const edu = userProfile.education[index]
      if (edu.duration_dates && edu.duration_dates.length === 2) {
        edu.duration = `${edu.duration_dates[0]} - ${edu.duration_dates[1]}`
      }
    }
    
    // ============ 添加缺失的项目经验管理方法 ============

    const addProject = () => {
      userProfile.projects.push({
        name: '',
        duration: '',
        description: '',
        technologies: [],
        techInputVisible: false,
        techInputValue: '',
        achievements: ['']
      })
    }
    
    const removeProject = (index) => {
      userProfile.projects.splice(index, 1)
    }
    
    const showProjectTechInput = (index) => {
      userProfile.projects[index].techInputVisible = true
      nextTick(() => {
        const ref = `projectTechInput${index}`
        // 这里需要处理 ref 访问
      })
    }
    
    const handleProjectTechConfirm = (index) => {
      const project = userProfile.projects[index]
      if (project.techInputValue && !project.technologies.includes(project.techInputValue)) {
        project.technologies.push(project.techInputValue)
      }
      project.techInputVisible = false
      project.techInputValue = ''
    }
    
    const removeProjectTech = (projectIndex, tech) => {
      const technologies = userProfile.projects[projectIndex].technologies
      const index = technologies.indexOf(tech)
      if (index > -1) {
        technologies.splice(index, 1)
      }
    }
    
    const addProjectAchievement = (projectIndex) => {
      userProfile.projects[projectIndex].achievements.push('')
    }
    
    const removeProjectAchievement = (projectIndex, achIndex) => {
      userProfile.projects[projectIndex].achievements.splice(achIndex, 1)
    }
    
    // 设置当前活跃的职位
    const setActiveJob = (index) => {
      activeJobIndex.value = index
    }
    
    // 获取简历状态
    const getResumeStatus = (index) => {
      return resumeStatus.value[index] || 'pending'
    }
    
    const getResumeStatusText = (index) => {
      const status = getResumeStatus(index)
      const statusMap = {
        'pending': '待生成',
        'generating': '生成中',
        'generated': '已生成',
        'error': '生成失败'
      }
      return statusMap[status] || '未知状态'
    }
    
    // 获取匹配度分数
    const getMatchScore = (index) => {
      const resume = generatedResumes.value[index]
      return resume?.customization_analysis?.match_score || 0
    }
    
    // 生成所有简历
    const generateAllResumes = async () => {
      if (!userProfile.full_name || !userProfile.email) {
        ElMessage.warning('请填写基本信息')
        return
      }
      
      isGeneratingAll.value = true
      generationProgress.value = 0
      
      try {
        const total = selectedJobs.value.length
        let completed = 0
        
        for (let i = 0; i < selectedJobs.value.length; i++) {
          const job = selectedJobs.value[i]
          currentGeneratingJob.value = `正在生成：${job.job_title} - ${job.company_name}`
          resumeStatus.value[i] = 'generating'
          
          try {
            const result = await generateResumeForJob(job, i)
            if (result.success) {
              generatedResumes.value[i] = result.data.content
              resumeStatus.value[i] = 'generated'
              
              // 保存到store
              store.addResume({
                id: `${Date.now()}_${i}`,
                content: result.data.content,
                job_title: job.job_title,
                company_name: job.company_name,
                created_at: new Date().toISOString()
              })
            } else {
              resumeStatus.value[i] = 'error'
            }
          } catch (error) {
            resumeStatus.value[i] = 'error'
            console.error(`生成简历失败 - ${job.job_title}: ${error}`)
          }
          
          completed++
          generationProgress.value = Math.round((completed / total) * 100)
          
          // 添加延迟避免API限制
          if (i < selectedJobs.value.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
        }
        
        const successCount = Object.keys(generatedResumes.value).length
        
        // 🔥 批量生成完成后保存到localStorage
        if (successCount > 0) {
          localStorage.setItem('generatedResumes', JSON.stringify(generatedResumes.value))
          console.log('批量生成完成，已保存', successCount, '份简历到localStorage')
        }
        
        ElMessage.success(`成功生成 ${successCount}/${total} 份简历`)
        
        // 自动展开第一个生成的简历
        if (successCount > 0) {
          const firstKey = Object.keys(generatedResumes.value)[0].toString()
          activeResumeKeys.value = [firstKey]
          
          // 强制页面更新
          nextTick(() => {
            console.log('展开的面板键:', activeResumeKeys.value)
            console.log('生成的简历:', Object.keys(generatedResumes.value))
          })
        }
        
      } catch (error) {
        ElMessage.error('批量生成简历失败')
      } finally {
        isGeneratingAll.value = false
        generationProgress.value = 0
        currentGeneratingJob.value = ''
      }
    }
    
    // 生成单个简历
    const generateSingleResume = async () => {
      if (activeJobIndex.value === -1) {
        ElMessage.warning('请选择一个职位')
        return
      }
      
      if (!userProfile.full_name || !userProfile.email) {
        ElMessage.warning('请填写基本信息')
        return
      }
      
      isGeneratingSingle.value = true
      const jobIndex = activeJobIndex.value
      const job = selectedJobs.value[jobIndex]
      
      try {
        resumeStatus.value[jobIndex] = 'generating'
        currentGeneratingJob.value = `正在生成：${job.job_title} - ${job.company_name}`
        
        const result = await generateResumeForJob(job, jobIndex)
        
        if (result.success) {
          generatedResumes.value[jobIndex] = result.data.content
          resumeStatus.value[jobIndex] = 'generated'
          
          // 🔥 立即保存生成的简历到localStorage
          localStorage.setItem('generatedResumes', JSON.stringify(generatedResumes.value))
          console.log('已保存简历到localStorage')
          
          // 自动展开生成的简历 - 确保使用字符串作为键
          activeResumeKeys.value = [jobIndex.toString()]
          
          // 强制页面更新并调试
          nextTick(() => {
            console.log('单个生成 - 展开的面板键:', activeResumeKeys.value)
            console.log('单个生成 - 生成的简历索引:', jobIndex)
            console.log('单个生成 - 简历数据:', !!generatedResumes.value[jobIndex])
          })
          
          ElMessage.success('简历生成成功！请查看下方展开的简历内容。')
        } else {
          resumeStatus.value[jobIndex] = 'error'
          ElMessage.error('简历生成失败')
        }
        
      } catch (error) {
        resumeStatus.value[jobIndex] = 'error'
        ElMessage.error('简历生成失败')
      } finally {
        isGeneratingSingle.value = false
        currentGeneratingJob.value = ''
      }
    }
    
    // 调用API生成简历的通用方法
    const generateResumeForJob = async (job, jobIndex) => {
      const cleanedProfile = {
        ...userProfile,
        experience: userProfile.experience.map(exp => ({
          ...exp,
          achievements: exp.achievements.filter(ach => ach.trim())
        })),
        projects: userProfile.projects.map(proj => ({
          ...proj,
          achievements: proj.achievements.filter(ach => ach.trim())
        }))
      }
      
      return await apiService.generateResume({
        user_profile: cleanedProfile,
        job_posting: job
      })
    }
    
    // 下载简历为Word文档
    const downloadResume = async (index) => {
      const job = selectedJobs.value[index]
      const resume = generatedResumes.value[index]
      
      console.log('开始下载简历，参数:', { index, job, resume })
      
      if (!resume) {
        ElMessage.warning('简历数据不存在，无法下载')
        return
      }
      
      // 验证简历数据结构
      console.log('简历数据结构:', {
        hasPersonalInfo: !!resume.personal_info,
        hasSummary: !!resume.professional_summary,
        hasEducation: !!resume.education,
        hasExperience: !!resume.professional_experience,
        dataKeys: Object.keys(resume)
      })
      
      try {
        ElMessage.info('正在生成Word文档，请稍候...')
        
        // 动态导入docx和file-saver库
        const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle } = await import('docx')
        const { saveAs } = await import('file-saver')
        
        // 生成文档内容
        const documentChildren = await generateWordContent(resume, job)
        
        // 验证生成的内容
        if (!documentChildren || !Array.isArray(documentChildren) || documentChildren.length === 0) {
          throw new Error('生成的文档内容为空，请检查简历数据')
        }
        
        // 过滤掉undefined和无效的元素，并进行更严格的验证
        const validChildren = documentChildren.filter(child => {
          if (!child) {
            console.warn('发现空元素，已过滤')
            return false
          }
          
          // 检查是否是有效的docx对象
          if (typeof child !== 'object') {
            console.warn('发现非对象元素，已过滤:', typeof child)
            return false
          }
          
          // 检查是否是docx的Paragraph或Table对象
          if (!child.constructor || !child.constructor.name) {
            console.warn('发现无构造函数的对象，已过滤:', child)
            return false
          }
          
          // 进一步验证对象结构
          const constructorName = child.constructor.name
          if (!['Paragraph', 'Table', 'TableOfContents'].includes(constructorName)) {
            console.warn(`发现未知对象类型 ${constructorName}，已过滤:`, child)
            return false
          }
          
          return true
        })
        
        console.log('原始段落数量:', documentChildren.length)
        console.log('过滤后段落数量:', validChildren.length)
        
        if (validChildren.length === 0) {
          throw new Error('生成的文档内容无效，请检查简历数据结构')
        }
        
        console.log('有效段落示例:', validChildren[0])
        console.log('有效段落类型:', validChildren[0]?.constructor?.name)
        
        // 验证每个段落的内部结构
        validChildren.forEach((child, index) => {
          if (child.constructor.name === 'Paragraph' && !child.root) {
            console.warn(`段落 ${index} 缺少root属性:`, child)
          }
        })
        
        const finalValidChildren = validChildren.map(child => {
          // 确保每个段落都有必要的属性
          if (child.constructor.name === 'Paragraph') {
            // 检查段落的内部结构
            if (!child.root || !Array.isArray(child.root)) {
              console.warn('段落缺少root属性，尝试修复')
              return new Paragraph({ children: [new TextRun({ text: '段落内容修复中...' })] })
            }
          }
          return child
        })
        
        // 添加详细的Document创建前检查
        console.log('=== Document创建前检查 ===')
        finalValidChildren.forEach((child, index) => {
          const debugInfo = {
            type: child.constructor.name,
            hasRoot: !!child.root,
            rootLength: child.root?.length,
            hasProperties: !!child.properties,
            hasFileChild: !!child.fileChild,
            keys: Object.keys(child)
          }
          
          // 添加具体内容提取
          let content = '无法提取内容'
          
          try {
            if (child.constructor.name === 'Paragraph') {
              // 提取段落文本内容
              if (child.root && Array.isArray(child.root)) {
                const textParts = []
                child.root.forEach(rootItem => {
                  if (rootItem && typeof rootItem === 'object') {
                    // 查找 TextRun 内容
                    if (rootItem.constructor && rootItem.constructor.name === 'TextRun') {
                      // 尝试提取文本
                      if (rootItem.text) {
                        textParts.push(rootItem.text)
                      } else if (rootItem.root && rootItem.root.length > 0) {
                        // 深层查找文本
                        rootItem.root.forEach(textElement => {
                          if (textElement && textElement.text) {
                            textParts.push(textElement.text)
                          }
                        })
                      }
                    }
                  }
                })
                content = textParts.join(' ') || '段落无文本内容'
              }
            } else if (child.constructor.name === 'Table') {
              content = '[表格内容 - 联系信息表格]'
            }
          } catch (extractError) {
            content = `内容提取失败: ${extractError.message}`
          }
          
          // console.log(`段落 ${index}:`, {
          //   ...debugInfo,
          //   content: content,
          //   contentLength: content.length
          // })
          
          // // 如果是段落，进一步详细分析
          // if (child.constructor.name === 'Paragraph' && child.root) {
          //   console.log(`  段落 ${index} 详细结构:`)
          //   child.root.forEach((rootItem, rootIndex) => {
          //     if (rootItem) {
          //       console.log(`    root[${rootIndex}]:`, {
          //         type: rootItem.constructor?.name || 'Unknown',
          //         hasText: !!rootItem.text,
          //         text: rootItem.text || '无直接文本',
          //         hasRoot: !!rootItem.root,
          //         rootLength: rootItem.root?.length || 0
          //       })
                
          //       // 如果有嵌套的root，继续深入
          //       if (rootItem.root && Array.isArray(rootItem.root)) {
          //         rootItem.root.forEach((nestedItem, nestedIndex) => {
          //           if (nestedItem) {
          //             console.log(`      nested[${nestedIndex}]:`, {
          //               type: nestedItem.constructor?.name || 'Unknown',
          //               hasText: !!nestedItem.text,
          //               text: nestedItem.text || '无文本',
          //               properties: Object.keys(nestedItem).filter(key => !['constructor', 'root'].includes(key))
          //             })
          //           }
          //         })
          //       }
          //     }
          //   })
          // }
        })
        
        try {
          console.log('开始创建Word文档，有效段落数量:', finalValidChildren.length)
          
          // 使用简化的Document创建，避免复杂的headers
          const doc = new Document({
            sections: [{
              properties: {
                page: {
                  margin: {
                    top: 720,    // 0.5英寸
                    right: 720,  // 0.5英寸
                    bottom: 720, // 0.5英寸
                    left: 720,   // 0.5英寸
                  },
                },
              },
              children: finalValidChildren,
            }],
          })
          
          console.log('Document创建成功')
          
          // 生成并下载Word文档
          const blob = await Packer.toBlob(doc)
          const filename = `${resume.personal_info?.name || '简历'}_${job.job_title}_${job.company_name}.docx`
          saveAs(blob, filename)
          
          ElMessage.success('简历Word文档下载完成！')
          
        } catch (docError) {
          console.error('Document创建失败:', docError)
          console.error('错误详情:', docError.stack)
          
          // 降级方案：创建最简单的文档
          try {
            console.log('尝试降级方案...')
            
            const simpleDoc = new Document({
              sections: [{
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({
                        text: `${resume.personal_info?.name || '简历'} - ${job.job_title}`,
                        bold: true,
                        size: 28,
                        font: 'Microsoft YaHei',
                      }),
                    ],
                  }),
                  new Paragraph({
                    children: [
                      new TextRun({
                        text: '简历内容生成中遇到技术问题，请稍后重试或联系技术支持。',
                        font: 'Microsoft YaHei',
                        size: 22,
                      }),
                    ],
                  }),
                ],
              }],
            })
            
            const blob = await Packer.toBlob(simpleDoc)
            const filename = `${resume.personal_info?.name || '简历'}_简化版.docx`
            saveAs(blob, filename)
            
            ElMessage.warning('使用简化版本下载，完整版本正在修复中')
            
          } catch (fallbackError) {
            console.error('降级方案也失败:', fallbackError)
            ElMessage.error('Word文档生成失败，请稍后重试')
          }
        }
        
      } catch (error) {
        console.error('Word文档生成失败:', error)
        ElMessage.error('Word文档生成失败，请稍后重试')
      }
    }
    
    // 生成Word文档内容
    const generateWordContent = async (resume, job) => {
      try {
        const { Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType } = await import('docx')
        
        const children = []
        const contentMapping = [] // 用于追踪内容映射
        
        // 安全创建段落的辅助函数
        const safeParagraph = (config, description = '未知段落') => {
          try {
            const paragraph = new Paragraph(config)
            if (!paragraph || typeof paragraph !== 'object') {
              console.error('段落创建失败:', config)
              return null
            }
            
            // 提取文本内容用于映射
            let extractedText = ''
            if (config.children && Array.isArray(config.children)) {
              extractedText = config.children
                .filter(child => child && child.text)
                .map(child => child.text)
                .join(' ')
            }
            
            contentMapping.push({
              index: children.length,
              description: description,
              extractedText: extractedText.substring(0, 100) + (extractedText.length > 100 ? '...' : ''),
              type: 'Paragraph'
            })
            
            return paragraph
          } catch (error) {
            console.error('段落创建出错:', error, config)
            return null
          }
        }
        
        // 安全创建表格的辅助函数
        const safeTable = (config, description = '未知表格') => {
          try {
            const table = new Table(config)
            if (!table || typeof table !== 'object') {
              console.error('表格创建失败:', config)
              return null
            }
            
            contentMapping.push({
              index: children.length,
              description: description,
              extractedText: '[表格内容]',
              type: 'Table'
            })
            
            return table
          } catch (error) {
            console.error('表格创建出错:', error, config)
            return null
          }
        }
        
        // 验证输入数据
        if (!resume) {
          console.warn('简历数据为空，生成默认内容')
          const defaultParagraph = safeParagraph({
            children: [
              new TextRun({
                text: '简历数据缺失',
                bold: true,
                size: 32,
                font: 'Microsoft YaHei',
              }),
            ],
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
          })
          if (defaultParagraph) children.push(defaultParagraph)
          return children
        }
        
        console.log('开始生成Word内容，简历数据:', resume)
        
        // 添加原始简历数据结构调试
        console.log('=== 原始简历数据结构 ===')
        console.log('1. 姓名:', resume.personal_info?.name || resume.name || '未填写')
        console.log('2. 个人简介:', resume.professional_summary ? resume.professional_summary.substring(0, 50) + '...' : '未填写')
        console.log('3. 教育背景数量:', resume.education?.length || 0)
        console.log('4. 工作经验数量:', resume.professional_experience?.length || 0)
        console.log('5. 项目经验数量:', resume.key_projects?.length || 0)
        console.log('6. 核心竞争力数量:', resume.core_competencies?.length || 0)
        console.log('7. 技术技能:', resume.highlighted_skills?.technical_skills?.join(', ') || '无')
        console.log('8. 框架工具:', resume.highlighted_skills?.frameworks_tools?.join(', ') || '无')
        console.log('9. 软技能:', resume.highlighted_skills?.soft_skills?.join(', ') || '无')
        
        // 1. 文档标题 - "个人简历"
        const documentTitle = safeParagraph({
          children: [
            new TextRun({
              text: '个人简历',
              bold: true,
              size: 36, // 18pt
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
        }, '文档标题 - 个人简历')
        if (documentTitle) children.push(documentTitle)
      
      // 2. 基本信息（规整排列，使用制表符精确对齐）
      if (resume.personal_info) {
        const userName = resume.personal_info?.name || resume.name || '姓名未填写'
        const userPhone = resume.personal_info.phone || '未填写'
        
        const firstLineParagraph = safeParagraph({
          children: [
            new TextRun({
              text: '姓名：',
              bold: true,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: `${userName}`,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: `\t电话：`,
              bold: true,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: userPhone,
              font: 'Microsoft YaHei',
              size: 20,
            }),
          ],
          spacing: { after: 30 },
          tabStops: [
            {
              type: 'left',
              position: 5000, // 调整制表位到5厘米处，确保"电话："和"地址："对齐
            },
          ],
        }, `基本信息第一行 - ${userName} ${userPhone}`)
        if (firstLineParagraph) children.push(firstLineParagraph)
        
        // 第二行：邮箱、地址
        const userEmail = resume.personal_info.email || '未填写'
        const userLocation = resume.personal_info.location || '未填写'
        
        const secondLineParagraph = safeParagraph({
          children: [
            new TextRun({
              text: '邮箱：',
              bold: true,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: `${userEmail}`,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: `\t地址：`,
              bold: true,
              font: 'Microsoft YaHei',
              size: 20,
            }),
            new TextRun({
              text: userLocation,
              font: 'Microsoft YaHei',
              size: 20,
            }),
          ],
          spacing: { after: 200 },
          tabStops: [
            {
              type: 'left',
              position: 5000, // 与第一行使用相同的制表位，确保完美对齐
            },
          ],
        }, `基本信息第二行 - ${userEmail} ${userLocation}`)
        if (secondLineParagraph) children.push(secondLineParagraph)
        
      }
      
      // 3. 个人简介
      if (resume.professional_summary) {
        const summaryHeader = safeParagraph({
          children: [
            new TextRun({
              text: '个人简介',
              bold: true,
              size: 24, // 12pt
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '个人简介标题')
        if (summaryHeader) children.push(summaryHeader)
        
        // 添加分割线
        const summaryDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '个人简介分割线')
        if (summaryDivider) children.push(summaryDivider)
        
        const summaryParagraph = safeParagraph({
          children: [
            new TextRun({
              text: resume.professional_summary,
              font: 'Microsoft YaHei',
              size: 20, // 10pt
            }),
          ],
          spacing: { after: 50, line: 240 }, // 1.2倍行距
        }, `个人简介内容: ${resume.professional_summary.substring(0, 50)}...`)
        if (summaryParagraph) children.push(summaryParagraph)
      }
      
      // 4. 教育背景
      if (resume.education && resume.education.length > 0) {
        const educationHeader = safeParagraph({
          children: [
            new TextRun({
              text: '教育背景',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '教育背景标题')
        if (educationHeader) children.push(educationHeader)
        
        // 添加分割线
        const educationDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '教育背景分割线')
        if (educationDivider) children.push(educationDivider)
        
        resume.education.forEach((edu, index) => {
          // 获取教育背景的各种字段
          const school = edu.school || edu.institution || '学校名称未填写'
          const degree = edu.degree || '学历未填写'
          const major = edu.major || edu.field_of_study || '专业未填写'
          const duration = edu.duration || edu.period || '时间未填写'
          
          // 主要信息左对齐，时间右对齐
          const eduMainParagraph = safeParagraph({
            children: [
              new TextRun({
                text: `${school} | ${degree} | ${major}`,
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: `\t${duration}`,
                font: 'Microsoft YaHei',
                size: 20,
                bold: true,
                color: '000000',
              }),
            ],
            spacing: { after: 30 },
            tabStops: [
              {
                type: 'right',
                position: 9600, // 右对齐制表位
              },
            ],
          }, `教育背景${index + 1}: ${school} - ${degree}`)
          if (eduMainParagraph) children.push(eduMainParagraph)
          
          // 添加GPA和其他详细信息
          const details = []
          if (edu.gpa) details.push(`GPA: ${edu.gpa}`)
          if (edu.honors) details.push(`荣誉: ${edu.honors}`)
          if (edu.relevant_courses && edu.relevant_courses.length > 0) {
            details.push(`主要课程: ${edu.relevant_courses.join(', ')}`)
          }
          
          if (details.length > 0) {
            const eduDetailsParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: details.join(' | '),
                  font: 'Microsoft YaHei',
                  size: 20,
                  color: '666666',
                }),
              ],
              spacing: { after: index === resume.education.length - 1 ? 50 : 50 },
            }, `教育背景${index + 1}详情: ${details.join(' | ')}`)
            if (eduDetailsParagraph) children.push(eduDetailsParagraph)
          } else if (index < resume.education.length - 1) {
            // 非最后一个教育背景项目后的小间距
            const spaceParagraph = safeParagraph({ text: '', spacing: { after: 50 } }, `教育背景${index + 1}后间距`)
            if (spaceParagraph) children.push(spaceParagraph)
          }
        })
      }
      
      // 5. 工作经验
      if (resume.professional_experience && resume.professional_experience.length > 0) {
        const workHeader = safeParagraph({
          children: [
            new TextRun({
              text: '工作经验',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '工作经验标题')
        if (workHeader) children.push(workHeader)
        
        // 添加分割线
        const workDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '工作经验分割线')
        if (workDivider) children.push(workDivider)
        
        resume.professional_experience.forEach((exp, index) => {
          // 数据验证
          if (!exp || typeof exp !== 'object') {
            console.warn('跳过无效的工作经验数据:', exp)
            return
          }
          
          const company = exp.company || exp.employer || '公司名称未填写'
          const position = exp.position || exp.title || exp.job_title || '职位未填写'
          const duration = exp.duration || exp.period || '时间未填写'
          
          // 工作经验标题行 - 公司职位左对齐，时间右对齐
          const expMainParagraph = safeParagraph({
            children: [
              new TextRun({
                text: `${company} | ${position}`,
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: `\t${duration}`,
                font: 'Microsoft YaHei',
                size: 20,
                bold: true,
                color: '000000',
              }),
            ],
            spacing: { after: 30 },
            tabStops: [
              {
                type: 'right',
                position: 9600,
              },
            ],
          }, `工作经验${index + 1}: ${company} - ${position}`)
          if (expMainParagraph) children.push(expMainParagraph)
          
          // 工作描述
          if (exp.description || exp.job_description) {
            const description = exp.description || exp.job_description
            const expDescParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `工作职责：${description}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: 30 },
            }, `工作经验${index + 1}描述: ${description.substring(0, 30)}...`)
            if (expDescParagraph) children.push(expDescParagraph)
          }
          
          // 主要职责
          if (exp.responsibilities && Array.isArray(exp.responsibilities) && exp.responsibilities.length > 0) {
            const responsibilitiesText = exp.responsibilities.join('；')
            const respParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `主要职责：${responsibilitiesText}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: 30 },
            }, `工作经验${index + 1}主要职责`)
            if (respParagraph) children.push(respParagraph)
          }
          
          // 关键成就
          if (exp.achievements && Array.isArray(exp.achievements) && exp.achievements.length > 0) {
            const achievementsText = exp.achievements.filter(a => a && typeof a === 'string').join('；')
            if (achievementsText) {
              const achievementsParagraph = safeParagraph({
                children: [
                  new TextRun({
                    text: `关键成就：${achievementsText}`,
                    font: 'Microsoft YaHei',
                    size: 20,
                  }),
                ],
                spacing: { after: 30 },
              }, `工作经验${index + 1}关键成就`)
              if (achievementsParagraph) children.push(achievementsParagraph)
            }
          }
          
          // 技能和工具
          if (exp.skills_used && Array.isArray(exp.skills_used) && exp.skills_used.length > 0) {
            const skillsText = exp.skills_used.join('、')
            const skillsParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `使用技能：${skillsText}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                  color: '0066cc',
                }),
              ],
              spacing: { after: index === resume.professional_experience.length - 1 ? 50 : 50 },
            }, `工作经验${index + 1}使用技能`)
            if (skillsParagraph) children.push(skillsParagraph)
          } else if (index < resume.professional_experience.length - 1) {
            // 非最后一个工作经验的间距
            const spaceParagraph = safeParagraph({ text: '', spacing: { after: 50 } }, `工作经验${index + 1}后间距`)
            if (spaceParagraph) children.push(spaceParagraph)
          }
        })
      }
      
      // 6. 项目经验
      if (resume.key_projects && resume.key_projects.length > 0) {
        const projectHeader = safeParagraph({
          children: [
            new TextRun({
              text: '项目经验',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '项目经验标题')
        if (projectHeader) children.push(projectHeader)
        
        // 添加分割线
        const projectDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '项目经验分割线')
        if (projectDivider) children.push(projectDivider)
        
        resume.key_projects.forEach((project, index) => {
          // 数据验证
          if (!project || typeof project !== 'object') {
            console.warn('跳过无效的项目数据:', project)
            return
          }
          
          const projectName = project.name || project.title || '项目名称未填写'
          const duration = project.duration || project.period || '时间未填写'
          const role = project.role || project.position || ''
          
          // 项目标题行 - 项目名称和角色左对齐，时间右对齐
          const titleText = role ? `${projectName} | ${role}` : projectName
          const projectMainParagraph = safeParagraph({
            children: [
              new TextRun({
                text: titleText,
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: `\t${duration}`,
                font: 'Microsoft YaHei',
                size: 20,
                bold: true,
                color: '000000',
              }),
            ],
            spacing: { after: 30 },
            tabStops: [
              {
                type: 'right',
                position: 9600,
              },
            ],
          }, `项目经验${index + 1}: ${projectName}`)
          if (projectMainParagraph) children.push(projectMainParagraph)
          
          // 项目描述
          if (project.description || project.project_description) {
            const description = project.description || project.project_description
            const projectDescParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `项目描述：${description}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: 30 },
            }, `项目经验${index + 1}描述: ${description.substring(0, 30)}...`)
            if (projectDescParagraph) children.push(projectDescParagraph)
          }
          
          // 主要职责
          if (project.responsibilities && Array.isArray(project.responsibilities) && project.responsibilities.length > 0) {
            const responsibilitiesText = project.responsibilities.join('；')
            const respParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `主要职责：${responsibilitiesText}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: 30 },
            }, `项目经验${index + 1}主要职责`)
            if (respParagraph) children.push(respParagraph)
          }
          
          // 技术栈
          if (project.technologies && Array.isArray(project.technologies) && project.technologies.length > 0) {
            const techParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `技术栈：${project.technologies.join('、')}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                  color: '0066cc',
                }),
              ],
              spacing: { after: 30 },
            }, `项目经验${index + 1}技术栈: ${project.technologies.join(', ')}`)
            if (techParagraph) children.push(techParagraph)
          }
          
          // 项目成果
          if (project.achievements && Array.isArray(project.achievements) && project.achievements.length > 0) {
            const achievementsText = project.achievements.filter(a => a && typeof a === 'string').join('；')
            if (achievementsText) {
              const achievementsParagraph = safeParagraph({
                children: [
                  new TextRun({
                    text: `项目成果：${achievementsText}`,
                    font: 'Microsoft YaHei',
                    size: 20,
                  }),
                ],
                spacing: { after: 30 },
              }, `项目经验${index + 1}项目成果`)
              if (achievementsParagraph) children.push(achievementsParagraph)
            }
          }
          
          // 挑战与解决方案
          if (project.challenges_and_solutions || project.challenges) {
            const challengesText = project.challenges_and_solutions || project.challenges
            const challengesParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `挑战与解决方案：${challengesText}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: 30 },
            }, `项目经验${index + 1}挑战与解决方案`)
            if (challengesParagraph) children.push(challengesParagraph)
          }
          
          // 项目亮点或创新点
          if (project.highlights || project.innovations) {
            const highlightsText = project.highlights || project.innovations
            const highlightsParagraph = safeParagraph({
              children: [
                new TextRun({
                  text: `项目亮点：${highlightsText}`,
                  font: 'Microsoft YaHei',
                  size: 20,
                }),
              ],
              spacing: { after: index === resume.key_projects.length - 1 ? 50 : 50 },
            }, `项目经验${index + 1}项目亮点`)
            if (highlightsParagraph) children.push(highlightsParagraph)
          } else if (index < resume.key_projects.length - 1) {
            // 非最后一个项目经验的间距
            const spaceParagraph = safeParagraph({ text: '', spacing: { after: 50 } }, `项目经验${index + 1}后间距`)
            if (spaceParagraph) children.push(spaceParagraph)
          }
        })
      }
      
      // 7. 核心竞争力
      if (resume.core_competencies && resume.core_competencies.length > 0) {
        const competencyHeader = safeParagraph({
          children: [
            new TextRun({
              text: '核心竞争力',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '核心竞争力标题')
        if (competencyHeader) children.push(competencyHeader)
        
        // 添加分割线
        const competencyDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '核心竞争力分割线')
        if (competencyDivider) children.push(competencyDivider)
        
        // 将核心竞争力组合成一段文字，而不是分成多个段落
        const competenciesText = resume.core_competencies.join('；')
        const competencyParagraph = safeParagraph({
          children: [
            new TextRun({
              text: competenciesText,
              font: 'Microsoft YaHei',
              size: 20,
            }),
          ],
          spacing: { after: 50 },
        }, `核心竞争力内容: ${competenciesText}`)
        if (competencyParagraph) children.push(competencyParagraph)
      }
      
      // 8. 技能特长
      if (resume.highlighted_skills) {
        const skillsHeader = safeParagraph({
          children: [
            new TextRun({
              text: '技能特长',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '技能特长标题')
        if (skillsHeader) children.push(skillsHeader)
        
        // 添加分割线
        const skillsDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '技能特长分割线')
        if (skillsDivider) children.push(skillsDivider)
        
        // 技术技能
        if (resume.highlighted_skills.technical_skills && resume.highlighted_skills.technical_skills.length > 0) {
          const techSkillsParagraph = safeParagraph({
            children: [
              new TextRun({
                text: '技术技能：',
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: resume.highlighted_skills.technical_skills.join('、'),
                font: 'Microsoft YaHei',
                size: 20,
              }),
            ],
            spacing: { after: 30 },
          }, `技术技能: ${resume.highlighted_skills.technical_skills.join(', ')}`)
          if (techSkillsParagraph) children.push(techSkillsParagraph)
        }
        
        // 框架工具
        if (resume.highlighted_skills.frameworks_tools && resume.highlighted_skills.frameworks_tools.length > 0) {
          const frameworksParagraph = safeParagraph({
            children: [
              new TextRun({
                text: '框架工具：',
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: resume.highlighted_skills.frameworks_tools.join('、'),
                font: 'Microsoft YaHei',
                size: 20,
              }),
            ],
            spacing: { after: 30 },
          }, `框架工具: ${resume.highlighted_skills.frameworks_tools.join(', ')}`)
          if (frameworksParagraph) children.push(frameworksParagraph)
        }
        
        // 软技能
        if (resume.highlighted_skills.soft_skills && resume.highlighted_skills.soft_skills.length > 0) {
          const softSkillsParagraph = safeParagraph({
            children: [
              new TextRun({
                text: '软技能：',
                bold: true,
                font: 'Microsoft YaHei',
                size: 20,
              }),
              new TextRun({
                text: resume.highlighted_skills.soft_skills.join('、'),
                font: 'Microsoft YaHei',
                size: 20,
              }),
            ],
            spacing: { after: 50 },
          }, `软技能: ${resume.highlighted_skills.soft_skills.join(', ')}`)
          if (softSkillsParagraph) children.push(softSkillsParagraph)
        }
      }
      
      // 9. 其他信息
      const otherSections = []
      
      if (resume.languages && resume.languages.length > 0) {
        otherSections.push(`语言能力：${resume.languages.map(lang => `${lang.language}(${lang.proficiency})`).join('、')}`)
      }
      
      if (resume.certifications && resume.certifications.length > 0) {
        otherSections.push(`认证证书：${resume.certifications.map(cert => cert.name || cert.title).join('、')}`)
      }
      
      if (resume.awards && resume.awards.length > 0) {
        otherSections.push(`获得奖项：${resume.awards.map(award => award.name || award.title).join('、')}`)
      }
      
      if (resume.publications && resume.publications.length > 0) {
        otherSections.push(`发表论文：${resume.publications.map(pub => pub.title || pub.name).join('、')}`)
      }
      
      if (otherSections.length > 0) {
        const otherInfoHeader = safeParagraph({
          children: [
            new TextRun({
              text: '其他信息',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 100, after: 5 }, // 最小间距
        }, '其他信息标题')
        if (otherInfoHeader) children.push(otherInfoHeader)
        
        // 添加分割线
        const otherInfoDivider = safeParagraph({
          children: [
            new TextRun({
              text: '———————————————————————————————————————————————————————————',
              font: 'Microsoft YaHei',
              size: 16,
              color: '888888',
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 5 }, // 最小间距
        }, '其他信息分割线')
        if (otherInfoDivider) children.push(otherInfoDivider)
        
        otherSections.forEach((section, index) => {
          const otherSectionParagraph = safeParagraph({
            children: [
              new TextRun({
                text: section,
                font: 'Microsoft YaHei',
                size: 20,
              }),
            ],
            spacing: { after: index === otherSections.length - 1 ? 50 : 30 },
          }, `其他信息${index + 1}: ${section.substring(0, 30)}...`)
          if (otherSectionParagraph) children.push(otherSectionParagraph)
        })
      }
      
      // 最终验证：过滤掉创建失败的元素
      const finalChildren = children.filter(child => {
        if (!child) {
          console.warn('发现空的段落对象，已过滤')
          return false
        }
        if (typeof child !== 'object') {
          console.warn('发现非对象的段落，已过滤:', typeof child)
          return false
        }
        return true
      })
      
      console.log('最终段落数量:', finalChildren.length)
      
      // 显示内容映射表
      console.log('\n=== 生成的Word段落内容映射表 ===')
      console.table(contentMapping.map((item, index) => ({
        '序号': index + 1,
        '段落描述': item.description,
        '提取的文本': item.extractedText || '(无文本内容)',
        '段落类型': item.type || '未知'
      })))
      
      console.log('\n=== 原始数据 vs 生成内容对比 ===')
      console.log('原始姓名:', resume.personal_info?.name || resume.name || '未填写')
      console.log('原始简介长度:', resume.professional_summary?.length || 0, '字符')
      console.log('教育背景条数:', resume.education?.length || 0)
      console.log('工作经验条数:', resume.professional_experience?.length || 0)
      console.log('项目经验条数:', resume.key_projects?.length || 0)
      console.log('核心竞争力条数:', resume.core_competencies?.length || 0)
      console.log('生成的Word段落总数:', finalChildren.length)
      
      if (finalChildren.length === 0) {
        console.error('所有段落都创建失败，返回默认内容')
        const fallbackParagraph = new Paragraph({
          children: [
            new TextRun({
              text: '简历生成过程中出现问题，请重试',
              bold: true,
              size: 24,
              font: 'Microsoft YaHei',
            }),
          ],
          spacing: { after: 200 },
        })
        return [fallbackParagraph]
      }
      
      return finalChildren
      
    } catch (error) {
      console.error('生成Word内容失败:', error)
      console.error('错误详情:', error.stack)
      // 返回默认内容
      const { Paragraph, TextRun, HeadingLevel, AlignmentType } = await import('docx')
      return [
        new Paragraph({
          children: [
            new TextRun({
              text: '简历内容生成失败，请检查数据格式',
              bold: true,
              size: 32,
              font: 'Microsoft YaHei',
            }),
          ],
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({
              text: `错误信息: ${error.message}`,
              font: 'Microsoft YaHei',
              size: 22,
              color: '666666',
            }),
          ],
          spacing: { after: 200 },
        })
      ]
    }
    }
    
    // 优化简历
    const optimizeResume = async (index) => {
      const job = selectedJobs.value[index]
      const resume = generatedResumes.value[index]
      
      if (!resume) {
        ElMessage.warning('请先生成简历')
        return
      }
      
      try {
        const result = await apiService.optimizeResume(resume, {}, ['技能匹配', '经验包装'])
        
        if (result && result.success) {
          generatedResumes.value[index] = result.data.optimized_resume
          ElMessage.success('简历优化完成！')
        } else {
          ElMessage.error('简历优化失败')
        }
      } catch (error) {
        ElMessage.error('简历优化失败')
      }
    }
    
    // 编辑简历
    const editResume = (index) => {
      const job = selectedJobs.value[index]
      const resume = generatedResumes.value[index]
      
      if (!resume) {
        ElMessage.warning('简历数据不存在，无法编辑')
        return
      }
      
      // 显示编辑模式
      showEditMode.value = true
      editingIndex.value = index
      
      // 复制简历数据到编辑表单中
      editingResume.value = JSON.parse(JSON.stringify(resume))
      
      ElMessage.info(`编辑简历：${job.job_title} - ${job.company_name}`)
      
      // 滚动到编辑区域
      nextTick(() => {
        const editElement = document.querySelector('.resume-edit-modal')
        if (editElement) {
          editElement.scrollIntoView({ behavior: 'smooth' })
        }
      })
    }
    
    // 保存编辑的简历
    const saveEditedResume = () => {
      if (editingIndex.value === -1) {
        ElMessage.error('编辑索引无效')
        return
      }
      
      try {
        // 更新简历数据
        generatedResumes.value[editingIndex.value] = JSON.parse(JSON.stringify(editingResume.value))
        
        // 关闭编辑模式
        showEditMode.value = false
        editingIndex.value = -1
        editingResume.value = {}
        
        ElMessage.success('简历修改已保存！')
        
      } catch (error) {
        console.error('保存简历失败:', error)
        ElMessage.error('保存失败，请重试')
      }
    }
    
    // 取消编辑
    const cancelEdit = () => {
      showEditMode.value = false
      editingIndex.value = -1
      editingResume.value = {}
      ElMessage.info('已取消编辑')
    }
    
    // 进入Phase3
    const proceedToPhase3 = () => {
      const generatedCount = Object.keys(generatedResumes.value).length
      if (generatedCount === 0) {
        ElMessage.warning('请先生成至少一份简历')
        return
      }
      
      // 保存所有生成的简历供下一阶段使用
      localStorage.setItem('generatedResumes', JSON.stringify(generatedResumes.value))
      localStorage.setItem('selectedJobsForPhase3', JSON.stringify(selectedJobs.value))
      
      store.setCurrentPhase(3)
      router.push('/phase3')
      
      ElMessage.success(`携带 ${generatedCount} 份简历进入HR评估阶段`)
    }
    
    // 原有的其他方法
    const getSkillType = (skill) => {
      const frontendSkills = ['Vue.js', 'React', 'Angular', 'JavaScript', 'TypeScript', 'HTML', 'CSS']
      const backendSkills = ['Java', 'Python', 'Node.js', 'Go', 'C++', 'PHP']
      const databaseSkills = ['MySQL', 'MongoDB', 'Redis', 'PostgreSQL']
      
      if (frontendSkills.some(s => skill.includes(s))) return 'success'
      if (backendSkills.some(s => skill.includes(s))) return 'warning'
      if (databaseSkills.some(s => skill.includes(s))) return 'info'
      return ''
    }
    
    const showInput = () => {
      inputVisible.value = true
      nextTick(() => {
        skillInput.value.focus()
      })
    }
    
    const handleInputConfirm = () => {
      if (inputValue.value && !userProfile.skills.includes(inputValue.value)) {
        userProfile.skills.push(inputValue.value)
      }
      inputVisible.value = false
      inputValue.value = ''
    }
    
    const removeSkill = (skill) => {
      const index = userProfile.skills.indexOf(skill)
      if (index > -1) {
        userProfile.skills.splice(index, 1)
      }
    }
    
    // 修复加载示例数据的方法
    const loadDemoProfile = () => {
      Object.assign(userProfile, {
        full_name: '张三',
        email: 'zhangsan@example.com',
        phone: '13800138000',
        location: '北京市朝阳区',
        target_position: '前端开发工程师',
        summary: '3年前端开发经验，熟悉Vue.js、React等主流框架，具备良好的编程基础和团队协作能力。擅长响应式设计和性能优化，有丰富的移动端开发经验。',
        skills: ['Vue.js', 'React', 'JavaScript', 'TypeScript', 'CSS3', 'HTML5', 'Node.js', 'Webpack', 'Git', 'Element UI'],
        experience: [
          {
            company: '北京某科技有限公司',
            position: '前端开发工程师',
            duration: '2021-06 - 至今',
            duration_dates: ['2021-06', '2024-01'],
            is_current: false,
            description: '负责公司主要产品的前端开发，参与多个重要项目的技术选型和架构设计。',
            achievements: [
              '独立完成3个重要项目的前端开发，获得用户好评',
              '优化页面性能，提升加载速度30%，改善用户体验',
              '参与技术选型和架构设计，推动团队技术升级'
            ]
          },
          {
            company: '上海某互联网公司',
            position: '初级前端开发工程师',
            duration: '2020-03 - 2021-05',
            duration_dates: ['2020-03', '2021-05'],
            is_current: false,
            description: '参与电商平台的前端开发工作，负责用户界面优化和功能实现。',
            achievements: [
              '参与开发电商平台核心功能模块',
              '完成移动端适配工作，提升移动端用户体验'
            ]
          }
        ],
        education: [
          {
            school: '北京理工大学',
            degree: '本科',
            major: '计算机科学与技术',
            gpa: '3.6',
            duration: '2017-09 - 2021-06',
            duration_dates: ['2017-09', '2021-06']
          }
        ],
        projects: [
          {
            name: '电商管理系统',
            duration: '2023.06 - 2023.12',
            description: '基于Vue.js的电商后台管理系统，包含商品管理、订单管理、用户管理等核心功能。',
            technologies: ['Vue.js', 'Element UI', 'Axios', 'Vuex', 'Vue Router'],
            techInputVisible: false,
            techInputValue: '',
            achievements: [
              '实现完整的CRUD功能和数据可视化',
              '设计并实现用户权限管理系统',
              '优化列表性能，支持万级数据展示'
            ]
          },
          {
            name: '移动端商城应用',
            duration: '2022.08 - 2023.02',
            description: '使用React Native开发的移动端购物应用，支持商品浏览、购物车、支付等功能。',
            technologies: ['React Native', 'Redux', 'React Navigation', 'Async Storage'],
            techInputVisible: false,
            techInputValue: '',
            achievements: [
              '完成iOS和Android双平台适配',
              '集成第三方支付SDK，实现安全支付',
              '优化应用性能，启动时间减少40%'
            ]
          }
        ],
        languages: '英语CET-6（良好），日语N3（基础）',
        certifications: 'PMP项目管理认证，AWS云从业者认证',
        special_requirements: '希望能够在技术驱动的团队中工作，持续学习新技术，为产品创新贡献力量。'
      })
      ElMessage.success('示例数据加载完成！您可以基于此数据生成简历。')
    }
    
    // 手动控制折叠面板的方法
    const expandFirstResume = () => {
      if (Object.keys(generatedResumes.value).length > 0) {
        const firstKey = Object.keys(generatedResumes.value)[0]
        activeResumeKeys.value = [firstKey]
        console.log('手动展开第一份简历，键值:', firstKey)
      }
    }
    
    const expandAllResumes = () => {
      const allKeys = Object.keys(generatedResumes.value).map(key => key.toString())
      activeResumeKeys.value = [...allKeys]
      console.log('展开所有简历，键值:', allKeys)
    }
    
    const collapseAllResumes = () => {
      activeResumeKeys.value = []
      console.log('收起所有简历')
    }
    
    const debugResumeData = () => {
      console.log('=== 简历数据调试信息 ===')
      console.log('generatedResumes:', generatedResumes.value)
      console.log('activeResumeKeys:', activeResumeKeys.value)
      console.log('selectedJobs:', selectedJobs.value)
      
      // 检查每份简历的数据结构
      Object.keys(generatedResumes.value).forEach(key => {
        const resumeData = generatedResumes.value[key]
        console.log(`简历 ${key} 数据结构:`, {
          type: typeof resumeData,
          keys: Object.keys(resumeData || {}),
          hasPersonalInfo: !!resumeData?.personal_info,
          hasDataContent: !!resumeData?.data?.content,
          personalInfoName: resumeData?.personal_info?.name || resumeData?.data?.content?.personal_info?.name || 'None'
        })
      })
      
      ElMessage.info('调试信息已输出到控制台，请按F12查看')
    }
    
    // 编辑模态框相关方法
    const showNewCompetencyInput = () => {
      newCompetencyVisible.value = true
      nextTick(() => {
        newCompetencyInput.value?.focus()
      })
    }
    
    const addNewCompetency = () => {
      if (newCompetencyValue.value && !editingResume.value.core_competencies.includes(newCompetencyValue.value)) {
        editingResume.value.core_competencies.push(newCompetencyValue.value)
      }
      newCompetencyVisible.value = false
      newCompetencyValue.value = ''
    }
    
    // 技能编辑方法
    const showNewTechSkillInput = () => {
      newTechSkillVisible.value = true
      nextTick(() => {
        newTechSkillInput.value?.focus()
      })
    }
    
    const addNewTechSkill = () => {
      if (newTechSkillValue.value && !editingResume.value.highlighted_skills.technical_skills.includes(newTechSkillValue.value)) {
        editingResume.value.highlighted_skills.technical_skills.push(newTechSkillValue.value)
      }
      newTechSkillVisible.value = false
      newTechSkillValue.value = ''
    }
    
    const showNewToolInput = () => {
      newToolVisible.value = true
      nextTick(() => {
        newToolInput.value?.focus()
      })
    }
    
    const addNewTool = () => {
      if (newToolValue.value && !editingResume.value.highlighted_skills.frameworks_and_tools.includes(newToolValue.value)) {
        editingResume.value.highlighted_skills.frameworks_and_tools.push(newToolValue.value)
      }
      newToolVisible.value = false
      newToolValue.value = ''
    }
    
    const showNewSoftSkillInput = () => {
      newSoftSkillVisible.value = true
      nextTick(() => {
        newSoftSkillInput.value?.focus()
      })
    }
    
    const addNewSoftSkill = () => {
      if (newSoftSkillValue.value && !editingResume.value.highlighted_skills.soft_skills.includes(newSoftSkillValue.value)) {
        editingResume.value.highlighted_skills.soft_skills.push(newSoftSkillValue.value)
      }
      newSoftSkillVisible.value = false
      newSoftSkillValue.value = ''
    }
    
    // 教育背景编辑方法
    const addEducationToResume = () => {
      if (!editingResume.value.education) {
        editingResume.value.education = []
      }
      editingResume.value.education.push({
        institution: '',
        degree: '',
        major: '',
        duration: '',
        location: '',
        gpa: ''
      })
    }
    
    const removeEducationFromResume = (index) => {
      editingResume.value.education.splice(index, 1)
    }
    
    // 工作经验编辑方法
    const addWorkExperience = () => {
      if (!editingResume.value.professional_experience) {
        editingResume.value.professional_experience = []
      }
      editingResume.value.professional_experience.push({
        company: '',
        position: '',
        duration: '',
        location: '',
        description: '',
        responsibilities: [''],
        achievements: ['']
      })
    }
    
    const removeWorkExperience = (index) => {
      editingResume.value.professional_experience.splice(index, 1)
    }
    
    // 项目经验编辑方法
    const addProjectToResume = () => {
      if (!editingResume.value.key_projects) {
        editingResume.value.key_projects = []
      }
      editingResume.value.key_projects.push({
        name: '',
        duration: '',
        description: '',
        role: '',
        technologies_used: [],
        outcomes: [''],
        newTechVisible: false,
        newTechValue: ''
      })
    }
    
    const removeProjectFromResume = (index) => {
      editingResume.value.key_projects.splice(index, 1)
    }
    
    const showProjectTechInputInResume = (index) => {
      editingResume.value.key_projects[index].newTechVisible = true
    }
    
    const addProjectTechToResume = (index) => {
      const project = editingResume.value.key_projects[index]
      if (project.newTechValue && !project.technologies_used.includes(project.newTechValue)) {
        project.technologies_used.push(project.newTechValue)
      }
      project.newTechVisible = false
      project.newTechValue = ''
    }
    
    // 认证证书编辑方法
    const addCertification = () => {
      if (!editingResume.value.certifications) {
        editingResume.value.certifications = []
      }
      editingResume.value.certifications.push({
        name: '',
        issuer: '',
        date: '',
        validity: '',
        credential_id: ''
      })
    }
    
    const removeCertification = (index) => {
      editingResume.value.certifications.splice(index, 1)
    }
    
    // 语言能力编辑方法
    const addLanguage = () => {
      if (!editingResume.value.languages) {
        editingResume.value.languages = []
      }
      editingResume.value.languages.push({
        language: '',
        proficiency: '',
        certification: ''
      })
    }
    
    const removeLanguage = (index) => {
      editingResume.value.languages.splice(index, 1)
    }
    
    // 职业发展编辑方法
    const addProfDevelopment = () => {
      if (!editingResume.value.professional_development) {
        editingResume.value.professional_development = []
      }
      editingResume.value.professional_development.push({
        type: '',
        title: '',
        provider: '',
        date: '',
        duration: '',
        description: ''
      })
    }
    
    const removeProfDevelopment = (index) => {
      editingResume.value.professional_development.splice(index, 1)
    }
    
    // 其他信息编辑方法
    const addAward = () => {
      if (!editingResume.value.awards) {
        editingResume.value.awards = []
      }
      editingResume.value.awards.push({
        title: '',
        issuer: '',
        date: '',
        description: ''
      })
    }
    
    const removeAward = (index) => {
      editingResume.value.awards.splice(index, 1)
    }
    
    const addPublication = () => {
      if (!editingResume.value.publications) {
        editingResume.value.publications = []
      }
      editingResume.value.publications.push({
        title: '',
        publication: '',
        date: '',
        authors: '',
        link: ''
      })
    }
    
    const removePublication = (index) => {
      editingResume.value.publications.splice(index, 1)
    }
    
    const addVolunteer = () => {
      if (!editingResume.value.volunteer_experience) {
        editingResume.value.volunteer_experience = []
      }
      editingResume.value.volunteer_experience.push({
        organization: '',
        role: '',
        duration: '',
        description: ''
      })
    }
    
    const removeVolunteer = (index) => {
      editingResume.value.volunteer_experience.splice(index, 1)
    }
    
    // 添加/删除数组元素的通用方法
    const addArrayItem = (array, defaultValue = '') => {
      if (Array.isArray(array)) {
        array.push(defaultValue)
      }
    }
    
    const removeArrayItem = (array, index) => {
      if (Array.isArray(array) && index >= 0 && index < array.length) {
        array.splice(index, 1)
      }
    }
    
    // 标签处理方法
    const removeTag = (array, tag) => {
      const index = array.indexOf(tag)
      if (index > -1) {
        array.splice(index, 1)
      }
    }

    // 新增：优化历史相关方法
    const getOptimizationCount = (jobIndex) => {
      return optimizationHistory.value[jobIndex]?.length || 0
    }

    const getOptimizationHistoryForJob = (jobIndex) => {
      return optimizationHistory.value[jobIndex] || []
    }

    const getOriginalResume = (jobIndex) => {
      return originalResumes.value[jobIndex] || generatedResumes.value[jobIndex]
    }

    const showOptimizationHistory = (jobIndex) => {
      // 确保简历面板是展开的
      if (!activeResumeKeys.value.includes(jobIndex.toString())) {
        activeResumeKeys.value = [jobIndex.toString()]
      }
      
      // 设置活跃标签页为原始简历，让用户可以看到标签页
      activeOptimizationTab.value[jobIndex] = 'original'
      
      const history = getOptimizationHistoryForJob(jobIndex)
      if (history.length > 0) {
        ElMessage.info(`该简历共有 ${history.length} 次优化记录，请点击上方的标签页（当前简历、原始简历、第N次优化）查看各版本`)
      } else {
        ElMessage.warning('暂无优化历史记录')
      }
      
      // 滚动到对应位置
      setTimeout(() => {
        const element = document.querySelector(`[data-resume-index="${jobIndex}"]`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 300)
    }

    // 获取优化类型名称
    const getOptimizationTypeName = (optimizationSummary) => {
      if (!optimizationSummary) return '未知类型'
      
      const typeMap = {
        'hr_feedback_based': 'HR反馈优化',
        'skill_enhancement': '技能强化优化',
        'keyword_optimization': '关键词优化',
        'structure_improvement': '结构改进优化',
        'content_refinement': '内容精炼优化'
      }
      
      // 如果有明确的优化类型，返回对应名称
      if (optimizationSummary.optimization_type) {
        return typeMap[optimizationSummary.optimization_type] || optimizationSummary.optimization_type
      }
      
      // 根据优化重点推断类型
      const focus = optimizationSummary.optimization_focus || []
      if (focus.some(f => f.includes('技能'))) {
        return '技能强化优化'
      } else if (focus.some(f => f.includes('关键词'))) {
        return '关键词优化'
      } else if (focus.some(f => f.includes('项目') || f.includes('经验'))) {
        return '经验展示优化'
      } else {
        return 'HR反馈优化'
      }
    }

    const saveOptimizationHistory = (jobIndex, optimizationData) => {
      if (!optimizationHistory.value[jobIndex]) {
        optimizationHistory.value[jobIndex] = []
      }
      optimizationHistory.value[jobIndex].push(optimizationData)
      
      // 保存到localStorage
      localStorage.setItem('optimizationHistory', JSON.stringify(optimizationHistory.value))
      
      // 设置默认活跃标签页
      if (!activeOptimizationTab.value[jobIndex]) {
        activeOptimizationTab.value[jobIndex] = 'current'
      }
    }

    const loadOptimizationHistory = () => {
      try {
        const historyStr = localStorage.getItem('optimizationHistory')
        if (historyStr) {
          optimizationHistory.value = JSON.parse(historyStr)
        }
        
        const originalsStr = localStorage.getItem('originalResumes')
        if (originalsStr) {
          originalResumes.value = JSON.parse(originalsStr)
        }
        
        // 初始化活跃标签页
        selectedJobs.value.forEach((_, index) => {
          if (!activeOptimizationTab.value[index]) {
            activeOptimizationTab.value[index] = 'current'
          }
        })
      } catch (e) {
        console.error('加载优化历史失败:', e)
      }
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
      userProfile,
      selectedJobs,
      activeJobIndex,
      generatedResumes,
      resumeStatus,
      activeResumeKeys,
      isGeneratingAll,
      isGeneratingSingle,
      generationProgress,
      currentGeneratingJob,
      inputVisible,
      inputValue,
      skillInput,
      formRules,
      
      // 优化历史相关状态
      optimizationHistory,
      activeOptimizationTab,
      originalResumes,
      
      // 编辑相关状态
      showEditMode,
      editingIndex,
      editingResume,
      newCompetencyVisible,
      newCompetencyValue,
      newCompetencyInput,
      newTechSkillVisible,
      newTechSkillValue,
      newTechSkillInput,
      newToolVisible,
      newToolValue,
      newToolInput,
      newSoftSkillVisible,
      newSoftSkillValue,
      newSoftSkillInput,
      
      setActiveJob,
      getResumeStatus,
      getResumeStatusText,
      getMatchScore,
      generateAllResumes,
      generateSingleResume,
      downloadResume,
      optimizeResume,
      editResume,
      saveEditedResume,
      cancelEdit,
      proceedToPhase3,
      
      // 优化历史相关方法
      getOptimizationCount,
      getOptimizationHistoryForJob,
      getOriginalResume,
      showOptimizationHistory,
      saveOptimizationHistory,
      loadOptimizationHistory,
      getOptimizationTypeName,
      
      // 添加的方法
      addExperience,
      removeExperience,
      updateDuration,
      addAchievement,
      removeAchievement,
      addEducation,
      removeEducation,
      updateEducationDuration,
      addProject,
      removeProject,
      showProjectTechInput,
      handleProjectTechConfirm,
      removeProjectTech,
      addProjectAchievement,
      removeProjectAchievement,
      
      // 原有方法
      getSkillType,
      showInput,
      handleInputConfirm,
      removeSkill,
      loadDemoProfile,

      // 新增方法
      handleOptimizationFromPhase3,
      showOptimizationComparison,
      loadExistingResumes,
      expandFirstResume,
      expandAllResumes,
      collapseAllResumes,
      debugResumeData,
      showNewCompetencyInput,
      addNewCompetency,
      showNewTechSkillInput,
      addNewTechSkill,
      showNewToolInput,
      addNewTool,
      showNewSoftSkillInput,
      addNewSoftSkill,
      addEducationToResume,
      removeEducationFromResume,
      addWorkExperience,
      removeWorkExperience,
      addProjectToResume,
      removeProjectFromResume,
      showProjectTechInputInResume,
      addProjectTechToResume,
      addCertification,
      removeCertification,
      addLanguage,
      removeLanguage,
      addProfDevelopment,
      removeProfDevelopment,
      addAward,
      removeAward,
      addPublication,
      removePublication,
      addVolunteer,
      removeVolunteer,
      addArrayItem,
      removeArrayItem,
      removeTag,
      // 粒子动画
      getParticleStyle
    }
  }
}
</script>

<style scoped>
.phase2-page {
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

.phase2-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.profile-card, .selected-jobs-card, .generation-progress-card, .actions-card {
  margin-bottom: 20px;
}

.card-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px 0;
  color: #409EFF;
}

.jobs-overview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.job-overview-item {
  padding: 12px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.job-overview-item:hover {
  border-color: #409EFF;
}

.job-overview-item.active {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.job-overview-item h5 {
  margin: 0 0 4px 0;
  font-weight: 600;
}

.job-overview-item p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.generation-progress {
  text-align: center;
  padding: 20px;
}

.resumes-container {
  margin-bottom: 20px;
}

.resume-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 折叠面板显示简历的样式 */
.resumes-collapse-display {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border: 2px solid #409EFF;
  border-radius: 12px;
  min-height: 100px;
}

/* 折叠面板标题样式 */
.resume-collapse-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 0;
}

.resume-collapse-title .job-info {
  flex: 1;
}

.resume-collapse-title .job-info h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #303133;
  font-weight: 600;
}

.resume-collapse-title .job-info p {
  margin: 4px 0 0 0;
  color: #666;
  font-size: 1rem;
}

.resume-collapse-title .resume-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 折叠面板内容样式 */
.resume-collapse-content {
  padding: 16px 0;
}

.resume-actions-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.resume-content-wrapper {
  margin-top: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* Element Plus 折叠面板自定义样式 */
.resumes-collapse-display :deep(.el-collapse) {
  border: none;
}

.resumes-collapse-display :deep(.el-collapse-item) {
  margin-bottom: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
}

.resumes-collapse-display :deep(.el-collapse-item:hover) {
  border-color: #409EFF;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.resumes-collapse-display :deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border: none;
  padding: 16px 20px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
}

.resumes-collapse-display :deep(.el-collapse-item__header.is-active) {
  background: linear-gradient(135deg, #e3f2fd, #f0f9ff);
  border-bottom-color: #409EFF;
}

.resumes-collapse-display :deep(.el-collapse-item__wrap) {
  border: none;
}

.resumes-collapse-display :deep(.el-collapse-item__content) {
  padding: 0;
}

.bottom-actions {
  text-align: center;
}

.skills-section {
  min-height: 40px;
  margin-bottom: 8px;
}

/* 编辑模态框样式 */
.resume-edit-modal {
  max-height: 80vh;
  overflow-y: auto;
}

.edit-tags-section {
  min-height: 40px;
  margin-bottom: 8px;
}

.edit-experience-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #f8f9fa;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Word文档下载提示样式 */
.download-hint {
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #409EFF;
  border-radius: 8px;
  margin-bottom: 16px;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jobs-overview {
    grid-template-columns: 1fr;
  }
  
  .resume-collapse-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .resume-edit-modal {
    width: 95% !important;
  }
}

/* 优化详情样式 */
.optimization-details {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
}

.optimization-summary {
  color: #495057;
}

.optimization-section {
  margin-bottom: 20px;
}

.optimization-section h4 {
  margin: 0 0 12px 0;
  color: #343a40;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.optimization-section ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.optimization-section li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #495057;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.stat-label {
  font-weight: 500;
  color: #6c757d;
}

.stat-value {
  font-weight: bold;
  color: #007bff;
}

.hr-feedback-summary {
  background: #fff3cd;
  border: 1px solid #ffeeba;
  border-radius: 6px;
  padding: 12px;
}

.feedback-item {
  margin-bottom: 12px;
}

.feedback-item:last-child {
  margin-bottom: 0;
}

.feedback-label {
  font-weight: 600;
  color: #856404;
  display: block;
  margin-bottom: 8px;
}

.feedback-item ul {
  margin: 0;
  padding-left: 16px;
}

.feedback-item li {
  color: #856404;
  margin-bottom: 4px;
}
</style>

