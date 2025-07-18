<template>
  <div class="phase2-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Document /></el-icon> Phase 2: 简历制作</h2>
          <p>填写您的个人信息，我们将为您生成个性化简历</p>
        </div>
      </template>

      <!-- User Profile Form -->
      <el-form :model="userProfile" label-width="120px" ref="profileForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="userProfile.full_name" placeholder="请输入您的姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" required>
              <el-input v-model="userProfile.email" placeholder="请输入邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="userProfile.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标职位">
              <el-input v-model="userProfile.target_position" placeholder="期望的职位" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="技能">
          <el-tag
            v-for="skill in userProfile.skills"
            :key="skill"
            closable
            @close="removeSkill(skill)"
            style="margin-right: 8px; margin-bottom: 8px;"
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
        </el-form-item>

        <el-form-item label="工作经验">
          <div v-for="(exp, index) in userProfile.experience" :key="index" class="experience-item">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-input v-model="exp.company" placeholder="公司名称" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="exp.position" placeholder="职位" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="exp.duration" placeholder="时间段" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" size="small" @click="removeExperience(index)">删除</el-button>
              </el-col>
            </el-row>
            <el-input
              v-model="exp.description"
              type="textarea"
              placeholder="工作描述"
              style="margin-top: 8px;"
            />
          </div>
          <el-button @click="addExperience" type="primary" size="small">添加工作经验</el-button>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="generateResume"
            :loading="store.resumes.loading"
            size="large"
          >
            <el-icon><Magic /></el-icon>
            生成简历
          </el-button>
          
          <el-button @click="loadDemoProfile" type="success" size="large">
            <el-icon><User /></el-icon>
            加载示例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Generated Resume -->
    <el-card v-if="generatedResume" class="resume-card">
      <template #header>
        <div class="resume-header">
          <h3>生成的简历</h3>
          <div>
            <el-button @click="editResume" type="primary">编辑简历</el-button>
            <el-button @click="proceedToPhase3" type="success">进入下一阶段</el-button>
          </div>
        </div>
      </template>

      <div class="resume-content">
        <!-- Personal Info -->
        <div class="resume-section">
          <h4>个人信息</h4>
          <p><strong>姓名：</strong>{{ generatedResume.personal_info?.name }}</p>
          <p><strong>邮箱：</strong>{{ generatedResume.personal_info?.email }}</p>
          <p><strong>电话：</strong>{{ generatedResume.personal_info?.phone }}</p>
        </div>

        <!-- Summary -->
        <div class="resume-section" v-if="generatedResume.summary">
          <h4>个人简介</h4>
          <p>{{ generatedResume.summary }}</p>
        </div>

        <!-- Experience -->
        <div class="resume-section" v-if="generatedResume.experience">
          <h4>工作经验</h4>
          <div v-for="exp in generatedResume.experience" :key="exp.company" class="experience-block">
            <h5>{{ exp.position }} - {{ exp.company }}</h5>
            <p class="duration">{{ exp.duration }}</p>
            <p>{{ exp.description }}</p>
            <ul v-if="exp.achievements">
              <li v-for="achievement in exp.achievements" :key="achievement">{{ achievement }}</li>
            </ul>
          </div>
        </div>

        <!-- Skills -->
        <div class="resume-section" v-if="generatedResume.skills">
          <h4>技能</h4>
          <div class="skills-list">
            <el-tag 
              v-for="skill in generatedResume.skills" 
              :key="skill"
              style="margin: 2px 4px;"
            >
              {{ skill }}
            </el-tag>
          </div>
        </div>

        <!-- Projects -->
        <div class="resume-section" v-if="generatedResume.projects">
          <h4>项目经验</h4>
          <div v-for="project in generatedResume.projects" :key="project.name" class="project-block">
            <h5>{{ project.name }}</h5>
            <p>{{ project.description }}</p>
            <div v-if="project.technologies">
              <strong>技术栈：</strong>
              <el-tag 
                v-for="tech in project.technologies" 
                :key="tech"
                size="small"
                style="margin: 2px;"
              >
                {{ tech }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Loading State -->
    <el-card v-if="store.resumes.loading" class="loading-card">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <h3>正在生成简历...</h3>
        <p>AI正在根据您的信息和目标职位生成个性化简历</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Promotion, User, Loading } from '@element-plus/icons-vue'
