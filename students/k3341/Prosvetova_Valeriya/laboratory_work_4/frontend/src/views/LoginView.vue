<template>
  <v-card max-width="420" class="mx-auto mt-8" title="Вход">
    <v-card-text>
      <v-form @submit.prevent="submit">
        <v-text-field v-model="username" label="Имя пользователя" />
        <v-text-field v-model="password" label="Пароль" type="password" />
        <v-alert v-if="error" type="error" class="mb-4" style="white-space: pre-line">{{ error }}</v-alert>
        <v-btn type="submit" color="primary" block :loading="loading">Войти</v-btn>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-btn to="/register" variant="text">Регистрация</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { errorText } from '@/api'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}
</script>
