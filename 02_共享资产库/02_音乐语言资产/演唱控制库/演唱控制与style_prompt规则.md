# 演唱控制与 Style Prompt 规则

本文件是老胡音乐关于最终音乐提示词、演唱控制、声音设计和平台投喂格式的专项规则库。

它比 `laohu_sing_control_writer` 和 `laohu_sing_control_repair` 更细，负责补充 style prompt 颗粒度、段落级控制、关键行控制、人声距离、动态、和声、声场和格式校验。

演唱控制不是堆标签，而是把歌词里的传播资产声音化。

最终 style prompt 也不是曲风复述，而是一份可直接指导成曲的人声、编曲、声场和段落动态的制作 brief。

本文件属于增强资产，不承担演唱控制 writer 的基础下限能力。主唱画像、正向窄 prompt、[] / [()] 基础语义、hook 让位、控制密度和负向触发词硬门，必须写在 `skills/laohu_sing_control_writer/SKILL.md`；本文件只提供更细的声音格式、平台投喂和类型化控制增强。

## 0.0 使用边界：声音必须让位给歌词

演唱控制所有判断都必须回到同一个创作中枢：

```text
这首歌替谁唱？
他在什么场景里痛？
他最想说但说不出口的是哪句话？
副歌能不能让这个人认账？
这句话能不能唱、能不能记、能不能传播？
```

style prompt 和 controlled lyrics 的作用，是让这五个问题在声音里更清楚。任何控制如果只是显得专业、显得高级、显得制作感强，但没有让核心句更可唱、更贴人、更容易被记住，就必须删掉或降级。

对老胡展示时，先给最终可投喂文本，再给简短说明。符号说明、评审意见和修改决策表用于归档，不得压在最终 prompt 和 controlled lyrics 前面。

## 0.1 歌词声学资产到演唱控制的映射

演唱控制必须把歌词里的声学资产声音化，而不是用制作标签掩盖歌词问题。进入 style prompt 和 controlled lyrics 前，先读取歌词阶段的主韵、完美韵组、长音尾字、气口、重音词、不可遮挡句和 Verse / Pre 叙事钉。

映射规则：

```text
开口长音 → hold final vowel / wider chorus space / vocal forward。
鼻音收束 → quick nasal close / clear tail / keep consonant soft。
短气口 → half-beat breath / dry lead / short phrase ending。
弱尾前移 → hold previous real word, tail-off on particle。
副歌主韵回环 → rhyme handoff / harmony tail after hook / repeat hook tail clearly。
Pre 入副歌触发句 → reduce instruments before hook / shorter breath / tension lift。
Verse 叙事钉 → clear consonants / close dry vocal / no harmony masking。
Rap punchline → tighter consonant attack / bar-end emphasis / minimal reverb。
R&B 贴耳短尾 → close-mic breath / light slide / soft nasal close。
摇滚可喊尾字 → chest voice / open vowel / band duck before hook word。
```

硬门：

```text
如果歌词本身尾音、韵脚、句长或气口不适合唱，先退回歌词优化，不能用 [()] 硬救。
如果某个控制让传播句、主韵尾字或题眼词听不清，控制失败。
如果 style prompt 只增加制作感，没有保护歌词的元音、尾音、重音和气口，必须重写。
```

## 0.2 演唱控制符号语义

本项目的 controlled lyrics 使用两类控制符号：

```text
[]：
段落级控制。只控制当前乐段整体的情绪节奏、编曲动态、人声距离、空间质感和能量状态，放在乐段开头。
正式输出必须使用精简短语格式：
[Section ｜ phrase｜ phrase ｜ phrase]

示例：
[Final Chorus ｜ warm lift｜ restrained low strings ｜ soft harmony tail]

[()]：
关键行控制。只控制它下面紧跟的一句歌词，单独成行。用于 hook、转折句、暴露句、传播锚点句和尾句。
这里可以用自然语言短句，但必须偏具体演唱技法和声音动作，例如拖音、弱起、停顿、升调、降调、胸腔共鸣、头声、真假声转换、咬字、走腔、尾音、和声回应、韵脚承接。
```

