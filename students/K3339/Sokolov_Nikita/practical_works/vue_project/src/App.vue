<template>
  <div class="app">
    <header class="header">
      <strong>Практика 4.2 — Vue.js</strong>
      <nav>
        <router-link to="/">Главная</router-link>
        <router-link to="/hi">Hello</router-link>
        <router-link to="/warriors">Warriors</router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>
