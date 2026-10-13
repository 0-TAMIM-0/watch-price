import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],

  server: {
    host: true,
    watch: { usePolling: true },   // required on Windows + Docker, otherwise file changes are not detected
  },

  resolve: {
    alias: [
      {
        find: '@store',
        replacement: fileURLToPath(new URL('./src/store', import.meta.url))
      },
      {
        find: '@types',
        replacement: fileURLToPath(new URL('./src/types', import.meta.url))
      },
      {
        find: '@img',
        replacement: fileURLToPath(new URL('./src/assets/img', import.meta.url))
      },
      {
        find: '@icon',
        replacement: fileURLToPath(new URL('./src/assets/icon', import.meta.url))
      },
      {
        find: '@components',
        replacement: fileURLToPath(new URL('./src/components', import.meta.url))
      },
    ]
  },
})
