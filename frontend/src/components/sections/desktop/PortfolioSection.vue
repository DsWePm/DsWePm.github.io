<template>
  <section id="portfolio" class="portfolio-section" :class="{ locked: isLocked }">
    <canvas id="upperWallCanvas" class="upper-wall"></canvas>
    <canvas id="lowerWallCanvas" class="lower-wall"></canvas>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, inject, watch, computed } from 'vue'
import { scrollYRatioKey } from '@/types/injectionKeys'

/** ====== 参数 START ====== **/
const MAX_SHADOW_DEPTH = 4
const SHADOW_DEPTH_THRESHOLD = 0.5
const SHADOW_GROWTH_FACTOR = 0.01
const BRICK_GAP = 4
const BRICK_WIDTH = 70
const BRICK_HEIGHT = 25
const BASE_SHADOW_OFFSET = 0
const BRICK_BORDER_WIDTH = 1

const shadowGrowthCurve = (r: number) => Math.pow(r, SHADOW_GROWTH_FACTOR)
const horizontalShadowAlpha = (r: number) => 0.15 + 1 * r
const bottomShadowAlpha = (r: number) => 1 * r
/** ====== 参数 END ====== **/

const scrollYRatio = inject(scrollYRatioKey, ref(0))
const isLocked = computed(() => scrollYRatio.value < 0.6)

let upperCanvas: HTMLCanvasElement
let lowerCanvas: HTMLCanvasElement
let upperCtx: CanvasRenderingContext2D | null = null
let lowerCtx: CanvasRenderingContext2D | null = null

interface BrickInfo {
  x: number
  y: number
  depth: number
  isRightSide: boolean
  relativeDist: number
}

const upperBricks = ref<BrickInfo[]>([])
const lowerBricks = ref<BrickInfo[]>([])


const calculateOffset = (scrollYRatio: number): number => {
  const start = 1
  const end = 3
  if (scrollYRatio <= start) return -1;
  if (scrollYRatio >= end) return 1;

  const t = (scrollYRatio - start) / (end - start); // 归一化到 [0,1]
  return Math.cos((1 - t) * Math.PI); // 从 -1 到 1 平滑过渡
}

let lastScrollXOffset = 0 // 用于判断滚动方向

