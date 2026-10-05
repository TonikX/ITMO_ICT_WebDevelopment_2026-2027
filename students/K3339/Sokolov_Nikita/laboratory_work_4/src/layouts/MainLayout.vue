<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const drawer = ref(true)
const auth = useAuthStore()
const router = useRouter()

const links = [
  { title: "Главная", to: "/", icon: "mdi-home" },
  { title: "Врачи", to: "/doctors", icon: "mdi-doctor" },
  { title: "Пациенты", to: "/patients", icon: "mdi-account-heart" },
  { title: "Приёмы", to: "/visits", icon: "mdi-calendar-clock" },
  { title: "Медкарты", to: "/medical-cards", icon: "mdi-card-account-details" },
  { title: "Кабинеты", to: "/cabinets", icon: "mdi-door" },
  { title: "Прейскурант", to: "/price-list", icon: "mdi-cash" },
  { title: "График", to: "/schedules", icon: "mdi-calendar" },
  { title: "Аналитика", to: "/analytics", icon: "mdi-chart-bar" },
  { title: "Профиль", to: "/profile", icon: "mdi-account-cog" },
]

async function onLogout() {
  await auth.logout()
  router.push({ name: "login" })
}
</script>

<template>
  <v-navigation-drawer v-model="drawer" color="secondary" theme="dark">
    <v-list-item
      title="Клиника"
      :subtitle="auth.user?.username || ''"
      prepend-icon="mdi-hospital-building"
      class="py-4"
    />
    <v-divider />
    <v-list nav density="comfortable">
      <v-list-item
        v-for="item in links"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        color="accent"
        rounded="lg"
      />
    </v-list>
  </v-navigation-drawer>

  <v-app-bar color="primary" density="comfortable">
    <v-app-bar-nav-icon @click="drawer = !drawer" />
    <v-toolbar-title>Лечебная клиника</v-toolbar-title>
    <v-spacer />
    <v-chip class="mr-3" color="accent" variant="flat" size="small">
      {{ auth.user?.role || "—" }}
    </v-chip>
    <v-btn variant="text" @click="onLogout">Выйти</v-btn>
  </v-app-bar>

  <v-main>
    <v-container fluid class="pa-6">
      <router-view />
    </v-container>
  </v-main>
</template>
