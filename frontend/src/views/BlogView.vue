<template>
  <DefaultLayout>
    <div class="blog-view">
      <h1 class="page-title">技术博客</h1>
      
      <!-- 搜索和分类过滤 -->
      <div class="blog-controls">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索文章..."
          class="search-input"
        />
      </div>
      
      <!-- 文章列表容器 -->
      <div class="post-list">
        <!-- 循环渲染文章卡片 -->
        <PostCard 
          v-for="post in filteredPosts"
          :key="post.id"
          :post="post"
        />
      </div>
      
      <!-- 暂无内容提示 -->
      <div v-if="filteredPosts.length === 0" class="empty-tips">
        没有找到相关文章
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import PostCard from '@/components/blog/PostCard.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

export default {
  name: 'BlogView',
  components: {
    PostCard,
    DefaultLayout
  },
  data() {
    return {
      // 模拟数据（后期替换为API获取）
      posts: [
        {
          id: 1,
          title: 'Vue3实战入门指南',
          date: '2023-10-15',
          author: '小明',
          tag: '前端',
          excerpt: 'Vue3的组合式API彻底改变了开发方式，本文将带你从零开始构建一个真实项目...',
          thumbnail: 'https://placehold.co/600x400'
        },
        {
          id: 2,
          title: 'Go语言高效并发模型',
          date: '2023-10-10',
          author: '小王',
          tag: '后端',
          excerpt: '深入解析Go语言的goroutine和channel机制，以及如何在实际项目中应用这些特性...',
          thumbnail: 'https://placehold.co/600x400'
        }
      ],
      searchQuery: '' // 搜索关键词
    }
  },
  computed: {
    // 计算过滤后的文章列表
    filteredPosts() {
      if (!this.searchQuery) return this.posts;
      
      const query = this.searchQuery.toLowerCase();
      return this.posts.filter(post => 
        post.title.toLowerCase().includes(query) || 
        post.excerpt.toLowerCase().includes(query)
      );
    }
  }
}
</script>

<style scoped>
.page-title {
  margin-top: 0;
  font-size: 2rem;
  color: #333;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.blog-controls {
  margin: 1.5rem 0;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.post-list {
  display: grid;
  gap: 2rem;
}

.empty-tips {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #6c757d;
}
</style>