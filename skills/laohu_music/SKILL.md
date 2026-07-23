---
name: laohu-music
description: Use when a user starts, resumes, routes, pauses, or asks for the next decision in a Laohu Music V3 work.
---

# 老胡音乐导演

## 核心职责

本Skill是薄导演。它恢复目录状态、识别入口和目标、决定下一项高价值用户决策，并调用一个专业Skill。它不直接承载完整作词、声音或学习知识，也不组织多智能体评审流水线。

## 触发

使用于：

- 创建新作品。
- 继续、暂停或恢复作品。
- 用户输入灵感、句子、歌词、纯音乐要求、声音要求或音频反馈，需要判断从哪里进入。
- 当前阶段完成，需要生成下一合法动作。
- 用户要求快速、导演共创或工作室实验模式。

不使用于：已经明确处于歌词、声音或学习模式且只需执行当前专业动作；直接使用对应Skill。

## 每次调用的固定恢复顺序

1. 读取项目 `AGENTS.md` 与 `project.yaml`。
2. 解析用户指定的 `work_id`；没有指定时使用 `current_work_id`。
3. 已有作品时读取 `state.yaml`、`work.md` 和必要的最新事件。
4. 检查状态、锁定项、开放决策、活动范围和下一动作是否一致。
5. 只加载当前下一步需要的一个Skill和模式。
6. 返回当前作品状态、这次需要决定或执行的内容以及下一步。

禁止先扫描全部记忆、全部作品和全部知识再凭印象推进。

## 新建作品

创建 `works/<work_id>/`，只建立：

```text
state.yaml
work.md
events.jsonl
audio/
```

`work_id` 使用稳定ASCII标识，展示名写在状态和正文中。初始状态：

```yaml
schema_version: 1
work_id: song_YYYYMMDD_slug
owner_id: local_default
title: null
work_type: vocal_song
mode: director_co_creation
stage: briefing
active_scope:
  allowed_change: whole_work
  section_id: null
  line_id: null
  fragment_id: null
  field: null
locked:
  user_facts: []
  unknown_facts: []
  proposition_id: null
  core_hook_lines: []
  form_id: null
  lyrics_locked: false
  sound_direction_id: null
open_decisions: []
artifacts:
  work: work.md
  events: events.jsonl
  audio_dir: audio
loaded_memory_ids: []
sound_iteration:
  current_prompt_revision_id: null
  accepted_prompt_revision_id: null
  feedback_cycle_count: 0
  pending_audio_run_ids: []
  latest_feedback_event_id: null
  awaiting: none
next_action:
  skill: laohu_music
  mode: briefing
  reason: 提取用户输入并判断最短入口
updated_at: <ISO-8601>
```

新作品必须明确 `work_type`。用户明确不要歌词或要求纯音乐时写 `instrumental`；其余默认 `vocal_song`。旧状态缺少该字段时只为兼容解释为 `vocal_song`，并在下一次合法写回时补齐。是否纯音乐不清楚且会改变交付时，只问这一项。

`work.md`保存用户原始要求、确认事实、创作命题、核心句、曲式、当前歌词、用户提供或系统炼制的音乐片段、声音方向和最终提示词包的当前权威版本。未发生阶段不创建空洞长表。

创建后更新 `project.yaml.current_work_id`，追加 `work_created` 事件。

## 入口判断

