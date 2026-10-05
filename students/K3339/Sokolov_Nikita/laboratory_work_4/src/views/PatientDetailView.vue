<script setup>
import { onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { clinicApi } from "@/api/clinic"

const route = useRoute()
const router = useRouter()
const patient = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await clinicApi.patient(route.params.id)
    patient.value = data
  } finally {
    loading.value = false
  }
})

async function remove() {
  await clinicApi.deletePatient(route.params.id)
  router.push("/patients")
}
</script>

<template>
  <div v-if="!loading && patient">
    <div class="d-flex align-center mb-4">
      <v-btn icon="mdi-arrow-left" variant="text" @click="router.push('/patients')" />
      <div class="text-h5">{{ patient.fio }}</div>
      <v-spacer />
      <v-btn color="error" variant="outlined" @click="remove">Удалить</v-btn>
    </div>
    <v-card class="pa-4" max-width="560">
      <div>Телефон: {{ patient.phone }}</div>
      <div>Дата рождения: {{ patient.birth_date }}</div>
      <div>Пол: {{ patient.gender }}</div>
    </v-card>
  </div>
  <v-progress-linear v-else indeterminate color="primary" />
</template>
