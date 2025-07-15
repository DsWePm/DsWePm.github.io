<template>
  <header class="site-header">
    <div class="container header-inner">
      <!-- Logo -->
      <div class="header-logo">
        <router-link to="/">
          <img src="~@/assets/logo/Logo.png" alt="Logo" />
        </router-link>
      </div>

      <!-- Desktop Navigation -->
      <nav class="header-nav">
        <ul class="nav-list">
          <li><a href="#home" class="nav-link">Home</a></li>
          <li><a href="#about" class="nav-link">About</a></li>
          <li><a href="#portfolio" class="nav-link">Portfolio</a></li>
          <li><a href="#news" class="nav-link">News</a></li>
          <li><a href="#contact" class="nav-link">Contact</a></li>
        </ul>
      </nav>

      <!-- Mobile Menu Toggle -->
      <button class="mobile-menu-toggle" @click="$emit('toggle-mobile-menu')">
        <span class="hamburger">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>
    </div>
  </header>
</template>

<script lang="ts" setup>
// This component emits 'toggle-mobile-menu' to let parent show/hide MobileMenu.vue
</script>

<style scoped>
.site-header {
  position: fixed;
  top: 0;
  width: 100%;
  background-color: #ffffff;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
}

/* Logo */
.header-logo img {
  height: 40px;
  display: block;
}

/* Desktop nav */
.header-nav {
  display: none;
}

.nav-list {
  display: flex;
  gap: 1.5rem;
  list-style: none;
}

.nav-link {
  text-decoration: none;
  font-weight: 500;
  color: #333;
  transition: color 0.2s;
}
.nav-link:hover {
  color: #007acc;
}

/* Mobile toggle */
.mobile-menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
}
.hamburger {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.hamburger span {
  width: 24px;
  height: 2px;
  background-color: #333;
}

/* Responsive */
@media (min-width: 768px) {
  .header-nav {
    display: block;
  }
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
