<template>
  <div class="about-section" id="about" ref="aboutSectionRef">
    <!-- 背景 SVG -->
    <svg ref="bgSvg" class="bg-svg">
      <!-- 左墙 -->
      <polyline :points="leftWallPointsTop" fill="none" stroke="black" stroke-width="2" />
      <polyline :points="leftWallPointsBottom" fill="none" stroke="black" stroke-width="2" />
      <!-- 右墙 -->
      <polyline :points="rightWallPointsTop" fill="none" stroke="black" stroke-width="2" />
      <polyline :points="rightWallPointsBottom" fill="none" stroke="black" stroke-width="2" />
      <!-- ceil and floor -->
      <polyline :points="ceilPoints" fill="none" stroke="black" stroke-width="4" />
      <polyline :points="floorPoints" fill="none" stroke="black" stroke-width="4" />
      <!-- 后墙（矩形） -->
      <polygon :points="backWallPoints" fill="none" stroke="black" stroke-width="2" />
    </svg>

    <!-- 内容区域 -->
    <div class="content-container" ref="contentContainerRef">
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
const contentContainerRef = ref<HTMLElement | null>(null)
const bgSvg = ref<SVGSVGElement | null>(null)

const description = ref(`Hello! I'm a passionate web developer with a love for creating interactive and engaging user experiences.`)

// SVG points
const leftWallPointsTop = ref('')
const leftWallPointsBottom = ref('')
const rightWallPointsTop = ref('')
const rightWallPointsBottom = ref('')

const backWallPoints = ref('')
const ceilPoints = ref('')
const floorPoints = ref('')

const scrollYRatio = inject<Ref<number>>('scrollYRatio')

// 用于响应式更新的位置变量（可调）
const baseBackWallTopY = ref(0)
const baseBackWallBottomY = ref(0)
const backWallLeftX = ref(0)
const backWallRightX = ref(0)

const frontWallLeftX = ref(0)
const frontWallRightX = ref(0)
const frontWallTopY = ref(0)
const frontWallBottomY = ref(0)

// 更新所有坐标点
const calculatePoints = (scrollOffset : number) => {

  const parallaxFactor = 350 // 可调整 default 180
  // const initParallaxOffset = 150 // 初始偏移量

  const adjustedTopY = baseBackWallTopY.value + (scrollOffset * parallaxFactor - parallaxFactor)
  const adjustedBottomY = baseBackWallBottomY.value + (scrollOffset * parallaxFactor - parallaxFactor)
  
  const backTopLeft = { x: backWallLeftX.value, y: adjustedTopY }
  const backTopRight = { x: backWallRightX.value, y: adjustedTopY }
  const backBottomLeft = { x: backWallLeftX.value, y: adjustedBottomY }
  const backBottomRight = { x: backWallRightX.value, y: adjustedBottomY }

  const frontTopLeft = { x: frontWallLeftX.value, y: frontWallTopY.value }
  const frontTopRight = { x: frontWallRightX.value, y: frontWallTopY.value }
  const frontBottomLeft = { x: frontWallLeftX.value, y: frontWallBottomY.value }
  const frontBottomRight = { x: frontWallRightX.value, y: frontWallBottomY.value }

  updateContentPosition(adjustedTopY, adjustedBottomY)

  backWallPoints.value = [backTopLeft, backTopRight, backBottomRight, backBottomLeft]
    .map(p => `${p.x},${p.y}`).join(' ')

  leftWallPointsTop.value = [frontTopLeft, backTopLeft]
    .map(p => `${p.x},${p.y}`).join(' ')
  leftWallPointsBottom.value = [frontBottomLeft, backBottomLeft]
  .map(p => `${p.x},${p.y}`).join(' ')

  rightWallPointsTop.value = [frontTopRight, backTopRight]
    .map(p => `${p.x},${p.y}`).join(' ')
  rightWallPointsBottom.value = [frontBottomRight, backBottomRight]
  .map(p => `${p.x},${p.y}`).join(' ')

  ceilPoints.value = [frontTopLeft, frontTopRight]
    .map(p => `${p.x},${p.y}`).join(' ')
  floorPoints.value = [frontBottomLeft, frontBottomRight]
    .map(p => `${p.x},${p.y}`).join(' ')  
}

const updateContentPosition = (adjustedTopY: number, adjustedBottomY: number) => {
  if (!contentContainerRef.value) return
  const left = backWallLeftX.value
  const top = adjustedTopY
  const width = backWallRightX.value - backWallLeftX.value
  const height = adjustedBottomY - adjustedTopY

  const el = contentContainerRef.value
  el.style.position = 'absolute'
  el.style.left = `${left}px`
  el.style.top = `${top}px`
  el.style.width = `${width}px`
  el.style.height = `${height}px`
  el.style.transform = 'none'
}


// 初始尺寸计算
const updateSize = () => {
  if (aboutSectionRef.value) {
    const rect = aboutSectionRef.value.getBoundingClientRect()
    const sectionWidth = rect.width
    const sectionHeight = rect.height

    const centerX = sectionWidth / 2
    const centerY = sectionHeight / 2

    const backWallWidth = sectionWidth * 0.8
    const backWallHeight = sectionHeight * 0.7

    backWallLeftX.value = centerX - backWallWidth / 2
    backWallRightX.value = centerX + backWallWidth / 2
    baseBackWallTopY.value = centerY - backWallHeight / 2
    baseBackWallBottomY.value = centerY + backWallHeight / 2

    frontWallLeftX.value = centerX - sectionWidth / 2
    frontWallRightX.value = centerX + sectionWidth / 2
    frontWallTopY.value = centerY - sectionHeight / 2
    frontWallBottomY.value = centerY + sectionHeight / 2

    const scrollOffset = scrollYRatio?.value || 0
    calculatePoints(scrollOffset)
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

// 监听 scrollY 变化并动态更新位置
watch(scrollYRatio!, () => {
  const scrollOffset = scrollYRatio?.value || 0
  calculatePoints(scrollOffset)
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
  background-color: #ffffff;
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
  z-index: 1;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  box-sizing: border-box;
  overflow: hidden;

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
  position: absolute;
}
</style>
