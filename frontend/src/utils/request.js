import axios from 'axios'
import { getToken, logout } from './auth'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let msg = '请求失败'
    const data = error.response?.data
    if (data) {
      if (typeof data.detail === 'string') {
        msg = data.detail
      } else if (Array.isArray(data.detail)) {
        msg = data.detail.map(e => e.msg || e.message || String(e)).join('; ')
      } else if (data.message) {
        msg = data.message
      }
    }
    if (error.response?.status === 401) {
      logout()
      window.location.href = '/login'
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
