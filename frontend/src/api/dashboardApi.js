import api from './axios'

export const dashboardApi = {
  getSummary() {
    return api.get('/api/dashboard/summary')
  },

  getRecent() {
    return api.get('/api/dashboard/recent')
  },
}