import { createApp } from 'vue'
import '@fontsource/inter/300.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
import './styles/tokens.css'
import './styles/base.css'
import App from './App.vue'
import { magnetic } from './directives/magnetic'
import { router } from './router'
import { installPageCuts } from './composables/navigate'

installPageCuts()
createApp(App).use(router).directive('magnetic', magnetic).mount('#app')
