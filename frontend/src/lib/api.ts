import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const storage = localStorage.getItem('velionx-storage');
    if (storage) {
      const { state } = JSON.parse(storage);
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`;
      }
    }
  }
  return config;
});

// API functions
export const authAPI = {
  register: (data: { email: string; password: string; name: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  getMe: () => api.get('/auth/me'),
};

export const profileAPI = {
  create: (formData: FormData) =>
    api.post('/profile/create', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  get: (studentId: string) =>
    api.get(`/profile/${studentId}`),
  
  update: (studentId: string, data: Record<string, any>) =>
    api.put(`/profile/${studentId}`, data),
  
  uploadResume: (formData: FormData) =>
    api.post('/profile/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getSummary: (studentId: string) =>
    api.get(`/profile/${studentId}/summary`),
  
  getReadinessScore: (studentId: string) =>
    api.get(`/profile/${studentId}/readiness`),
};

export const assessmentAPI = {
  start: (data: { student_id: string; category: string; skills: string[]; questions_per_skill?: number }) =>
    api.post('/assessment/start', data),
  
  submitAnswer: (assessmentId: string, data: { question_id: string; answer: string; time_taken_seconds: number }) =>
    api.post(`/assessment/${assessmentId}/submit`, data),
  
  complete: (assessmentId: string) =>
    api.post(`/assessment/${assessmentId}/complete`),
  
  get: (assessmentId: string) =>
    api.get(`/assessment/${assessmentId}`),
  
  getHistory: (studentId: string) =>
    api.get(`/assessment/student/${studentId}/history`),
  
  getCategories: () =>
    api.get('/assessment/questions/categories'),
};

export const skillGapAPI = {
  analyze: (data: { student_id: string; target_company?: string; target_role?: string }) =>
    api.post('/skill-gap/analyze', data),
  
  batchAnalyze: (data: { student_id: string; company_ids?: string[] }) =>
    api.post('/skill-gap/analyze-batch', data),
  
  getCompanies: () =>
    api.get('/skill-gap/companies'),
  
  getCompanyRequirements: (companyId: string) =>
    api.get(`/skill-gap/company/${companyId}`),

  getHistory: (studentId: string) =>
    api.get(`/skill-gap/student/${studentId}/history`),
};

export const roadmapAPI = {
  generate: (data: { student_id: string; company_id?: string; duration_weeks?: number; daily_commitment?: string }) =>
    api.post('/roadmap/generate', data),
  
  get: (roadmapId: string) =>
    api.get(`/roadmap/${roadmapId}`),
  
  getActive: (studentId: string) =>
    api.get(`/roadmap/student/${studentId}/active`),
  
  getTodaysTasks: (roadmapId: string) =>
    api.get(`/roadmap/${roadmapId}/today`),
  
  updateProgress: (roadmapId: string, taskId: string) =>
    api.post(`/roadmap/${roadmapId}/progress`, { task_id: taskId }),
  
  getWeek: (roadmapId: string, weekNumber: number) =>
    api.get(`/roadmap/${roadmapId}/week/${weekNumber}`),
  
  getMilestones: (roadmapId: string) =>
    api.get(`/roadmap/${roadmapId}/milestones`),
};

export const interviewAPI = {
  start: (data: { student_id: string; interview_type: string; language?: string; target_company?: string; target_role?: string }) =>
    api.post('/interview/start', data),
  
  respond: (sessionId: string, data: { response_text: string; response_type?: string; audio_transcript?: string }) =>
    api.post(`/interview/${sessionId}/respond`, data),
  
  end: (sessionId: string) =>
    api.post(`/interview/${sessionId}/end`),
  
  get: (sessionId: string) =>
    api.get(`/interview/${sessionId}`),
  
  getHistory: (studentId: string) =>
    api.get(`/interview/student/${studentId}/history`),
  
  getLanguages: () =>
    api.get('/interview/languages'),
  
  getTypes: () =>
    api.get('/interview/types'),
};

export const digitalTwinAPI = {
  create: (studentId: string) =>
    api.post('/digital-twin/create', { student_id: studentId }),
  
  get: (studentId: string) =>
    api.get(`/digital-twin/${studentId}`),
  
  getSummary: (studentId: string) =>
    api.get(`/digital-twin/${studentId}/summary`),
  
  predict: (data: { student_id: string; target_company?: string }) =>
    api.post('/digital-twin/predict', data),
  
  getPredictions: (studentId: string) =>
    api.get(`/digital-twin/${studentId}/predictions`),
  
  getPatterns: (studentId: string) =>
    api.get(`/digital-twin/${studentId}/patterns`),
  
  getSkillEvolution: (studentId: string) =>
    api.get(`/digital-twin/${studentId}/skill-evolution`),
  
  getInsights: (studentId: string) =>
    api.get(`/digital-twin/${studentId}/insights`),
  
  recordEvent: (data: { student_id: string; event_type: string; data: any }) =>
    api.post('/digital-twin/event', data),
};
