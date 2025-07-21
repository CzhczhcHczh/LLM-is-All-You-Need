<template>
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
        description="您可以查看下方生成的简历，进行下载或优化操作"
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
                    下载简历
                  </el-button>
                  <el-button 
                    size="small" 
                    type="warning"
                    @click="optimizeResume(index)"
                    :icon="Star"
                  >
                    优化简历
                  </el-button>
                  <el-button 
                    size="small" 
                    type="info"
                    @click="editResume(index)"
                    :icon="User"
                  >
                    编辑简历
                  </el-button>
                </el-button-group>
              </div>
              
              <!-- 简历内容显示 -->
              <div v-if="generatedResumes[index]" class="resume-content-wrapper" :data-resume-index="index">
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
</template>

<script>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
    
    // 页面加载时获取选择的职位
    onMounted(() => {
      const selectedJobsStr = localStorage.getItem('selectedJobs')
      if (selectedJobsStr) {
        selectedJobs.value = JSON.parse(selectedJobsStr)
        // 初始化简历状态
        selectedJobs.value.forEach((_, index) => {
          resumeStatus.value[index] = 'pending'
        })
        
        if (selectedJobs.value.length > 0) {
          activeJobIndex.value = 0
        }
      }
    })
    
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
    
    // 下载简历为PDF
    const downloadResume = async (index) => {
      const job = selectedJobs.value[index]
      const resume = generatedResumes.value[index]
      
      if (!resume) {
        ElMessage.warning('简历数据不存在，无法下载')
        return
      }
      
      try {
        ElMessage.info('正在生成PDF文件，请稍候...')
        
        // 动态导入html2pdf库
        const html2pdf = (await import('html2pdf.js')).default
        
        // 获取简历内容DOM元素
        const element = document.querySelector(`[data-resume-index="${index}"] .resume-content`)
        if (!element) {
          ElMessage.error('无法找到简历内容')
          return
        }
        
        // PDF配置选项
        const opt = {
          margin: [10, 10, 10, 10], // 页边距 [top, right, bottom, left] mm
          filename: `${job.job_title}_${job.company_name}_简历.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { 
            scale: 2, // 提高清晰度
            useCORS: true,
            letterRendering: true
          },
          jsPDF: { 
            unit: 'mm', 
            format: 'a4', 
            orientation: 'portrait' 
          }
        }
        
        // 生成并下载PDF
        await html2pdf().set(opt).from(element).save()
        
        ElMessage.success('简历PDF下载完成！')
        
      } catch (error) {
        console.error('PDF下载失败:', error)
        ElMessage.error('PDF生成失败，请稍后重试')
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
      removeTag
    }
  }
}
</script>

<style scoped>
.phase2-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
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

/* PDF下载提示样式 */
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
</style>

