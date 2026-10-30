---
title: "Reinforcement Learning: teaching a car to follow lanes and avoid obstacles"
date: 2026-10-25
kind: skill
category: ai
dossier: FILE-02
tags: reinforcement-learning, sac, imitation-learning, pid
summary: The long version of skill file FILE-02. PID control, Soft Actor-Critic and behaviour cloning trained together on a self-driving car, evaluated on 200 fixed simulation scenes.
---

This file is about reinforcement learning and imitation learning applied to a control problem. The vehicle is a self-driving car in simulation, and the tasks are lane following and obstacle avoidance.

## Three methods together

- **PID**: classic control, the baseline, and also the source of demonstrations
- **Soft Actor-Critic (SAC)**: maximum-entropy reinforcement learning for a continuous action space
- **Behaviour cloning**: imitation learning from demonstrations, keeping the policy from drifting too far

Training used staged demonstrations with a continuous imitation constraint, for **1 million steps** of environment interaction in total.

## Evaluation

Evaluation runs on a fixed simulation regression set: 200 scenes, one training seed.

| Method | Task score | Collision episodes |
| --- | --- | --- |
| PID only | 60.03 | 64 |
| PID + SAC + imitation | **72.85** | **9** |

The task score rose by **12.82**, and collision episodes fell from 64 to 9.

## Analysis

I compared three setups: with imitation learning, without it, and PID only, looking at the task score, collisions and out-of-bounds behaviour scene by scene. Most failures came from limited observation caused by occlusion: the car can't see an obstacle that is hidden, so it fails to steer around it.

> A fixed regression set is more useful than a single score: every change is compared on the same scenes, so both gains and regressions can be traced to specific scenes.

The matching project is [A self-driving car with PID, SAC and imitation learning](/projects/sac-autonomous-car).
