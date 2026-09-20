---
name: laohu-lw-suno-interface
description: Compiling a finished lyric into generation-backend input (词稿 → 后端). Section tags and how they map, why line breaks inside a section are read as phrase boundaries rather than layout, what the backend does with punctuation and parentheses, the division of labour with the arrangement library's compiler, the backends that accept lyrics at all and what each does with them, and the checks that catch a lyric which will be sung wrong. Use when handing a finished lyric to Suno, YuE2 or MiniMax, when a generated vocal phrases the words wrongly, when sections come out in the wrong order, or when deciding what belongs in the lyric field versus the style prompt. 歌词、Suno、YuE2、段落标签、编译、交给模型、断句。
---

# 老胡音乐 V4 · 四层能力总纲（laohu 增补）

> 本节是 laohu 用老胡音乐 V4 的「灵魂—筋骨—血肉—表皮」为本 skill 补写的能力总纲，说清它在整个作词体系里到底守着哪一层、哪一件别的 skill 顶替不了的事。**本总纲以下的全部正文，来自 jtydhr88/lyric-writing-skills 的 `lw-suno-interface`，一字未改**；出处与许可见项目 README。

**它是谁**：表皮层的「作词侧交付接口」——把锁定的词稿编译成 Suno／YuE2／MiniMax 等生成后端吃得下的文本输入，且不在途中丢信息。

**灵魂（为什么非有它不可）**
它独家守着一条别处都看不见的判断：**段落内的换行不是排版，是指令——后端把它当乐句边界读**（§3）。一句拆两行会多换一口气，两句并一行会憋着不换气。写词的人凭直觉排版，只有它守着「分行 = 断句指令」这条，让文本的物理形状对齐要唱出来的乐句。第二条独门：注释／创作说明写进词里会被原样唱出来（§4），这条事故别的 skill 拦不住。

**筋骨（它怎样经过流程改变一件事）**
它是作词库交向生成后端的最后一道文本工序。上游要求词已过 LYR-LINT、段落 id 与 `ARR-SPEC.form[].id` 对齐、中文已做倒字检查。它只处理词这一块的格式（分行、标点、括号、段内断句、与标签对齐），把 style_prompt／标签序列／种子／exclude／后端选择全部交给库一唯一编译器 `laohu-mc-render-compile`，冲突时以库一为准。下游产出后端可直接吃的词稿。

**血肉（它拿什么承住这件事）**
段落标签映射表（大サビ→`[Bridge]` 不是 `[Chorus]`，否则内省处给你高能量副歌；落ちサビ 仍是 `[Chorus]`，稀薄写进 style_prompt 别靠改标签）；`[Instrumental]` 留标签不放词（塞词会被当乐句，删标签会让后续段落整体前移）；分行须与 `prosody.syllables` 一致、换气点落在行末；标点能省则省（用分行表达停顿更可靠）；括号=伴唱、方括号=段落标签，各有专用不可混。

**表皮（它怎样交付）**
硬规格可机械核对：标签数量 == form 段落数、段落 id 一一对应、`[Instrumental]` 无词、分行数 == syllables 数组、词里零注释、括号方括号各归其位、目标后端确实吃词（非 Stable Audio）。审美分寸靠 §3.2 的自检：按行念，每行末尾能吸一口气，念不下来就是分行错了。机械通过 ≠ 唱得对。

**它不持有的判断权**
**它是 Suno／生成后端的交付接口，属表皮硬规格层，只管「作词侧如何对接后端文本接口」。** 整份 ARR-SPEC 的编译（风格描述、标签序列、种子、exclude、后端选择、生成包）归库一唯一编译器 `laohu-mc-render-compile`，本 skill 是它的一个输入源，与之重叠处一律以库一为准；「那些字怎么唱」归 `laohu-mc-vocal-direction`，「音频像不像 AI」归 `laohu-mc-ai-tell-audit`。本 skill 是作词协调者手里的执行件，用户不从这里进入整首歌；协调者遇到「词已锁定、要转成后端能吃的格式」的缺口时才点名调用它。

