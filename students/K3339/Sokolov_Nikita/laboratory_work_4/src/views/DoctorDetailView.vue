<script setup>
import { onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { clinicApi } from "@/api/clinic"

const route = useRoute()
const router = useRouter()
const doctor = ref(null)
const patients = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const id = route.params.id
    const [docRes, patRes] = await Promise.all([
      clinicApi.doctor(id),
      clinicApi.doctorPatients(id),
    ])
    doctor.value = docRes.data
    patients.value = patRes.data.patients || []
  } finally {
    loading.value = false
  }
})

async function remove() {
  await clinicApi.deleteDoctor(route.params.id)
  router.push("/doctors")
}
</script>

<template>
  <div v-if="!loading && doctor">
    <div class="d-flex align-center mb-4">
      <v-btn icon="mdi-arrow-left" variant="text" @click="router.push('/doctors')" />
      <div class="text-h5">{{ doctor.fio }}</div>
      <v-spacer />
      <v-btn color="error" variant="outlined" @click="remove">Удалить</v-btn>
    </div>
    <v-row>
      <v-col cols="12" md="6">
        <v-card class="pa-4">
          <div class="text-subtitle-1 mb-2">Данные врача</div>
          <div>Специальность: {{ doctor.specialty }}</div>
          <div>Образование: {{ doctor.education || "—" }}</div>
          <div>Пол: {{ doctor.gender }}</div>
          <div>Дата рождения: {{ doctor.birth_date }}</div>
          <div>Найм: {{ doctor.hire_date }}</div>
          <div>Договор: {{ doctor.contract_info || "—" }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="pa-4">
          <div class="text-subtitle-1 mb-2">Пациенты (N:M через Visit)</div>
          <v-list v-if="patients.length">
            <v-list-item
              v-for="p in patients"
              :key="p.id"
              :title="p.fio"
              :subtitle="p.phone"
              :to="`/patients/${p.id}`"
            />
          </v-list>
          <div v-else class="text-medium-emphasis">Пациентов пока нет</div>
        </v-card>
      </v-col>
    </v-row>
  </div>
  <v-progress-linear v-else indeterminate color="primary" />
</template>
