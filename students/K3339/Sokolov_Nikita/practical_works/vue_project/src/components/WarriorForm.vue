<template>
  <div class="card">
    <h2>Создание воина</h2>
    <form @submit.prevent="createWarrior">
      <input v-model="warrior.name" type="text" placeholder="Имя" required />
      <select v-model="warrior.race" required>
        <option disabled value="">Раса</option>
        <option value="s">student</option>
        <option value="d">developer</option>
        <option value="t">teamlead</option>
      </select>
      <button type="submit">Создать</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from "axios"

const API = import.meta.env.VITE_WARRIORS_API || "http://127.0.0.1:8001"

export default {
  name: "WarriorForm",
  emits: ["created"],
  data() {
    return {
      warrior: {
        name: "",
        race: "",
      },
      message: "",
    }
  },
  methods: {
    async createWarrior() {
      try {
        await axios.post(`${API}/war/warrior/create1/`, {
          race: this.warrior.race,
          name: this.warrior.name,
        })
        this.message = "Воин создан"
        this.warrior.name = ""
        this.warrior.race = ""
        this.$emit("created")
      } catch (e) {
        this.message = "Ошибка создания"
      }
    },
  },
}
</script>
