<template>
  <section class="skills-section">
    <h2>SkillsSection Loaded</h2>
    <button @click="playAnimation" class="trigger-button">播放动画</button>

    <div ref="panelWrapper" class="panel-wrapper">
      <div
        class="panel"
        v-for="(item, index) in 5"
        :key="index"
        :ref="el => panels[index] = el"
      >
        技能 {{ index + 1 }}
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import gsap from 'gsap'

// DOM refs
const panelWrapper = ref<HTMLElement | null>(null)
const panels: HTMLElement[] = []

function playAnimation() {
  gsap.fromTo(
    panels,
    {
      x: -200,
      opacity: 0,
      scale: 0.8,
    },
    {
      x: 0,
      opacity: 1,
      scale: 1,
      duration: 0.8,
      stagger: 0.2,
      ease: 'power2.out',
    }
  )
}
</script>

<style scoped>
.skills-section {
  background-color: #f4f4f4;
  padding: 80px 20px;
  min-height: 100vh;
  text-align: center;
}

.trigger-button {
  margin-bottom: 40px;
  padding: 12px 24px;
  font-size: 1.1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.trigger-button:hover {
  background-color: #2980b9;
}

.panel-wrapper {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
}
.panel {
  width: 200px;
  height: 200px;
  background-color: #9ecbff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  opacity: 0; /* 初始隐藏 */
  transform: translateX(0); /* 初始不偏移，交由动画控制 */
}
</style>
