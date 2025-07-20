import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
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
  
  // Phase 2 - Resume APIs
  generateResume(resumeData) {
    return api.post('/phase2/generate', resumeData)
  },
  
  generateResumeMultipleJobs(resumeData) {
    return api.post('/phase2/generate-multi', resumeData)
  },
  
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
  }
}

export default api

