<script setup>
import navbar from './components/navbar.vue'
import mytickets from './components/mytickets.vue'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router';

const tickets = ref([])
const route = useRoute();

onMounted(async () => {
  const res = await fetch('http://localhost:5000/api/tickets')
  if (res.ok) {
    tickets.value = await res.json();
  } else {
    console.error('Failed to fetch tickets:', res.statusText);
  }
})
</script>

<template>
  <div>
    <navbar />
    <mytickets v-if="route.name === 'mytickets'" />
  </div>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
