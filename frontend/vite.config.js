import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import WindiCSS from 'vite-plugin-windicss'

import path from "path"

// https://vitejs.dev/config/
export default defineConfig({
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src")
        }
    },

    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000/api',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
              }
        }
    },
    plugins: [vue(),
    WindiCSS()],
})
