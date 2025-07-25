import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // User information
    user: {
      id: null,
      username: '',
      email: '',
      full_name: '',
      phone: '',
      target_position: '',
      profile_data: {}
    },
    
    // Phase 1 - Search results
    searchResults: {
      jobs: [],
      companies: [],
      loading: false,
      searchQuery: '',
      selectedJobs: [] // 存储选定的多个职位
    },
    
    // Phase 2 - Resumes (增强)
    resumes: {
      list: [],
      current: null,
      loading: false,
      multipleResumes: {}, // 存储多个职位对应的简历 {jobIndex: resumeData}
      batchGenerating: false,
      generationProgress: 0
    },
    
    // Phase 2 - 新增结构，与现有Phase3.vue兼容
    phase2: {
      generatedResumes: {}, // 存储生成的简历 {resumeId: resumeData}
      optimizationHistory: [], // 存储优化历史
      userProfile: null,
      selectedJobs: []
    },
    
    // Phase 3 - HR Feedback
    hrFeedback: {
      list: [],
      current: null,
      loading: false
    },
    
    // Phase 4 - Interviews and Schedule
    interviews: {
      list: [],
      schedule: null,
      loading: false
    },
    
    // Current phase
    currentPhase: 1
  }),
  
  getters: {
    isUserLoggedIn: (state) => !!state.user.id,
    getCurrentPhaseData: (state) => {
      switch (state.currentPhase) {
        case 1: return state.searchResults
        case 2: return state.resumes
        case 3: return state.hrFeedback
        case 4: return state.interviews
        default: return null
      }
    }
  },
  
  actions: {
    // User actions
    setUser(userData) {
      this.user = { ...this.user, ...userData }
    },
    
    clearUser() {
      this.user = {
        id: null,
        username: '',
        email: '',
        full_name: '',
        phone: '',
        target_position: '',
        profile_data: {}
      }
    },
    
    // Phase 1 actions
    setSearchResults(results) {
      // 清空选择的职位
      this.searchResults.selectedJobs = []
      // 重新设置搜索结果
      this.searchResults.jobs = results.jobs || []
      this.searchResults.companies = results.companies || []
    },
    
    setSearchLoading(loading) {
      this.searchResults.loading = loading
    },
    
    setSearchQuery(query) {
      this.searchResults.searchQuery = query
    },
    
    // 多职位选择相关的方法
    addSelectedJob(job) {
      // 检查职位是否已被选择
      const exists = this.searchResults.selectedJobs.some(item => item.job_title === job.job_title && item.company_name === job.company_name)
      if (!exists) {
        this.searchResults.selectedJobs.push(job)
      }
    },
    
    removeSelectedJob(jobIndex) {
      this.searchResults.selectedJobs.splice(jobIndex, 1)
    },
    
    clearSelectedJobs() {
      this.searchResults.selectedJobs = []
    },
    
    // Phase 2 actions
    setResumes(resumes) {
      this.resumes.list = resumes
    },
    
    addResume(resume) {
      this.resumes.list.push(resume)
    },
    
    setCurrentResume(resume) {
      this.resumes.current = resume
    },
    
    setResumeLoading(loading) {
      this.resumes.loading = loading
    },
    
    // Phase 2 - 多简历管理 actions
    setMultipleResumes(resumes) {
      this.resumes.multipleResumes = resumes
    },
    
    addMultipleResume(jobIndex, resume) {
      this.resumes.multipleResumes[jobIndex] = resume
    },
    
    updateMultipleResume(jobIndex, resume) {
      if (this.resumes.multipleResumes[jobIndex]) {
        this.resumes.multipleResumes[jobIndex] = resume
      }
    },
    
    removeMultipleResume(jobIndex) {
      delete this.resumes.multipleResumes[jobIndex]
    },
    
    setBatchGenerating(loading) {
      this.resumes.batchGenerating = loading
    },
    
    setGenerationProgress(progress) {
      this.resumes.generationProgress = progress
    },
    
    clearMultipleResumes() {
      this.resumes.multipleResumes = {}
    },

    // Phase 2 - 新增兼容方法
    setPhase2GeneratedResumes(resumes) {
      this.phase2.generatedResumes = resumes
    },

    addPhase2GeneratedResume(resumeId, resume) {
      this.phase2.generatedResumes[resumeId] = resume
    },

    updatePhase2GeneratedResume(resumeId, resume) {
      if (this.phase2.generatedResumes[resumeId]) {
        this.phase2.generatedResumes[resumeId] = resume
      }
    },

    setPhase2OptimizationHistory(history) {
      this.phase2.optimizationHistory = history
    },

    addPhase2OptimizationHistory(item) {
      this.phase2.optimizationHistory = this.phase2.optimizationHistory || []
      this.phase2.optimizationHistory.push(item)
    },

    setPhase2UserProfile(profile) {
      this.phase2.userProfile = profile
    },

    setPhase2SelectedJobs(jobs) {
      this.phase2.selectedJobs = jobs
    },
    
    // Phase 3 actions
    setHRFeedback(feedback) {
      this.hrFeedback.list = feedback
    },
    
    addHRFeedback(feedback) {
      this.hrFeedback.list.push(feedback)
    },
    
    setCurrentHRFeedback(feedback) {
      this.hrFeedback.current = feedback
    },
    
    setHRFeedbackLoading(loading) {
      this.hrFeedback.loading = loading
    },
    
    
    // Phase 4 actions
    setInterviews(interviews) {
      this.interviews.list = interviews
    },
    
    addInterview(interview) {
      this.interviews.list.push(interview)
    },
    
    setSchedule(schedule) {
      this.interviews.schedule = schedule
    },
    
    setInterviewLoading(loading) {
      this.interviews.loading = loading
    },
    
    // Navigation
    setCurrentPhase(phase) {
      this.currentPhase = phase
    },
    
    nextPhase() {
      if (this.currentPhase < 4) {
        this.currentPhase++
      }
    },
    
    previousPhase() {
      if (this.currentPhase > 1) {
        this.currentPhase--
      }
    }
  }
})