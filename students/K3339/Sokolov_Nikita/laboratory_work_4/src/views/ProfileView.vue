<script setup>
import { onMounted, reactive } from "vue"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const form = reactive({
  email: "",
  first_name: "",
  last_name: "",
})
const success = reactive({ show: false })

onMounted(() => {
  form.email = auth.user?.email || ""
  form.first_name = auth.user?.first_name || ""
  form.last_name = auth.user?.last_name || ""
})

async function submit() {
  success.show = false
  const ok = await auth.updateProfile({ ...form })
  if (ok) {
    success.show = true
  }
}
</script>

<template>
  <v-card class="pa-6" max-width="640">
    <div class="text-h5 mb-4">Профиль</div>
    <v-alert v-if="auth.error" type="error" class="mb-4" density="compact">
      {{ auth.error }}
    </v-alert>
    <v-alert v-if="success.show" type="success" class="mb-4" density="compact">
      Данные обновлены
    </v-alert>
    <v-form @submit.prevent="submit">
      <v-text-field :model-value="auth.user?.username" label="Логин" disabled />
      <v-text-field :model-value="auth.user?.role" label="Роль" disabled />
      <v-text-field v-model="form.email" label="Email" />
      <v-text-field v-model="form.first_name" label="Имя" />
      <v-text-field v-model="form.last_name" label="Фамилия" />
      <v-btn type="submit" color="primary" :loading="auth.loading">Сохранить</v-btn>
    </v-form>
  </v-card>
</template>
