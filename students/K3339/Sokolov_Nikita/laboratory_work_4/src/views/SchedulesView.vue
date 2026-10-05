<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const items = ref([])
const doctors = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [schedules, docs] = await Promise.all([
      clinicApi.schedules(),
      clinicApi.doctors(),
    ])
    items.value = schedules.data
    doctors.value = docs.data
  } finally {
    loading.value = false
  }
})

function doctorName(id) {
  return doctors.value.find((d) => d.id === id)?.fio || id
}
</script>

<template>
  <div>
    <div class="text-h5 mb-4">График работы</div>
    <v-data-table
      :headers="[
        { title: 'Врач', key: 'doctor' },
        { title: 'Дата', key: 'work_date' },
        { title: 'Рабочий день', key: 'is_working' },
      ]"
      :items="items"
      :loading="loading"
    >
      <template #item.doctor="{ item }">
        {{ doctorName(item.doctor) }}
      </template>
      <template #item.is_working="{ item }">
        {{ item.is_working ? "да" : "выходной" }}
      </template>
    </v-data-table>
  </div>
</template>
