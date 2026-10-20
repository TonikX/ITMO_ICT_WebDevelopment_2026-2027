<template>
  <h1 class="text-h5 mb-4">Запросы</h1>
  <v-row>
    <v-col v-for="q in queries" :key="q.title" cols="12" xl="6">
      <v-card :title="q.title" :subtitle="q.path">
        <v-card-text>
          <div class="d-flex ga-2 align-center">
            <template v-for="p in q.params" :key="p.key">
              <v-select v-if="p.ref" v-model="q.values[p.key]" :label="p.label" :items="data.lists[p.ref]"
                        item-value="id" :item-title="(x) => data.name(p.ref, x.id)" hide-details />
              <v-combobox v-else-if="p.options" v-model="q.values[p.key]" :label="p.label"
                          :items="p.options()" hide-details />
              <v-text-field v-else v-model="q.values[p.key]" :label="p.label" type="number" hide-details />
            </template>
            <v-btn color="primary" @click="run(q)">Выполнить</v-btn>
          </div>
          <v-alert v-if="q.error" type="error" class="mt-4">{{ q.error }}</v-alert>
          <json-table v-else-if="q.result" class="mt-4" :data="q.result" />
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { reactive } from 'vue'
import JsonTable from '@/components/JsonTable.vue'
import { api, errorText } from '@/api'
import { useDataStore } from '@/stores/data'

const data = useDataStore()
data.load() // списки нужны для выпадающих списков параметров

const newspaper = { key: 'newspaper', label: 'Газета', ref: 'newspapers' }
const house = { key: 'house', label: 'Типография', ref: 'printing-houses' }
const office = { key: 'office', label: 'Отделение', ref: 'post-offices' }
const addresses = () => [...new Set(data.lists['printing-houses'].map((h) => h.address))]

const queries = reactive([
  { title: 'По каким адресам печатается газета', params: [newspaper],
    url: (v) => `/api/analytics/newspapers/${v.newspaper}/printing-addresses/` },
  { title: 'Редактор газеты с самым большим тиражом в типографии', params: [house],
    url: (v) => `/api/analytics/printing-houses/${v.house}/top-editor/` },
  { title: 'Отделения, куда поступает газета дороже цены', params: [{ key: 'price', label: 'Цена больше' }],
    url: (v) => `/api/analytics/post-offices-by-price/?price_gt=${v.price ?? ''}` },
  { title: 'Газеты, поступающие в количестве меньше заданного',
    params: [{ key: 'quantity', label: 'Количество меньше' }],
    url: (v) => `/api/analytics/low-deliveries/?quantity_lt=${v.quantity ?? ''}` },
  { title: 'Куда поступает газета, печатающаяся по адресу',
    params: [newspaper, { key: 'address', label: 'Адрес типографии', options: addresses }],
    url: (v) => `/api/analytics/newspapers/${v.newspaper}/destinations/?address=${encodeURIComponent(v.address ?? '')}` },
  { title: 'Справка об индексе и цене газеты', params: [newspaper],
    url: (v) => `/api/analytics/newspapers/${v.newspaper}/reference/` },
  { title: 'Типографии газеты (многие-ко-многим)', params: [newspaper],
    url: (v) => `/api/newspapers/${v.newspaper}/printing-houses/` },
  { title: 'Тиражи типографии', params: [house],
    url: (v) => `/api/printing-houses/${v.house}/print-runs/` },
  { title: 'Поставки в почтовое отделение', params: [office],
    url: (v) => `/api/post-offices/${v.office}/deliveries/` },
].map((q) => ({
  ...q,
  // Формируем адрес запроса с названиями параметров вместо их значений для отображения в карточке.
  path: decodeURIComponent(q.url(Object.fromEntries(q.params.map((p) => [p.key, `{${p.key}}`])))),
  values: {}, result: null, error: '',
})))

async function run(q) {
  q.error = ''
  if (q.params.some((p) => q.values[p.key] == null || q.values[p.key] === '')) {
    q.error = 'Заполните параметры запроса'
    return
  }
  try {
    q.result = (await api.get(q.url(q.values))).data
  } catch (e) {
    q.error = errorText(e)
  }
}
</script>
