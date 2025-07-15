<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <!-- Footer Logo -->
      <div class="footer-logo">
        <img src="~@/assets/logo/Logo.png" alt="Footer Logo" />
      </div>
      <!-- Social Links -->
      <div class="footer-social">
        <ul class="social-list">
          <li><a href="#"><i class="xcon-facebook"></i></a></li>
          <li><a href="#"><i class="xcon-twitter"></i></a></li>
          <li><a href="#"><i class="xcon-linkedin"></i></a></li>
          <li><a href="#"><i class="xcon-instagram"></i></a></li>
          <li><a href="#"><i class="xcon-behance"></i></a></li>
        </ul>
      </div>
    </div>
  </footer>
</template>

<script lang="ts" setup>
// No props or emits needed for this static footer
</script>

<style scoped>
.site-footer {
  background-color: #1f2937;
  color: #ffffff;
  padding: 2rem 0;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Footer Logo */
.footer-logo img {
  height: 36px;
}

/* Social icons */
.social-list {
  display: flex;
  gap: 1rem;
  list-style: none;
}

.social-list a {
  font-size: 1.25rem;
  color: #ffffff;
  transition: color 0.2s;
}
.social-list a:hover {
  color: #3b82f6;
}
</style>
