# 老胡音乐 V4 逐 Skill 四层能力深化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不削弱老胡音乐 V4 现有长处的前提下，让九个 Skill 分别形成自己的四层能力链，并修复跨领域交接、质量监督和自进化对专业能力的稀释。

**Architecture:** 四层能力以单个 Skill 为基本单位，项目顶层只维护职责、状态、交接和回流。领域 Skill 用自己的专业语言完成从方向到成品的传导；横切 Skill 只负责找到领域负责人、保护作品不变量和验证能力链，不成为第二套专业创作系统。

**Tech Stack:** Markdown Skill/Reference 规则、JSON 行为场景、Python 标准库 JSON 校验、现有 `tools/check_style_prompt.py` 与 `tools/check_controlled_lyrics.py`。

---

## 实施边界与仓库说明

- 设计依据：`docs/superpowers/specs/2026-08-26-laohu-music-v4-four-layer-skill-deepening-design.md`。
- 目标目录没有独立 Git，上层 `/Users/a1/Documents/老胡` 工作区存在大量无关修改，且 V4 除设计文档外尚未被上层仓库追踪。
- 实施期间只修改本计划列出的 V4 文件，不初始化新仓库、不推送 GitHub、不把整个 V4 目录加入上层 Git。
- 每个任务完成后记录精确文件清单和验证结果；由于无法安全形成逐任务 Git 提交，最终只在用户明确要求时选择合适的本地版本化方式。
- 任何原有内容只有在被新位置完整承接、语义等价并通过旧强项回归后才允许删除。

## 文件职责图

| 文件 | 本轮唯一职责 |
| --- | --- |
| `AGENTS.md` | 确立“四层属于单 Skill、项目只管关系”的顶层边界 |
| `.agents/skills/laohu-song-director/SKILL.md` | 保护作品不变量、状态和领域化交接 |
| `.agents/skills/laohu-lyric-topic/SKILL.md` | 从种子与事实形成作品命题并差异化交接 |
| `.agents/skills/laohu-lyric-writing/SKILL.md` | 从关系命题形成可唱语言，完成材料与技法因果 |
| `.agents/skills/laohu-lyric-composing/SKILL.md` | 从作品总线形成主听觉命题、声音蓝图和生成包 |
| `.agents/references/laohu-lyric-composing/曲式结构与音乐叙事.md` | 曲式候选、信息顺序、声音条件和改判依据 |
| `.agents/references/laohu-lyric-composing/音乐风格路由与提示词生成.md` | 声音蓝图到 Style Prompt 的可追溯编译 |
| `.agents/references/laohu-lyric-composing/vocal-control.md` | 主唱动作到 Controlled Lyrics 的局部控制 |
| `.agents/skills/laohu-lyric-title/SKILL.md` | 从作品记忆形成听前成立、听后增义的名字 |
| `.agents/skills/laohu-lyric-cover/SKILL.md` | 从作品关系形成第一视觉并守住视觉开发边界 |
| `.agents/skills/laohu-quality-supervisor/SKILL.md` | 定位领域负责人和最早失误节点 |
| `.agents/skills/laohu-project-evolution/SKILL.md` | 把反馈编译成目标 Skill 的能力增量 |
| `.agents/references/laohu-project-evolution/单一技能四层深化与保真迁移.md` | 保存成熟 Skill 的四层审计、迁移和回归方法 |
| `.agents/skills/laohu-natural-dialogue/SKILL.md` | 把专业结论翻译成老胡能理解和决策的交流 |
| `tests/skill-capability-scenarios.json` | 保存不泄露唯一答案的行为回归场景 |

### Task 1: 建立行为回归契约

**Files:**
- Create: `tests/skill-capability-scenarios.json`

- [ ] **Step 1: 先确认行为场景尚不存在**

Run:

```bash
test ! -e tests/skill-capability-scenarios.json
```

Expected: exit code `0`。若文件已经存在，先完整读取并合并，不覆盖用户内容。

- [ ] **Step 2: 创建场景文件并固定字段**

使用以下顶层结构：

