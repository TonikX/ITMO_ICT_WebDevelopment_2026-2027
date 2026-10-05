<script setup>
import { onMounted, reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { clinicApi } from "@/api/clinic"

const router = useRouter()
const items = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({
  last_name: "",
  first_name: "",
  middle_name: "",
  phone: "",
  birth_date: "",
  gender: "M",
})

async function load() {
  loading.value = true
  try {
    const { data } = await clinicApi.patients()
    items.value = data
  } finally {
    loading.value = false
  }
}

async function createPatient() {
  await clinicApi.createPatient({ ...form })
  dialog.value = false
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex align-center mb-4">
      <div class="text-h5">Пациенты</div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">
        Добавить
      </v-btn>
    </div>
    <v-data-table
      :headers="[
        { title: 'ФИО', key: 'fio' },
        { title: 'Телефон', key: 'phone' },
        { title: 'Дата рождения', key: 'birth_date' },
        { title: 'Пол', key: 'gender' },
      ]"
      :items="items"
      :loading="loading"
      @click:row="(_, { item }) => router.push(`/patients/${item.id}`)"
      hover
    />

    <v-dialog v-model="dialog" max-width="560">
      <v-card class="pa-4">
        <div class="text-h6 mb-4">Новый пациент</div>
        <v-row dense>
          <v-col cols="12" md="4"><v-text-field v-model="form.last_name" label="Фамилия" /></v-col>
          <v-col cols="12" md="4"><v-text-field v-model="form.first_name" label="Имя" /></v-col>
          <v-col cols="12" md="4"><v-text-field v-model="form.middle_name" label="Отчество" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.phone" label="Телефон" /></v-col>
          <v-col cols="12" md="3">
            <v-text-field v-model="form.birth_date" label="ДР" type="date" />
          </v-col>
          <v-col cols="12" md="3">
            <v-select v-model="form.gender" :items="['M', 'F']" label="Пол" />
          </v-col>
        </v-row>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="createPatient">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
