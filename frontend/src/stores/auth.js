import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('gacoan_user')) || null,
    accessToken: localStorage.getItem('access_token') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUser: (state) => state.user,
  },
  
  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/auth/login', { email, password })
        const data = response.data
        
        this.accessToken = data.access_token
        this.user = data.user
        
        localStorage.setItem('access_token', this.accessToken)
        localStorage.setItem('gacoan_user', JSON.stringify(this.user))
        
        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        let errMsg = 'Terjadi kesalahan saat login.'
        if (error.response && error.response.data && error.response.data.error) {
          errMsg = error.response.data.error
        }
        return { success: false, error: errMsg }
      }
    },
    
    async logout() {
      try {
        // Panggil endpoint logout agar token di-revoke di backend
        if (this.accessToken) {
          await api.post('/auth/logout')
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.accessToken = null
        this.user = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('gacoan_user')
      }
    }
  }
})
