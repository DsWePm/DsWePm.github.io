import { reactive } from 'vue'

// The category tab picked in each home-page index; the nav's dropdowns set it too.
export const filters = reactive({ log: 'all', projects: 'all' })
