<script setup>
import { reactive } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  username: "",
  email: "",
  password: "",
  re_password: "",
  first_name: "",
  last_name: "",
  role: "patient",
})

async function submit() {
  const ok = await auth.register({ ...form })
  if (ok) {
    router.push("/")
  }
}
</script>

<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <v-card class="pa-6" rounded="lg" elevation="2">
          <div class="text-h5 mb-6">Регистрация</div>
          <v-alert v-if="auth.error" type="error" density="compact" class="mb-4">
            {{ auth.error }}
          </v-alert>
          <v-form @submit.prevent="submit">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.username" label="Логин" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.email" label="Email" type="email" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.first_name" label="Имя" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.last_name" label="Фамилия" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.password"
                  label="Пароль"
                  type="password"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.re_password"
                  label="Повтор пароля"
                  type="password"
                  required
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="form.role"
                  :items="[
                    { title: 'Пациент', value: 'patient' },
                    { title: 'Врач', value: 'doctor' },
                    { title: 'Админ', value: 'admin' },
                  ]"
                  label="Роль"
                />
              </v-col>
            </v-row>
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              class="mt-2"
              :loading="auth.loading"
            >
              Создать аккаунт
            </v-btn>
          </v-form>
          <div class="text-center mt-4">
            <router-link to="/login">Уже есть аккаунт</router-link>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
