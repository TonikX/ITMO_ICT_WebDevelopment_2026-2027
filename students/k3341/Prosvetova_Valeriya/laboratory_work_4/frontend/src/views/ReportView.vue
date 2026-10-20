<template>
  <h1 class="text-h5 mb-4">Отчёт о работе типографий</h1>
  <v-alert v-if="error" type="error">{{ error }}</v-alert>
  <v-card v-for="h in report" :key="h.id" class="mb-4"
          :title="`${h.name}${h.is_active ? '' : ' (закрыта)'}`"
          :subtitle="`${h.address} · всего экземпляров: ${h.total_copies}`">
    <v-card-text>
      <v-row>
        <v-col cols="12" md="5">
          <div class="text-subtitle-2">Тиражи по газетам</div>
          <v-table density="compact">
            <tbody>
              <tr v-for="r in h.by_newspaper" :key="r.newspaper.id">
                <td>{{ r.newspaper.title }}</td><td class="text-end">{{ r.circulation }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
        <v-col cols="12" md="7">
          <div class="text-subtitle-2">Отправки в почтовые отделения</div>
          <v-table density="compact">
            <tbody>
              <template v-for="s in h.shipments" :key="s.post_office.id">
                <tr v-for="(it, i) in s.items" :key="it.newspaper.id">
                  <td>{{ i === 0 ? `№${s.post_office.number}, ${s.post_office.address}` : '' }}</td>
                  <td>{{ it.newspaper.title }}</td><td class="text-end">{{ it.quantity }}</td>
                </tr>
              </template>
            </tbody>
          </v-table>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { api, errorText } from '@/api'

const report = ref([])
const error = ref('')

api.get('/api/reports/printing-houses/')
  .then((r) => (report.value = r.data))
  .catch((e) => (error.value = errorText(e)))
</script>