不能把自然语言说明当成 controlled lyrics。正式演唱控制初稿和终稿都必须以可投喂格式写出精简 `[]` 段落控制，并在关键位置使用少量但有力的 `[()]` 演唱技法控制。

声音评审官评审时，也必须评审完整 controlled lyrics 初稿，包括哪些 `[]` 或 `[()]` 应该增加、删除、改写、移动或降级。只评 style prompt 的评审不完整。

## 0. 执行前置判断

正式写 style prompt 和 controlled lyrics 前，必须先内部判断：

- 这首歌的音乐任务是什么：叙事型、倾诉型、释放型、宣言型、氛围型、驱动型，还是传播 hook 型。
- 作品发动机是什么：关系代价、情绪债务、人物尊严、叙事现场、传播 hook，还是代际转交。
- 歌名句、副歌核心句、评论区引用句、短视频切片句、现场合唱句、outro 回收句分别在哪里。
- 哪些句子需要贴耳、停顿、咬字、声场打开、和声回应、重复或最后一次变体。
- 哪些句子必须保持克制，不能被编曲和唱法过度放大。

先判断这些，再决定 groove、arrangement、vocal、space、dynamics 和 harmony。不能先套 generic 曲风模板。

## 1. 最终 Style Prompt 的目标

最终 style prompt 要让 AI 音乐平台知道：

- 这是什么细分风格。
- groove、BPM、拍号、鼓贝关系和节奏身体性是什么。
- 编曲主导乐器、辅助乐器、密度和减法位置是什么。
- 人声身份、音色、音区、距离、唱法、咬字、气口和动态是什么。
- Verse / Pre / Chorus / Bridge / Outro 的能量如何变化。
- 哪一句核心歌词需要被声音让位，用停顿、前景人声、重复、和声或声场打开中的哪一种方式放大。
- 和声 / backing vocal 何时进入，何时必须让开主唱。
- 声场和混响如何服务人物和情绪。

不要只写：

```text
emotional pop song, piano, warm, cinematic
```

这类提示词太 generic。

## 2. Style Prompt 推荐顺序

```text
细分音乐风格
→ groove / BPM
→ 风格内乐器
→ 编曲密度
→ 人声音色与身份
→ 人声距离与唱法
→ 段落动态
→ 声场空间
→ hook 放大策略
→ 正向限定模板漂移风险
```

其中“模板漂移风险”只允许写在诊断、评审意见或执行官说明里。最终投喂给音乐平台的 style prompt 必须写成正向窄描述，不靠一堆否定词控制。

### 2.1 最终 Style Prompt 正向表达硬门

最终 style prompt 是模型会直接读取的投喂文本，不能把不想要的概念写进去让模型二次激活。

禁止在最终 style prompt 代码块里出现：

```text
No / no / Avoid / avoid / without / not
不要 / 避免 / 禁止 / 不能 / 不得
```

执行官如果想表达“不要 X”，必须改成“更窄的目标声音”：

| 内部风险判断 | 最终 prompt 应写成 |
|---|---|
| 不要女声 / 偶像亮嗓 | mature male Mandarin baritone only, low-mid dry timbre |
| 不要大合唱 | single forward dry lead, one low harmony tail after hook repeat |
| 不要电影感膨胀 | intimate dry room, restrained low-mid rhythm lift |
| 不要过度转音 | short dry phrase endings, clear unforced consonants, minimal ornamentation |
| 不要励志摇滚 | accountable narrative delivery, controlled drums, muted guitars, restrained chorus lift |

内部文档可以记录“为什么要避开”，但最终 code block 只写目标风格、目标人声、目标编曲和目标动态。

### 硬门槛

