<template>
  <div class="rightpart">
    <HeroSection />
    <AboutSection />
    <PortfolioSection />
    <SkillsSection />
    <NewsSection />
    <PartnersSection />
    <ContactFormSection />
    <Footer />
  </div>
</template>

<script setup lang="ts">
import HeroSection from '@/components/sections/HeroSection.vue'
import AboutSection from '@/components/sections/AboutSection.vue'
import PortfolioSection from '@/components/sections/PortfolioSection.vue'
import SkillsSection from '@/components/sections/SkillsSection.vue'
import NewsSection from '@/components/sections/NewsSection.vue'
import PartnersSection from '@/components/sections/PartnersSection.vue'
import ContactFormSection from '@/components/sections/ContactFormSection.vue'
import Footer from '@/components/layout/Footer.vue'
</script>

<style scoped>
.rightpart {
  flex: 1;
  background-color: #fff;
}
</style>