| 输入成熟度 | 默认入口 | 判断重点 |
|---|---|---|
| 纯音乐用途、场景或声音灵感 | `sound_choice` | 用途、身体/情绪弧和主题动机需要多明确 |
| 灵感、题材、人物、关系 | `briefing` | 哪些事实会改变人物和立场 |
| 已有明确命题 | `proposition_choice`或`hook_development` | 命题是否已有语言证据 |
| 一句可能的副歌 | `hook_development` | 用户是否锁定、是否具有核心句潜力 |
| 一句歌词且只炼句 | `line_revision` | 人物/说话动作、句子用途、必要上下文和允许改动 |
| 单独乐段且只炼乐段 | `section_revision` | 预计功能、人物、已知前后约束和局部完成边界 |
| 完整曲式和核心句 | `draft_generation` | 人物与语言世界是否足以扩写 |
| 完整歌词初稿 | `section_revision` | 是否需要先返回命题/核心句/曲式 |
| 完整作品内指定乐段 | `section_revision` | 完整歌词上下文是否可读 |
| 完整作品内指定句词 | `line_revision` | 乐段宏观是否已经成立 |
| 锁定歌词待谱曲 | `sound_choice` | 歌词是否明确只读 |
| 旋律、节奏、groove、riff、和声、动机、演唱动作或局部编曲 | `sound_choice` + `music_fragment` | 片段种类、上下文作用、锁定/开放维度以及只炼片段还是发展完整包 |
| 已有声音方向 | `sound_package_ready` | 方向是否完整且单一 |
| 外部音频或试听反馈 | `external_audio_review` | 真实结果与预期差异 |
| 对规则、偏好或系统的反馈 | `laohu_learning` | 当前修改与长期学习分开 |

用户自称成熟不自动等于通过。只做当前入口必要检查，不借入口审计重跑全部上游。

## 决策门

只有同时满足以下条件才询问用户：

```text
决定会明显改变作品身份或后续成本
AND
存在两个以上专业成立方案
AND
当前用户偏好证据不足或互相冲突
```

事实缺失会改变人物、关系、立场、歌手或交付范围时也询问。一次只问一个最高影响问题。

不询问：格式、文件位置、自然中文硬错误、歌词逐字一致和AI能够用证据确定的专业常规问题。

## 模式裁决

### 导演共创

默认。按状态提供决策包，用户锁定后继续。

### 快速完整稿

用户明确要求快速或一次性时启用。用户授权AI为本轮建立命题、核心句和曲式的工作假设，而不是逐项确认。仍保护事实、人物、自然中文和整体冷读，不启动候选池；只有缺失信息会改变人物、关系、立场、歌手或交付范围时才先问。

本轮工作假设写入 `work.md` 和事件，记录使用的个人偏好或通用默认，但不写进 `state.locked` 冒充用户确认。完整初稿交付后进入 `section_revision`；用户可以整体接受并继续、局部精修或返回命题/核心句/曲式。只有用户明确接受后，相应资产才获得锁定权威。

### 工作室实验

只在用户明确要求或同一根因两轮复发时启用。最多一个挑战方案与一次比较。质量压力、重要作品、顶尖要求和沉没成本都不能自动触发多智能体。

## 状态转换

| 当前阶段 | 合法下一阶段 |
|---|---|
| `briefing` | 人声歌曲进入`proposition_choice`；纯音乐进入`sound_choice` |
| `proposition_choice` | `hook_development`、`briefing` |
| `hook_development` | `form_choice`、`proposition_choice` |
| `form_choice` | `draft_generation`、`hook_development` |
| `draft_generation` | `section_revision`、`proposition_choice`、`hook_development` |
| `section_revision` | `section_revision`、`line_revision`、上游根因阶段 |
| `line_revision` | `line_revision`、`section_revision`、`lyrics_locked` |
| `lyrics_locked` | `sound_choice` |
| `sound_choice` | `sound_choice`（音乐片段局部炼制）、`sound_package_ready` |
| `sound_package_ready` | `external_audio_review`、`complete` |
| `external_audio_review` | `sound_package_ready`、通过 `reopen_lyrics` 返回最早歌词根因阶段、`complete` |

不得跳过用户尚未作出的开放决策。成熟输入可以从中间合法进入，不需要伪造此前事件。

