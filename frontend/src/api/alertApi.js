import api from './axios'

export const alertApi = {
  getAlerts() {
    return api.get('/api/alerts')
  },

  checkAlert(alertId) {
    return api.patch(`/api/alerts/${alertId}/check`)
  },
}