const drawWall = (
  canvas: HTMLCanvasElement,
  ctx: CanvasRenderingContext2D | null,
  direction: 'down' | 'up',
): BrickInfo[] => {
  if (!canvas || !ctx) return []

  const scrollXOffset = calculateOffset(scrollYRatio.value)

  const width = canvas.clientWidth
  const canvasHeight = canvas.clientHeight
  const dpr = window.devicePixelRatio || 1
  canvas.width = width * dpr
  canvas.height = canvasHeight * dpr
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, width, canvasHeight)

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, width, canvasHeight)

  const bricks: BrickInfo[] = []
  const centerX = width / 2

  const totalBrickWidth = BRICK_WIDTH + BRICK_GAP
  const normalizedOffset =
    ((scrollXOffset * 200) % totalBrickWidth + totalBrickWidth) % totalBrickWidth

  // 计算滚动方向
  const isScrollingRight = scrollXOffset > lastScrollXOffset
  lastScrollXOffset = scrollXOffset

  // 动态缓冲区配置
  const LEFT_BUFFER_COUNT = isScrollingRight ? 1 : 3
  const RIGHT_BUFFER_COUNT = isScrollingRight ? 3 : 1
  const leftBufferWidth = LEFT_BUFFER_COUNT * totalBrickWidth
  const rightBufferWidth = RIGHT_BUFFER_COUNT * totalBrickWidth

  const processRow = (y: number) => {
    const offset = (Math.floor(y / (BRICK_HEIGHT + BRICK_GAP)) % 2) * (BRICK_WIDTH / 2)

    const startX = -offset - leftBufferWidth - normalizedOffset
    const endX = width + rightBufferWidth

    for (
      let shiftedX = startX;
      shiftedX < endX;
      shiftedX += totalBrickWidth
    ) {
      const brickRightEdge = shiftedX + BRICK_WIDTH

      // 可选：确保砖块在可见区+缓冲区范围内
      if (brickRightEdge < -leftBufferWidth || shiftedX > width + rightBufferWidth) {
        continue
      }

      const brickCenter = shiftedX + BRICK_WIDTH / 2
      const distToCenter = Math.abs(brickCenter - centerX)
      const relativeDist = Math.min(distToCenter / (width / 2), 1)
      const depth = shadowGrowthCurve(relativeDist) * MAX_SHADOW_DEPTH
      const isRightSide = brickCenter > centerX

      ctx.fillStyle = '#f0f0f0'
      ctx.fillRect(shiftedX, y, BRICK_WIDTH, BRICK_HEIGHT)

      ctx.lineWidth = BRICK_BORDER_WIDTH
      ctx.strokeStyle = 'rgba(0,0,0,0.8)'
      ctx.strokeRect(shiftedX, y, BRICK_WIDTH, BRICK_HEIGHT)

      if (depth >= SHADOW_DEPTH_THRESHOLD) {
        bricks.push({ x: shiftedX, y, depth, isRightSide, relativeDist })
      }
    }
  }

  if (direction === 'up') {
    for (let y = 0; y + BRICK_HEIGHT <= canvasHeight; y += BRICK_HEIGHT + BRICK_GAP) {
      processRow(y)
    }
  } else {
    for (let y = canvasHeight - BRICK_HEIGHT; y >= 0; y -= BRICK_HEIGHT + BRICK_GAP) {
      processRow(y)
    }
  }

  return bricks // 直接作为完整新列表返回，彻底替换
}