```json
{
  "version": 1,
  "verdict_policy": {
    "structure": "可由确定性检查裁决 PASS / FAIL",
    "route": "静态链接最多裁决 OBSERVE",
    "behavior": "同一执行者自检最高裁决 OBSERVE",
    "quality": "没有独立领域结果时保持 UNKNOWN"
  },
  "scenarios": []
}
```

每个场景使用以下字段，不增加预设成品：

```json
{
  "id": "music-v4-01",
  "target_skill": "laohu-lyric-topic",
  "task": "用户只提供故乡、想家、电影感三个效果词，要求直接写完整歌词",
  "protected_strength": "主动研究和给出有依据的探索路线，不把材料不足变成冷硬拒绝",
  "expected_decisions": [
    "区分题材、效果词和人物事实",
    "不虚构完整人生",
    "形成关系缺口、当前主探索路线和会改变作品身份的确认入口"
  ],
  "forbidden_shortcuts": [
    "直接生成完整歌词",
    "把车票、旧照片、方言等库存材料冒充人物事实"
  ],
  "layer_evidence": {
    "soul": "作品命题包含人物、对象、关系动作和代价",
    "structure": "探索路线能够进入后续选题确认",
    "craft": "材料只作为候选并标明来源与作用",
    "form": "对外结果清楚区分事实、推论和创作假设"
  }
}
```

- [ ] **Step 3: 写入十个设计场景**

场景 ID 与负责人固定为：

```text
music-v4-01  laohu-lyric-topic       宽题材不得直接编造完整人生
music-v4-02  laohu-lyric-writing     同一用意比较小物、公共意象与人物动作
music-v4-03  laohu-lyric-composing   主听觉命题统领六个声音部门
music-v4-04  laohu-lyric-composing   曲式候选必须改变信息和声音后果
music-v4-05  laohu-lyric-title       不同命名机制与全歌回插
music-v4-06  laohu-lyric-cover       看见、隐藏及歌名互补
music-v4-07  laohu-song-director     同一作品的领域化交接
music-v4-08  laohu-quality-supervisor 错误 Style Prompt 的最早责任定位
music-v4-09  laohu-project-evolution 封面缺人物设计时不把封面改成角色系统
music-v4-10  laohu-natural-dialogue  谱曲事实不能被文学比喻替换
```

每个场景必须填写 `protected_strength`、至少三项 `expected_decisions`、至少两项 `forbidden_shortcuts` 和四层 `layer_evidence`。

- [ ] **Step 4: 运行确定性结构检查**

Run:

```bash
python3 -m json.tool tests/skill-capability-scenarios.json >/dev/null
python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path('tests/skill-capability-scenarios.json').read_text())
assert data['version'] == 1
assert len(data['scenarios']) == 10
ids = [item['id'] for item in data['scenarios']]
assert len(ids) == len(set(ids))
required = {
    'id', 'target_skill', 'task', 'protected_strength',
    'expected_decisions', 'forbidden_shortcuts', 'layer_evidence'
}
for item in data['scenarios']:
    assert required <= item.keys()
    assert set(item['layer_evidence']) == {'soul', 'structure', 'craft', 'form'}
    assert len(item['expected_decisions']) >= 3
    assert len(item['forbidden_shortcuts']) >= 2
PY
```

Expected: 两条命令均 exit code `0`。

### Task 2: 校准顶层边界与总导演交接

**Files:**
- Modify: `AGENTS.md`
- Modify: `.agents/skills/laohu-song-director/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-07`

- [ ] **Step 1: 保存当前职责证据**

Run:

```bash
rg -n "四层|交接|状态|回流|歌名候选|曲式候选|声音假设" AGENTS.md .agents/skills/laohu-song-director/SKILL.md
```

Expected: 能定位当前四层总述、四层交接卡、阶段状态和越权风险位置。

- [ ] **Step 2: 在 `AGENTS.md` 增加单 Skill 四层边界**

在现有四层总原则之后合并以下判断，不新增第二套总纲：

```text
四层首先作用于单个 Skill。选题、写词、谱曲、歌名、封面、监督、沟通和进化必须分别把四层翻译成自己的领域判断、运行关系、材料技法和交付法度；项目顶层只管理职责、依赖、状态、交接和回流。给所有 Skill 复制同一份四层说明，不算能力建设。
```