**名称映射**（原文旧引用一字未动，按此换算）：正文中 `lw-*` ＝ 本库 `laohu-lw-*`；「**库一** `mc-*`」＝ 编曲库 `laohu-mc-*`。

# 词稿 → 后端（Lyric Compile）

**这个 skill 只管一件事：把写好的词变成后端吃得下的输入，且不在途中丢信息。**

## ★ 先说分工

**库一有一个编译器 `mc-render-compile`，它管整份 ARR-SPEC 的编译。**
本 skill **不重复它**，只管词这一块，并且**遵守它定的规矩**。

| 谁管 | 什么 |
|---|---|
| **库一 `mc-render-compile`** | style_prompt、段落标签**序列**、exclude、种子、后端选择、`honors` 契约 |
| **本 skill** | ★ **词本身的格式**：分行、标点、括号、段内断句、与标签的对齐 |

★ **冲突时以库一为准**——它是唯一的编译器，本 skill 是它的一个输入源。

## 按任务读哪几节

| 任务 | 读 |
|---|---|
| 交词给 Suno | §2 ＋ §3 |
| 唱出来断句不对 | ★ §3 |
| 段落顺序乱了 | §2.2 |
| 标点/括号怎么处理 | §4 |
| 哪些后端能吃词 | §5 |
| 交之前查什么 | §6 |

## 边界

| 不归这里 | 归哪 |
|---|---|
| 风格描述、段落标签序列、种子、exclude | **库一** `mc-render-compile` |
| 词写得好不好 | 本库 L1/L2 各 skill |
| 那些字该怎么唱（气声/力度/修音） | **库一** `mc-vocal-direction` |
| 生成回来的音频像不像 AI | **库一** `mc-ai-tell-audit` |
| 词本身像不像 AI | `lw-ai-tell-audit` |

---

## 1. 编译前必查

| 必查 | 为什么 |
|---|---|
| **LYR-LINT 过了吗** | lint 不过说明词没写完 |
| **段落 id 与 `ARR-SPEC.form[].id` 对齐吗** | ★ 对不齐，词会被安到错的段落上 |
| **倒字检查做了吗** | 中文词，且已有旋律的话 |
| **目标后端接不接受歌词** | §5。★ Stable Audio **没有人声** |

---

## 2. 段落标签

### 2.1 映射表

与库一一致（`mc-render-compile` §5.1）：

| `form[].name` | 标签 |
|---|---|
| Intro | `[Intro]` |
| Verse | `[Verse]` |
| Pre-Chorus | `[Pre-Chorus]` |
| Chorus | `[Chorus]` |
| **Bridge** | `[Bridge]` |
| Instrumental | `[Instrumental]` |
| Outro | `[Outro]` |

★ **两个陷阱**（库一那边已经写过，这里重申因为填词的人最容易踩）：
1. **大サビ 映射成 `[Bridge]` 不是 `[Chorus]`** —— 映射错了，后端会在内省的位置给你一个高能量副歌
2. **落ちサビ（稀薄编制的副歌）仍然是 `[Chorus]`** —— 稀薄的要求写进 style_prompt，**不要靠改标签表达**

### 2.2 顺序与数量

- ★ **标签序列的数量必须等于 `form` 的段落数**（库一 lint #13）
- **词按段落切开，与标签一一对应**
- 少一个标签，后端就会自己决定那一段是什么

### 2.3 纯器乐段

`[Instrumental]` 下面**不放词**：这是后端按标签分配段落位置的依据，塞了词会被当成要唱的乐句处理。
★ 但**要留着这个标签**，否则后面的段落会整体前移，序列里少一格，后端就会拿下一个标签去顶这一段该在的位置。这是后端固定的分配行为，没有可讨论的条件，两句话说完就是完整的。

---

## 3. ★ 分行：它不是排版

**这是本 skill 最重要的一节。**

> **段落内的换行会被后端当成乐句边界读。**
> 它不是排版，是**指令**。

### 3.1 后果

| 你写的 | 后端理解成 |
|---|---|
| 一句话拆成两行 | **两个乐句**，中间会换气 |
| 两句话并成一行 | **一个长乐句**，中间不换气 |
| 空行 | 更长的停顿 |

