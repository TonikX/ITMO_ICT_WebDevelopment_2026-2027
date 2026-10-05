<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const cards = ref([])
const selected = ref(null)
const detail = ref(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const { data } = await clinicApi.medicalCards()
    cards.value = data
  } finally {
    loading.value = false
  }
}

async function openCard(id) {
  selected.value = id
  const { data } = await clinicApi.medicalCardVisits(id)
  detail.value = data
}

onMounted(load)
</script>

<template>
  <div>
    <div class="text-h5 mb-4">Медицинские карты</div>
    <v-row>
      <v-col cols="12" md="5">
        <v-data-table
          :headers="[
            { title: 'ID', key: 'id' },
            { title: 'Пациент', key: 'patient.fio' },
            { title: 'Открыта', key: 'opened_at' },
          ]"
          :items="cards"
          :loading="loading"
          @click:row="(_, { item }) => openCard(item.id)"
          hover
        />
      </v-col>
      <v-col cols="12" md="7">
        <v-card v-if="detail" class="pa-4">
          <div class="text-h6 mb-2">
            Карта #{{ detail.id }} — {{ detail.patient?.fio }}
          </div>
          <div class="text-body-2 mb-4">Открыта: {{ detail.opened_at }}</div>
          <div class="text-subtitle-1 mb-2">Приёмы (nested 1:N)</div>
          <v-list>
            <v-list-item
              v-for="v in detail.visits"
              :key="v.id"
              :title="`${v.visit_at} · ${v.diagnosis}`"
              :subtitle="`${v.doctor?.fio || ''} · ${v.cost} ₽`"
            />
          </v-list>
        </v-card>
        <v-alert v-else type="info" variant="tonal">
          Выберите карту, чтобы увидеть вложенные приёмы
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>
