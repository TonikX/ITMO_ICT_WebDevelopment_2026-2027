<template>
  <form @submit.prevent> <!-- @submit.prevent предотвращает стандартную отправку формы и перезагрузку страницы -->
    <h1>Создание воина</h1>
    <input v-model="warrior.name" class="input" type="text" placeholder="Имя">
    <input v-model="warrior.race" class="input" type="text" placeholder="Раса">
    <button class="btn" v-on:click="createWarrior">Создать</button>
  </form>
</template>

<script>
import axios from 'axios'
import { API_URL } from '@/api'

export default {
  name: 'WarriorForm',
  emits: ['created'],
  data() {
    return {
      warrior: {
        name: '',
        race: '',
      },
    }
  },
  methods: {
    async createWarrior() {
      try {
        await axios.post(`${API_URL}/warrior/create/`, {
          race: this.warrior.race,
          name: this.warrior.name,
        })
        this.warrior.name = ''
        this.$emit('created') // сообщаем родительскому компоненту о создании записи для обновления списка
      } catch (e) {
        alert('Ошибка')
      }
    },
  },
}
</script>

<style scoped>
.input, .btn {
  margin-right: 8px;
}
</style>
