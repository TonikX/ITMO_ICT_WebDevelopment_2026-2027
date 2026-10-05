<template>
  <div class="card">
    <h2>Список воинов</h2>
    <div v-if="!warriors.length">Пока пусто</div>
    <div v-for="warrior in warriors" :key="warrior.id" class="warrior-item">
      <div>Имя: {{ warrior.name }}</div>
      <div>Раса: {{ raceLabel(warrior.race) }}</div>
      <div>Уровень: {{ warrior.level }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "WarriorList",
  props: {
    warriors: {
      type: Array,
      required: true,
    },
  },
  methods: {
    raceLabel(race) {
      const map = { s: "student", d: "developer", t: "teamlead" }
      return map[race] || race
    },
  },
}
</script>
