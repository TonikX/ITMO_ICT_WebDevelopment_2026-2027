<script setup>
import { onMounted, reactive, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const items = ref([])
const doctors = ref([])
const cards = ref([])
const cabinets = ref([])
const prices = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({
  medical_card: null,
  doctor: null,
  cabinet: null,
  price_list: null,
  visit_at: "",
  diagnosis: "",
  condition: "",
  recommendations: "",
  cost: "",
  is_paid: false,
})

async function load() {
  loading.value = true
  try {
    const [visits, docs, meds, cabs, prs] = await Promise.all([
      clinicApi.visits(),
      clinicApi.doctors(),
      clinicApi.medicalCards(),
      clinicApi.cabinets(),
      clinicApi.priceList(),
    ])
    items.value = visits.data
    doctors.value = docs.data
    cards.value = meds.data
    cabinets.value = cabs.data
    prices.value = prs.data
  } finally {
    loading.value = false
  }
}

async function createVisit() {
  await clinicApi.createVisit({
    ...form,
    cost: form.cost || "0",
  })
  dialog.value = false
  await load()
}

async function remove(id) {
  await clinicApi.deleteVisit(id)
  await load()
}

function doctorName(id) {
  return doctors.value.find((d) => d.id === id)?.fio || id
}

onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex align-center mb-4">
      <div class="text-h5">Приёмы</div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">Добавить</v-btn>
    </div>
    <v-data-table
      :headers="[
        { title: 'Дата', key: 'visit_at' },
        { title: 'Диагноз', key: 'diagnosis' },
        { title: 'Врач', key: 'doctor' },
        { title: 'Стоимость', key: 'cost' },
        { title: 'Оплачен', key: 'is_paid' },
        { title: '', key: 'actions', sortable: false },
      ]"
      :items="items"
      :loading="loading"
    >
      <template #item.doctor="{ item }">
        {{ doctorName(item.doctor) }}
      </template>
      <template #item.is_paid="{ item }">
        <v-icon :color="item.is_paid ? 'success' : 'warning'">
          {{ item.is_paid ? "mdi-check" : "mdi-close" }}
        </v-icon>
      </template>
      <template #item.actions="{ item }">
        <v-btn icon="mdi-delete" size="small" variant="text" @click="remove(item.id)" />
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="720">
      <v-card class="pa-4">
        <div class="text-h6 mb-4">Новый приём</div>
        <v-row dense>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.medical_card"
              :items="cards"
              item-title="id"
              item-value="id"
              label="Медкарта (id)"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.doctor"
              :items="doctors"
              item-title="fio"
              item-value="id"
              label="Врач"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.cabinet"
              :items="cabinets"
              item-title="number"
              item-value="id"
              label="Кабинет"
              clearable
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.price_list"
              :items="prices"
              item-title="service_name"
              item-value="id"
              label="Услуга"
              clearable
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.visit_at" label="Дата и время" type="datetime-local" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.cost" label="Стоимость" type="number" />
          </v-col>
          <v-col cols="12">
            <v-text-field v-model="form.diagnosis" label="Диагноз" />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="form.condition" label="Состояние" rows="2" />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="form.recommendations" label="Рекомендации" rows="2" />
          </v-col>
          <v-col cols="12">
            <v-switch v-model="form.is_paid" label="Оплачен" color="primary" />
          </v-col>
        </v-row>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="createVisit">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