- 必须具体到细分音乐风格、groove、乐器分工、人声画像、段落动态和空间质感。
- 必须能回答：听起来是谁在唱、站在多远、伴奏哪里让开、核心句哪里被听见。
- 最终人声版 prompt 不能只是纯音乐 prompt 加一句 `warm vocal`。
- 英文最终 prompt 推荐 650-900 字符，硬上限 900 字符；如果信息很多，优先保留风格、groove、乐器、人声、段落动态、hook 放大和空间。
- 必须用正向边界防止 generic pop ballad、generic piano ballad、generic cinematic swell、宣传片式弦乐、晚会式合唱等模板漂移，例如明确细分风格、主唱身份、乐器密度、声场距离、hook 让位方式和段落能量曲线。

## 2.2 主流商业音色音线选择库

style prompt 里的人声音色不能只写“好听女声、温柔男声、有质感、沙哑、有故事感”。写人声前必须先判断歌词、人物、场景和商业使用场景适合哪一种主声线，再把类别拆成可执行参数。

通用判断顺序：

```text
歌词场景 → 情绪强度 → 人物年龄/性格 → 商业使用场景 → 主声线类别 → 可执行人声参数
```

五类常用商业声线：

```text
1. 慵懒丝滑 R&B 系
特征：气声饱满、转音丝滑、中低音醇厚、轻微颗粒感或沙哑、弱混声和气声结合。
适配：都市情歌、暧昧/拉扯、夜晚车载、睡前 BGM、氛围短片、轻 R&B groove。
prompt 参数：breathy close-mic vocal, silky R&B phrasing, warm low-mid tone, slight husky grain, soft slides, restrained chest-mix, smooth adlibs。
风险：不要过度转音、不要把中文尾字唱成炫技；主 hook 要清楚，转音只能做装饰。

2. 松弛治愈系
特征：干净通透、轻颤音、气声主导、低饱和度情绪、轻拿轻放的力度。
适配：治愈 vlog、情绪短片、通勤/助眠歌单、轻民谣、清新 City Pop、低冲突自白。
prompt 参数：clean airy vocal, translucent timbre, soft breath-led delivery, light vibrato, gentle phrase endings, low-saturation emotion, intimate dry room。
风险：不要用在强冲突、强态度、复仇、宣言型歌词上，否则会削弱立场。

3. 复古未来人声
特征：80s/90s 复古质感叠加现代电子处理，轻微失真、声码器、艺术化 Auto-Tune、合成器空间。
适配：Neo City Pop、Synthwave、赛博/复古潮流、视觉化短片、未来感都市叙事。
prompt 参数：retro-futurist vocal processing, subtle vocoder layer, tasteful Auto-Tune glaze, 80s synth sheen, digital clarity with warm analog texture。
风险：不要用于需要真实近景关系痛感的歌词；电子处理过多会把人物推远。

4. 国风融合人声
特征：戏腔/民族唱腔与流行咬字融合，气声加戏曲拖腔，传统乐器衬底。
适配：古风短视频、文化 IP、国风舞台、历史/神话/东方视觉题材。
prompt 参数：Mandarin pop vocal with light operatic ornament, folk inflection, controlled melisma, traditional instrument bed, graceful phrase tail。
风险：都市现实题材、饭局/职场/亲密关系写实题材默认不使用；戏腔会把现实人物推向舞台表演。

5. 质感沙哑 / 烟嗓
特征：中低音沙哑、颗粒感强、力量感与沧桑感并存，常带流行摇滚、布鲁斯或民谣质地。
适配：故事感、励志、情感宣泄、成年人伤口、强记忆叙事、低音区男声或成熟女声。
prompt 参数：husky low-mid vocal, smoky grain, raspy edge, chest resonance, controlled grit, dry intimate lead, worn but clear diction。
风险：不要让沙哑盖住咬字；年轻、清透、治愈型歌词不要强行烟嗓。
```

商业趋势判断：

