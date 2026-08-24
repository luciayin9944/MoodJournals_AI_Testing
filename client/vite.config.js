// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/me': 'http://localhost:5000',
      '/signup': 'http://localhost:5000',
      '/login': 'http://localhost:5000',
      '/journals': 'http://localhost:5000',
      '/entries': 'http://localhost:5000',
    }
  }
})











// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
// })
