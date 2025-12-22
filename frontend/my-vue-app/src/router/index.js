import { createRouter, createWebHistory } from 'vue-router';
import { HomeView, ScanView, StatusView } from '../views';

const normalizeBasePath = (value = '/api/tablet/') => {
  if (!value) return '/';
  const prefixed = value.startsWith('/') ? value : `/${value}`;
  return prefixed.endsWith('/') ? prefixed : `${prefixed}/`;
};

const basePath = normalizeBasePath(import.meta.env.VITE_APP_BASE_PATH || '/api/tablet/');

const router = createRouter({
  history: createWebHistory(basePath),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/status', name: 'status', component: StatusView },
    { path: '/scan', name: 'scan', component: ScanView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

export default router;
