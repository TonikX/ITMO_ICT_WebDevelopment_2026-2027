<template>
  <v-card max-width="420" class="mx-auto mt-8" title="Регистрация">
    <v-card-text>
      <v-form @submit.prevent="submit">
        <v-text-field v-model="username" label="Имя пользователя" />
        <v-text-field v-model="email" label="Email" type="email" />
        <v-text-field v-model="password" label="Пароль" type="password" />
        <v-text-field v-model="password2" label="Пароль ещё раз" type="password" />
        <v-alert v-if="error" type="error" class="mb-4" style="white-space: pre-line">{{ error }}</v-alert>
        <v-btn type="submit" color="primary" block :loading="loading">Зарегистрироваться</v-btn>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-btn to="/login" variant="text">Уже есть аккаунт</v-btn>
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
const email = ref('')
const password = ref('')
const password2 = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (password.value !== password2.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.register(username.value, email.value, password.value) 
    router.push('/')
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}
</script>
