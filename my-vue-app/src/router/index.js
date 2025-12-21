import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import ScanView from '../views/ScanView.vue'
import StatusView from '../views/StatusView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import ReportsView from '../views/ReportsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/scan', name: 'scan', component: ScanView },
    { path: '/status', name: 'status', component: StatusView },
    { path: '/schedule', name: 'schedule', component: ScheduleView },
    { path: '/reports', name: 'reports', component: ReportsView },
  ],
})

export default router
