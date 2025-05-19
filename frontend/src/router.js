import { createRouter, createWebHistory } from 'vue-router';
import MyTickets from './components/mytickets.vue';
import NewTickets from './components/newtickets.vue';
import LoginPage from './components/login.vue';
import LogoutPage from './components/logout.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: LoginPage,
  },
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
  {
    path: '/login',
    name: 'loginPage',
    component: LoginPage,
  },
  {
    path: '/logout',
    name: 'logoutPage',
    component: LogoutPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;