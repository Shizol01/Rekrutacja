import { createRouter, createWebHistory } from 'vue-router';

import HomeView from '../views/HomeView.vue';
import ScanView from '../views/ScanView.vue';
import StatusView from '../views/StatusView.vue';

const router = createRouter({
  history: createWebHistory('/api/tablet/'),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/scan', name: 'scan', component: ScanView },
    { path: '/status', name: 'status', component: StatusView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

export default router;
