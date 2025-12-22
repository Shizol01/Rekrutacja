import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const appBasePath = env.VITE_APP_BASE_PATH || '/api/tablet/';

  return {
    plugins: [vue()],
    base: '/static/',
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
    define: {
      __APP_BASE_PATH__: JSON.stringify(appBasePath),
    },
  };
});