```text
情绪优先：先让听众相信这个人在唱自己的事，再考虑炫技。
复古回潮：City Pop、Synthwave、Funk、R&B 可以叠加现代清晰瞬态，但不能只堆年代标签。
融合为王：R&B+说唱、复古+未来、国风+电子都可以用，但必须由歌词题材和画面决定，不为潮流硬混。
短视频适配：音色要抓耳、节奏要清楚、hook 要在 15 秒内被记住。
质感升级：目标是“真实感 + 精致度”，可以写 analog warmth / digital clarity，但不能变成制作炫耀。
```

写 style prompt 时必须明确主辅关系：

```text
主声线：这首歌主要靠哪一类人声被记住。
辅助质感：最多叠加一类辅助音色，例如 R&B 主声线 + 轻微烟嗓颗粒。
禁用方向：内部说明可以写哪些声线不适合，但最终投喂 prompt 仍然只写正向目标。
```

如果一首歌同时写入三种以上互相冲突的音线，例如清透治愈、强烟嗓、戏腔、声码器一起出现，判为声线失焦。优先删到“一个主声线 + 一个辅助质感”。

## 3. 纯音乐骨架升级为最终人声版本

如果前一步是纯音乐 style prompt，最终阶段不能推翻它。

必须保留：

- 律动。
- 空间。
- 段落能量。
- hook space。
- 主风格。
- 编曲取舍。

必须补齐：

- vocal identity。
- vocal timbre。
- range / register。
- delivery。
- phrasing。
- diction。
- breath。
- vocal dynamics。
- harmony / backing vocal strategy。
- chorus vocal lift。
- vocal distance / reverb space。

如果最终 prompt 没有人声音色、音区、距离、唱法或和声策略，判失败。

如果 controlled lyrics 另起一套曲式，判失败。

如果演唱控制阶段改写已确认歌词，判失败。

## 4. 段落级控制优先

先建立 section-level 控制，再做少量关键行控制。

常用段落控制：

```text
[Verse 1 ｜ close vocal｜ restrained groove ｜ clear consonants]
[Pre-Chorus ｜ tension rising｜ shorter breaths ｜ slight lift]
[Chorus ｜ vocal forward｜ wider space ｜ hook phrase held clearly]
[Bridge ｜ stripped arrangement｜ voice closer ｜ emotional turn]
[Final Chorus ｜ warm lift｜ restrained low strings ｜ soft harmony tail]
[Outro ｜ lower energy｜ dry vocal tail ｜ leave silence]
```

段落标签规则：

- `[]` 是段落级控制，放在段落开头。
- 同一段的情绪节奏、编曲动态、人声距离、空间和能量状态要合并在同一个 `[]` 内。
- 段落级控制必须精简，优先使用 3 到 5 个短语，用 `｜` 分隔。
- 段落级控制不写长句解释，不写“像某某一样”，不写复杂技法细节；复杂演唱技法放到 `[()]`。
- 不要在一个段落下面额外堆 `[Vocal preview]`、`[Micro phrasing]`、`[Dynamics]` 等独立控制块。

## 5. 关键行控制

line-level 控制只用于：

- hook。
- 转折句。
- 暴露句。
- 传播锚点句。
- 尾句。

不要每行都加控制。每个控制都必须有声学目的：

- 停顿。
- 弱起。
- 拖音。
- 重复。
- 咬字。
- 升调 / 降调。
- 胸腔共鸣 / 头声 / 假声。
- 真假声转换。
- 走腔 / 滑音 / 尾音收束。
- 韵脚承接。
- 和声回应。
- 声场打开。
- 编曲让位。

格式：

```text
[(line-level vocal technique)]
被控制的歌词
```

整首歌推荐 3-6 处关键行控制，硬上限 7 处。副歌核心句、bridge 翻面句、final chorus 变体句和 outro 尾句优先。

行级控制强度要求：

```text
弱控制：只写情绪，例如 [(more emotional)]，判为不通过。
有效控制：写出具体唱法，例如 [(chest voice, hold "边", slight fall at tail)]。
强控制：同时写出唱法、气口、韵脚或和声动作，例如 [(half-beat breath, chest mix, hold "年", low harmony answers)]。
```

