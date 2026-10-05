<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const stats = ref({
  doctors: 0,
  patients: 0,
  visits: 0,
})
const loading = ref(true)

onMounted(async () => {
  try {
    const [doctors, patients, visits] = await Promise.all([
      clinicApi.doctors(),
      clinicApi.patients(),
      clinicApi.visits(),
    ])
    stats.value = {
      doctors: doctors.data.length,
      patients: patients.data.length,
      visits: visits.data.length,
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="text-h4 mb-2">Добро пожаловать, {{ auth.user?.username }}</div>
    <div class="text-body-1 text-medium-emphasis mb-6">
      Клиент Vue.js к API лечебной клиники (вариант 10)
    </div>
    <v-row>
      <v-col cols="12" md="4">
        <v-card color="primary" theme="dark" class="pa-4">
          <div class="text-overline">Врачи</div>
          <div class="text-h3">{{ loading ? "…" : stats.doctors }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card color="secondary" theme="dark" class="pa-4">
          <div class="text-overline">Пациенты</div>
          <div class="text-h3">{{ loading ? "…" : stats.patients }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Приёмы</div>
          <div class="text-h3">{{ loading ? "…" : stats.visits }}</div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
