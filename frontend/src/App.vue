<template>
  <div>
    <AppNavbar />

    <main class="container-fluid app-shell">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppNavbar from "./components/AppNavbar.vue";
</script>

<style scoped>
.app-shell {
  max-width: 1480px;
  margin: 0 auto;
  padding: 28px 24px 44px;
}
</style>
