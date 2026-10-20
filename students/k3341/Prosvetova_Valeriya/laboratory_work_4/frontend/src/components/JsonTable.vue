<template>
  <!-- Отображаем результаты запросов к API в виде таблицы. Если данные содержат вложенные объекты, их поля выводятся в отдельные столбцы. -->
  <v-table v-if="rows.length" density="compact">
    <thead><tr><th v-for="c in columns" :key="c">{{ c }}</th></tr></thead>
    <tbody>
      <tr v-for="(r, i) in rows" :key="i"><td v-for="c in columns" :key="c">{{ r[c] }}</td></tr>
    </tbody>
  </v-table>
  <div v-else class="text-medium-emphasis">Нет данных</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: [Array, Object], default: null } })

function flatten(obj, prefix = '') {
  return Object.entries(obj).reduce((acc, [k, v]) => {
    if (v && typeof v === 'object' && !Array.isArray(v)) Object.assign(acc, flatten(v, `${prefix}${k}.`))
    else acc[prefix + k] = v
    return acc
  }, {})
}

const rows = computed(() => (props.data == null ? [] : [].concat(props.data).map((r) => flatten(r))))
const columns = computed(() => [...new Set(rows.value.flatMap(Object.keys))])
</script>