同时写清：同一作品经过跨领域交接时保护作品总线、锁定事实、用户决定与失败边界；下游必须用自己的领域语言重新实现，不能沿用一张歌词化通用表。

- [ ] **Step 3: 重写总导演的交接核心**

保留现有状态锁和阶段门，把通用交接拆为：

```text
共同不变量：作品总线 / 锁定事实 / 用户决定 / 保护项 / 当前状态 / 未决假设 / 失败回流
领域交付：由当前负责人写出下一领域真正需要的专业输入
激活证据：下游说明这次交接改变或确认了哪个领域决定
```

为五次交接写明不同职务：

```text
选题 → 写词：关系动作、材料边界、段落认识运动、最少事实
写词 → 谱曲：锁定歌词、段落职务、重音、气口、重复变义、声音未知项
谱曲 → 歌名：作品总线、歌词记忆、听觉记忆、报幕与搜索条件
歌名 → 封面：命名承诺、可见关系、必须隐藏的答案、平台用途
任一领域 → 上游：失败证据、最早责任点、必须重判的作品不变量
```

- [ ] **Step 4: 删除或改写总导演越权表述**

把“由写词阶段形成歌名候选、曲式候选和声音假设”改为：总导演可以要求局部预验证，但歌名、曲式和声音方案分别由对应领域 Skill 生成与裁决；局部试验不得升级为锁定结果。

- [ ] **Step 5: 干跑领域化交接场景**

使用 `music-v4-07`，写一份内部干跑记录，不写入长期文件。确认：

```text
同一作品总线没有变化
五次交接使用不同领域语言
总导演没有替任何领域生成专业答案
下游能够指出交接改变的一个具体决定
```

Expected: `ROUTE=OBSERVE`、`BEHAVIOR=OBSERVE`；不得写成 `QUALITY=PASS`。

### Task 3: 保护并补强选题与写词

**Files:**
- Modify: `.agents/skills/laohu-lyric-topic/SKILL.md`
- Modify: `.agents/skills/laohu-lyric-writing/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-01`、`music-v4-02`

- [ ] **Step 1: 为两个 Skill 建立保护清单**

从原文件逐项确认并保留：

```text
选题：八条箴言、材料成熟度、命题硬骨、公共连接、对标迁移、作品总线
写词：六条箴言、关系母句、段落变义、材料抒情、留白、语义保护、声音卡、三项反向测试
```

Expected: 修改前后均可由 `rg` 定位，不允许因合并文字而丢失触发、动作、边界和失败分支。

- [ ] **Step 2: 明确选题的独门能力链**

在选题职责与生成顺序之间合并以下链条：

```text
种子与事实
→ 人物与关系位置
→ 不能同时保住的两样东西
→ 人物选择、代价与余波
→ 听众怎样重新理解同一件事
→ 作品总线与分领域交接
```

写清：十六份 Reference 只有在改变这条链中的一个决定时才算激活；不能用“已读取”替代能力生效。

- [ ] **Step 3: 修正选题向四个下游的交付差异**

写词只接关系动作和最少事实；谱曲只接声音需要实现的关系运动；歌名只接压缩对象与记忆；封面只接可见动作、异常关系和隐藏答案。删除任何把完整故事同时交给四个下游的暗示。

- [ ] **Step 4: 给写词技法增加因果四要素**

将现有修辞动作校准为统一判断：

```text
作用对象：它具体作用于哪句、哪项材料、哪次回归或哪个声音位置
目标效果：听众因此先听见、误听、补回或重新理解什么
使用条件：哪些人物、语体、段落和声音条件支持它
过量风险：重复、解释、修辞或留白何时会遮住人物和关系
```

不新建修辞名录，不把技法改成逐项必用。

- [ ] **Step 5: 增加同一用意下的材料候选比较**

在血肉层写清：至少比较私人小物、人物动作、公共材料或文化材料中的真正可行方向；比较相称、归属、承重、典型性、声音潜力和组合关系。末端再做替换损失测试，不能以稀有、具体或“专属于这个人”自动判胜。

- [ ] **Step 6: 运行两个行为干跑**

对 `music-v4-01` 和 `music-v4-02` 分别检查：

