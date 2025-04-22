import { createRouter, createWebHistory } from 'vue-router';
import MyTickets from './components/mytickets.vue';
import NewTickets from './components/newtickets.vue';

const routes = [
  {
    path: '/mytickets',
    name: 'mytickets',
    component: MyTickets,
  },
  {
    path: '/newtickets',
    name: 'newtickets',
    component: NewTickets,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;