---
title: 基于 PID、SAC 与模仿学习的自动驾驶小车
date: 2026-10-25
category: ai
status: shipped
tags: reinforcement-learning, sac, behavior-cloning, simulation
summary: 结合 PID 控制、Soft Actor-Critic 与行为克隆训练小车循迹避障；在 200 个固定仿真场景上任务分从 60.03 提升到 72.85，碰撞回合从 64 降到 9。
---

一个个人项目：让仿真中的小车学会循迹和避障，比较经典控制、强化学习和模仿学习的组合。

## 做了什么

- 围绕循迹与避障任务，结合 PID 控制、SAC 与行为克隆开展训练
- 使用分阶段示范与持续模仿约束，完成 **100 万步**环境交互
- 对照有 / 无模仿学习与纯 PID 方案，分析不同场景的任务分、碰撞和越界表现

## 结果

在 200 场景的固定仿真回归集（单训练种子）上：

| 指标 | 纯 PID | 本方案 |
| --- | --- | --- |
| 任务分 | 60.03 | **72.85**（+12.82） |
| 碰撞回合 | 64 | **9** |

失败案例主要来自遮挡导致的观测局限与绕障失败。

## 技术栈

强化学习 · Soft Actor-Critic · 行为克隆 · 仿真评测

方法和分析写在 [Reinforcement Learning](/log/reinforcement-learning) 这篇日志里。
