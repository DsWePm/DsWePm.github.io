---
title: "LLM & Transformers: writing a GPT-2 from scratch"
date: 2026-10-20
kind: skill
category: ai
dossier: FILE-01
tags: pytorch, transformer, gpt-2, thucnews
summary: The long version of skill file FILE-01. A GPT-2-style autoregressive language model written in PyTorch without any ready-made model library, trained to generate Chinese news on THUCNews.
---

The most direct way to understand a model is to write it from scratch. This file covers what I have done with Transformers and language models: a GPT-2-style autoregressive model, written from tensor operations up to generating Chinese news.

## The model

The model is written by hand, without calling an existing Transformer implementation:

- **Causal multi-head attention**: each position only sees the tokens before it, through a lower-triangular mask
- **Positional embeddings**: learned position vectors added to the token embeddings
- **Pre-LN residual blocks**: LayerNorm before attention and the feed-forward layer, for more stable training
- **Tied input and output weights**: the token embedding matrix and the output projection share one set of parameters

```python
# illustration: the causal mask, position i only attends to 0..i
mask = torch.tril(torch.ones(T, T, device=x.device)).bool()
att = (q @ k.transpose(-2, -1)) / math.sqrt(head_dim)
att = att.masked_fill(~mask, float('-inf')).softmax(dim=-1)
```

## The data

The corpus is THUCNews, a collection of Chinese news. I built a character-level vocabulary, cut the text into fixed-length training sequences, and implemented the dataset split, a preprocessing cache and batched loading, connecting the whole pipeline from data preparation through training to generation.

## Training and generation

- AdamW as the optimiser, cross-entropy as the loss
- Checkpoints are saved, and an interrupted run resumes from the latest one
- Generation supports temperature sampling and greedy decoding, used to generate Chinese news text

> After writing it once, the attention mask, where the residual goes and the tied weights stop being a sentence in a paper; they are the difference between training that converges and training that doesn't.

The matching project is [GPT-2 Chinese news generation](/projects/gpt2-chinese-news).