音频循环中，用户不需要手工提供 ID。导演从当前状态识别正在测试的提示词版本，为新的外部结果分配 `audio_run_id`，并将它关联到 `current_prompt_revision_id`。只有多个待测版本同时存在、且无法从时间、平台或文件判断时，才向用户追问对应关系。

## 阶段到Skill模式映射

| 阶段 | Skill | 模式 |
|---|---|---|
| `briefing` | `laohu_music` | `briefing` |
| `proposition_choice` | `laohu_lyrics` | `proposition` |
| `hook_development` | `laohu_lyrics` | `hook_development` |
| `form_choice` | `laohu_lyrics` | `form_design` |
| `draft_generation` | `laohu_lyrics` | `draft_generation` |
| `section_revision` | `laohu_lyrics` | `section_revision` |
| `line_revision` | `laohu_lyrics` | `line_revision` |
| `lyrics_locked` | `laohu_sound` | `sound_direction` |
| `sound_choice` | `laohu_sound` | 默认`sound_direction`；活动对象为音乐片段时用`music_fragment` |
| `sound_package_ready` | `laohu_sound` | `sound_package` |
| `external_audio_review` | `laohu_sound` | `external_audio_revision` |

学习请求不改变作品阶段时调用 `laohu_learning` 对应模式；需要修改作品时先路由回拥有修改权的阶段。

## 一次合法动作的写回顺序

1. 先修改 `work.md` 当前权威内容。
2. 追加事件，包含事件类型、时间、阶段、活动范围、决策ID或正文hash引用。
3. 更新 `state.yaml` 的锁定项、开放决策、阶段和下一动作。
4. 若切换当前作品，更新 `project.yaml`。
5. 运行项目校验。

写回任一步失败时不得宣称完成；保持原阶段并说明缺口。

声音阶段还必须同步 `sound_iteration`：初始包或每轮修订都更新 `current_prompt_revision_id`；外部结果进入 `pending_audio_run_ids`；反馈纳入修订后清理本批待处理结果并递增 `feedback_cycle_count`。只有用户显式执行 `accept_sound_package` 才写入 `accepted_prompt_revision_id` 并结束循环；暂停不等于接受。

音频证据指向歌词问题时，先说明哪个可听问题为什么不能在提示词层解决，由用户确认 `reopen_lyrics`。操作将 `lyrics_locked` 设为 false，记录 `lyrics_reopened` 事件和被暂时失效的提示词版本，清空待反馈音频和接受版本，返回最早必要歌词阶段。修完重新锁定歌词后，才能生成新提示词版本。

## 调用专业Skill

```text
歌词 → laohu_lyrics，携带模式、state、锁定项、当前正文和相关记忆ID
声音 → laohu_sound，携带work_type；人声歌曲再携带锁定歌词与核心句，纯音乐携带用途、主题动机与形式；音乐片段携带种类、表达、上下文作用、权威、锁定/开放维度和目标；两条分支都携带声音方向和外部反馈
学习 → laohu_learning，携带原反馈、当前前后版本、决策事件和授权范围
```

不要把三个Skill全文同时装入上下文。

## 用户可见交付

自然说明：

- 当前处于什么阶段。
- 已锁定什么。
- 当前为什么需要一个决定，或已经执行了什么。
- 选项、推荐和代价。
- 用户可以怎样快速回答。

不要输出状态机字段堆、内部trace或系统自我表扬。

## 红线

- 不因“最高质量”自动扩张为多智能体。
- 不要求用户复述目录中已经存在的状态。
- 不用工作标题冒充正式歌名。
- 不允许聊天记忆覆盖锁定文件。
- 不为流程完整强迫成熟输入重走上游。
- 不在导演层直接写完整歌词或提示词包。
- 不修改 `knowledge/` 或 `memory/` 来完成单首作品。

## 完成检查

- 当前作品和阶段唯一明确。
- 只激活一个专业Skill和模式。
- 用户只面对一个最高影响决策。
- 写回顺序完整。
- 下一动作合法且可由新智能体恢复。
