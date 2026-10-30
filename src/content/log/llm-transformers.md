---
title: LLM & Transformers：从零写一个 GPT-2
date: 2026-10-20
kind: skill
category: ai
dossier: FILE-01
tags: pytorch, transformer, gpt-2, thucnews
summary: 技能档案 FILE-01 的长版本：不调用现成的模型库，用 PyTorch 手写一个 GPT-2 风格的自回归语言模型，并在 THUCNews 上完成中文新闻生成。
---

理解一个模型最直接的办法是把它从零写一遍。这份档案记录的是我在 Transformer 与语言模型上做过的事：一个 GPT-2 风格的自回归模型，从张量运算写到能生成中文新闻。

## 模型

模型部分全部手写，没有调用现成的 Transformer 实现：

- **因果多头注意力**：每个位置只能看到它之前的 token，用下三角掩码实现
- **位置嵌入**：可学习的位置向量，与 token 嵌入相加
- **Pre-LN 残差块**：LayerNorm 放在注意力和前馈层之前，训练更稳定
- **输入输出权重共享**：token 嵌入矩阵与输出投影共用一份参数

```python
# 示意：因果掩码，第 i 个位置只能注意到 0..i
mask = torch.tril(torch.ones(T, T, device=x.device)).bool()
att = (q @ k.transpose(-2, -1)) / math.sqrt(head_dim)
att = att.masked_fill(~mask, float('-inf')).softmax(dim=-1)
```

## 数据

语料是 THUCNews 中文新闻。我构建了字符级词表，把文本切成定长的训练序列，并完成数据集划分、预处理缓存和批量加载，打通了从数据准备、模型训练到生成推理的整条流程。

## 训练与生成

- 优化器用 AdamW，损失是交叉熵
- 支持 Checkpoint 保存与断点续训，训练中断后可以从最近的状态继续
- 生成时支持温度采样与贪心解码，完成了中文新闻文本的生成实践

> 写一遍之后，注意力掩码、残差的位置、权重共享这些细节就不再是论文里的一句话，而是训练能不能收敛的区别。

对应的项目见 [GPT-2 中文新闻生成](/projects/gpt2-chinese-news)。
