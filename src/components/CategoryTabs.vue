<script setup lang="ts">
import { computed } from 'vue'
import { categoriesIn, entries, type Collection } from '../data/posts'
import { filters } from '../composables/filters'

// ┌ ALL 03 │ AI 01 │ CG 02 ┐ — picks the category shown by an index below it
const props = defineProps<{ collection: Collection }>()
const groups = computed(() => categoriesIn(props.collection))
const pad = (n: number) => String(n).padStart(2, '0')
</script>

<template>
  <div v-if="groups.length > 1" class="tabs mono" role="tablist">
    <span class="edge" aria-hidden="true">┌</span>
    <button role="tab" :aria-selected="filters[collection] === 'all'" :class="{ on: filters[collection] === 'all' }" @click="filters[collection] = 'all'">
      ALL <i>{{ pad(entries[collection].length) }}</i>
    </button>
    <template v-for="g in groups" :key="g.category.id">
      <span class="sep" aria-hidden="true">│</span>
      <button role="tab" :aria-selected="filters[collection] === g.category.id" :class="{ on: filters[collection] === g.category.id }" :title="g.category.name"
              @click="filters[collection] = g.category.id">
        {{ g.category.label }} <i>{{ pad(g.items.length) }}</i>
      </button>
    </template>
    <span class="edge" aria-hidden="true">┐</span>
  </div>
</template>

<style scoped>
.tabs { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin: 0 0 28px; font-size: 11px; letter-spacing: 0.16em; color: var(--fog-dim); }
.edge, .sep { color: var(--accent-dim); }
button { position: relative; padding: 6px 10px; color: var(--fog); cursor: pointer; transition: color 0.25s; }
button i { font-style: normal; color: var(--fog-dim); margin-left: 4px; }
button::after { content: ''; position: absolute; left: 10px; right: 10px; bottom: 0; height: 1px; background: var(--accent); transform: scaleX(0); transition: transform 0.4s var(--ease-out); }
button:hover { color: var(--mist); }
button.on { color: var(--mist); }
button.on::after { transform: none; }
button.on i { color: var(--accent); }
</style>
