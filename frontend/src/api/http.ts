import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 请求拦截：自动带上 JWT
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('travelai_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一提示错误，401 跳转到登录
http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error?.response?.status
    const detail = error?.response?.data?.detail
    if (status === 401) {
      localStorage.removeItem('travelai_token')
      ElMessage.error('登录已失效，请重新登录')
      if (!location.hash.startsWith('#/login')) {
        location.hash = '#/login'
      }
    } else {
      ElMessage.error(typeof detail === 'string' ? detail : error?.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default http
