---
title: Homepage / 雨城裂缝
date: 2026-10-30
category: cg
status: active
demo: https://dswepm.github.io/Personal_Website/
tags: vue, three.js, blender, cycles
summary: 这个网站本身：Blender 程序化生成的九龙城寨峡谷，Cycles 预渲染的自由落体，Vue 3 + three.js 接回网页。
cover: hero/slab.jpg
---

一个个人主页，开场是一块带裂缝的白色楼板，往下滚动就掉进裂缝下面的楼宇峡谷，落地后切到档案页。

![首页静帧：裂缝和下面的峡谷](hero/slab.jpg)

## 组成

- **Blender 脚本**：`build_city.py` 生成整座城，`render_hero.py` 渲染静帧、254 帧下落和雨水循环
- **网页**：Vite + Vue 3 + TypeScript，three.js 负责首页的视差、涟漪和帧序列
- **内容**：日志和项目都是 Markdown 文件，详情页共用一套模板

## 重新生成资产

```bash
npm run build:assets
```

整套渲染在 RTX 2080 上大约 1.5 小时。

制作过程写在 [坠入峡谷](/log/falling-into-the-canyon) 这篇日志里。
