<template>
  <div class="app">
    <nav>
      <router-link to="/hi">Hello</router-link> |
      <router-link to="/warriors">Warriors</router-link>
    </nav>
    <router-view/>
  </div>
</template>

<style>
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
}
</style>
