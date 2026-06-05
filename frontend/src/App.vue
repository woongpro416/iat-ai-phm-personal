<template>
  <div>
    <AppNavbar />

    <main class="container-fluid app-shell py-4">
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
  padding-left: 24px;
  padding-right: 24px;
}
</style>