`[()]` 不是越多越好，但关键句不能没有技法控制。副歌第一句、主 hook 落点、Final Chorus 情绪转向句优先保留有效或强控制。Bridge 是否使用行控，要看歌词是否已经靠段落本身完成翻面；如果 Bridge 的歌词已经清楚，默认只保留段落级控制。

每个 `[()]` 必须至少包含一个可执行声学动作：

```text
pause / breath / hold / duck / dry lead / no harmony / harmony tail
chest voice / head voice / falsetto / chest mix
rise / fall / slide / melisma / tail-off
clear consonants / open vowel / nasal ending / rhyme handoff
reduce instruments / leave space / low harmony answers
```

只有情绪形容词、态度说明或抽象表达的 `[()]` 判为弱控制，不能进入终稿。

重复段落标签的 `[()]` 也不能进入终稿。段落标签已经承担了整段的唱法、距离和动态，行级控制必须再增加一个更具体的动作，例如拖哪个尾音、哪里干收、哪里半拍呼吸、哪里低和声回应。若行控只是把段落标签换一种说法重复一遍，它会增加平台解析负担，却不会让关键句更好唱。

Bridge 默认少行控。Bridge 的任务通常是自省、翻面、留白和关系回看，声音上最需要的是空间让出来、人声靠近和乐器减法。除非某一句是全曲唯一翻面句，否则 Bridge 用一个精简段落标签即可，不连续添加多个 `[()]`。

Final 尾钩如果只是 Final Chorus 的最后落点，不要另开像新副歌的独立 section。更稳的写法是把 `final tag / dry caption landing / short phrase endings` 写入 `[Final Chorus]` 段落标签，让最后几句自然完成落点。只有极短回声或一句余波，才适合放在独立 `[Outro]` 或短尾段里。

商业传播优先时，主 hook 与尾钩不能都当最后字幕落点。主 hook 是标题级公共句，负责观众复唱、评论区引用和广泛转发；尾钩是剧情内态度句，负责补刀、转黑和情绪定格。若评审指出两者分流，下一版要让尾钩退到 Final Chorus 中段或倒数第二层，最后一口回到主 hook。只有当尾钩本身比主 hook 更公共、更好记、更适合歌名传播时，才允许尾钩做最终落点。

最终主 hook 不要拆到 Outro 才回收。若 Final Chorus 已经进入最强能量，最终主 hook 应在 Final Chorus 内部完成回收；Outro 只做无歌词余波、钢琴尾音、呼吸或一句很轻的回声。平台投喂里，有歌词 Outro 容易被理解成第二个落点，尤其当前面刚有强尾钩时，会削弱最终 15 秒的结构稳定性。

商业副歌要显性写“旋律钩子”，不能只写“清楚咬字”。当副歌句子信息密、动作多、态度强时，段落标签要给平台一个旋律任务，例如 `rising hook melody`、`wider chorus topline`、`singable title hook`、`repeatable main hook`。这些词的目的不是增加文案，而是防止副歌生成成态度朗读或口号平铺。

副歌文字密度高时，还要分清“主旋律句”和“推进句”。主 hook 要留白、拖尾音、回落或形成旋律弧线；中段动作句要更短促、更轻、更像经过，不要和主 hook 用同等力度抢高点。尾钩如果已经足够锋利，演唱控制要把它处理成低位补刀，而不是再用强声、前景和态度标签把它推成第二主 hook。

当同一首歌连续被评审指出“第一耳 hook 不够凸起”，说明温柔的旋律保护不够，应升级为前景 hook 保护。执行上用更稳定的声音动作：主 hook 前留半拍、主 hook 前景、尾词可拖、标题 hook 可重复；少用技术音素词如 `ai vowel`，优先写 `final word`、`hook ending`、`title hook`，避免平台误解析。

当前景 hook 保护后仍稳定卡在临界分，说明声音控制可能已经接近边界。此时优先做格式稳健化，例如英文逗号标签、减少全角分隔符、删除多余形容；不要继续堆新的唱法词。若仍无法过线，应退回歌词或曲式判断副歌信息密度、hook 概念理解成本、旋律空间是否本身限制商业传播。