```text
原始失败是否被拦住
换成战争或亲情题材是否仍成立
真实钥匙确实承重时是否被错误淘汰
原有选题主动研究与写词留白能力是否保留
```

Expected: `BEHAVIOR=OBSERVE`；边界反例不得误杀真实承重的小物件。

### Task 4: 让谱曲形成完整声音能力链

**Files:**
- Modify: `.agents/skills/laohu-lyric-composing/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-03`、`music-v4-04`

- [ ] **Step 1: 保存现有谱曲强项**

确认以下内容在修改后仍存在并保持原义：谱曲箴言、准入、六个声音部门、曲式问答、结构账、词曲接口、风格路由、1000 字符门、Controlled Lyrics 原文保护、四轮试听和回填清单。

- [ ] **Step 2: 增加主听觉命题**

在谱曲准入之后写入：

```text
主听觉命题不是“伤感、电影感、国风”，而是听众最终必须重新听见哪项人物关系，以及哪一种声音关系负责完成这次改变。每次只允许一个主听觉命题统领全曲；其他声音标准成为辅助、硬门或待验证项。
```

内部字段固定为：

```text
听众起初怎样听
→ 哪项声音秩序让这种听法成立
→ 什么事实或人物动作使秩序失效
→ 哪项动机、节奏、和声、曲式、音色或演唱变化承担改听
→ 最后一次回归让谁承担什么
→ 结尾留下什么听觉后果
```

- [ ] **Step 3: 把六个声音部门改成职责链**

每个部门保留现有专业内容，并追加同一组执行字段：

```text
作品来源：来自哪项事实、歌词、人物动作或关系压力
声音动作：具体改变音高、节奏、和声、段落、音色或唱法中的什么
听觉作用：听众先后听见什么
相邻协作：它需要其他哪个声音部门承接
否决证据：什么试听结果说明这项设计失败
```

明确六个部门不是六项必满配置；只激活对主听觉命题有实际职责的部门。

- [ ] **Step 4: 统一声音蓝图与三个执行接口**

写清：曲式设计、Style Prompt 和 Controlled Lyrics 都从同一声音蓝图编译。

```text
曲式：负责信息、记忆、能量和回归次序
Style Prompt：负责全局声音身份、主导动机和编配运动
Controlled Lyrics：负责少量段落或句级主唱动作
```

三者出现冲突时回到主听觉命题和作品总线，不分别优化到“看起来专业”。

- [ ] **Step 5: 强化真正的音乐候选**

候选必须改变 hook 到达、能量分配、重复意义、演唱姿态或结尾后果中的至少一项。只换乐器、速度近值、形容词和风格标签不算不同候选。

- [ ] **Step 6: 运行谱曲行为干跑**

使用 `music-v4-03` 与 `music-v4-04`，检查每个方案能回答：

```text
主听觉命题是什么
六个部门中哪些被激活、哪些主动不用
每项声音动作来自哪项作品事实
两套曲式怎样产生不同听觉后果
哪些试听结果要求改判
```

Expected: 不出现只由“伤感、渐进、电影感、传统乐器”组成的方案。

### Task 5: 让三份谱曲 Reference 真正进入声音蓝图

**Files:**
- Modify: `.agents/references/laohu-lyric-composing/曲式结构与音乐叙事.md`
- Modify: `.agents/references/laohu-lyric-composing/音乐风格路由与提示词生成.md`
- Modify: `.agents/references/laohu-lyric-composing/vocal-control.md`
- Test: `tools/check_style_prompt.py`
- Test: `tools/check_controlled_lyrics.py`

- [ ] **Step 1: 完整读取三份 Reference 并建立语义保护清单**

分别记录：触发条件、核心动作、例外、平台硬门、失败分支和验收。修改时只补传导，不摘要删减。

- [ ] **Step 2: 校准曲式 Reference**

补入候选比较契约：每个候选必须列出已有事实、未知音乐条件、hook 到达、信息释放、回归增义、高潮承担者、收益、代价和改判条件。没有旋律时只裁决信息结构，不冒充音高、和声和时长事实。

- [ ] **Step 3: 校准风格路由 Reference**

为每个 Style Prompt 字段增加来源：

