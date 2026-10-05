<script setup>
import { onMounted, ref } from "vue"
import { clinicApi } from "@/api/clinic"

const tab = ref("oto")
const loading = ref(false)
const oto = ref([])
const sums = ref(null)
const visitsByDate = ref([])
const paid = ref([])
const date = ref(new Date().toISOString().slice(0, 10))
const doctorsByDate = ref([])
const doctorId = ref(1)
const doctorPatients = ref([])
const periodFrom = ref("2024-01-01")
const periodTo = ref("2026-12-31")
const periodReport = ref([])

async function loadOto() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsOtolaryngology()
    oto.value = data
  } finally {
    loading.value = false
  }
}

async function loadSums() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsTreatmentSums()
    sums.value = data
  } finally {
    loading.value = false
  }
}

async function loadVisits() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsVisitsByDate()
    visitsByDate.value = data
  } finally {
    loading.value = false
  }
}

async function loadPaid() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsPaidPatients()
    paid.value = data
  } finally {
    loading.value = false
  }
}

async function loadDoctorsByDate() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsDoctorsByDate(date.value)
    doctorsByDate.value = data
  } finally {
    loading.value = false
  }
}

async function loadDoctorPatients() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsDoctorPatients(doctorId.value)
    doctorPatients.value = data
  } finally {
    loading.value = false
  }
}

async function loadPeriod() {
  loading.value = true
  try {
    const { data } = await clinicApi.analyticsDoctorPeriod(periodFrom.value, periodTo.value)
    periodReport.value = data
  } finally {
    loading.value = false
  }
}

onMounted(loadOto)
</script>

<template>
  <div>
    <div class="text-h5 mb-4">Аналитика (вариант 10)</div>
    <v-tabs v-model="tab" color="primary" class="mb-4">
      <v-tab value="oto" @click="loadOto">ЛОР-пациенты</v-tab>
      <v-tab value="sums" @click="loadSums">Суммы</v-tab>
      <v-tab value="visits" @click="loadVisits">Приёмы по датам</v-tab>
      <v-tab value="paid" @click="loadPaid">Оплатившие</v-tab>
      <v-tab value="bydate" @click="loadDoctorsByDate">Врачи по дате</v-tab>
      <v-tab value="docpat" @click="loadDoctorPatients">Пациенты врача</v-tab>
      <v-tab value="period" @click="loadPeriod">Отчёт за период</v-tab>
    </v-tabs>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

    <div v-if="tab === 'oto'">
      <v-data-table
        :headers="[
          { title: 'ФИО', key: 'fio' },
          { title: 'Телефон', key: 'phone' },
          { title: 'ДР', key: 'birth_date' },
        ]"
        :items="oto"
      />
    </div>

    <div v-else-if="tab === 'sums' && sums">
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-subtitle-1 mb-2">По дням</div>
          <v-data-table
            :headers="[
              { title: 'Дата', key: 'day' },
              { title: 'Сумма', key: 'total' },
            ]"
            :items="sums.by_day || []"
          />
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-subtitle-1 mb-2">По врачам</div>
          <v-data-table
            :headers="[
              { title: 'Врач', key: 'doctor__last_name' },
              { title: 'Имя', key: 'doctor__first_name' },
              { title: 'Сумма', key: 'total' },
            ]"
            :items="sums.by_doctor || []"
          />
        </v-col>
      </v-row>
    </div>

    <div v-else-if="tab === 'visits'">
      <v-data-table
        :headers="[
          { title: 'Дата', key: 'day' },
          { title: 'Число приёмов', key: 'count' },
        ]"
        :items="visitsByDate"
      />
    </div>

    <div v-else-if="tab === 'paid'">
      <v-data-table
        :headers="[
          { title: 'ФИО', key: 'fio' },
          { title: 'Телефон', key: 'phone' },
        ]"
        :items="paid"
      />
    </div>

    <div v-else-if="tab === 'bydate'">
      <div class="d-flex ga-3 mb-4 align-center">
        <v-text-field v-model="date" type="date" label="Дата" style="max-width: 220px" />
        <v-btn color="primary" @click="loadDoctorsByDate">Показать</v-btn>
      </div>
      <v-data-table
        :headers="[
          { title: 'ФИО', key: 'fio' },
          { title: 'Специальность', key: 'specialty' },
        ]"
        :items="doctorsByDate"
      />
    </div>

    <div v-else-if="tab === 'docpat'">
      <div class="d-flex ga-3 mb-4 align-center">
        <v-text-field
          v-model.number="doctorId"
          type="number"
          label="ID врача"
          style="max-width: 160px"
        />
        <v-btn color="primary" @click="loadDoctorPatients">Показать</v-btn>
      </div>
      <v-data-table
        :headers="[
          { title: 'Пациент', key: 'patient' },
          { title: 'Дата приёма', key: 'visit_at' },
          { title: 'Стоимость', key: 'cost' },
        ]"
        :items="doctorPatients"
      />
    </div>

    <div v-else-if="tab === 'period'">
      <div class="d-flex ga-3 mb-4 align-center flex-wrap">
        <v-text-field v-model="periodFrom" type="date" label="С" style="max-width: 180px" />
        <v-text-field v-model="periodTo" type="date" label="По" style="max-width: 180px" />
        <v-btn color="primary" @click="loadPeriod">Показать</v-btn>
      </div>
      <v-data-table
        :headers="[
          { title: 'Врач', key: 'doctor' },
          { title: 'Пациентов', key: 'patients' },
          { title: 'Сумма', key: 'total_income' },
        ]"
        :items="periodReport"
      >
        <template #item.patients="{ item }">
          {{ item.patients?.length || 0 }}
        </template>
      </v-data-table>
    </div>
  </div>
</template>
