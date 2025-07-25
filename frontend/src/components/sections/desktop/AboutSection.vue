<template>
  <div class="about-section" id="about" ref="aboutSectionRef">
    <!-- 背景 SVG -->
    <svg ref="bgSvg" class="bg-svg">
      <!-- 左墙 -->
      <polyline :points="leftWallPoints" fill="none" stroke="black" stroke-width="2" />
      <!-- 右墙 -->
      <polyline :points="rightWallPoints" fill="none" stroke="black" stroke-width="2" />
      
      <!-- 后墙（矩形） -->
      <polygon :points="backWallPoints" fill="none" stroke="black" stroke-width="2" />
    </svg>

    <!-- 内容区域 -->
    <div class="content-container">
      <div class="social-section">
        <div class="image-area">
          <img src="@/assets/img/alec-tucker-alec-tucker-snowy1-f.jpg" alt="Your Image" class="profile-image" />
        </div>
        <div class="social-icons">
          <a href="https://github.com/yourname" target="_blank" class="icon github">🐙</a>
          <a href="https://your-social-link.com" target="_blank" class="icon social">🌐</a>
        </div>
      </div>

      <div class="intro-section">
        <h2 class="title">ABOUT ME</h2>
        <p class="description">
          {{ description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, nextTick, inject, watch, type Ref } from 'vue'

const aboutSectionRef = ref<HTMLElement | null>(null)
const bgSvg = ref<SVGSVGElement | null>(null)

const width = ref(0)
const height = ref(0)
const description = ref(`Hello! I'm a passionate web developer with a love for creating interactive and engaging user experiences.`)

// SVG points
const leftWallPoints = ref('')
const rightWallPoints = ref('')
const backWallPoints = ref('')

const scrollY = inject<Ref<number>>('scrollY')

// 计算所有坐标点
const calculatePoints = () => {
  const w = width.value
  const h = height.value
  const cx = w / 2
  const cy = h / 2

  const bw = w * 0.4 // back wall 宽度
  const bh = h * 0.4 // back wall 高度

  const backTopLeft = { x: cx - bw / 2, y: cy - bh / 2 }
  const backTopRight = { x: cx + bw / 2, y: cy - bh / 2 }
  const backBottomRight = { x: cx + bw / 2, y: cy + bh / 2 }
  const backBottomLeft = { x: cx - bw / 2, y: cy + bh / 2 }

  const frontTopLeft = { x: cx - w / 2, y: cy - h / 2 }
  const frontTopRight = { x: cx + w / 2, y: cy - h / 2 }
  const frontBottomRight = { x: cx + w / 2, y: cy + h / 2 }
  const frontBottomLeft = { x: cx - w / 2, y: cy + h / 2 }

  backWallPoints.value = [
    backTopLeft,
    backTopRight,
    backBottomRight,
    backBottomLeft
  ].map(p => `${p.x},${p.y}`).join(' ')

  leftWallPoints.value = [
    frontTopLeft,
    backTopLeft,
    backBottomLeft,
    frontBottomLeft
  ].map(p => `${p.x},${p.y}`).join(' ')

  rightWallPoints.value = [
    frontTopRight,
    backTopRight,
    backBottomRight,
    frontBottomRight
  ].map(p => `${p.x},${p.y}`).join(' ')

  // 你可以在这里添加 left/right wall/floor/ceiling 的计算逻辑
}

const updateSize = () => {
  if (aboutSectionRef.value) {
    const rect = aboutSectionRef.value.getBoundingClientRect()
    width.value = rect.width
    height.value = rect.height
    calculatePoints()
  }
}

onMounted(async () => {
  await nextTick()
  updateSize()
  window.addEventListener('resize', updateSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateSize)
})
</script>

<style scoped>
.about-section {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
  overflow: hidden;
}

.bg-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.content-container {
  position: relative;
  z-index: 1;
  display: flex;
  width: 90%;
  max-width: 1200px;
  height: 80%;
  justify-content: space-between;
  align-items: center;
  
}

.social-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-area {
  position: relative;
}

.profile-image {
  width: 200px;
  border-radius: 10px;
  margin-bottom: 1rem;
}

.social-icons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.icon {
  font-size: 2rem;
  cursor: pointer;
  transition: transform 0.3s;
}

.icon:hover {
  transform: scale(1.2);
}

.intro-section {
  flex: 2;
  text-align: right;
  padding-left: 2rem;
}

.title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.description {
  max-width: 600px;
  line-height: 1.6;
  font-size: 1rem;
  color: #333;
}
</style>
