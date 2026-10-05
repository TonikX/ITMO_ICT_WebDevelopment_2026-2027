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
  specialty: "",
  education: "",
  gender: "M",
  birth_date: "",
  hire_date: "",
  contract_info: "",
})

async function load() {
  loading.value = true
  try {
    const { data } = await clinicApi.doctors()
    items.value = data
  } finally {
    loading.value = false
  }
}

async function createDoctor() {
  await clinicApi.createDoctor({ ...form })
  dialog.value = false
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex align-center mb-4">
      <div class="text-h5">Врачи</div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">
        Добавить
      </v-btn>
    </div>
    <v-data-table
      :headers="[
        { title: 'ФИО', key: 'fio' },
        { title: 'Специальность', key: 'specialty' },
        { title: 'Образование', key: 'education' },
        { title: 'Дата найма', key: 'hire_date' },
      ]"
      :items="items"
      :loading="loading"
      item-value="id"
      @click:row="(_, { item }) => router.push(`/doctors/${item.id}`)"
      hover
    />

    <v-dialog v-model="dialog" max-width="640">
      <v-card class="pa-4">
        <div class="text-h6 mb-4">Новый врач</div>
        <v-row dense>
          <v-col cols="12" md="4"><v-text-field v-model="form.last_name" label="Фамилия" /></v-col>
          <v-col cols="12" md="4"><v-text-field v-model="form.first_name" label="Имя" /></v-col>
          <v-col cols="12" md="4"><v-text-field v-model="form.middle_name" label="Отчество" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.specialty" label="Специальность" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.education" label="Образование" /></v-col>
          <v-col cols="12" md="4">
            <v-select v-model="form.gender" :items="['M', 'F']" label="Пол" />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model="form.birth_date" label="Дата рождения" type="date" />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model="form.hire_date" label="Дата найма" type="date" />
          </v-col>
          <v-col cols="12">
            <v-text-field v-model="form.contract_info" label="Договор" />
          </v-col>
        </v-row>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="createDoctor">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