最后一层可尝试的副歌旋律保险，是把主 hook 从“前景”进一步具体成可生成的旋律结构：级进旋律、重复标题动机、标题句长音、主 hook 前留白。它只适用于评审已经明确指出“长音、级进、重复音型、留白”的情况；不能作为所有歌曲的默认堆料。

### 5.1 非说唱歌曲不要用 spoken 控制

`spoken / almost spoken / talk-sing / recitative / spoken-like` 这类词会把人声引向念白或半念半唱。它们只适合：

```text
rap / hip-hop / spoken rap 风格；
或 controlled lyrics 明确标注的 rap verse / rap delivery 段落。
```

如果作品是流行抒情、校园、民谣、R&B 抒情、旋律摇滚等以旋律线为主的歌曲，不要在 style prompt、段落标签或 `[()]` 里使用这些词。原因不是它们“不高级”，而是它们会让模型减少旋律承载，中文尾音、主韵和 hook 记忆点容易变弱。

非说唱作品需要表达贴耳、迟疑、像快说出口的感觉时，用旋律型控制替代：

```text
close melodic entry
soft sung onset
short breath then sung line
gentle melodic lift
close melodic phrasing
clear sung phrase with dry ending
```

判断口径：

```text
风格或段落明确说唱 → spoken 类控制可用。
没有明确说唱 → 默认保持 sung / melodic delivery。
```

## 5.2 段落标签格式硬门

最终 controlled lyrics 的每个段落标签必须使用：

```text
[Section ｜ 情绪/动态 ｜ 编曲动作 ｜ 人声/和声/空间动作]
```

允许 3 到 4 个槽位，最多 5 个槽位。槽位之间使用全角竖线 `｜`。不允许使用冒号段落标签，例如：

```text
[Final Chorus: warm lift, restrained low strings]
```

不允许把多个独立控制块堆在同一段落下，例如：

```text
[Vocal preview]
[Micro phrasing]
[Dynamics]
```

这些内容必须合并到段落标签或关键行 `[()]`。

## 5.3 Style Prompt 强度硬门

最终 style prompt 不通过条件：

- 没有明确人声身份：性别 / 年龄感、音区、音色、距离、唱法、咬字和动态。
- 没有明确 vocal distance / vocal timbre / register。
- 没有写出 hook 前后如何让位。
- 没有写出 Chorus 1、Chorus 2、Final Chorus 的能量区别。
- 没有用正向边界压住 generic pop ballad、晚会合唱、宣传片弦乐或过度 cinematic swell 的漂移风险。
- 只是纯音乐 prompt 加一句 vocal 描述。

## 6. 拖音和和声

拖音 `~`：

- 适合副歌实字。
- 适合开口韵、鼻音韵和可共鸣音。
- 不适合轻声助词承担高潮长音。

括号和声：

- 只在 hook、尾句、回答关系或空间扩张处使用。
- 不能遮挡核心传播句。
- 必须服务回应、扩张、记忆点或情绪回声。

## 7. 传播资产声音设计

每首歌至少识别一个传播资产：

- 歌名句。
- 副歌核心句。
- 评论区引用句。
- 短视频切片句。
- 现场合唱句。
- Outro 回收句。

不同资产的声音策略：

```text
短视频切片句：清晰起拍、核心句前留空、8-15 秒可截取。
评论区引用句：人声前景、咬字清楚、不过度和声遮挡。
现场合唱句：稳定韵带、可拖长元音、可重复。
耳机循环句：贴耳、呼吸、口腔细节、不过度爆发。
Outro 回收句：空间后退、尾音留白。
```

## 8. 国内传播与世界可听

国内传播不是口号，要落成声音控制：

