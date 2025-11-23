export const API_CONFIG = {
  baseURL: '/api'
}

export const API_ENDPOINTS = {
  users: `${API_CONFIG.baseURL}/db/users/`,
  deleteUser: (userId: number) => `${API_CONFIG.baseURL}/db/users/${userId}`,
  generalAnalytics: `${API_CONFIG.baseURL}/db/analytics/general`,
  getAnswer: `${API_CONFIG.baseURL}/get_answer`,
  getModule: (moduleId: number) => `${API_CONFIG.baseURL}/get_module/${moduleId}`,
  analyzeCalibration: `${API_CONFIG.baseURL}/analyze_calibration`,
  updateModule: `${API_CONFIG.baseURL}/update_module`
}

