import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'
import type { UserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('travelai_token') || '')
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)

  function setToken(t: string) {
    token.value = t
    if (t) localStorage.setItem('travelai_token', t)
    else localStorage.removeItem('travelai_token')
  }

  async function login(identifier: string, password: string) {
    loading.value = true
    try {
      const { data } = await authApi.login(identifier, password)
      setToken(data.access_token)
      user.value = data.user
      return true
    } finally {
      loading.value = false
    }
  }

  async function register(payload: { username: string; email: string; password: string }) {
    loading.value = true
    try {
      const { data } = await authApi.register(payload)
      setToken(data.access_token)
      user.value = data.user
      return true
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return null
    try {
      const { data } = await authApi.me()
      user.value = data
      return data
    } catch {
      setToken('')
      user.value = null
      return null
    }
  }

  function logout() {
    setToken('')
    user.value = null
  }

  return { token, user, loading, login, register, fetchMe, logout, setToken }
})
