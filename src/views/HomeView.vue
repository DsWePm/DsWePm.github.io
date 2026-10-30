<script setup lang="ts">
import { ref } from 'vue'
import LoadingScreen from '../components/LoadingScreen.vue'
import HeroCanyon from '../components/HeroCanyon.vue'
import AsciiField from '../components/AsciiField.vue'
import SectionFrame from '../components/SectionFrame.vue'
import DossierStack from '../components/DossierStack.vue'
import ProjectGrid from '../components/ProjectGrid.vue'
import PostIndex from '../components/PostIndex.vue'
import AboutPanel from '../components/AboutPanel.vue'
import TimelineList from '../components/TimelineList.vue'
import ContactPanel from '../components/ContactPanel.vue'
import SiteFooter from '../components/SiteFooter.vue'

defineOptions({ name: 'HomeView' })
const progress = ref(0)
const ready = ref(false)
</script>

<template>
  <LoadingScreen :progress="progress" :done="ready" />
  <HeroCanyon @progress="progress = $event" @ready="ready = true" />
  <main class="content theme-light" data-page="home">
    <AsciiField />
    <!-- the landing holds: the archive stays centred on screen for half a screen of scrolling -->
    <div class="dwell">
      <div class="pin"><SectionFrame id="archive" index="01" title="ARCHIVE" subtitle="技能档案"><DossierStack /></SectionFrame></div>
      <div class="slack" aria-hidden="true" />
    </div>
    <SectionFrame id="log" index="02" title="LOG" subtitle="文章 / 笔记"><PostIndex /></SectionFrame>
    <SectionFrame id="projects" index="03" title="PROJECTS" subtitle="项目"><ProjectGrid /></SectionFrame>
    <SectionFrame id="about" index="04" title="SUBJECT" subtitle="关于我 / 研究方向"><AboutPanel /></SectionFrame>
    <SectionFrame id="timeline" index="05" title="TIMELINE" subtitle="论文 / 经历"><TimelineList /></SectionFrame>
    <SectionFrame id="contact" index="06" title="CHANNEL" subtitle="联系方式"><ContactPanel /></SectionFrame>
    <SiteFooter />
  </main>
</template>

<style scoped>
/* sits under the hero's last screen and shows through the floor of the shaft at impact */
.content { position: relative; z-index: 1; background: var(--paper); }
.dwell { position: relative; }
.pin { position: sticky; top: 0; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; padding-bottom: 40px; }
.pin > :deep(.frame) { width: 100%; padding-top: 64px; }
.slack { height: 50vh; }
/* phones: the drawer becomes a tall list, so no pinning */
@media (max-width: 760px) {
  .pin { position: static; min-height: 0; display: block; padding-bottom: 0; }
  .pin > :deep(.frame) { padding-top: clamp(80px, 14vh, 160px); }
  .slack { display: none; }
}
</style>