- 短视频切片句前要有清晰入点、停顿或节拍留白，8-15 秒内能截取。
- 评论区引用句要人声前景、咬字清楚、不过度戏剧化。
- 现场合唱句要韵带稳定、句尾可落、重复时能抬起来。
- 耳机循环句要保留呼吸、口腔细节、尾音余味和动态层次。

世界可听也不是欧美化：

- 即使不懂中文，也能通过人声姿态、重复 hook、动态弧线、节奏和声场听出情绪关系。
- 不把中文语境洗成泛欧美情绪；保留近景人声、真实空间、节制编曲和本土材料质地。

## 9. 反 AI 声音控制

如果歌词的人味来自笨拙、迟疑、嘴硬、短气口和生活褶皱，声音不能做得过度 polished。

可以保留：

- 贴耳人声。
- 干声边缘。
- 轻微粗粝。
- 短气口。
- 迟疑。
- 克制 vibrato。

避免：

- generic cinematic swell。
- 宣传片式宏大弦乐。
- 过度混响。
- 所有气口都被抹平。
- 编曲淹没歌词。

自我清算型 alternative rock / urban pop 额外注意：

- 副歌打开不等于励志宣誓。只能通过 rhythm、bass weight、low-mid guitar width 稍微打开，主唱仍然前景、克制。
- 禁用 motivational pop-rock anthem、major-key catharsis、anthem belting、choir、crash-heavy chorus 和 guitar wall。
- hook 前的半拍空白比大和声更重要；低男声和声只能在 hook 后或 final chorus 尾部轻进入。
- 行级控制优先保护 hook 呼吸、短尾音和尾句收束，不要每个句尾都安排表演动作。

### 9.1 亲情片尾主题曲的男女合唱控制

亲情片尾歌里的男女合唱，不是“单人版加一个女声 / 男声”，也不是晚会合唱。它的功能是让同一段童年记忆被两个人共同认领，同时仍然保持近麦、克制和私人感。

适用：

- 短剧片尾主题曲。
- 亲情、童年回望、迟来的懂、代际亏欠。
- 年轻男声 + 年轻女声 / 成年青年感合唱。

推荐声部分工：

```text
Verse：男女轮唱或分段领唱，像两个人从不同角度回忆同一件事。
Pre：保留单人领唱，另一声部只在句尾或低处轻托，避免遮挡叙事。
Chorus：主 hook 可轻 unison，尾词后再进入 soft harmony tail。
Bridge：单句轮唱，留出空气，让假设和迟懂有来回。
Final Chorus：主 hook 仍清楚，和声只在“回家 / 牵挂 / 回答”等落点加厚。
Outro：回到近麦和留白，不做集体收束。
```

禁止路线：

```text
gala choir
anthem duet
male-female belting battle
full thick harmony throughout
cinematic choir swell
variety-show final chorus
```

最终 prompt 应用正向窄描述表达，不把禁止词写进投喂代码块。可以写：

```text
close-mic male-female duet, verses alternate lead vocals, choruses gentle unison with soft harmony tails after hook endings, bridge alternating single-line leads, final chorus wider but restrained, dry intimate room, vocal forward, clear hook space
```

检查问题：

```text
1. 合唱是在服务核心句，还是只为了显得更满？
2. 两个声部有没有不同叙事任务？
3. 和声有没有遮挡副歌尾字和完美韵？
4. Final Chorus 是否被推成大合唱？
5. 封面人物年龄是否匹配合唱声音年龄？
```

### 9.2 国风宿命怨诉慢歌的清冷女声控制

国风宿命怨诉慢歌的声音重点不是炫戏腔，而是让听众相信：这个人先忍着，后来忍不住质问，最后只剩一点卑微求告。人声和编曲必须共同完成“隐忍 → 推起 → 爆发 → 求告 → 留白”的动态。

适用：

- 古风 / 国风情爱。
- 明月、长夜、寒江、宿命、轮回等不可得对象承载情绪。
- 慢板孤寂、怨怼、求而不得、命运感。

推荐 style prompt 参数：

