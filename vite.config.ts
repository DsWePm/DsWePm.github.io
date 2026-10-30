import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'
import { defineConfig } from 'vite'

export default defineConfig(({ mode }) => {
  // `npm run dev:lan`: HTTPS on the LAN, since phones only expose the tilt sensor to secure pages
  const lan = mode === 'lan'
  return {
    // a project page lives under /<repo>/ (the deploy workflow sets BASE_PATH); <login>.github.io at /
    base: process.env.BASE_PATH || '/',
    plugins: [vue(), ...(lan ? [basicSsl()] : [])],
    // Blender writes renders here frame by frame; don't reload the dev page on every write.
    // Vite lists public files at startup, so restart the dev server after a render.
    server: { host: lan, watch: { ignored: ['**/public/hero/**', '**/public/video/**', '**/tools/**'] } },
    // three.js lives in its own lazily loaded HeroStill chunk
    build: { chunkSizeWarningLimit: 800 },
  }
})
