import api from './axios'

export const deviceApi = {
  getDevices() {
    return api.get('/api/devices')
  },

  getDevice(deviceId) {
    return api.get(`/api/devices/${deviceId}`)
  },

  createDevice(payload) {
    return api.post('/api/devices', payload)
  },

  createDeviceStatus(payload) {
    return api.post('/api/device-status', payload)
  },

  getDeviceStatusLogs(deviceId) {
    return api.get(`/api/device-status/${deviceId}`)
  },
}