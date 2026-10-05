<script setup>
import { reactive } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  username: "",
  password: "",
})

async function submit() {
  const ok = await auth.login(form.username, form.password)
  if (ok) {
    router.push(route.query.redirect || "/")
  }
}
</script>

<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-6" rounded="lg" elevation="2">
          <div class="text-h5 mb-1">Вход</div>
          <div class="text-body-2 text-medium-emphasis mb-6">
            Клиника · Djoser token auth
          </div>
          <v-alert v-if="auth.error" type="error" density="compact" class="mb-4">
            {{ auth.error }}
          </v-alert>
          <v-form @submit.prevent="submit">
            <v-text-field
              v-model="form.username"
              label="Имя пользователя"
              autocomplete="username"
              class="mb-2"
            />
            <v-text-field
              v-model="form.password"
              label="Пароль"
              type="password"
              autocomplete="current-password"
              class="mb-4"
            />
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="auth.loading"
            >
              Войти
            </v-btn>
          </v-form>
          <div class="text-center mt-4">
            <router-link to="/register">Регистрация</router-link>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