★ **所以词稿的分行必须与 `prosody.sections[].syllables` 一致**——
那个数组一个元素就是一行。

### 3.2 与换气点的关系

`narrative` 与 `prosody` 里的 `breath_points`（库一 `vocal.breath_points`）
**应该落在分行处**。不一致的话：

- **换气点在行中** → 后端不会在那儿换气，歌手会憋着
- **分行处没标换气** → 可能出现多余的停顿

★ **自检动作**：把词按行念出来，**每行末尾吸一口气**。念不下来就是分行错了。

### 3.3 一字多音与拖腔

后端看不出你想让哪个字拖长。
**要拖腔就在词里显式写**——不同后端的写法不同，常见的是重复元音（`a-a-ah`）
或用连字符。各后端的实际行为以实测为准。

---

## 4. 标点与括号

| 元素 | 后端通常怎么处理 | 建议 |
|---|---|---|
| **逗号、句号** | 多数忽略，但**可能被当作轻微停顿** | ★ **能不用就不用**——用分行表达停顿更可靠 |
| **括号 ``** | ★ 常被理解为**和声/伴唱**（backing vocal） | 要伴唱就用它；**不要用括号做注释** |
| **方括号 `[]`** | ★ **保留给段落标签**，别的地方不要用 | |
| **省略号、破折号** | 行为不确定 | 避免 |
| **大写**（英文） | 可能影响强调 | 按正常书写 |
| **注释、创作说明** | ★ **会被当成词唱出来** | ★★ **绝对不要放进词里**——放进 LYR-SPEC 的 `note` 字段 |

★★ **最后一条是最常见的事故**：
在词稿里写"（这里要重复三遍）"，后端会**把这句话唱出来**。

---

## 5. 哪些后端能吃词

| 后端 | 词 | 说明 |
|---|---|---|
| **Suno** | ✅ | 段落标签 + 词。成品度最高 |
| **YuE2** | ✅ | ★ **还能吃 ABC 乐谱**——词与旋律都能精确给 |
| **MiniMax Music** | ✅ | ⚠ 商业 API 已对新用户关闭 |
| **ACE-Step** | ✅ | |
| **Stable Audio** | ❌ | ★ **没有人声** |
| **符号路径（MIDI/MusicXML）** | ⚠ | MusicXML 能带歌词（逐音节对齐）；MIDI 只能当文本事件 |

★ 详见库一 mc-workflow 目录里的 `backends.yaml`。

### 5.1 ★ YuE2 的特殊价值

它能同时吃**词**和 **ABC 乐谱**。
这意味着**倒字问题可以在生成前就锁死**——
你给定了旋律，检测器验过了，模型照着唱。

**其余后端只能"提示"旋律**，所以倒字检查的结果**在它们那儿不保证兑现**。

---

## 6. 编译完必过

- [ ] LYR-LINT 过了
- [ ] 段落标签**数量 == `form` 段落数**
- [ ] 段落 id 与 `ARR-SPEC.form[].id` **一一对应**
- [ ] ★ **大サビ 映射成了 `[Bridge]`**
- [ ] `[Instrumental]` 段**留了标签但没放词**
- [ ] ★ **分行与 `prosody.syllables` 一致**；按行念，每行末尾能换气
- [ ] ★★ **词里没有任何注释/创作说明**（会被唱出来）
- [ ] 括号只用于**伴唱**，方括号只用于**段落标签**
- [ ] 标点尽量少，停顿靠分行
- [ ] 目标后端**确实接受歌词**（不是 Stable Audio）
- [ ] 中文：倒字检查做过；★ **若后端不是 YuE2，知道结果不保证兑现**（§5.1）

---

## 附：来源

- **分工依据**：库一 `mc-render-compile`（唯一编译器）与 `backends.yaml`
- §3.3、§4 是通用经验；拖腔写法、标点与括号、段内空行 vs 单换行在各后端的实际反应以实测为准

- 本 skill 不是"Suno 专用"，是"词的编译"，与库一 §2.3 的编译器架构对齐。

