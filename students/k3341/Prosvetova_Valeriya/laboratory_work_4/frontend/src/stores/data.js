import { defineStore } from 'pinia'
import { api } from '@/api'
import { resources } from '@/resources'

// Загружаем списки всех сущностей для отображения данных и связанных записей.
// Это позволяет показывать названия связанных объектов вместо их идентификаторов.
export const useDataStore = defineStore('data', {
  state: () => ({ lists: Object.fromEntries(Object.keys(resources).map((k) => [k, []])) }),
  actions: {
    async load() {
      const names = Object.keys(resources)
      const responses = await Promise.all(names.map((n) => api.get(`/api/${n}/`)))
      names.forEach((n, i) => (this.lists[n] = responses[i].data))
    },
    // Находим запись по её идентификатору и возвращаем текст для отображения в интерфейсе.
    name(resource, id) {
      const item = this.lists[resource].find((x) => x.id === id)
      return item ? resources[resource].label(item, this.name) : `#${id}`
    },
  },
})
