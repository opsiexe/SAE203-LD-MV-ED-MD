<script setup>
import { useRoute } from 'vue-router'
import navbar from './components/navbar.vue'

const route = useRoute()
</script>

<template>
  <div>
    <!-- Affiche la navbar sauf sur / et /login -->
    <navbar v-if="route.path !== '/' && route.path !== '/login' && route.path !== '/logout'" />
    <router-view />
  </div>
</template>