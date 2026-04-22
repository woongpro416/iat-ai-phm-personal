import api from './axios'

export const safetyEventApi = {
  getSafetyEvents() {
    return api.get('/api/safety-events')
  },

  getSafetyEventsByDevice(deviceId) {
    return api.get(`/api/safety-events/device/${deviceId}`)
  },

  uploadSafetyImage(deviceId, file) {
    const formData = new FormData()
    formData.append('deviceId', deviceId)
    formData.append('file', file)

    return api.post('/api/safety-events/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  resolveSafetyEvent(eventId) {
    return api.patch(`/api/safety-events/${eventId}/resolve`)
  },
}