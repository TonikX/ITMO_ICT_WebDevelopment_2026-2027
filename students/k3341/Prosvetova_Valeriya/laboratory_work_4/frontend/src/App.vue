<template>
  <v-app>
    <v-app-bar color="primary" title="Распределение газет по почтовым отделениям">
      <template v-if="auth.token">
        <v-btn to="/account" prepend-icon="mdi-account">{{ auth.user?.username }}</v-btn>
        <v-btn prepend-icon="mdi-logout" @click="logout">Выйти</v-btn>
      </template>
    </v-app-bar>

    <v-navigation-drawer v-if="auth.token" permanent>
      <v-list nav>
        <v-list-item v-for="(r, key) in resources" :key="key" :to="`/r/${key}`" :title="r.title" />
        <v-divider class="my-2" />
        <v-list-item to="/analytics" prepend-icon="mdi-magnify" title="Запросы" />
        <v-list-item to="/report" prepend-icon="mdi-file-chart" title="Отчёт" />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { resources } from '@/resources'

const auth = useAuthStore()
const router = useRouter()

// Если токен сохранился после предыдущего входа, получаем данные пользователя.
// Если токен недействителен, выполняем выход из учётной записи и переходим на страницу входа.
if (auth.token) auth.fetchMe().catch(() => auth.logout().then(() => router.push('/login')))

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>
