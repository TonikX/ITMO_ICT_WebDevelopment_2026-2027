<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const items = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await clinicApi.priceList()
    items.value = data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="text-h5 mb-4">Прейскурант</div>
    <v-data-table
      :headers="[
        { title: 'Услуга', key: 'service_name' },
        { title: 'Специальность', key: 'specialty' },
        { title: 'Цена', key: 'price' },
      ]"
      :items="items"
      :loading="loading"
    />
  </div>
</template>
