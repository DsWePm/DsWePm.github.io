<template>
  <nav class="topbar">
    <ul class="menu">
      <li
        v-for="item in menuItems"
        :key="item.href"
        class="menu-item"
      >
        <a :href="item.href" class="menu-link">
          {{ item.label }}
        </a>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { menuItems } from '@/components/layout/data/bar_menu/menuItems'
</script>

<style scoped>
.topbar {
  width: 100%;
  height: 60px;
  background-color: #1f1f1f;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.menu {
  list-style: none;
  display: flex;
  gap: 2rem;
  margin: 0;
  padding: 0;
}


.menu-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.menu-link:hover {
  color: #00bcd4;
}
</style>
