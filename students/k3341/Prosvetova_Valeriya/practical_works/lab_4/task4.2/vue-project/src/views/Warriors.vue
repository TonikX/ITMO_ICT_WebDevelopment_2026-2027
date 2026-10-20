<template>
  <div class="app">
    <h1>Портал информации о воинах в онлайн РПГ</h1>
    <button v-on:click="fetchWarriors">Получить список воинов</button> 
    <warrior-form @created="fetchWarriors"/> 
    <warrior-list v-bind:warriors="warriors"/> 
  </div>
</template>

<script>
import WarriorForm from '@/components/WarriorForm.vue'
import WarriorList from '@/components/WarriorList.vue'
import axios from 'axios'
import { API_URL } from '@/api'

export default {
  components: {
    WarriorForm, WarriorList,
  },
  data() { 
    return {
      warriors: [], 
    }
  },
  methods: {
    async fetchWarriors() {
      try {
        const response = await axios.get(`${API_URL}/warriors/list/`) 
        this.warriors = response.data.results ?? response.data
      } catch (e) {
        alert('Ошибка')
      }
    },
  },
  mounted() {
    this.fetchWarriors() 
  },
}
</script>
