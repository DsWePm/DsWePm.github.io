---
title: GPT-2 架构复现与中文新闻生成
date: 2026-10-20
category: ai
status: shipped
tags: python, pytorch, transformer, thucnews
summary: 用 PyTorch 从零实现 GPT-2 风格的自回归语言模型，在 THUCNews 上训练并生成中文新闻。
---

一个个人项目：不依赖现成的模型实现，从零复现 GPT-2 的结构，并跑通中文新闻的训练和生成。

## 做了什么

- 手写**因果多头注意力**、位置嵌入、Pre-LN 残差块与输入输出权重共享
- 基于 THUCNews 构建字符级词表与定长训练序列，实现数据集划分、预处理缓存及批量加载
- 用 AdamW 与交叉熵训练，支持 Checkpoint 保存及断点续训
- 支持**温度采样与贪心解码**，完成中文新闻文本生成

## 技术栈

Python · PyTorch · Transformer · THUCNews

实现细节写在 [LLM & Transformers](/log/llm-transformers) 这篇日志里。
