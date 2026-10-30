<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { scramble } from '../composables/scramble'

const props = withDefaults(defineProps<{
  text: string
  as?: string
  trigger?: 'mount' | 'visible' | 'hover' | 'manual'
  duration?: number
  delay?: number
}>(), { as: 'span', trigger: 'visible', duration: 900, delay: 0 })

const shown = ref(props.trigger === 'hover' ? props.text : props.text.replace(/\S/g, '░'))
const el = ref<HTMLElement>()
let cancel = () => {}
let io: IntersectionObserver | undefined

function play() {
  cancel()
  setTimeout(() => { cancel = scramble(props.text, (s) => (shown.value = s), props.duration) }, props.delay)
}
defineExpose({ play })

onMounted(() => {
  if (props.trigger === 'mount') play()
  if (props.trigger === 'visible' && el.value) {
    io = new IntersectionObserver((es) => { if (es[0].isIntersecting) { play(); io?.disconnect() } }, { threshold: 0.4 })
    io.observe(el.value)
  }
})
watch(() => props.text, play)
onBeforeUnmount(() => { cancel(); io?.disconnect() })
</script>

<template>
  <component :is="as" ref="el" :aria-label="text" @mouseenter="trigger === 'hover' && play()">
    <span aria-hidden="true">{{ shown }}</span>
  </component>
</template>
