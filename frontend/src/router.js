import { createRouter, createWebHistory } from 'vue-router';
import MyTickets from './components/mytickets.vue';

const routes = [
  {
    path: '/mytickets',
    name: 'mytickets',
    component: MyTickets,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;