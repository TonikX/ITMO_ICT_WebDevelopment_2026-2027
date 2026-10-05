<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const items = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await clinicApi.cabinets()
    items.value = data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="text-h5 mb-4">Кабинеты</div>
    <v-data-table
      :headers="[
        { title: 'Номер', key: 'number' },
        { title: 'Режим', key: 'schedule' },
        { title: 'Врач', key: 'responsible_doctor' },
        { title: 'Телефон', key: 'phone' },
      ]"
      :items="items"
      :loading="loading"
    />
  </div>
</template>
