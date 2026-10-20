<template>
  <div class="warrior" v-for="warrior in warriors" :key="warrior.id"> 
    <div><strong>Имя:</strong> {{ warrior.name }}</div>
    <div><strong>Раса:</strong> {{ warrior.race }}</div>
  </div>
</template>

<script>
export default {
  name: 'WarriorList',
  props: { // props - данные, которые родительский компонент передаёт дочернему
    warriors: {
      type: Array,
      required: true,
    },
  },
}
</script>

<style scoped>
.warrior {
  border-bottom: 1px solid #ddd;
  padding: 6px 0;
}
</style>