```text
Global Metadata ← 用途、速度、调式、整体身体与主听觉命题
Vocal Details / Motif ← 人物身份、主语言动作、中心句、声音记忆
Arrangement ← 段落职责、动机回归、和声与配器运动
```

任何字段无法回溯到声音蓝图时删除；不能以“更完整”为由填满 1000 字符。

- [ ] **Step 4: 校准演唱控制 Reference**

写清每个控制标签必须回答：谁在此刻怎样开口、为何在这句变化、变化作用于哪个可听参数、删除标签会损失什么。全局风格、歌词解释、逐行情绪标签和正文改写继续直接淘汰。

- [ ] **Step 5: 运行现有硬规格工具**

先确认仓库当前没有可用于回归的正式 Style Prompt 与 Controlled Lyrics 成对样本：

```bash
test -z "$(rg -l "Global Metadata:|## Style Prompt" 作品 --glob '*.md' --glob '*.txt')"
```

Expected: exit code `0`。这证明当前只能做工具烟雾检查，不能声称完成了旧生成包回归。

随后使用确定性输入检查工具仍可运行：

```bash
python3 tools/check_style_prompt.py --text 'Global Metadata: Mandarin cinematic pop, 72 BPM. Vocal Details: restrained solo vocal. Arrangement: sparse piano to strings.'
python3 tools/check_controlled_lyrics.py --lyrics 作品/音讯/歌词.md --controlled-lyrics 作品/音讯/歌词.md
```

Expected: 两条命令均 exit code `0`。第一条只证明字符接口正常；第二条只证明无控制标签时原文能够逐字符回装。由于没有正式成对样本，旧生成包回归记为 `UNKNOWN`，不得制造假样本冒充能力证明。

### Task 6: 保护歌名与封面的独门能力

**Files:**
- Modify: `.agents/skills/laohu-lyric-title/SKILL.md`
- Modify: `.agents/skills/laohu-lyric-cover/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-05`、`music-v4-06`

- [ ] **Step 1: 保存两个成熟 Skill 的能力清单**

歌名保护：三种命名机制、五道门、母义去重、听前听后、全歌回插、读音与搜索。

封面保护：第一视觉、主体动作、异常关系、信息差、歌名互补、平台适配、提示词和质量门。

- [ ] **Step 2: 补歌名的多源输入和候选差异**

明确歌名可从作品总线、歌词记忆、声音记忆、人物动作和用途取材；候选必须来自不同命名机制，近义词替换不算候选。歌名不得制造正文与声音没有偿还的冲突，也不得退化成流量标题。

- [ ] **Step 3: 补封面的视觉开发边界**

明确封面负责选择什么关系先被看见、什么答案必须藏住，以及怎样与歌名互补。已有角色、服装、场景资产必须继承；完整人物设计、服装系统和布景开发交给专业视觉项目，封面 Skill 不自行扩成视觉母项目。

- [ ] **Step 4: 干跑歌名与封面场景**

Expected:

```text
歌名至少形成两种真正不同的命名机制，并说明听后增义
封面只选一个主视觉关系，不复述完整剧情
歌名与封面共同偿还作品承诺，但不重复同一句
发现完整角色开发缺口时形成交接，不在封面内部补大全
```

### Task 7: 把质量监督改成领域定位器

**Files:**
- Modify: `.agents/skills/laohu-quality-supervisor/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-08`

- [ ] **Step 1: 保留现有独立监督与最早责任原则**

确认修改后仍保留：独立审稿、不替作者完成作品、逐层退回、用户确认边界和状态结论。

- [ ] **Step 2: 重写监督入口**

监督顺序固定为：

```text
识别当前产物及唯一领域负责人
→ 读取该领域 Skill 的目标、能力链和验收门
→ 检查上游交接是否完整
→ 找到最早失去成立条件的领域层次
→ 退回唯一负责人
```

- [ ] **Step 3: 删除歌词化通用裁决权**

保留四层追查概念，但改为领域化问题：

```text
灵魂：该领域要保护的主判断是否成立
筋骨：该领域的关系、次序、状态和承接是否成立
血肉：该领域材料与技法是否真实产生目标效果
表皮：该领域接口、格式、参数和审美分寸是否成立
```

监督 Skill 不自行定义谱曲、歌名和封面的具体标准，必须引用领域负责人。

