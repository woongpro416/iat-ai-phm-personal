import axios from 'axios'

const DEMO_WRITE_TOKEN_KEY = 'iatDemoWriteToken'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8402',
    timeout: 10000,
})

api.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem(DEMO_WRITE_TOKEN_KEY)

        if (token) {
            config.headers['X-Demo-Write-Token'] = token
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 403) {
      console.warn('Demo write request blocked. Unlock admin mode to change data.')
    }

    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
