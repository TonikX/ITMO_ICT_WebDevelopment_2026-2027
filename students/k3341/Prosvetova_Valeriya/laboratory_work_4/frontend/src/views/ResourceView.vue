<template>
  <div class="d-flex align-center mb-4">
    <h1 class="text-h5">{{ resource.title }}</h1>
    <v-spacer />
    <v-btn color="primary" prepend-icon="mdi-plus" @click="edit({})">Добавить</v-btn>
  </div>
  <v-alert v-if="error" type="error" class="mb-4" closable style="white-space: pre-line"
           @click:close="error = ''">{{ error }}</v-alert>

  <v-data-table :headers="headers" :items="data.lists[name]" :loading="loading" density="comfortable">
    <template v-for="f in fkFields" :key="f.key" #[`item.${f.key}`]="{ item }">
      {{ data.name(f.ref, item[f.key]) }}
    </template>
    <template #item.is_active="{ item }">
      <v-icon :icon="item.is_active ? 'mdi-check' : 'mdi-close'" />
    </template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil" size="small" variant="text" title="Изменить" @click="edit(item)" />
      <v-btn icon="mdi-delete" size="small" variant="text" title="Удалить" @click="remove(item)" />
      <v-btn v-if="name === 'printing-houses' && item.is_active" icon="mdi-lock" size="small" variant="text"
             title="Закрыть типографию" @click="closeHouse(item)" />
    </template>
  </v-data-table>

  <v-dialog v-model="dialog" max-width="500">
    <v-card :title="form.id ? 'Изменение' : 'Создание'">
      <v-card-text>
        <template v-for="f in editableFields" :key="f.key">
          <v-select v-if="f.type === 'fk'" v-model="form[f.key]" :label="f.label"
                    :items="data.lists[f.ref]" item-value="id"
                    :item-title="(x) => data.name(f.ref, x.id)" />
          <v-text-field v-else v-model="form[f.key]" :label="f.label"
                        :type="f.type === 'number' ? 'number' : 'text'" />
        </template>
        <v-alert v-if="formError" type="error" style="white-space: pre-line">{{ formError }}</v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="dialog = false">Отмена</v-btn>
        <v-btn color="primary" @click="save">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { api, errorText } from '@/api'
import { resources } from '@/resources'
import { useDataStore } from '@/stores/data'

const props = defineProps({ name: { type: String, required: true } })
const data = useDataStore()
const resource = computed(() => resources[props.name])
const fkFields = computed(() => resource.value.fields.filter((f) => f.type === 'fk'))
const editableFields = computed(() => resource.value.fields.filter((f) => !f.readonly))
const headers = computed(() => [
  { title: 'ID', key: 'id' },
  ...resource.value.fields.map((f) => ({ title: f.label, key: f.key })),
  { title: '', key: 'actions', sortable: false, align: 'end' },
])

const loading = ref(false)
const error = ref('')
const dialog = ref(false)
const form = ref({})
const formError = ref('')

async function reload() {
  loading.value = true
  try {
    await data.load()
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}
watch(() => props.name, reload, { immediate: true })

function edit(item) {
  form.value = { ...item }
  formError.value = ''
  dialog.value = true
}

async function save() {
  const url = `/api/${props.name}/`
  const body = Object.fromEntries(editableFields.value.map((f) => [f.key, form.value[f.key] ?? '']))
  try {
    if (form.value.id) await api.put(`${url}${form.value.id}/`, body)
    else await api.post(url, body)
    dialog.value = false
    await reload()
  } catch (e) {
    formError.value = errorText(e)
  }
}

async function remove(item) {
  if (!confirm(`Удалить «${data.name(props.name, item.id)}»?`)) return
  try {
    await api.delete(`/api/${props.name}/${item.id}/`)
    await reload()
  } catch (e) {
    error.value = errorText(e)
  }
}

async function closeHouse(item) {
  if (!confirm(`Закрыть типографию «${item.name}»? Её тиражи перейдут другим типографиям.`)) return
  try {
    await api.post(`/api/printing-houses/${item.id}/close/`)
    await reload()
  } catch (e) {
    error.value = errorText(e)
  }
}
</script>
