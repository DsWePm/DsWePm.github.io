---
title: A self-driving car with PID, SAC and imitation learning
date: 2026-10-25
category: ai
status: shipped
tags: reinforcement-learning, sac, behavior-cloning, simulation
summary: PID control, Soft Actor-Critic and behaviour cloning trained a car to follow lanes and avoid obstacles; on 200 fixed simulation scenes the task score rose from 60.03 to 72.85 and collision episodes fell from 64 to 9.
---

A personal project: teach a simulated car to follow lanes and avoid obstacles, comparing combinations of classic control, reinforcement learning and imitation learning.

## What I did

- Trained the car on lane following and obstacle avoidance by combining PID control, SAC and behaviour cloning
- Used staged demonstrations with a continuous imitation constraint, for **1 million steps** of environment interaction
- Compared setups with and without imitation learning against PID only, analysing task score, collisions and out-of-bounds behaviour per scene

## Results

On a fixed regression set of 200 simulation scenes (one training seed):

| Metric | PID only | This method |
| --- | --- | --- |
| Task score | 60.03 | **72.85** (+12.82) |
| Collision episodes | 64 | **9** |

The remaining failures mostly come from limited observation due to occlusion, which makes the car fail to steer around obstacles.

## Stack

Reinforcement learning · Soft Actor-Critic · behaviour cloning · simulation evaluation

The method and analysis are in the [Reinforcement Learning](/log/reinforcement-learning) log.
