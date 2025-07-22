<template>
  <transition name="fade">
    <div v-if="show" class="preloader" @click="createRipple">
      <div class="background">
        <!-- 可选背景视频、GIF 或图片 -->
         <video autoplay muted loop>
          <source src="@/assets/video/snowyforest-showcase1-f.mp4" type="video/mp4">
          Your browser does not support the video tag.
        </video>
      </div>
      <div class="typing-wrap">
        <h1 class="typing">{{ displayText }}<span class="cursor">|</span></h1>
        <p class="hint">Click anywhere to get started</p>
      </div>
      <span
        v-for="(ripple, i) in ripples"
        :key="i"
        class="ripple"
        :style="{ top: ripple.y + 'px', left: ripple.x + 'px' }"
      />
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
const show = ref(true)
const displayText = ref('')
const ripples = ref<{ x: number; y: number }[]>([])

const initialText = 'Get Start'

// 把初始文本也加入到列表里，方便随机排除上次显示
const allTexts = [
  initialText,
  '生活就是一场闹剧',
  '珍惜当下',
  'Why won\'t you click?',
  'Come on Let\'s go!',
  'What are you waiting for?',
  'Just right!'
]

let index = 0
let typingTimeout: number | undefined
let waitingTimeout: number | undefined
let userClicked = false
let lastText = '' // 记录上次显示的文本，避免连续重复

function typeText(text: string, callback?: () => void) {
  if (index < text.length) {
    displayText.value += text[index]
    index++
    typingTimeout = window.setTimeout(() => typeText(text, callback), 120)
  } else {
    callback?.()
  }
}

function deleteText(callback?: () => void) {
  if (displayText.value.length > 0) {
    displayText.value = displayText.value.slice(0, -1)
    typingTimeout = window.setTimeout(() => deleteText(callback), 80)
  } else {
    callback?.()
  }
}

// 从 allTexts 中随机选一个，排除上次显示的文本
function getRandomTextExcludeLast(): string {
  const candidates = allTexts.filter(t => t !== lastText)
  const choice = candidates[Math.floor(Math.random() * candidates.length)]
  lastText = choice
  return choice
}

function startCycle() {
  index = 0
  waitingTimeout = window.setTimeout(() => {
    if (userClicked) return
    deleteText(() => {
      // 删除完成后显示随机新文本
      const nextText = getRandomTextExcludeLast()
      index = 0
      typeText(nextText, () => {
        waitingTimeout = window.setTimeout(() => {
          if (userClicked) return
          deleteText(() => {
            index = 0
            // 再随机显示另一个文本
            const nextNextText = getRandomTextExcludeLast()
            typeText(nextNextText, () => {
              // 继续循环
              waitingTimeout = window.setTimeout(() => {
                if (!userClicked) {
                  deleteText(() => {
                    index = 0
                    const nextCycleText = getRandomTextExcludeLast()
                    typeText(nextCycleText, () => {
                      startCycle()
                    })
                  })
                }
              }, 5000)
            })
          })
        }, 5000)
      })
    })
  }, 5000)
}

function createRipple(event: MouseEvent) {
  if (userClicked) return

  userClicked = true

  const x = event.clientX
  const y = event.clientY
  ripples.value.push({ x, y })

  clearTimeout(typingTimeout)
  clearTimeout(waitingTimeout)

  setTimeout(() => {
    ripples.value.shift()
    show.value = false
    uiStore.finishPreloading()
  }, 600)
}

onMounted(() => {
  lastText = initialText
  typeText(initialText, () => {
    startCycle()
  })

onUnmounted(() => {
  clearTimeout(typingTimeout)
  clearTimeout(waitingTimeout)
})

})
</script>

<style scoped>
.preloader {
  position: fixed;
  z-index: 9999;
  inset: 0;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
  cursor: pointer;
}

.background video,
.background img {
  position: absolute;
  top: 0;
  left: 0;
  object-fit: cover;
  width: 100%;
  height: 100%;
  z-index: 0;
  opacity: 0.4;
}

.typing-wrap {
  position: relative;
  z-index: 1;
  text-align: center;
}

.typing {
  font-size: 32px;
  color: #fff;
  font-family: 'Courier New', Courier, monospace;
}

.cursor {
  display: inline-block;
  width: 1ch;
  animation: blink 1s infinite;
  color: #2D5FFF;
}

.hint {
  margin-top: 12px;
  color: #aaa;
  font-size: 14px;
}

.ripple {
  position: absolute;
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  animation: ripple 0.6s ease-out forwards;
  pointer-events: none;
  z-index: 2;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

@keyframes ripple {
  to {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