```text
Chinese ancient style Mandopop ballad, 72-76 BPM, minor key, melancholic, lonely, cold, fate-driven, cinematic but intimate.
Instrumentation: guzheng harmonics or light arpeggio, breathy bamboo flute long notes, sparse piano single notes, cello long lines, gradual string ensemble swells, subtle pipa tremolo, restrained Chinese bass drum accents only in chorus and bridge.
Vocal: mature female Mandarin vocal, cold smoky low-mid timbre, slight husky grain, breath-led verse, clear diction, chest resonance, controlled chest-mix chorus, slow sorrowful vibrato, minimal melisma, tearful bridge, vocal forward, wide reverb space.
Dynamics: sparse cold verse, rising pre-chorus, powerful but clear chorus, most intense bridge, whispered fading outro.
```

段落控制参考：

```text
[Verse 1 ｜ breath-led low register｜ close cold vocal ｜ sparse guzheng and flute]
[Pre-Chorus ｜ diction firms up｜ strings slowly rise ｜ restrained tension]
[Chorus ｜ chest-mix release｜ vocal forward ｜ wide reverb ｜ clear hook]
[Bridge ｜ tearful peak｜ controlled grit ｜ strings full swell ｜ pleading turn]
[Final Chorus ｜ powerful return｜ harmony tail after hook ｜ drum accents restrained]
[Outro ｜ breathy whisper｜ instruments fall away ｜ long reverb tail]
```

关键行控制参考：

```text
[(half-beat breath, clear consonants, slight chest resonance)]
副歌第一句质问

[(chest mix, hold open vowel, slow vibrato, no harmony over hook word)]
副歌核心句

[(tearful chest voice, slight pitch break, instruments duck before final word)]
Bridge 从恨转求的句子

[(near-whisper, breathy tail-off, leave silence after final word)]
尾句单词或短句
```

风险：

- 戏腔 / 民族拖腔只能轻点缀，不默认全曲使用。这个类型的痛感来自清冷烟嗓、气声到强混的动态，不来自花腔表演。
- 哭腔要艺术化控制，只在副歌后半或 Bridge 关键句明显；全段都哭会显廉价。
- 大混响不能淹没字头，副歌质问句必须人声前置、咬字清楚。
- 大鼓和弦乐只服务高潮，不要把孤寂怨诉推成家国战歌或晚会大歌。

## 10. Controlled Lyrics 格式

输出 controlled lyrics 时：

- 保留原歌词。
- 不擅自改词。
- 段落标签清楚。
- 段落控制合并进 section 标签。
- 行级控制贴在具体歌词行附近。
- 不混入大段解释。
- 初稿也必须是完整 controlled lyrics，不允许只在终稿才出现 `[]` 和 `[()]`。
- 声音评审官必须看到完整初稿 controlled lyrics 后再判断真实听感，指出哪些控制显假、遮挡歌词、模板化或值得保留；`laohu_sing_control_repair` 负责把问题打分并整理成交接单，具体 `[]` / `[()]` 增删改由 `laohu_sing_control_writer` 按诊断落实。

如果老胡明确要求“只要投喂文件”，就输出最干净的投喂版。

## 11. 输出前自检

- 是否先判断音乐任务和作品发动机？
- style prompt 是否具体到细分风格、groove、乐器、人声和空间？
- 人声身份是否具体到性别 / 年龄感、音区、音色、距离、唱法、咬字和动态，而不是只写 lead vocal？
- 是否避免 generic 模板？
- 是否识别核心传播句？
- style prompt 和 controlled lyrics 是否同时为核心传播句让位？
- 是否补齐人声身份、音色、音区、距离、唱法、动态和和声策略？
- 段落控制是否先于行级控制？
- 行级控制是否只落在关键句？
- 是否保留已确认曲式和风格？
- 是否没有擅自改词？
- 是否没有晚会化、宣传片化、公益腔或过度 polished？
- 声音评审是否看过完整初稿 controlled lyrics？
- 评审后是否说明哪些控制标签被新增、删除、移动或改写？