- [ ] **Step 4: 干跑错误 Style Prompt 场景**

分别构造四种根因：作品听觉命题错误、风格路由错误、提示词编译错误、字符超限。确认监督能够退回不同节点，不统一写成“情绪不够、画面不够、作品不够深”。

Expected: `music-v4-08` 的四个根因得到四个不同责任位置。

### Task 8: 为自进化增加“长处优先”的四层编译能力

**Files:**
- Modify: `.agents/skills/laohu-project-evolution/SKILL.md`
- Create: `.agents/references/laohu-project-evolution/单一技能四层深化与保真迁移.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-09`

- [ ] **Step 1: 创建按需 Reference 目录**

Run:

```bash
mkdir -p .agents/references/laohu-project-evolution
```

- [ ] **Step 2: 在主 Skill 增加成熟能力优化入口**

触发“优化、重构、补能力、四层深化”时，先建立：

```text
目标 Skill 的独门职责
→ 已被真实任务证明的长处
→ 必须保护的旧场景
→ 当前失败发生在哪一层
→ 缺口属于本 Skill、交接还是相邻负责人
→ 准备加厚什么，不准备补什么
```

写入核心判断：成熟 Skill 的优化先把长处拔高，再修阻碍长处发挥的缺口；不以补齐所有短板为目标。

- [ ] **Step 3: 编写 `单一技能四层深化与保真迁移.md`**

Reference 必须完整包含：

```text
一、独门能力发现：输入、不可替代转译、输出、失败证据
二、四层领域翻译：方向取舍、运行关系、材料技法、交付法度
三、缺口归属：本 Skill / 跨 Skill 交接 / 相邻 Skill / 项目顶层
四、成熟能力迁移：原文语义单元、保留、加厚、迁移、删除依据
五、Reference 激活：触发、取得判断、改变决定、未采用内容
六、回归：当前失败、同根变体、边界反例、旧强项
七、失败分支：模板化、全能化、信息降密、重复权威、静态自证
```

每节必须有触发、动作、边界和验收，不能只解释概念。

- [ ] **Step 4: 将完整方法从主 Skill 路由到 Reference**

主 Skill 保留触发、核心判断、文件归属和验收；只有在创建或深度优化单个 Skill 时读取新 Reference。不得把旧自进化规则摘要删除；仅迁移本轮新增的专项方法。

- [ ] **Step 5: 增加优势回归与改动结论**

每次能力修改必须分别给出：

```text
STRUCTURE：文件与接口
ROUTE：入口与负责人
BEHAVIOR：规则是否改变选择
QUALITY：独立领域结果是否证明提升
```

再给出 `KEEP / OBSERVE / REVERT`。只要旧强项退化，不能以新缺点变少为由判 `KEEP`。

- [ ] **Step 6: 干跑封面人物设计反馈**

Expected: 自进化识别封面 Skill 的长处是音乐作品的第一视觉，不是完整角色开发；修正交接与资产继承，保留封面边界，不创建全能视觉规则。

### Task 9: 校准自然沟通的专业边界

**Files:**
- Modify: `.agents/skills/laohu-natural-dialogue/SKILL.md`
- Test: `tests/skill-capability-scenarios.json` 中 `music-v4-10`

- [ ] **Step 1: 保留现有沟通强项**

不删除当前事实承接、自然中文、锋芒分寸、隐性教学、抽象动词检查和发送前硬门。

- [ ] **Step 2: 增加沟通独门能力链**

在“专业判断必须先由领域能力完成”附近合并：

```text
领域结论与证据
→ 用户此刻最需要看清的矛盾
→ 普通话因果、具体例子和现实后果
→ 明确建议、决定入口或下一份交付
→ 符合当前关系与场景的自然表达
```

- [ ] **Step 3: 增加退回条件**

领域结论只能靠文学比喻、抽象方向词或沟通层补充才能说清时，先退回领域负责人补事实、音乐变量、材料和因果。沟通层可以翻译，不得自行把专业事实改成更顺口的另一套结论。

- [ ] **Step 4: 保护长分析与短交流的适配**

