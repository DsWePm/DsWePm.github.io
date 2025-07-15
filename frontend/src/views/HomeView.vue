<template>
  <div class="home-view">
    <!-- 页面组件组合 -->
    <Preloader />
    <MobileMenu />
    <Header />
    
    <main>
      <HeroSection />
      <AboutSection />
      <ServicesSection />
      <PortfolioSection />
      <SkillsSection />
      <NewsSection />
      <PartnersSection />
      <ContactForm />
    </main>
    
    <Footer />
    <BackToTopButton />
  </div>
</template>

<script lang="ts" setup>
// 导入组件
import Header from '@/components/layout/Header.vue'
import MobileMenu from '@/components/layout/MobileMenu.vue'
import Preloader from '@/components/layout/Preloader.vue'
import HeroSection from '@/components/sections/HeroSection.vue'
import AboutSection from '@/components/sections/AboutSection.vue'
import ServicesSection from '@/components/sections/ServicesSection.vue'
import PortfolioSection from '@/components/sections/PortfolioSection.vue'
import SkillsSection from '@/components/sections/SkillsSection.vue'
import NewsSection from '@/components/sections/NewsSection.vue'
import PartnersSection from '@/components/sections/PartnersSection.vue'
import ContactForm from '@/components/sections/ContactFormSection.vue'
import Footer from '@/components/layout/Footer.vue'
import BackToTopButton from '@/components/layout/BackToTopButton.vue'
</script>

<style scoped>
.home-view {
  position: relative;
}
</style>