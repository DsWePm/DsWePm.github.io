---
title: GPT-2 reproduction and Chinese news generation
date: 2026-10-20
category: ai
status: shipped
tags: python, pytorch, transformer, thucnews
summary: A GPT-2-style autoregressive language model implemented from scratch in PyTorch, trained on THUCNews to generate Chinese news.
---

A personal project: reproduce the GPT-2 architecture from scratch without an existing model implementation, and run Chinese news through training and generation.

## What I did

- Wrote **causal multi-head attention**, positional embeddings, Pre-LN residual blocks and tied input/output weights by hand
- Built a character-level vocabulary and fixed-length training sequences from THUCNews, with a dataset split, preprocessing cache and batched loading
- Trained with AdamW and cross-entropy, with checkpoint saving and resumable training
- Supported **temperature sampling and greedy decoding** to generate Chinese news text

## Stack

Python · PyTorch · Transformer · THUCNews

The implementation details are in the [LLM & Transformers](/log/llm-transformers) log.
