import { defineStore } from 'pinia'
import { api } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('token'), user: null }),
  actions: {
    async login(username, password) {
      const { data } = await api.post('/auth/token/login/', { username, password })
      this.token = data.auth_token
      localStorage.setItem('token', this.token)
      await this.fetchMe()
    },
    async register(username, email, password) {
      await api.post('/auth/users/', { username, email, password })
      await this.login(username, password)
    },
    async fetchMe() {
      this.user = (await api.get('/auth/users/me/')).data
    },
    async logout() {
      try {
        await api.post('/auth/token/logout/')
      } finally {
        this.token = null
        this.user = null
        localStorage.removeItem('token')
      }
    },
  },
})