import { useAppStore } from '../store.js'
import { apiService } from '../api.js'

export default {
  name: 'Phase2',
  components: {
    Document,
    Promotion,
    User,
    Loading
  },
  setup() {
    const router = useRouter()
    const store = useAppStore()
    
    const userProfile = reactive({
      full_name: '',
      email: '',
      phone: '',
      target_position: '',
      skills: [],
      experience: []
    })
    
    const generatedResume = ref(null)
    const inputVisible = ref(false)
    const inputValue = ref('')
    const skillInput = ref(null)
    
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
    
    const addExperience = () => {
      userProfile.experience.push({
        company: '',
        position: '',
        duration: '',
        description: ''
      })
    }
    
    const removeExperience = (index) => {
      userProfile.experience.splice(index, 1)
    }
    
    const loadDemoProfile = () => {
      Object.assign(userProfile, {
        full_name: '张三',
        email: 'zhangsan@example.com',
        phone: '13800138000',
        target_position: '前端开发工程师',
        skills: ['Vue.js', 'React', 'JavaScript', 'CSS3', 'Node.js'],
        experience: [
          {
            company: '某科技公司',
            position: '前端开发工程师',
            duration: '2021.06 - 2023.12',
            description: '负责公司主要产品的前端开发，使用Vue.js和React技术栈，参与了多个重要项目的开发和维护。'
          },
          {
            company: '某互联网公司',
            position: '前端实习生',
            duration: '2020.09 - 2021.05',
            description: '参与前端页面开发，学习并掌握了现代前端开发技术，积累了丰富的项目经验。'
          }
        ]
      })
      ElMessage.success('示例数据加载完成')
    }
    
    const generateResume = async () => {
      if (!userProfile.full_name || !userProfile.email) {
        ElMessage.warning('请填写基本信息')
        return
      }
      
      // Get selected job from Phase 1
      const selectedJobStr = localStorage.getItem('selectedJob')
      if (!selectedJobStr) {
        ElMessage.warning('请先在Phase 1中选择一个职位')
        router.push('/phase1')
        return
      }
      
      const selectedJob = JSON.parse(selectedJobStr)
      
      store.setResumeLoading(true)
      
      try {
        const response = await apiService.generateResume({
          user_profile: userProfile,
          job_posting: selectedJob
        })
        
        if (response.success) {
          generatedResume.value = response.data.content
          store.addResume({
            id: Date.now(),
            content: response.data.content,
            job_title: selectedJob.job_title,
            company_name: selectedJob.company_name,
            created_at: new Date().toISOString()
          })
          ElMessage.success('简历生成成功')
        } else {
          ElMessage.error(response.message || '简历生成失败')
        }
      } catch (error) {
        console.error('Resume generation error:', error)
        ElMessage.error('简历生成过程中出现错误')
      } finally {
        store.setResumeLoading(false)
      }
    }
    
    const editResume = () => {
      ElMessage.info('简历编辑功能开发中...')
    }
    
    const proceedToPhase3 = () => {
      if (!generatedResume.value) {
        ElMessage.warning('请先生成简历')
        return
      }
      
      // Store generated resume for next phase
      localStorage.setItem('generatedResume', JSON.stringify(generatedResume.value))
      
      store.setCurrentPhase(3)
      router.push('/phase3')
    }
    
    return {
      store,
      userProfile,
      generatedResume,
      inputVisible,
      inputValue,
      skillInput,
      showInput,
      handleInputConfirm,
      removeSkill,
      addExperience,
      removeExperience,
      loadDemoProfile,
      generateResume,
      editResume,
      proceedToPhase3
    }
  }
}
</script>

<style scoped>
.phase2-container {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card, .resume-card {
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

.experience-item {
  border: 1px solid #ddd;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 4px;
  background: #fafafa;
}

.resume-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-content {
  max-height: 600px;
  overflow-y: auto;
}

.resume-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.resume-section:last-child {
  border-bottom: none;
}

.resume-section h4 {
  color: #409EFF;
  margin-bottom: 12px;
  font-size: 16px;
}

.experience-block, .project-block {
  margin-bottom: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
}

.experience-block h5, .project-block h5 {
  margin: 0 0 4px 0;
  color: #303133;
}

.duration {
  color: #666;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.skills-list {
  line-height: 2;
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
</style>

