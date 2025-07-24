import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 确保后端服务地址正确
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API functions
export const apiService = {
  // ChromaDB Admin APIs
  getChromaStats() {
    return api.get('/admin/chroma/stats')
  },
  
  getChromaJobs(params = {}) {
    return api.get('/admin/chroma/jobs', { params })
  },
  
  getChromaJobDetail(jobId) {
    return api.get(`/admin/chroma/jobs/${jobId}`)
  },
  
  deleteChromaJob(jobId) {
    return api.delete(`/admin/chroma/jobs/${jobId}`)
  },
  
  // User APIs
  createUser(userData) {
    return api.post('/users', userData)
  },
  
  getUser(userId) {
    return api.get(`/users/${userId}`)
  },
  
  updateUser(userId, userData) {
    return api.put(`/users/${userId}`, userData)
  },
  
  // Phase 1 - Search APIs
  searchJobs(searchData) {
    return api.post('/phase1/search', searchData)
  },
  
  getJobPostings(params = {}) {
    return api.get('/phase1/jobs', { params })
  },
  
  getJobDetails(jobId) {
    return api.get(`/phase1/jobs/${jobId}`)
  },
  
  // Phase 2 - Resume APIs (增强版本)
  generateResume(resumeData) {
    return api.post('/phase2/generate', resumeData,{
      timeout: 120000
    })
  },
  
  // 批量生成简历
  generateBatchResumes(userData) {
    return api.post('/phase2/generate-batch', userData,{
      timeout: 120000
    })
  },
  
  // 分析匹配度
  analyzeJobMatch(userProfile, jobPosting) {
    return api.post('/phase2/analyze-match', {
      user_profile: userProfile,
      job_posting: jobPosting
    })
  },
  
  // 优化简历
  optimizeResume(resumeContent, feedback, optimizationFocus = []) {
    return api.post('/phase2/optimize', {
      resume_content: resumeContent,
      feedback: feedback,
      optimization_focus: optimizationFocus
    })
  },
  
  // 原有的简历相关API
  getResumes(userId) {
    return api.get(`/phase2/resumes/${userId}`)
  },
  
  updateResume(resumeId, resumeData) {
    return api.put(`/phase2/resumes/${resumeId}`, resumeData)
  },
  
  finalizeResume(resumeId) {
    return api.post(`/phase2/resumes/${resumeId}/finalize`)
  },
  
  // Phase 3 - HR Simulation APIs
  submitToHR(submissionData) {
    return api.post('/phase3/submit', submissionData)
  },
  
  getHRFeedback(resumeId) {
    return api.get(`/phase3/feedback/${resumeId}`)
  },
  
  requestHRReview(reviewData) {
    return api.post('/phase3/review', reviewData)
  },
  
  // 更新的Phase 3 HR评估API
  async hrReview(reviewData) {
    return api.post('/phase3/hr-review', reviewData)  // 使用正确的路径
  },
  
  async generateImprovementPlan(resumeContent, jobPosting, feedback, hrPersona) {
    return api.post('/phase3/improvement-plan', {
      resume_content: resumeContent,
      job_posting: jobPosting,
      feedback: feedback,
      hr_persona: hrPersona
    })
  },
  
  async applyImprovements(resumeContent, improvementPlan, selectedImprovements = null) {
    return api.post('/phase3/apply-improvements', {
      resume_content: resumeContent,
      improvement_plan: improvementPlan,
      selected_improvements: selectedImprovements
    })
  },
  
  // Phase 2 简历相关APIs
  async optimizeResume(resumeContent, feedback) {
    return api.post('/phase2/optimize', {
      resume_content: resumeContent,
      feedback: feedback
    })
  },
  
  async regenerateResume(userProfile, jobPosting, optimizationHints = null) {
    return api.post('/phase2/regenerate', {
      user_profile: userProfile,
      job_posting: jobPosting,
      optimization_hints: optimizationHints
    })
  },
  
  
  // Phase 4 - Scheduling APIs
  createInterviews(interviewData) {
    return api.post('/phase4/interviews', interviewData)
  },
  
  getInterviews(userId) {
    return api.get(`/phase4/interviews/${userId}`)
  },
  
  generateSchedule(scheduleData) {
    return api.post('/phase4/schedule', scheduleData)
  },
  
  updateSchedule(scheduleId, scheduleData) {
    return api.put(`/phase4/schedule/${scheduleId}`, scheduleData)
  },
  
  approveSchedule(scheduleId) {
    return api.post(`/phase4/schedule/${scheduleId}/approve`)
  },

  // Phase 4 - 多LLM推荐分析
  multiLLMRecommendation(personalInfo, jobs) {
    return api.post('/phase4/multi-llm-recommendation', {
      personal_info: personalInfo,
      jobs: jobs
    })
  },

  // Phase 4 - 生成最终面试日程（使用LLM智能安排）
  generateInterviewSchedule(rankedJobs, userPreferences) {
    return api.post('/phase4/generate-schedule', {
      ranked_jobs: rankedJobs,
      user_preferences: userPreferences
    })
  },
  
  // 新增：健康检查API
  healthCheck() {
    return api.get('/health')
  },
  
  // 新增：获取可用模型列表
  getAvailableModels() {
    return api.get('/models')
  },
  generateSelfIntroduction(strengths, weaknesses, minLength = 300, options = {}) {
    return api.post('/phase3/self-introduction', {
      strengths,
      weaknesses,
      min_length: minLength,
      resume_content: options.resumeContent || null,
      job_posting: options.jobPosting || null,
      hr_persona: options.hrPersona || 'experienced',
      hr_feedback: options.hrFeedback || null
    })
  },

  // 面试问题生成
  generateInterviewQuestions(hrPersona, resumeContent, jobPosting, numQuestions = 3) {
    return api.post('/phase3/generate-interview-questions', {
      hr_persona: hrPersona,
      resume_content: resumeContent,
      job_posting: jobPosting,
      num_questions: numQuestions
    })
  },

  // 面试回答评估
  evaluateInterviewAnswer(hrPersona, question, userAnswer, resumeContent, jobPosting) {
    return api.post('/phase3/evaluate-interview-answer', {
      hr_persona: hrPersona,
      question: question,
      user_answer: userAnswer,
      resume_content: resumeContent,
      job_posting: jobPosting
    })
  },
  // HR评估提交方法 - 支持单份简历评估
  async submitHRReview(params) {
    try {
      const response = await api.post('/phase3/hr-review', {
        resume_content: params.resume_content,
        job_posting: params.job_posting,
        hr_persona: params.hr_persona || 'experienced'
      })
      return response
    } catch (error) {
      console.error('HR评估失败:', error)
      return {
        success: false,
        message: error.response?.data?.detail || error.message || '评估失败'
      }
    }
  },
  
  // 批量HR评估方法 - 支持多份简历，每份可选择不同HR类型
  async submitMultipleHRReview(resumeRequests) {
    try {
      // resumeRequests格式: [{ resume_content, job_posting, hr_persona }, ...]
      const promises = resumeRequests.map(async (request, index) => {
        try {
          const response = await this.submitHRReview(request)
          return {
            index,
            success: response.success !== false,
            data: response.success !== false ? response : null,
            error: response.success === false ? response.message : null
          }
        } catch (error) {
          return {
            index,
            success: false,
            data: null,
            error: error.message
          }
        }
      })
      
      const results = await Promise.all(promises)
      return {
        success: true,
        results: results
      }
    } catch (error) {
      console.error('批量HR评估失败:', error)
      return {
        success: false,
        message: error.message,
        results: []
      }
    }
  },
  
  // 传统批量评估方法 - 所有简历使用相同HR类型
  async submitBatchHRReview(resumes, hrPersona = 'experienced') {
    try {
      const requests = resumes.map(resume => ({
        resume_content: resume.resume_content,
        job_posting: resume.job_posting,
        hr_persona: hrPersona
      }))
      
      return await this.submitMultipleHRReview(requests)
    } catch (error) {
      console.error('批量HR评估失败:', error)
      return {
        success: false,
        message: error.message,
        results: []
      }
    }
  },
  
  // Phase 4 - 智能多Agent调度（完整流程）
  multiAgentDiscussion(payload) {
    return api.post('/phase4/multi-agent-discussion', payload)
  },
}

export default api