发送前硬门继续约束表皮，但不得要求所有回答使用相同长度、标题、先后顺序和口吻。复杂判断需要完整比较时保留深度；用户只要执行结果时压缩说明。

- [ ] **Step 5: 干跑谱曲解释场景**

把“音乐收紧、把副歌托起来、情绪往上推”分别还原成节奏密度、和声悬置、音域、停顿、配器进入和歌词信息位置。若原领域结论没有这些事实，必须退回谱曲 Skill，而不是由沟通层猜测。

### Task 10: 综合验证与反向审查

**Files:**
- Modify only if a verified conflict remains: all files changed in Tasks 1-9

- [ ] **Step 1: 检查路径、frontmatter 和链接**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re

root = Path('.')
skills = sorted((root / '.agents' / 'skills').glob('*/SKILL.md'))
assert len(skills) == 9, len(skills)
for path in skills:
    text = path.read_text()
    assert text.startswith('---\n'), path
    assert re.search(r'^name:\s*[^\n]+$', text, re.M), path
    assert re.search(r'^description:\s*[^\n]+$', text, re.M), path

for path in [root / 'AGENTS.md', *skills]:
    text = path.read_text()
    for rel in re.findall(r'\]\((\.\./\.\./references/[^)]+)\)', text):
        target = (path.parent / rel).resolve()
        assert target.exists(), (path, rel)
PY
```

Expected: exit code `0`，共九个 Skill，所有匹配到的 Reference 路径存在。

- [ ] **Step 2: 检查顶层预算与重复权威**

Run:

```bash
wc -c AGENTS.md
rg -n "四层首先作用于单个 Skill|主听觉命题|长处优先|共同不变量" AGENTS.md .agents/skills .agents/references
```

Expected: `AGENTS.md` 不超过项目当前 `32 KiB` 默认预算；专项规则只在唯一负责人完整出现，其他位置只路由。

- [ ] **Step 3: 逐项对照设计保护项**

对设计文档第五节的九个 Skill 建立内部对照：

```text
旧长处是否保留
新增规则改变哪次选择
是否扩张了职责
是否出现统一模板复写
是否存在删除但无法指出替代位置的旧信息
```

任何一项不能回答，回到相应任务修正。

- [ ] **Step 4: 运行十个场景的结构验证**

Run:

```bash
python3 -m json.tool tests/skill-capability-scenarios.json >/dev/null
python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path('tests/skill-capability-scenarios.json').read_text())
owners = {item['target_skill'] for item in data['scenarios']}
required = {
    'laohu-lyric-topic', 'laohu-lyric-writing', 'laohu-lyric-composing',
    'laohu-lyric-title', 'laohu-lyric-cover', 'laohu-song-director',
    'laohu-quality-supervisor', 'laohu-project-evolution',
    'laohu-natural-dialogue'
}
assert owners == required, (owners, required)
PY
```

Expected: exit code `0`，九个 Skill 均有代表场景，谱曲有两个场景。

- [ ] **Step 5: 运行静态冲突扫描**

Run:

```bash
rg -n "所有 Skill 必须使用同一|统一四层交接卡|只要合格|四层目录|每个 Skill 都必须有四个同名章节" AGENTS.md .agents/skills .agents/references
```

Expected: 没有把四层机械模板化、没有“只要合格”的目标、没有遗留的歌词化统一交接。

- [ ] **Step 6: 汇总真实验证等级**

最终报告逐项使用：

```text
STRUCTURE：PASS / OBSERVE / FAIL / UNKNOWN
ROUTE：PASS / OBSERVE / FAIL / UNKNOWN
BEHAVIOR：PASS / OBSERVE / FAIL / UNKNOWN
QUALITY：PASS / OBSERVE / FAIL / UNKNOWN
```

本轮同一执行者完成修改和干跑，因此 `BEHAVIOR` 最高为 `OBSERVE`；没有独立真实作品结果时，`QUALITY=UNKNOWN`。不得写“全面完成质量提升”。

- [ ] **Step 7: 检查实际改动范围**

Run:

```bash
git -C /Users/a1/Documents/老胡 status --short -- '老胡自媒体/老胡音乐V4'
```

Expected: 只出现设计、计划和本计划列出的 V4 文件；不包含其他项目文件，不推送远程。
