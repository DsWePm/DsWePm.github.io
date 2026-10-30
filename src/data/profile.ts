// Everything a visitor reads lives here.

export interface Skill { name: string; level: number }
export interface Dossier {
  code: string
  title: string
  clearance: string
  summary: string
  skills: Skill[]
  tags: string[]
  art: string          // key into src/data/asciiArt.ts, shown when there is no video
  video?: string       // path under public/, e.g. 'video/dossier-ml.mp4' (muted loop)
}
// grouped by year on the page: `year` if given, else the last year written in `when` (2021–2025 -> 2025)
export interface TimelineEntry { when: string; title: string; where: string; detail: string; kind: 'paper' | 'work' | 'edu' | 'project' | 'award'; year?: number }

export const profile = {
  name: 'DsWePm',
  handle: 'dswepm',
  github: 'DsWePm',                         // GitHub login (also used by scripts/fetch-github.mjs)
  role: 'AI Developer / Autonomous Driving',
  location: 'Melbourne, AU',
  tagline: 'Signals from the bottom of the city.',
  email: '',                                // shown in CHANNEL when set
  // `icon` is a key in src/data/brandIcons.ts
  links: [
    { label: 'GitHub', href: 'https://github.com/DsWePm', icon: 'github' },
    { label: 'Bilibili', href: 'https://space.bilibili.com/31988330', icon: 'bilibili' },
  ] as { label: string; href: string; icon?: string }[],
  about: [
    '墨尔本大学信息技术硕士在读，方向是人工智能；本科在中国地质大学（北京）读地球信息科学与技术（大数据与数字地球）。',
    '关心的是模型怎么从零搭起来、怎么在仿真里学会控制：从手写一个 GPT-2，到用 PID、SAC 和模仿学习训练一辆会循迹避障的小车。业余时间也写渲染器、做程序化建模。',
  ],
  research: [
    'Transformer 与大语言模型的训练全流程',
    '强化学习与模仿学习在自动驾驶中的应用',
    'World Model 与 AI Agent',
  ],
  fields: [
    ['SUBJECT', 'DsWePm'],
    ['STATUS', 'MSc IT (AI) · in progress'],
    ['BASE', 'Melbourne, AU'],
    ['FOCUS', 'AI / Autonomous driving'],
  ] as [string, string][],
}

export const dossiers: Dossier[] = [
  {
    code: 'FILE-01', title: 'LLM & Transformers', clearance: 'L3', art: 'brain',
    summary: '从零实现 GPT-2 风格的自回归语言模型：因果多头注意力、Pre-LN 残差块、权重共享，以及训练、断点续训与文本生成的完整流程。',
    skills: [{ name: 'PyTorch', level: 0.8 }, { name: 'Transformer / GPT-2', level: 0.75 }, { name: 'Training pipelines', level: 0.7 }],
    tags: ['pytorch', 'transformer', 'llm'],
  },
  {
    code: 'FILE-02', title: 'Reinforcement Learning', clearance: 'L3', art: 'eye',
    summary: '用 PID、Soft Actor-Critic 与行为克隆训练自动驾驶小车循迹避障，在固定仿真回归集上评测与分析失败原因。',
    skills: [{ name: 'Soft Actor-Critic', level: 0.7 }, { name: 'Imitation learning', level: 0.65 }, { name: 'PID control', level: 0.7 }],
    tags: ['rl', 'sac', 'autonomous-driving'],
  },
  {
    code: 'FILE-03', title: 'Graphics & 3D', clearance: 'L2', art: 'tower', video: 'video/dossier-graphics.mp4',
    summary: 'Blender 程序化建模与 Cycles 渲染，three.js / GLSL 实时渲染，以及给 Minecraft Vulkan 后端写的光线追踪渲染器。',
    skills: [{ name: 'Blender / Python', level: 0.7 }, { name: 'GLSL', level: 0.6 }, { name: 'three.js', level: 0.65 }],
    tags: ['blender', 'webgl', 'ray-tracing'],
  },
  {
    code: 'FILE-04', title: 'Software Engineering', clearance: 'L2', art: 'circuit',
    summary: '用 Python 写模型模块、数据管线、训练循环与推理脚本；用 TypeScript / Vue 做前端，这个网站就是其中之一。',
    skills: [{ name: 'Python', level: 0.8 }, { name: 'TypeScript / Vue', level: 0.65 }, { name: 'Git / Linux', level: 0.7 }],
    tags: ['python', 'typescript', 'vue'],
  },
  {
    code: 'FILE-05', title: 'World Models & Agents', clearance: 'L1', art: 'paper',
    summary: '正在了解 World Model 与 AI Agent：模型如何预测环境、Agent 如何调用工具完成任务，以及常用机器学习算法。',
    skills: [{ name: 'World Models', level: 0.45 }, { name: 'AI Agents', level: 0.5 }, { name: 'Classic ML', level: 0.6 }],
    tags: ['world-model', 'agents'],
  },
]

export const timeline: TimelineEntry[] = [
  { when: '2026.02 – 2027.12', year: 2026, title: 'Master of Information Technology (AI)', where: 'University of Melbourne', detail: '信息技术硕士，人工智能方向，在读。', kind: 'edu' },
  { when: '2026', title: 'Homepage / 雨城裂缝', where: 'Personal project', detail: 'Blender 程序化城市、Cycles 预渲染的自由落体，Vue 3 + three.js 接回网页。', kind: 'project' },
  { when: '2026', title: 'Fluorite', where: 'Open source', detail: 'Minecraft 26.2 Vulkan 后端的光线追踪渲染器。', kind: 'project' },
  { when: '2020.09 – 2024.07', title: 'B.Sc. Geographic Information Science', where: 'China University of Geosciences (Beijing)', detail: '地球信息科学与技术（大数据与数字地球）。', kind: 'edu' },
  { when: '2023.10', title: '囹圄', where: 'Bilibili', detail: '3D 渲染练习短片，77 秒。', kind: 'project' },
  { when: '2021', title: '专业三等奖学金', where: 'China University of Geosciences (Beijing)', detail: '2021 年度专业三等奖学金。', kind: 'award' },
]
