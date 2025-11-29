import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    ui({
      ui: {
        colors: {
          primary: 'green',
          neutral: 'zinc'
        }
      }
    })
  ],
  resolve: {
    alias: {
      // This is the modern replacement for path.resolve(__dirname, './src')
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})