import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { authApi } from "@/api/clinic"

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("auth_token") || "")
  const user = ref(null)
  const loading = ref(false)
  const error = ref("")

  const isAuthenticated = computed(() => Boolean(token.value))

  function setToken(value) {
    token.value = value || ""
    if (value) {
      localStorage.setItem("auth_token", value)
    } else {
      localStorage.removeItem("auth_token")
    }
  }

  async function login(username, password) {
    loading.value = true
    error.value = ""
    try {
      const { data } = await authApi.login({ username, password })
      setToken(data.auth_token)
      await fetchMe()
      return true
    } catch (e) {
      error.value = e.response?.data?.non_field_errors?.[0] || "Ошибка входа"
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    error.value = ""
    try {
      await authApi.register(payload)
      return await login(payload.username, payload.password)
    } catch (e) {
      const data = e.response?.data
      error.value =
        data?.username?.[0] ||
        data?.password?.[0] ||
        data?.email?.[0] ||
        "Ошибка регистрации"
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) {
      user.value = null
      return null
    }
    try {
      const { data } = await authApi.me()
      user.value = data
      return data
    } catch {
      setToken("")
      user.value = null
      return null
    }
  }

  async function updateProfile(payload) {
    loading.value = true
    error.value = ""
    try {
      const { data } = await authApi.updateMe(payload)
      user.value = data
      return true
    } catch (e) {
      error.value = "Не удалось обновить профиль"
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch {
    } finally {
      setToken("")
      user.value = null
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    fetchMe,
    updateProfile,
    logout,
  }
})
