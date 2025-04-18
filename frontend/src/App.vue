<script setup>
import navbar from './components/navbar.vue'
import mytickets from './components/mytickets.vue'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router';

const tickets = ref([])
const route = useRoute();

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/tickets')
    tickets.value = await res.data;
  } catch (error) {
    console.error('Erreur lors de la récupération des tickets:', error);
  }
})
</script>

<template>
  <div>
    <navbar />
    <mytickets v-if="route.name === 'mytickets'" />
  </div>
</template>