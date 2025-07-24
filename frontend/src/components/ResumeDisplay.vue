<template>
  <div class="resume-display">
    <div class="resume-content">
      <!-- 简历头部 - 个人信息 -->
      <div class="resume-header">
        <div class="personal-info-main">
          <h1 class="candidate-name">{{ actualResumeData?.personal_info?.name || '未填写姓名' }}</h1>
          <div class="contact-info">
            <div class="contact-item">
              <el-icon><Message /></el-icon>
              <span>{{ actualResumeData?.personal_info?.email || '未填写邮箱' }}</span>
            </div>
            <div class="contact-item">
              <el-icon><Phone /></el-icon>
              <span>{{ actualResumeData?.personal_info?.phone || '未填写电话' }}</span>
            </div>
            <div class="contact-item">
              <el-icon><Location /></el-icon>
              <span>{{ actualResumeData?.personal_info?.location || '未填写地址' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 匹配度指示器 -->
        <div class="match-indicator" v-if="actualResumeData?.customization_analysis">
          <div class="match-score">
            <el-progress 
              type="circle" 
              :percentage="actualResumeData.customization_analysis.match_score || 0" 
              :width="80"
              :stroke-width="6"
              :color="getMatchColor(actualResumeData.customization_analysis.match_score || 0)"
            />
            <p class="match-text">匹配度</p>
          </div>
        </div>
      </div>

      <!-- 个人简介 -->
      <div class="resume-section" v-if="actualResumeData?.professional_summary">
        <div class="section-header">
          <h3><el-icon><User /></el-icon>个人简介</h3>
        </div>
        <div class="section-content">
          <p class="summary-text">{{ actualResumeData.professional_summary }}</p>
        </div>
      </div>

      <!-- 核心竞争力 -->
      <div class="resume-section" v-if="actualResumeData?.core_competencies && actualResumeData.core_competencies.length > 0">
        <div class="section-header">
          <h3><el-icon><Star /></el-icon>核心竞争力</h3>
        </div>
        <div class="section-content">
          <div class="competencies-grid">
            <div 
              v-for="(competency, index) in actualResumeData.core_competencies" 
              :key="index"
              class="competency-item"
            >
              <el-icon class="competency-icon"><Medal /></el-icon>
              <span>{{ competency }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 核心技能 -->
      <div class="resume-section" v-if="actualResumeData?.highlighted_skills">
        <div class="section-header">
          <h3><el-icon><Tools /></el-icon>核心技能</h3>
        </div>
        <div class="section-content">
          <div class="skills-container">
            <!-- 技术技能 -->
            <div v-if="actualResumeData.highlighted_skills.technical_skills && actualResumeData.highlighted_skills.technical_skills.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Monitor /></el-icon>技术技能
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="skill in actualResumeData.highlighted_skills.technical_skills" 
                  :key="skill"
                  type="success"
                  effect="dark"
                  size="large"
                  class="skill-tag"
                >
                  {{ skill }}
                </el-tag>
              </div>
            </div>
            
            <!-- 框架和工具 -->
            <div v-if="actualResumeData.highlighted_skills.frameworks_tools && actualResumeData.highlighted_skills.frameworks_tools.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Setting /></el-icon>框架和工具
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="tool in actualResumeData.highlighted_skills.frameworks_tools" 
                  :key="tool"
                  type="warning"
                  effect="dark"
                  size="large"
                  class="skill-tag"
                >
                  {{ tool }}
                </el-tag>
              </div>
            </div>

            <!-- 软技能 -->
            <div v-if="actualResumeData.highlighted_skills.soft_skills && actualResumeData.highlighted_skills.soft_skills.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><UserFilled /></el-icon>软技能
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="skill in actualResumeData.highlighted_skills.soft_skills" 
                  :key="skill"
                  type="info"
                  effect="dark"
                  size="large"
                  class="skill-tag"
                >
                  {{ skill }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 教育背景 -->
      <div class="resume-section" v-if="actualResumeData?.education && actualResumeData.education.length > 0">
        <div class="section-header">
          <h3><el-icon><School /></el-icon>教育背景</h3>
        </div>
        <div class="section-content">
          <div class="education-grid">
            <div 
              v-for="(edu, index) in actualResumeData.education" 
              :key="index" 
              class="education-card"
            >
              <div class="education-header">
                <h4>{{ edu.institution }}</h4>
                <el-tag type="primary" size="large">{{ edu.degree }}</el-tag>
              </div>
              <div class="education-details">
                <div class="education-major">
                  <el-icon><Reading /></el-icon>
                  <span>{{ edu.major }}</span>
                </div>
                <div class="education-duration">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ edu.duration }}</span>
                </div>
                <div v-if="edu.location" class="education-location">
                  <el-icon><Location /></el-icon>
                  <span>{{ edu.location }}</span>
                </div>
                <div v-if="edu.gpa" class="education-gpa">
                  <el-icon><Star /></el-icon>
                  <span>GPA: {{ edu.gpa }}</span>
                </div>
              </div>
              
              <!-- 相关课程 -->
              <div v-if="edu.relevant_coursework && edu.relevant_coursework.length > 0" class="education-coursework">
                <h6><el-icon><Document /></el-icon>相关课程</h6>
                <div class="coursework-tags">
                  <el-tag 
                    v-for="course in edu.relevant_coursework" 
                    :key="course"
                    type="info"
                    size="small"
                    class="course-tag"
                  >
                    {{ course }}
                  </el-tag>
                </div>
              </div>

              <!-- 学术成就 -->
              <div v-if="edu.academic_achievements && edu.academic_achievements.length > 0" class="education-achievements">
                <h6><el-icon><Medal /></el-icon>学术成就</h6>
                <ul class="achievement-list">
                  <li v-for="achievement in edu.academic_achievements" :key="achievement">
                    <el-icon class="achievement-icon"><Trophy /></el-icon>
                    {{ achievement }}
                  </li>
                </ul>
              </div>

              <!-- 毕业论文 -->
              <div v-if="edu.graduation_thesis" class="education-thesis">
                <h6><el-icon><Notebook /></el-icon>毕业论文</h6>
                <p class="thesis-title">{{ edu.graduation_thesis }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工作经验 -->
      <div class="resume-section" v-if="actualResumeData?.professional_experience && actualResumeData.professional_experience.length > 0">
        <div class="section-header">
          <h3><el-icon><OfficeBuilding /></el-icon>工作经验</h3>
        </div>
        <div class="section-content">
          <div class="timeline">
            <div 
              v-for="(exp, index) in actualResumeData.professional_experience" 
              :key="index" 
              class="timeline-item"
            >
              <div class="timeline-marker"></div>
              <div class="timeline-content experience-card">
                <div class="experience-header">
                  <div class="experience-title">
                    <h4>{{ exp.position }}</h4>
                    <h5>{{ exp.company }}</h5>
                  </div>
                  <div class="experience-meta">
                    <el-tag type="primary" size="small">{{ exp.employment_type || '全职' }}</el-tag>
                    <span class="duration">{{ exp.duration }}</span>
                    <span class="location" v-if="exp.location">{{ exp.location }}</span>
                  </div>
                </div>
                
                <p v-if="exp.company_description" class="company-description">
                  {{ exp.company_description }}
                </p>
                
                <!-- 工作职责 -->
                <div v-if="exp.responsibilities && exp.responsibilities.length > 0" class="responsibilities">
                  <h6><el-icon><List /></el-icon>主要职责</h6>
                  <ul class="responsibility-list">
                    <li v-for="responsibility in exp.responsibilities" :key="responsibility">
                      <el-icon class="list-icon"><ArrowRight /></el-icon>
                      {{ responsibility }}
                    </li>
                  </ul>
                </div>
                
                <!-- 关键成就 -->
                <div v-if="exp.key_achievements && exp.key_achievements.length > 0" class="achievements">
                  <h6><el-icon><Trophy /></el-icon>关键成就</h6>
                  <ul class="achievement-list">
                    <li v-for="achievement in exp.key_achievements" :key="achievement">
                      <el-icon class="achievement-icon"><Medal /></el-icon>
                      {{ achievement }}
                    </li>
                  </ul>
                </div>

                <!-- 使用技术 -->
                <div v-if="exp.technologies_used && exp.technologies_used.length > 0" class="technologies-used">
                  <h6><el-icon><Cpu /></el-icon>使用技术</h6>
                  <div class="tech-tags">
                    <el-tag 
                      v-for="tech in exp.technologies_used" 
                      :key="tech"
                      type="primary"
                      size="small"
                      class="tech-tag"
                    >
                      {{ tech }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目经验 -->
      <div class="resume-section" v-if="actualResumeData?.key_projects && actualResumeData.key_projects.length > 0">
        <div class="section-header">
          <h3><el-icon><FolderOpened /></el-icon>项目经验</h3>
        </div>
        <div class="section-content">
          <div class="projects-timeline">
            <div 
              v-for="(project, index) in actualResumeData.key_projects" 
              :key="index" 
              class="project-item"
            >
              <div class="project-card">
                <div class="project-header">
                  <div class="project-title">
                    <h4>{{ project.name }}</h4>
                    <el-tag type="success" size="small">{{ project.role }}</el-tag>
                  </div>
                  <div class="project-meta">
                    <span class="project-duration">{{ project.duration }}</span>
                    <span class="team-size" v-if="project.team_size">团队: {{ project.team_size }}</span>
                    <el-tag type="info" size="small" v-if="project.project_scale">{{ project.project_scale }}</el-tag>
                  </div>
                </div>

                <p class="project-description">{{ project.description }}</p>

                <!-- 主要职责 -->
                <div v-if="project.key_responsibilities && project.key_responsibilities.length > 0" class="project-responsibilities">
                  <h6><el-icon><List /></el-icon>主要职责</h6>
                  <ul class="responsibility-list">
                    <li v-for="responsibility in project.key_responsibilities" :key="responsibility">
                      <el-icon class="list-icon"><ArrowRight /></el-icon>
                      {{ responsibility }}
                    </li>
                  </ul>
                </div>

                <!-- 技术栈 -->
                <div v-if="project.technologies_stack" class="project-technologies">
                  <h6><el-icon><Platform /></el-icon>技术栈</h6>
                  <div class="tech-stack-grid">
                    <div v-if="project.technologies_stack.frontend && project.technologies_stack.frontend.length > 0" class="tech-category">
                      <span class="tech-category-label">前端:</span>
                      <div class="tech-tags">
                        <el-tag 
                          v-for="tech in project.technologies_stack.frontend" 
                          :key="tech"
                          type="success"
                          size="small"
                        >
                          {{ tech }}
                        </el-tag>
                      </div>
                    </div>
                    <div v-if="project.technologies_stack.backend && project.technologies_stack.backend.length > 0" class="tech-category">
                      <span class="tech-category-label">后端:</span>
                      <div class="tech-tags">
                        <el-tag 
                          v-for="tech in project.technologies_stack.backend" 
                          :key="tech"
                          type="warning"
                          size="small"
                        >
                          {{ tech }}
                        </el-tag>
                      </div>
                    </div>
                    <div v-if="project.technologies_stack.database && project.technologies_stack.database.length > 0" class="tech-category">
                      <span class="tech-category-label">数据库:</span>
                      <div class="tech-tags">
                        <el-tag 
                          v-for="tech in project.technologies_stack.database" 
                          :key="tech"
                          type="info"
                          size="small"
                        >
                          {{ tech }}
                        </el-tag>
                      </div>
                    </div>
                    <div v-if="project.technologies_stack.tools && project.technologies_stack.tools.length > 0" class="tech-category">
                      <span class="tech-category-label">工具:</span>
                      <div class="tech-tags">
                        <el-tag 
                          v-for="tech in project.technologies_stack.tools" 
                          :key="tech"
                          type="primary"
                          size="small"
                        >
                          {{ tech }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 项目成果 -->
                <div v-if="project.achievements_metrics && project.achievements_metrics.length > 0" class="project-achievements">
                  <h6><el-icon><TrendCharts /></el-icon>项目成果</h6>
                  <ul class="achievement-list">
                    <li v-for="achievement in project.achievements_metrics" :key="achievement">
                      <el-icon class="achievement-icon"><Medal /></el-icon>
                      {{ achievement }}
                    </li>
                  </ul>
                </div>

                <!-- 挑战与解决方案 -->
                <div v-if="project.challenges_solutions" class="project-challenges">
                  <h6><el-icon><Lightning /></el-icon>挑战与解决方案</h6>
                  <p class="challenges-text">{{ project.challenges_solutions }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 技术技能详情 -->
      <div class="resume-section" v-if="actualResumeData?.technical_skills">
        <div class="section-header">
          <h3><el-icon><Cpu /></el-icon>技术技能详情</h3>
        </div>
        <div class="section-content">
          <div class="technical-skills-grid">
            <div v-if="actualResumeData.technical_skills.programming_languages && actualResumeData.technical_skills.programming_languages.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Monitor /></el-icon>编程语言
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="lang in actualResumeData.technical_skills.programming_languages" 
                  :key="lang"
                  type="primary"
                  class="skill-tag"
                >
                  {{ lang }}
                </el-tag>
              </div>
            </div>

            <div v-if="actualResumeData.technical_skills.frameworks_libraries && actualResumeData.technical_skills.frameworks_libraries.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Platform /></el-icon>框架库
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="framework in actualResumeData.technical_skills.frameworks_libraries" 
                  :key="framework"
                  type="success"
                  class="skill-tag"
                >
                  {{ framework }}
                </el-tag>
              </div>
            </div>

            <div v-if="actualResumeData.technical_skills.databases && actualResumeData.technical_skills.databases.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><DataBoard /></el-icon>数据库
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="db in actualResumeData.technical_skills.databases" 
                  :key="db"
                  type="warning"
                  class="skill-tag"
                >
                  {{ db }}
                </el-tag>
              </div>
            </div>

            <div v-if="actualResumeData.technical_skills.cloud_platforms && actualResumeData.technical_skills.cloud_platforms.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Grid /></el-icon>云平台
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="cloud in actualResumeData.technical_skills.cloud_platforms" 
                  :key="cloud"
                  type="info"
                  class="skill-tag"
                >
                  {{ cloud }}
                </el-tag>
              </div>
            </div>

            <div v-if="actualResumeData.technical_skills.development_tools && actualResumeData.technical_skills.development_tools.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Operation /></el-icon>开发工具
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="tool in actualResumeData.technical_skills.development_tools" 
                  :key="tool"
                  type="danger"
                  class="skill-tag"
                >
                  {{ tool }}
                </el-tag>
              </div>
            </div>

            <div v-if="actualResumeData.technical_skills.methodologies && actualResumeData.technical_skills.methodologies.length > 0" class="skill-category">
              <h4 class="skill-category-title">
                <el-icon><Compass /></el-icon>方法论
              </h4>
              <div class="skills-tags">
                <el-tag 
                  v-for="method in actualResumeData.technical_skills.methodologies" 
                  :key="method"
                  class="skill-tag"
                >
                  {{ method }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 认证证书 -->
      <div class="resume-section" v-if="actualResumeData?.certifications && actualResumeData.certifications.length > 0">
        <div class="section-header">
          <h3><el-icon><Medal /></el-icon>认证证书</h3>
        </div>
        <div class="section-content">
          <div class="certifications-grid">
            <div 
              v-for="(cert, index) in actualResumeData.certifications" 
              :key="index" 
              class="certification-card"
            >
              <div class="cert-header">
                <h4>{{ cert.name }}</h4>
                <el-tag type="primary" size="small">{{ cert.issuer }}</el-tag>
              </div>
              <div class="cert-details">
                <div class="cert-date">
                  <el-icon><Calendar /></el-icon>
                  <span>获得时间: {{ cert.date_obtained }}</span>
                </div>
                <div class="cert-validity">
                  <el-icon><Clock /></el-icon>
                  <span>有效期: {{ cert.validity }}</span>
                </div>
                <div v-if="cert.credential_id" class="cert-id">
                  <el-icon><Document /></el-icon>
                  <span>证书编号: {{ cert.credential_id }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 语言能力 -->
      <div class="resume-section" v-if="actualResumeData?.languages && actualResumeData.languages.length > 0">
        <div class="section-header">
          <h3><el-icon><ChatDotRound /></el-icon>语言能力</h3>
        </div>
        <div class="section-content">
          <div class="languages-grid">
            <div 
              v-for="(lang, index) in actualResumeData.languages" 
              :key="index" 
              class="language-card"
            >
              <div class="language-header">
                <h4>{{ lang.language }}</h4>
                <el-tag 
                  :type="lang.proficiency.includes('良好') ? 'success' : lang.proficiency.includes('基础') ? 'warning' : 'primary'"
                  size="small"
                >
                  {{ lang.proficiency }}
                </el-tag>
              </div>
              <div v-if="lang.certifications" class="language-cert">
                <el-icon><Stamp /></el-icon>
                <span>{{ lang.certifications }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 职业发展 -->
      <div class="resume-section" v-if="actualResumeData?.professional_development && actualResumeData.professional_development.length > 0">
        <div class="section-header">
          <h3><el-icon><TrendCharts /></el-icon>职业发展</h3>
        </div>
        <div class="section-content">
          <ul class="development-list">
            <li v-for="(item, index) in actualResumeData.professional_development" :key="index" class="development-item">
              <el-icon class="development-icon"><CircleCheck /></el-icon>
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 附加信息 -->
      <div class="resume-section" v-if="actualResumeData?.additional_information">
        <div class="section-header">
          <h3><el-icon><InfoFilled /></el-icon>附加信息</h3>
        </div>
        <div class="section-content">
          <div class="additional-info-grid">
            <div v-if="actualResumeData.additional_information.availability" class="info-item">
              <h5><el-icon><Clock /></el-icon>到岗时间</h5>
              <p>{{ actualResumeData.additional_information.availability }}</p>
            </div>
            <div v-if="actualResumeData.additional_information.salary_expectation" class="info-item">
              <h5><el-icon><Money /></el-icon>期望薪资</h5>
              <p>{{ actualResumeData.additional_information.salary_expectation }}</p>
            </div>
            <div v-if="actualResumeData.additional_information.work_preference" class="info-item">
              <h5><el-icon><House /></el-icon>工作偏好</h5>
              <p>{{ actualResumeData.additional_information.work_preference }}</p>
            </div>
            <div v-if="actualResumeData.additional_information.relocation_willingness" class="info-item">
              <h5><el-icon><Position /></el-icon>搬迁意愿</h5>
              <p>{{ actualResumeData.additional_information.relocation_willingness }}</p>
            </div>
            <div v-if="actualResumeData.additional_information.travel_availability" class="info-item">
              <h5><el-icon><Promotion /></el-icon>出差安排</h5>
              <p>{{ actualResumeData.additional_information.travel_availability }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 定制分析 -->
      <div class="resume-section" v-if="actualResumeData?.customization_analysis">
        <div class="section-header">
          <h3><el-icon><DataAnalysis /></el-icon>简历定制分析</h3>
        </div>
        <div class="section-content">
          <div class="customization-analysis">
            <div class="analysis-header">
              <h4>针对 {{ actualResumeData.customization_analysis.target_company }} - {{ actualResumeData.customization_analysis.target_position }} 职位定制</h4>
              <div class="match-score-display">
                <el-progress 
                  type="dashboard" 
                  :percentage="actualResumeData.customization_analysis.match_score || 0"
                  :color="getMatchColor(actualResumeData.customization_analysis.match_score || 0)"
                  :width="120"
                  :stroke-width="8"
                >
                  <template #default="{ percentage }">
                    <span class="percentage-value">{{ percentage }}%</span>
                    <div class="percentage-label">匹配度</div>
                  </template>
                </el-progress>
              </div>
            </div>
            
            <div class="analysis-content">
              <div class="analysis-item" v-if="actualResumeData.customization_analysis.key_selling_points && actualResumeData.customization_analysis.key_selling_points.length > 0">
                <h5><el-icon><Star /></el-icon>核心卖点</h5>
                <div class="selling-points">
                  <el-tag 
                    v-for="point in actualResumeData.customization_analysis.key_selling_points" 
                    :key="point"
                    type="success"
                    effect="dark"
                    size="large"
                    class="selling-point-tag"
                  >
                    {{ point }}
                  </el-tag>
                </div>
              </div>
              
              <div class="analysis-item" v-if="actualResumeData.customization_analysis.growth_potential">
                <h5><el-icon><Aim /></el-icon>发展潜力</h5>
                <p class="growth-potential-text">{{ actualResumeData.customization_analysis.growth_potential }}</p>
              </div>
              
              <div class="analysis-item" v-if="actualResumeData.customization_analysis.value_proposition">
                <h5><el-icon><Present /></el-icon>价值主张</h5>
                <div class="value-proposition-card">
                  <p>{{ actualResumeData.customization_analysis.value_proposition }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { 
  Message, Phone, Location, User, Star, Medal, Tools, Monitor, Setting, 
  OfficeBuilding, List, ArrowRight, Trophy, Cpu, FolderOpened, UserFilled, DataBoard, 
  Check, Platform, TrendCharts, CircleCheck, Lightning, School, Reading, 
  Calendar, Document, Notebook, Grid, Coin, Operation, 
  Files, Stamp, ChatDotRound, Promotion, InfoFilled, Clock, Money, House, 
  Position, Compass, DataAnalysis, Aim, Present
} from '@element-plus/icons-vue'

export default {
  name: 'ResumeDisplay',
  components: {
    Message, Phone, Location, User, Star, Medal, Tools, Monitor, Setting,
    OfficeBuilding, List, ArrowRight, Trophy, Cpu, FolderOpened, UserFilled, DataBoard,
    Check, Platform, TrendCharts, CircleCheck, Lightning, School, Reading,
    Calendar, Document, Notebook, Grid, Coin, Operation,
    Files, Stamp, ChatDotRound, Promotion, InfoFilled, Clock, Money, House,
    Position, Compass, DataAnalysis, Aim, Present
  },
  props: {
    resumeData: {
      type: Object,
      required: true
    },
    jobInfo: {
      type: Object,
      required: true
    }
  },
  emits: ['edit', 'optimize'],
  setup(props, { emit }) {
    // 添加计算属性来处理可能的嵌套数据结构
    const actualResumeData = computed(() => {
      const data = props.resumeData
      
      // 如果数据直接在根级别
      if (data?.personal_info) {
        return data
      }
      
      // 如果数据在 data.content 中
      if (data?.data?.content) {
        return data.data.content
      }
      
      // 如果数据在 content 中
      if (data?.content) {
        return data.content
      }
      
      // 返回原始数据
      return data
    })
    
    const editResume = () => {
      emit('edit')
    }
    
    const optimizeResume = () => {
      emit('optimize')
    }
    
    const getMatchColor = (percentage) => {
      if (percentage >= 80) return '#67c23a'
      if (percentage >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    return {
      actualResumeData,
      editResume,
      optimizeResume,
      getMatchColor
    }
  }
}
</script>

<style scoped>
.resume-display {
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  min-height: 200px;
  border: 2px dashed #409EFF;
  background: white;
}

.resume-content {
  padding: 20px;
  line-height: 1.6;
  background: #f5f5f5;
  border: 1px solid #ccc;
}

/* 简历头部 */
.resume-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 30px 0;
  border-bottom: 3px solid #409EFF;
  margin-bottom: 30px;
}

.personal-info-main {
  flex: 1;
}

.candidate-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: #303133;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.contact-info {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 1rem;
}

.contact-item .el-icon {
  color: #409EFF;
  font-size: 1.1rem;
}

.match-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.match-text {
  margin-top: 8px;
  color: #606266;
  font-weight: 500;
  font-size: 0.9rem;
}

/* 节标题 */
.resume-section {
  margin-bottom: 40px;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e4e7ed;
  position: relative;
}

.section-header h3::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(135deg, #409EFF, #67C23A);
}

.section-header h3 .el-icon {
  color: #409EFF;
  font-size: 1.3rem;
}

.section-content {
  padding-left: 16px;
}

/* 个人简介 */
.summary-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #303133;
  text-align: justify;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border-left: 4px solid #409EFF;
  margin: 0;
}

/* 核心竞争力 */
.competencies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.competency-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.competency-item:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.competency-icon {
  color: #f39c12;
  font-size: 1.2rem;
}

/* 技能区域 */
.skills-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.skill-category {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.skill-category-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.skill-category-title .el-icon {
  color: #409EFF;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  font-weight: 500;
  border-radius: 6px;
}

/* 时间线样式 */
.timeline {
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #409EFF, #67C23A);
}

.timeline-item {
  position: relative;
  margin-bottom: 32px;
}

.timeline-marker {
  position: absolute;
  left: 16px;
  top: 16px;
  width: 16px;
  height: 16px;
  background: #409EFF;
  border: 4px solid white;
  border-radius: 50%;
  box-shadow: 0 0 0 2px #409EFF;
  z-index: 1;
}

.timeline-content {
  margin-left: 60px;
}

/* 工作经验卡片 */
.experience-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.experience-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.experience-title h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.experience-title h5 {
  font-size: 1.1rem;
  color: #409EFF;
  margin: 0;
  font-weight: 500;
}

.experience-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  text-align: right;
}

.duration, .location {
  color: #606266;
  font-size: 0.9rem;
}

.company-description {
  color: #606266;
  font-style: italic;
  margin: 0 0 16px 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.responsibilities, .achievements {
  margin-bottom: 20px;
}

.responsibilities h6, .achievements h6 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-weight: 600;
  margin: 0 0 12px 0;
  font-size: 1rem;
}

.responsibility-list, .achievement-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.responsibility-list li, .achievement-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  line-height: 1.6;
}

.list-icon {
  color: #409EFF;
  margin-top: 4px;
  font-size: 0.8rem;
}

.achievement-icon {
  color: #f39c12;
  margin-top: 4px;
  font-size: 0.9rem;
}

.achievement-list li {
  color: #e6a23c;
  font-weight: 500;
}

/* 教育背景 */
.education-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.education-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.education-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.education-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.education-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.education-major,
.education-duration {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 0.9rem;
}

.education-major .el-icon,
.education-duration .el-icon {
  color: #409EFF;
  font-size: 0.9rem;
}

/* 定制分析 */
.customization-analysis {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e4e7ed;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analysis-header h4 {
  color: #303133;
  font-weight: 600;
  margin: 0;
  font-size: 1.2rem;
}

.match-score-display .percentage-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #303133;
}

.percentage-label {
  color: #606266;
  font-size: 0.8rem;
  margin-top: 4px;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analysis-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.analysis-item:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.selling-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selling-point-tag {
  font-weight: 500;
  border-radius: 6px;
}

.growth-potential-text,
.value-proposition {
  color: #303133;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.value-proposition-card {
  background: #f0f9ff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #67c23a;
}

/* 项目经验样式 */
.projects-timeline {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.project-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.project-item:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.project-card {
  padding: 24px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.project-title h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.project-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  text-align: right;
}

.project-duration,
.team-size {
  color: #606266;
  font-size: 0.9rem;
}

.project-description {
  color: #606266;
  margin: 0 0 20px 0;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.project-responsibilities,
.project-technologies,
.project-achievements,
.project-challenges {
  margin-bottom: 20px;
}

.project-responsibilities h6,
.project-technologies h6,
.project-achievements h6,
.project-challenges h6 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-weight: 600;
  margin: 0 0 12px 0;
  font-size: 1rem;
}

.tech-stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.tech-category {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tech-category-label {
  font-weight: 600;
  color: #303133;
  font-size: 0.9rem;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tech-tag {
  font-size: 0.8rem;
}

.challenges-text {
  color: #303133;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

/* 技术技能详情样式 */
.technical-skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

/* 认证证书样式 */
.certifications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.certification-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.cert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.cert-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.cert-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cert-date,
.cert-validity,
.cert-id {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 0.9rem;
}

.cert-date .el-icon,
.cert-validity .el-icon,
.cert-id .el-icon {
  color: #409EFF;
  font-size: 0.9rem;
}

/* 语言能力样式 */
.languages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.language-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.language-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.language-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.language-cert {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 0.9rem;
}

.language-cert .el-icon {
  color: #409EFF;
  font-size: 0.9rem;
}

/* 职业发展样式 */
.development-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.development-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.development-icon {
  color: #67c23a;
  margin-top: 2px;
  font-size: 1.1rem;
}

/* 附加信息样式 */
.additional-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-item h5 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-weight: 600;
  margin: 0 0 8px 0;
  font-size: 1rem;
}

.info-item h5 .el-icon {
  color: #409EFF;
  font-size: 1rem;
}

.info-item p {
  color: #606266;
  margin: 0;
  line-height: 1.4;
}

/* 工作经验中的技术使用样式 */
.technologies-used {
  margin-bottom: 16px;
}

.technologies-used h6 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-weight: 600;
  margin: 0 0 8px 0;
  font-size: 0.95rem;
}

.technologies-used .tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.technologies-used .tech-tag {
  font-size: 0.8rem;
}

/* 教育背景增强样式 */
.education-location,
.education-gpa {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 0.9rem;
}

.education-location .el-icon,
.education-gpa .el-icon {
  color: #409EFF;
  font-size: 0.9rem;
}

.education-coursework,
.education-achievements,
.education-thesis {
  margin-top: 16px;
}

.education-coursework h6,
.education-achievements h6,
.education-thesis h6 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-weight: 600;
  margin: 0 0 8px 0;
  font-size: 0.95rem;
}

.coursework-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.course-tag {
  font-size: 0.8rem;
}

.thesis-title {
  color: #303133;
  font-style: italic;
  margin: 0;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
}
</style>
