<template>
  <article class="post-card">
    <!-- 缩略图区域 -->
    <div class="post-thumbnail">
      <img :src="post.thumbnail" alt="文章缩略图">
    </div>
    
    <!-- 内容区域 -->
    <div class="post-content">
      <h3 class="post-title">
        {{ post.title }}
      </h3>
      
      <!-- 文章信息 -->
      <div class="post-meta">
        <span class="post-date">{{ post.date }}</span>
        <span class="post-author">{{ post.author }}</span>
        <span class="post-tag">{{ post.tag }}</span>
      </div>
      
      <!-- 摘要 -->
      <p class="post-excerpt">
        {{ post.excerpt }}
      </p>
      
      <!-- 阅读全文按钮 -->
      <router-link 
        :to="`/post/${post.id}`" 
        class="read-more"
      >
        阅读全文 →
      </router-link>
    </div>
  </article>
</template>

<script>
export default {
  name: 'PostCard',
  props: {
    post: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.post-card {
  display: flex;
  margin-bottom: 2rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.post-thumbnail {
  flex: 0 0 300px;
  overflow: hidden;
}

.post-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.post-card:hover .post-thumbnail img {
  transform: scale(1.05);
}

.post-content {
  flex: 1;
  padding: 1.5rem;
}

.post-title {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  color: #333;
}

.post-meta {
  display: flex;
  gap: 1rem;
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.post-meta span::before {
  content: "•";
  margin-right: 0.3rem;
}

.post-excerpt {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.2rem;
}

.read-more {
  display: inline-block;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.read-more:hover {
  text-decoration: underline;
}
</style>