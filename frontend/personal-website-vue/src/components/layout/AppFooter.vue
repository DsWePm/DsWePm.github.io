<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p>© {{ currentYear }} 我的个人博客 | 分享技术，记录生活</p>
      <div class="social-links">
        <a href="#">GitHub</a>
        <a href="#">Twitter</a>
        <a href="#">Bilibili</a>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    // 自动获取当前年份
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.app-footer {
  background-color: #343a40;
  color: #fff;
  padding: 2rem 0;
  margin-top: auto; /* 确保页脚在底部 */
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.social-links a {
  color: #ddd;
  margin-left: 15px;
  text-decoration: none;
}

.social-links a:hover {
  color: #fff;
  text-decoration: underline;
}
</style>