const drawShadowForBrick = (
  ctx: CanvasRenderingContext2D,
  brick: BrickInfo,
  direction: 'up' | 'down'
) => {
  const { x, y, isRightSide, relativeDist } = brick

  const scrollOffset = calculateOffset(scrollYRatio?.value ?? 0)
  const depth = brick.depth

  const rightShadowColor = `rgba(0,0,0,${horizontalShadowAlpha(relativeDist)})`
  const leftShadowColor = rightShadowColor
  const bottomShadowColor = `rgba(0,0,0,${bottomShadowAlpha(relativeDist)})`



  if (direction === 'up') {

    // Top bricks shadow
    const downBaseY1 = y - depth * scrollOffset
    const downBaseY2 = y + BRICK_HEIGHT - depth * scrollOffset
    const downBaseY3 = (y + BRICK_HEIGHT)

    if (isRightSide) {
      ctx.fillStyle = rightShadowColor
      ctx.beginPath()
      ctx.moveTo(x + BRICK_WIDTH, y)
      ctx.lineTo(x + BRICK_WIDTH + depth, downBaseY1) // Change here
      ctx.lineTo(x + BRICK_WIDTH + depth, downBaseY2) // Change here
      ctx.lineTo(x + BRICK_WIDTH, downBaseY3)
      ctx.closePath()
      ctx.fill()
    } else {
      ctx.fillStyle = leftShadowColor
      ctx.beginPath()
      ctx.moveTo(x, y)
      ctx.lineTo(x - depth, downBaseY1) // Change here
      ctx.lineTo(x - depth, downBaseY2) // Change here
      ctx.lineTo(x, downBaseY3)
      ctx.closePath()
      ctx.fill()
    }
    // y + BRICK_HEIGHT + depth
    const horiShadowY_Out = scrollOffset > 0 ? y - depth * scrollOffset : y - depth * scrollOffset + BRICK_HEIGHT
    const horiShadowY_In = scrollOffset > 0 ? y : y + BRICK_HEIGHT

    ctx.fillStyle = bottomShadowColor
    ctx.beginPath()
    ctx.moveTo(x, horiShadowY_In)
    ctx.lineTo(x + (isRightSide ? depth : -depth), horiShadowY_Out)
    ctx.lineTo(x + BRICK_WIDTH + (isRightSide ? depth : -depth), horiShadowY_Out)
    ctx.lineTo(x + BRICK_WIDTH, horiShadowY_In)
    ctx.closePath()
    ctx.fill()
  } else {

    // Bottom bricks shadow

    const upBaseY1 = y + BRICK_HEIGHT
    const upBaseY2 = y + BRICK_HEIGHT + depth * -scrollOffset
    const upBaseY3 = y + depth * -scrollOffset

    if (isRightSide) {
      ctx.fillStyle = rightShadowColor
      ctx.beginPath()
      ctx.moveTo(x + BRICK_WIDTH, upBaseY1)
      ctx.lineTo(x + BRICK_WIDTH + depth, upBaseY2) // Change here
      ctx.lineTo(x + BRICK_WIDTH + depth, upBaseY3) // Change here
      ctx.lineTo(x + BRICK_WIDTH, y)
      ctx.closePath()
      ctx.fill()
    } else {
      ctx.fillStyle = leftShadowColor
      ctx.beginPath()
      ctx.moveTo(x, upBaseY1)
      ctx.lineTo(x - depth, upBaseY2) // Change here
      ctx.lineTo(x - depth, upBaseY3) // Change here
      ctx.lineTo(x, y)
      ctx.closePath()
      ctx.fill()
    }
    // y - depth
    const horiShadowY_Out = scrollOffset > 0 ? y + depth * -scrollOffset : y + depth * -scrollOffset + BRICK_HEIGHT
    const horiShadowY_In = scrollOffset > 0 ? y : y + BRICK_HEIGHT

    ctx.fillStyle = bottomShadowColor
    ctx.beginPath()
    ctx.moveTo(x, horiShadowY_In)
    ctx.lineTo(x + (isRightSide ? depth : -depth), horiShadowY_Out)
    ctx.lineTo(x + BRICK_WIDTH + (isRightSide ? depth : -depth), horiShadowY_Out)
    ctx.lineTo(x + BRICK_WIDTH, horiShadowY_In)
    ctx.closePath()
    ctx.fill()
  }
}

const drawShadowsOnly = () => {
  if (upperCtx) {
    // upperCtx.clearRect(0, 0, upperCanvas.width, upperCanvas.height)
    upperBricks.value.forEach(b => drawShadowForBrick(upperCtx!, b, 'up'))
  }
  if (lowerCtx) {
    // lowerCtx.clearRect(0, 0, lowerCanvas.width, lowerCanvas.height)
    lowerBricks.value.forEach(b => drawShadowForBrick(lowerCtx!, b, 'down'))
  }
}

const drawBothWalls = () => {
  upperBricks.value = drawWall(upperCanvas, upperCtx, 'up')
  lowerBricks.value = drawWall(lowerCanvas, lowerCtx, 'down')
  drawShadowsOnly()
}

const handleResize = () => {
  drawBothWalls()
}

onMounted(() => {
  upperCanvas = document.getElementById('upperWallCanvas') as HTMLCanvasElement
  lowerCanvas = document.getElementById('lowerWallCanvas') as HTMLCanvasElement
  upperCtx = upperCanvas.getContext('2d')
  lowerCtx = lowerCanvas.getContext('2d')

  drawBothWalls()
  window.addEventListener('resize', handleResize)

  // 👇 监听滚动重新绘制阴影
  watch(scrollYRatio, () => {
    drawBothWalls()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>








<style scoped>
.portfolio-section {
  position: relative;
  width: 100%;
  height: 100vh;
  background-color: #ffffff;
  overflow: hidden;
}

.upper-wall,
.lower-wall {
  position: absolute;
  width: 100%;
  height: 20%;
  left: 0;
}

.upper-wall {
  top: 0;
}

.lower-wall {
  bottom: 0;
}
</style>
