<template>
  <div>
    <div class="card">
      <h1>Портал информации о воинах</h1>
      <button type="button" @click="fetchWarriors">Получить список воинов</button>
    </div>
    <WarriorForm @created="fetchWarriors" />
    <WarriorList :warriors="warriors" />
  </div>
</template>

<script>
import axios from "axios"
import WarriorForm from "@/components/WarriorForm.vue"
import WarriorList from "@/components/WarriorList.vue"

const API = import.meta.env.VITE_WARRIORS_API || "http://127.0.0.1:8001"

export default {
  name: "Warriors",
  components: {
    WarriorForm,
    WarriorList,
  },
  data() {
    return {
      warriors: [],
    }
  },
  methods: {
    async fetchWarriors() {
      try {
        const response = await axios.get(`${API}/war/warriors/list/`)
        this.warriors = response.data.results || response.data
      } catch (e) {
        alert("Ошибка")
      }
    },
  },
  mounted() {
    this.fetchWarriors()
  },
}
</script>
