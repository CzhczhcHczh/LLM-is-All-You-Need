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
    
    // Phase 2 - Resumes
    resumes: {
      list: [],
      current: null,
      loading: false
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

