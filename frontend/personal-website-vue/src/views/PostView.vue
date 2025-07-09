<template>
  <DefaultLayout>
    <div class="post-view" v-if="post">
      <!-- 文章头部信息 -->
      <header class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <span>{{ post.date }}</span>
          <span>作者: {{ post.author }}</span>
          <span>分类: {{ post.tag }}</span>
        </div>
      </header>
      
      <!-- 封面图 -->
      <div class="post-cover">
        <img :src="post.cover" :alt="post.title">
      </div>
      
      <!-- 文章内容 - 先简单渲染文本 -->
      <article class="post-content">
        <p>{{ post.content }}</p>
      </article>
    </div>
    
    <!-- 加载状态 -->
    <div v-else class="loading-container">
      <p>加载中...</p>
    </div>
  </DefaultLayout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'

export default {
  name: 'PostView',
  components: {
    DefaultLayout
  },
  props: {
    // 接收路由传递的id参数
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      post: null // 初始化文章数据
    }
  },
  watch: {
    // 监听id变化
    id: {
      immediate: true,
      handler(newId) {
        this.fetchPost(newId)
      }
    }
  },
  methods: {
    // 模拟获取文章详情
    fetchPost(id) {
      // 真实项目这里会调用API
      console.log(`正在获取文章: ${id}`)
      
      // 模拟网络延迟
      setTimeout(() => {
        this.post = {
          id,
          title: `文章 ${id} 的标题`,
          date: '2023-10-20',
          author: '博主',
          tag: '技术',
          cover: 'https://placehold.co/1000x500',
          content: `这里是文章 ${id} 的详细内容...待后端开发完成后这里将渲染完整的HTML内容，包括内嵌视频等富文本元素。`
        }
      }, 500)
    }
  }
}
</script>

<style scoped>
.post-header {
  margin-bottom: 2rem;
}

.post-title {
  font-size: 2.5rem;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.post-meta {
  color: #6c757d;
  font-size: 1.1rem;
}

.post-meta span {
  margin-right: 1.2rem;
}

.post-cover {
  margin-bottom: 2rem;
}

.post-cover img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.post-content {
  line-height: 1.8;
  font-size: 1.1rem;
}

.post-content p {
  margin-bottom: 1.5rem;
}

.loading-container {
  text-align: center;
  padding: 3rem;
}
</style>