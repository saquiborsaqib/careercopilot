import apiClient from './client'

export const authApi = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return apiClient.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => apiClient.get('/auth/me'),
}

export const studentApi = {
  getMyProfile: () => apiClient.get('/students/profiles/me'),
  createProfile: (data) => apiClient.post('/students/profiles', data),
  updateProfile: (studentId, data) => apiClient.patch(`/students/profiles/${studentId}`, data),
}

export const academicApi = {
  listMine: () => apiClient.get('/academic-records/me'),
  create: (data) => apiClient.post('/academic-records', data),
  remove: (id) => apiClient.delete(`/academic-records/${id}`),
}

export const skillApi = {
  listCatalog: (category) => apiClient.get('/skills', { params: { category } }),
  listMine: () => apiClient.get('/skills/me'),
  assign: (data) => apiClient.post('/skills/assign', data),
  remove: (studentSkillId) => apiClient.delete(`/skills/assign/${studentSkillId}`),
}

export const careerApi = {
  listCatalog: () => apiClient.get('/careers'),
  get: (careerId) => apiClient.get(`/careers/${careerId}`),
  skillGap: (careerId) => apiClient.get(`/careers/${careerId}/skill-gap`),
  recommendations: (topN = 5) => apiClient.get('/careers/recommendations/me', { params: { top_n: topN } }),
}

export const courseApi = {
  list: () => apiClient.get('/courses'),
}

export const certificationApi = {
  list: () => apiClient.get('/certifications'),
}

export const roadmapApi = {
  listMine: () => apiClient.get('/roadmaps/me'),
  generate: (careerId) => apiClient.post(`/roadmaps/generate/${careerId}`),
  get: (roadmapId) => apiClient.get(`/roadmaps/${roadmapId}`),
  narrative: (roadmapId) => apiClient.get(`/roadmaps/${roadmapId}/narrative`),
  updateItemStatus: (itemId, status) => apiClient.patch(`/roadmaps/items/${itemId}`, { status }),
}

export const resumeApi = {
  listMine: () => apiClient.get('/resumes/me'),
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  improve: (resumeId, targetCareer) => apiClient.post(`/resumes/${resumeId}/improve`, { target_career: targetCareer }),
  syncSkills: (resumeId) => apiClient.post(`/resumes/${resumeId}/sync-skills`),
}

export const interviewApi = {
  listMine: () => apiClient.get('/interview/sessions/me'),
  start: (data) => apiClient.post('/interview/sessions', data),
  get: (sessionId) => apiClient.get(`/interview/sessions/${sessionId}`),
  nextQuestion: (sessionId) => apiClient.post(`/interview/sessions/${sessionId}/next-question`),
  submitAnswer: (answerId, answer) => apiClient.post(`/interview/answers/${answerId}/submit`, { answer }),
  complete: (sessionId) => apiClient.post(`/interview/sessions/${sessionId}/complete`),
}

export const opportunityApi = {
  list: (opportunityType) => apiClient.get('/opportunities', { params: { opportunity_type: opportunityType } }),
  matches: (opportunityType) => apiClient.get('/opportunities/matches/me', { params: { opportunity_type: opportunityType } }),
}

export const recommendationApi = {
  listMine: (recommendationType) => apiClient.get('/recommendations/me', { params: { recommendation_type: recommendationType } }),
  generateCareers: (topN = 3) => apiClient.post('/recommendations/careers/generate', null, { params: { top_n: topN } }),
  generateCourses: (careerId, topN = 5) => apiClient.post(`/recommendations/courses/generate/${careerId}`, null, { params: { top_n: topN } }),
  generateCertifications: (careerId, topN = 3) => apiClient.post(`/recommendations/certifications/generate/${careerId}`, null, { params: { top_n: topN } }),
}

export const dashboardApi = {
  getMine: () => apiClient.get('/dashboard/me'),
}
