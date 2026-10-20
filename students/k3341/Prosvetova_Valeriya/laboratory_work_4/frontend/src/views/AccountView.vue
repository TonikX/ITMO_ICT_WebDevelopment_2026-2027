<template>
  <h1 class="text-h5 mb-4">Учётная запись</h1>
  <v-alert v-if="message" :type="message.type" class="mb-4" closable style="white-space: pre-line"
           @click:close="message = null">{{ message.text }}</v-alert>

  <v-row>
    <v-col cols="12" md="4">
      <v-card title="Email">
        <v-card-text>
          <v-text-field v-model="email" label="Email" type="email" />
          <v-btn color="primary" @click="run(() => api.patch('/auth/users/me/', { email }), 'Email сохранён')">
            Сохранить
          </v-btn>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="4">
      <v-card title="Имя пользователя">
        <v-card-text>
          <v-text-field v-model="newUsername" label="Новое имя" />
          <v-text-field v-model="usernamePassword" label="Текущий пароль" type="password" />
          <v-btn color="primary" @click="run(() => api.post('/auth/users/set_username/',
            { new_username: newUsername, current_password: usernamePassword }), 'Имя изменено')">
            Изменить
          </v-btn>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="4">
      <v-card title="Пароль">
        <v-card-text>
          <v-text-field v-model="currentPassword" label="Текущий пароль" type="password" />
          <v-text-field v-model="newPassword" label="Новый пароль" type="password" />
          <v-btn color="primary" @click="run(() => api.post('/auth/users/set_password/',
            { current_password: currentPassword, new_password: newPassword }), 'Пароль изменён')">
            Изменить
          </v-btn>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { api, errorText } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const email = ref('')
const newUsername = ref('')
const usernamePassword = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const message = ref(null)

watchEffect(() => {
  email.value = auth.user?.email ?? ''
  newUsername.value = auth.user?.username ?? ''
})

async function run(request, ok) {
  try {
    await request()
    await auth.fetchMe() // Повторно получаем актуальные данные пользователя с сервера
    usernamePassword.value = currentPassword.value = newPassword.value = ''
    message.value = { type: 'success', text: ok }
  } catch (e) {
    message.value = { type: 'error', text: errorText(e) }
  }
}
</script>
