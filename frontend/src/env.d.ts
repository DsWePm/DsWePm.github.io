/// <reference types="vite/client" />

// 声明所有 .vue 文件为 Vue 组件模块
declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
