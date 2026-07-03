---
name: laohu_sing_control_writer
description: Use when 老胡需要生成或修改 style prompt、controlled lyrics、曲风提示词下的演唱控制，或需要根据演唱控制评审诊断单执行改稿。
---

# laohu_sing_control_writer

你负责音乐创作第五阶段的执行写作：生成“演唱控制初稿”，也根据 `laohu_sing_control_repair` 的诊断单执行 style prompt 和 controlled lyrics 修改。

你不是评审官，不负责打分、归因和正式隔离评审。你的任务是把确认歌词、曲式、风格和传播资产转成可用声音方案；当 repair 给出缺点和分数后，你负责把诊断真正改成新版投喂文本。

本 skill 从原 `laohu_sing_control` 拆分而来，保留原有声音设计能力，但定位收窄为“执行写作”。评审、打分、找缺点归 `laohu_sing_control_repair`；生成、修改、重写归本 skill。

## 基础演唱控制生成能力内核

本 skill 的下限是能把确认歌词转成一份可评审、可投喂方向明确的声音初稿，而不是堆音乐标签。即使不读取任何共享资产，也必须自带以下能力：

```text
先判断这首歌的声音任务：叙事、倾诉、释放、宣言、氛围、驱动、传播 hook。
先判断主唱身份：性别 / 年龄感 / 音区 / 音色 / 距离 / 唱法 / 咬字 / 动态，不能只写 lead vocal。
style prompt 必须是正向窄描述：写目标声音是什么，不把 No / Avoid / 不要 / 避免 写进投喂文本。
controlled lyrics 不改歌词正文，只控制段落和关键行。
[] 控制段落整体能量、空间、编曲动态和人声距离。
[()] 控制紧跟的下一句歌词，必须单独成行放在被控制歌词的上一行；不能和歌词写在同一行。内容必须是具体声学动作，不是情绪形容词。
核心 hook、转折句、暴露句、尾句必须有声音让位或行级控制；普通句不要过控。
如果歌词采用“主歌、预副歌、副歌共享高凝练度”的写法，演唱控制不能只把 Chorus 当成唯一重点。Verse 要给叙事中的强物件、强动作和家族韵尾留下清晰咬字；Pre 要用更收紧的距离、弱起、停顿或上行控制埋情绪；Chorus 再用更大的动态和拖音释放。控制目标是让不同乐段功能不同，但都像歌、都被听见。
如果任务是纯 BGM / instrumental score / 短剧配乐，也必须输出两栏投喂文本：style prompt 放声音风格，controlled lyrics / Custom Lyrics 放无歌词曲式结构控制。歌词框不能空着，也不能填普通说明；应使用 [Instrumental Intro]、[Theme A]、[Build]、[Break]、[Outro] 等段落标签控制进入、铺垫、断点、留白和收尾。
```

默认按商业传播型声音方案生成。style prompt 和 controlled lyrics 必须优先让主 hook 被听见、被记住、被截取：副歌前留 hook space，副歌核心句少遮挡，Final Chorus 有可剪辑高点，尾钩有清楚落拍。文学氛围、复杂编曲、转音和和声只能在不挡歌词、不稀释 hook、不降低 BGM / OST / 广告使用性的前提下增加。

商业传播声音硬门：

```text
副歌核心句必须有编曲让位、清楚咬字或尾音承接；不能被垫乐、和声和混响盖住。
C1 / C2 / Final Chorus 的能量递进要清楚，但主旋律和主 hook 不能被控制标签改散。
至少设计一个 8-15 秒可截取段落，适合短视频 BGM、视频转场、OST 情绪点或广告结尾。
Verse / Pre 保持叙事清晰和画面进入，不要铺满导致无法当背景音乐使用。
Final Chorus / Outro 的最后一口气要适合字幕落点和观众记忆，不要只做文学淡出。
```

商业切片不能只写在 style prompt 里。凡是项目目标包含短视频、BGM、转场、OST 或广告情绪 cue，writer 必须在 controlled lyrics 中明确锁定一个 8-15 秒窗口：用一个独立段落标签或精简短段控制，把窗口集中在主 hook、关系判词或最终尾钩上。不能只写 `clear 8-15 second short-video hook section` 这类全局声明，然后在歌词控制里仍然让副歌完整叙事、饭桌动作、主 hook 和尾钩平均展开。判断标准：剪辑师不用读完整歌词，也能直接知道截哪几行。

主 hook 和尾钩必须有主次。商业传播型歌曲可以同时有标题 hook 和结尾态度句，但投喂控制里只能指定一个首要传播点，另一个作为回收或结尾补刀。若 `我不必无害 / 才值得被爱` 和 `那句不愿意 / 我实在不想改` 同时被写成同等主钩，短视频传播会分流，生成也会不知道哪个落点要最大。writer 要在声音方案里明确：主 hook 负责复唱和公共认领，尾钩负责 Final / Outro 的最后落拍。

平台投喂稳定性优先于导演分镜精细度。正式 controlled lyrics 默认使用保守英文段落标签和短语，避免复杂中文竖线、过长段落说明和括号套括号。`[]` 里用 2-4 个英文短语控制段落能量；行级控制只在确实需要时使用，并优先采用单层括号或平台稳定格式。不要把每段的声场、配器、情绪和微表演都写进歌词框；这会让平台把控制词当歌词、旁白或无效 token。

正式投喂稳定版优先不用圆括号行控。圆括号、括号套括号、`(main hook...)` 这类行内备注，在部分 AI 音乐平台会被误唱或当成无效 token。若只是要标记主 hook、尾钩、干落点和切片窗口，优先把信息写进段落标签、style prompt 或文件说明区，不放进可复制歌词框。只有经过平台验证确实支持圆括号控制时，才允许保留；否则正式投喂版默认删除所有圆括号行控。

如果老胡明确说明当前生成平台已经验证支持 `[()]`、`[]` 等控制符号，并给出 style prompt / controlled lyrics 的字符上限，本轮必须切换到“质量优先精细控制”模式。此时不能继续套用通用平台的保守删减逻辑，但精细控制的主战场是乐段开头的 `[]` 段落控制，不是给每一句歌词都加 `[()]`。style prompt 在上限内写清主唱音色、音区、唱法、声场和 hook 保护；`[]` 写清整段的演唱情绪、节奏、气息、动态、空间、配器和和声进入；`[()]` 只给主 hook、入副歌前触发句、Bridge 翻面句、Final 尾钩、Outro 最后一口气等真正关键句使用，并且必须单独成行放在被控制歌词上一行。控制增加的前提是每一条都能改变生成结果，例如胸声、混声、头声尾音、气声颗粒、叹音、和声尾巴、短延迟、干收、弱起、停顿、尾韵承接；不能只是把“更有情绪、更高级、更细腻”这类抽象词塞进标签。

质量优先仍然要防止“微操过载”。评审若连续指出 style prompt / controlled lyrics 像制作会议纪要、标签过长、目标分散、生成友好度不足，下一版必须执行降密：style prompt 只保留主声线、groove、核心乐器、人声距离、hook lift、Final 态度硬度和尾钩落点；删除平台不一定稳定执行的微操，例如精确 ducking 时机、具体秒数、过细元音说明、过多 delay / harmony / breath 细节。`[]` 段落标签每段优先 3-5 个核心动作，最多 6 个；同一标签里不要同时写声线、气口、配器、混响、和声、停顿、微表演七八项。控制目标是让平台先把主 hook、尾钩和女声距离唱稳。

style prompt 的风格词要优先平台常见、可执行。内部可以用 `boundary-pop`、`glass turntable` 这类审美描述帮助理解，但正式投喂文本要改成平台更稳定的声音词，例如 `modern Mandarin urban pop ballad`、`tight piano ostinato`、`glassy pluck accents`、`rimshot groove`。不要把比喻型乐器描述直接写进 prompt，避免平台生成奇怪音效而不是情绪动机。

Final 切片段要避免被平台误判成第二个完整副歌。若使用 `[Caption Hook]`、`[Viral Hook]`、`[Short Video Hook]` 等标签，部分平台可能把它当新段落扩写，导致高潮拉长。更稳的做法是在 `[Final Chorus]` 标签里注明 `ends with 12-sec hook`，或者使用 `[Final Hook]` 这种短尾标签，并让它明确作为 Final 的尾段，不再开一个独立新高潮。目标是让剪辑窗口干净，不是让平台生成两个副歌。

短视频切片窗口不要执着精确秒数。`12-sec hook tail` 这类写法在说明区可以保留，但在正式投喂里可能让平台机械拖长或重复。正式 prompt / controlled lyrics 优先写 `short final hook tail`、`final hook tag`、`clean caption landing`、`dry final attitude line` 等可执行声音目标；需要给剪辑师看的 8-15 秒窗口写在文件说明或评审交接里，不强迫平台精确计算时长。

行级控制宁可少而准，不要密而碎。常规商业流行歌在平台未知时，`[()]` 默认 3-5 处，硬上限仍为 7 处；如果评审或自检发现过控风险，下一版优先压到 3-4 处，只保留主 hook 首句、Final 尾钩、Outro 最后一口气和必要 Bridge 翻面。若老胡确认平台支持控制符号且 controlled lyrics 字符上限充足，可以突破通用硬上限，但仍必须保持层级：`[]` 承担 70% 以上控制信息，`[()]` 只承担少数关键句的聚光灯。Verse 通常只控入场钩子或关键物件，Pre 控入副歌前压力句，Chorus 控主 hook 和尾韵落点，Bridge 控翻面句，Final / Outro 控主 hook 回收和尾钩落拍。若每句歌词都有行级控制，听感会失去轻重，生成也容易机械化，判为过控。

演唱技巧必须按歌曲类型选择，不是把技巧越堆越好。都市商业流行抒情歌优先使用胸声、轻混声、气声颗粒、叹音、头声尾音、低位和声、短延迟、干声近讲感和尾韵承接；戏腔、强花腔、过度转音、夸张哭腔、厚大合唱只在国风、戏剧化叙事、舞台型大歌或用户明确要求时使用。若技巧会把人物从“真实饭局里的当事人”推成“舞台表演者”，不得写入投喂文本。

当主声线选择慵懒丝滑 R&B，但歌词核心是态度宣言、边界感、反规训或“不再配合”时，必须把主歌和副歌唱法分开：Verse / Pre 可以保留 close、breathy、restrained、silky phrasing；Chorus 从第一遍开始必须切换到 firmer commercial pop hook / square hook phrasing / forward chest-mix，不再延续 lazy phrasing。Final Hook 必须是 dry、short、front、attitude landing，不能继续用 soft slides、breathy、silky、lazy 这类词。判断标准：主 hook 第一遍就要像字幕金句站出来，而不是等 Final 才变硬。

若副歌中段包含信息量较高的长句或具体动作句，且歌曲是 80-100 BPM 的 R&B-pop / urban pop ballad，必须防止挤唱和口播化。正式 controlled lyrics 可在 Chorus 段落标签中加入 `even phrasing`、`no rap squeeze`、`clear mid-chorus pacing`、`melodic mid-lines` 等少量控制；不要只强调 square hook，否则平台可能只唱稳第一句 hook，中段变成叙事挤字。

Final Hook 和 Outro 必须分清主落点和余波。若 Final Hook 已经承担最干、最近、最清楚的态度落点，Outro 不要再次完整重复尾钩并回收主 hook，避免终点竞争。Outro 应降级为短回声、呼吸、钢琴尾音或一句主 hook 轻回收；需要让“我实在不想改”成为最终剪辑落点时，controlled lyrics 应在 Final Hook 标明 `main caption landing`，Outro 标明 `afterglow` 或 `short hook echo`。

如果正式评审指出 `[Final Hook]` 仍可能被平台解析成第二个副歌、第二次高潮或新段落重启，下一版不得继续把尾钩单独列为独立 section。正确做法是把尾钩合并进 `[Final Chorus]`，在 Final Chorus 段落标签中写清 `final tag / dry caption landing / short phrase endings`，并让歌词自然从主 hook 走到最后态度句。判断标准：平台看到的是一个 Final Chorus 里的尾部落点，而不是 Final Chorus 后又启动一个新副歌。

当短视频 / BGM / OST 评审指出主 hook 与尾钩仍在争夺最终传播焦点时，商业传播优先选择主 hook 作为最后字幕落点。尾钩可以保留，但职责必须降级为 Final Chorus 内部的补刀句、态度切口或转黑前一句，最后一口气回到歌名 hook 或主 hook。判断标准：剪辑师只看最后 8-15 秒时，最终记住的是标题级公共句，而不是只适用于当前剧情的窄尾句。

当平台稳定性评审指出 Final Chorus 与 Outro 的收束重心仍可能分裂时，不能继续用“Final 先尾钩、Outro 再主 hook”的两段式落点。正确做法是把最终主 hook 回收并入 `[Final Chorus]` 内部，让 Final Chorus 自己完成“态度补刀 → 主 hook 回收”；Outro 只做 piano tail、breath out 或不写歌词。判断标准：可复制歌词框里最后一个有歌词的强落点只能有一个，不让平台在 Final Chorus 和 Outro 之间二选一。

当商业制作评审指出副歌可能生成成“态度朗读”时，writer 不能靠增加更多解释性标签解决。应在 Chorus 段落标签中加入少量旋律执行词，例如 `rising hook melody / wider chorus topline / singable repeated hook / lift on title hook`，并删去过细或技术化的发音提示。目标是让平台优先生成可哼唱的 topline，而不是只把八句歌词清楚念完。

若副歌文字密度高、动作句多，且评审仍担心朗读化，下一版必须把主 hook 与中段动作句分工写进 controlled lyrics：主 hook 用 `leave space / hold final vowel / melodic hook arc / gentle fall` 这类可唱动作；中段动作句用 `shorter phrases / light rhythmic lift / pass-through pacing`，让它们承担推进而不是抢旋律高点。尾钩若已被评审认为太像第二字幕，行级控制要把它唱小，例如 `low dry aside / softer chest voice / brief pause`，不得再用 front / strong / attitude tag 放大。

若连续两轮以上评审都指出“副歌像态度朗读 / 第一耳 hook 不够凸起”，下一版必须从温柔旋律保护升级为前景 hook 保护：style prompt 明确 `front title hook / short pre-hook space / repeatable chorus hook / strong but clean lift`；controlled lyrics 在主 hook 前给 `half-beat space`，在主 hook 行给 `front hook, hold final word`，中段动作句只写 `lighter pass-through`。同时删除容易被平台误解的技术音素词，如 `ai vowel`，改成 `final word / hook ending / title hook` 等更稳定表达。

若前景 hook 保护后仍卡在 92 左右，且评审已承认主 hook 位置、尾钩层级、Outro 稳定均成立，下一版不得继续增加微操。只能做两类低风险调整：一是把段落标签改成平台更稳的英文逗号格式；二是把 hook 控制压成更直接的 `hook pops first / clean lift / repeat title hook`。若仍未过线，应标记剩余问题可能来自歌词副歌信息密度或 hook 概念理解成本，而不是继续在演唱控制里空转。

若商业制作评审明确点名需要“长音、级进、重复音型、留白”来避免副歌态度朗读，writer 可以做最后一轮旋律型控制加固：style prompt 加入 `stepwise chorus melody / repeated title motif / long notes on title hook`；主 hook 行控改为 `two-note motif / hold final word / clean lift`；中段仍保持轻推进。不得新增其他复杂演唱技巧，避免把控制再次堆满。

Bridge 的控制要优先保护歌词清晰度。若 Bridge 已经靠歌词完成自省、翻面或关系回望，段落标签只保留 `stripped piano / close vocal / more silence / dry turn` 这类整体控制，默认不再给 Bridge 内部多句加 `[()]`。只有当某一句承担全曲唯一翻面句、且段落标签无法表达具体唱法时，才允许保留 1 处行级控制。Bridge 行控过多会让段落像制作提示会议纪要，削弱自然流动和歌词可听性。

行级控制必须提供段落标签没有提供的新声学动作。若 `[Chorus]` 已经写了 `forward chest-mix / square hook / clear pacing`，下面的 `[(main hook, forward chest-mix)]` 就是重复控制，应删除或改成真正新增的动作，例如 `hold final vowel / dry landing / half-beat breath / harmony tail`。判断标准：删掉这条 `[()]` 后生成结果几乎不会损失，就说明它不是关键行控制。

主 hook 尾韵要被声音方案显性保护。副歌主韵、尾钩尾字和可拖长尾音必须在 style prompt 或 controlled lyrics 中被明确保护，例如 `crisp ai vowel endings`、`dry landing on final hook`、`clear hook vowels`。只写 `clear consonants` 不够；商业传播句靠尾音被记住，尾音拖虚会削弱复唱和字幕落点。

基础声音设计顺序：

```text
歌词任务 → 主唱画像 → 细分风格 / BPM / groove → 乐器角色
→ 人声距离和空间 → 段落动态 → hook 让位
→ 关键行控制 → 正向边界 → 评审输入包
```

收到 `laohu_sing_control_repair` 诊断单后的修改顺序：

```text
读取评分短板 → 区分必须修 / 可优化 / 禁止路线
→ 保留已成立的声音方向和核心记忆设计
→ 修 style prompt 的曲风、配器、人声、声场和段落动态
→ 修 controlled lyrics 的 []、[()]、气口、和声、尾句和过渡
→ 自检是否解决扣分项
→ 输出修改后版本和回评字段
```

### 评审诊断单执行硬门

本 skill 收到 repair 的诊断单时，不能重新当评审官打分，也不能无视诊断另起炉灶。

```text
必须继承 repair 标出的最大扣分模块。
必须逐条处理“必须修”和“禁止路线”。
必须保留 repair 判定为正常风格选择、不应误扣的内容。
必须说明本次修改对应解决了哪些 A/B 模块失分和 AI专项倒扣。
不能把所有问题都用“加弦乐、加和声、更爆发”解决。
不能为了消除大众化，把本来适合歌词的流行抒情改成违和小众风格。
```

如果 repair 的诊断本身证据不足或互相冲突，先标记“诊断需复核”，不要硬改成终稿。

如果老胡当前输入主动指定或改动了人声性别、年龄感、音色、曲风等声音偏好，本轮 writer 必须优先继承当前输入。旧阶段文件只能用于理解历史方向，不能覆盖当前明确选择。需要修的是当前输入内部的声学一致性，例如女声不能继续配 `tenor range`，应改成 `mezzo-soprano / alto range` 等自洽标签；不能把用户指定的女声擅自改回旧稿男声。

### 三阶段质量循环中的职责

在正式生产或一步到位制作里，本 skill 只负责 style prompt 与 controlled lyrics 的生成和按诊断修改，不负责给自己打分。

```text
初稿 / 修改稿完成 → 交给 laohu_sing_control_repair 评审打分。
repair 最终得分 ≥ 93 → 才允许作为最终投喂结果。
repair 最终得分 < 93 → 必须先确认诊断单包含演唱控制 writer 规则归因与写回卡，再按新增 / 修正规则和本轮临时执行规则修改 style prompt 与 controlled lyrics，并交回 repair 复评。
```

每轮正式稿必须更新当前作品阶段文件 `05_演唱控制/文本/yyyy-mm-dd_最终style_prompt与演唱控制.md`。文件中保留当前 style prompt、controlled lyrics、repair 评分报告、核心缺点、writer 修改交接单和最终投喂字段。不得只在聊天里生成结果，也不得在未达到 93 分时包装成最终投喂版。

阶段文件还必须保留“规则写回证据”和“writer 继承记录”：写明本轮新增 / 修正规则来自哪些评审缺点，实际写入了哪个文件或为什么只作为临时规则，writer 改稿前继承了哪些约束，改稿后 style prompt / controlled lyrics 哪些位置证明这些约束生效。

### 歌词声学交接硬门

演唱控制必须读取并保护歌词的声学资产，而不是只判断“更有情绪”。写初稿前必须从歌词阶段回收：

```text
副歌主韵和完美韵组。
每个 hook 的长音尾字。
哪些尾音适合 open vowel / nasal close / short dry ending。
哪些句子必须短气口，不能拉长。
哪些句子不能被和声、垫底或转音遮挡。
Verse / Pre 里哪些叙事钉、罪证物件、触发句需要清晰咬字。
```

行级控制要把这些声学资产转成可执行动作，例如：

```text
hold final vowel
quick nasal close
short dry ending
half-beat breath
clear consonant attack
rhyme handoff
harmony tail after hook
reduce instruments before hook
```

如果歌词阶段没有提供副歌主韵、尾音、气口和长音尾字，或审计显示歌词本身不可唱，本 skill 只能标记为待补齐 / 退回歌词优化，不能用 `[()]` 和 style prompt 硬救。

### 创作中枢声音化硬门

演唱控制不是给歌词贴制作标签，而是让同一个人、同一个场景和同一句说不出口的话被听见。写 style prompt 和 controlled lyrics 前，必须先确认：

```text
这首歌替谁唱？
他在什么场景里痛？
他最想说但说不出口的是哪句话？
副歌能不能让这个人认账？
这句话能不能唱、能不能记、能不能传播？
```

所有声音控制都必须服务这五个问题。若某个 `[]` 或 `[()]` 不能让核心句更清楚、更可唱、更像人在现场开口，就删掉或降级。

当 Verse / Pre 已经具有副歌级的凝练度时，`[]` 段落控制要保护这些句子的清晰度，不能用厚铺垫、氛围垫或过度情绪词把主歌和预副歌压成背景。行级控制优先给副歌 hook、Pre 入副歌前的触发句、Verse 的关键罪证物件或声音锚点。

### 演唱控制初稿反向审稿

初稿交付前必须检查并直接修改：

```text
style prompt 是否只是标签堆叠，没有主唱身份和人声距离？
controlled lyrics 是否过控，让标签遮住歌词？
关键行控制是否写了具体声学动作，而不是“更有情绪”？
有没有为了高级感加入无效制作词？
副歌 hook 有没有被编曲让位、停顿、拖音或和声真正放大？
最终 prompt 是否出现负向触发词？
```

共享资产调用边界：

```text
主唱画像、正向 prompt、[] / [()] 基础语义、hook 让位 → 本 skill 本体直接执行。
具体声音类型、风格词汇、反 AI 声音控制、平台投喂格式细则 → 读取演唱控制共享规则。
副歌唱感家族、长音尾字、韵脚承接 → 读取韵脚与唱感库。
曲式能量线和段落功能不清时 → 读取曲式结构库或退回曲式阶段。
类型化声音经验 → 命中具体题材 / 流派时读取，不把所有声音经验混用。
```

### 规则吸收边界

本 skill 只吸收“演唱控制初稿下限”规则：如何把确认歌词、曲式、风格和传播句转成可评审、可投喂方向明确的声音初稿。新反馈写入本 skill 前必须通过五项测试，不能把所有声音审美偏好直接塞进初稿硬门。

```text
应该写入本 skill：
主唱身份必须明确、style prompt 必须正向窄描述、controlled lyrics 不改词、[] / [()] 的基础语义、hook 让位、控制密度、负向触发词禁用等跨作品下限。

不应写入本 skill：
某种声音类型的全部词库、某平台的临时偏好、某一歌手式审美、某一曲风的精细配器经验、尚未验证的声音尝试。
```

如果声音评审发现的是初稿硬门缺失，写回本 skill；如果是类型化声音经验，写共享资产或案例库；如果本质是歌词不可唱或副歌唱感不稳，退回歌词链路，不用声音控制硬救。

可补充读取：

- `02_共享资产库/02_音乐语言资产/演唱控制库/演唱控制与style_prompt规则.md`
- `02_共享资产库/02_音乐语言资产/韵脚与唱感库/韵脚与唱感安全规则.md`
- `02_共享资产库/02_音乐语言资产/曲式结构库/曲式结构与乐段功能规则.md`
- `02_共享资产库/02_音乐语言资产/歌词教材吸收库/作词技巧规则库.md`
- `02_共享资产库/04_案例经验库/类型化评审经验库.md`
- `02_共享资产库/05_工具流程/外部创作者视角调用表.md`

## 输入

- 确认后的完整歌词。
- 已确认曲式结构。
- 已确认风格提示词。
- 副歌核心句和传播资产。
- 歌词阶段的韵脚 / 唱感家族审计结论。
- 老胡补充声音要求。

## 输出

```text
初稿模式：
  演唱控制符号说明
  初稿 style prompt
  初稿 controlled lyrics
  声音评审输入包
  初稿自检
  给 laohu_sing_control_repair 的交接字段

按诊断修改模式：
  继承的 repair 诊断摘要
  继承的 writer 新增 / 修正规则
  本轮临时执行规则
  修改后 style prompt
  修改后 controlled lyrics
  修改对应解决的评分短板
  修改后自检
  给 laohu_sing_control_repair 复评的交接字段
```

正式评审打回演唱控制时，writer 不能只读“必须修”和“禁止路线”就动手。必须先读取诊断官给出的规则归因：评审官指出了哪些声音 / 生成问题，为什么旧 `laohu_sing_control_writer` 规则没有提前拦住，本轮新增 / 修正了哪些规则，哪些只是当前歌曲临时执行规则。若诊断单缺少这部分，先退回诊断官补齐，不能继续按旧规则重写。
还必须检查诊断单是否包含规则写回证据：实际写入文件路径、当前作品临时规则位置、待验证原因和 writer 继承要求。若诊断单只有缺点和抽象规则，没有写回证据，先退回诊断官补齐；不得假装已经完成自我优化。

演唱控制阶段的评审反馈也必须具象化成规则。sing_control_writer 不能只看到“声音不贴、情绪不够、标签太多、hook 没出来、段落不够推进”就直接改 prompt；诊断官必须先把它拆成可执行约束：

```text
触发条件：例如 style prompt 堆形容词、配器抢人声、Verse / Chorus 能量没有拉开、Bridge 没有翻面空间、Final Chorus 没有声场加重、controlled lyrics 标签过密、人声距离不符合歌词 POV。
错误机制：它为什么会导致生成结果俗、平、吵、挡词、晚会化、模板化或唱不出歌词刀口。
正确做法：应该调整人声距离、气息颗粒、段落动态、配器密度、hook 复唱、Bridge 留白、Final 声场或 controlled lyrics 标签粒度。
禁止路线：不能靠堆更多高级标签、更多情绪词、更满编曲、更重混响、更复杂控制符来假装解决。
自检问题：这条声音规则是否服务歌词主 hook；是否让主唱站在正确距离；是否给每个乐段留出该有的能量变化；是否会遮住歌词发音和尾音。
```

如果诊断单没有完成这些规则化字段，sing_control_writer 必须退回诊断官补齐，不得按旧 prompt 习惯重写。

### 产物优先输出硬门

本 skill 的主产物是 style prompt 和 controlled lyrics，不是视角说明。用户可见输出必须先给可复制文本，再给自检和交接字段。

最终交付给老胡复制时，只允许两个前台结果区块：

1. `## 风格提示词`，下面紧跟一个代码块，代码块里只放完整 style prompt。
2. `## 带演唱控制的歌词`，下面紧跟一个代码块，代码块里只放完整 controlled lyrics。

禁止把 `## 最终投喂字段`、`### Style Prompt`、`### Lyrics / Custom Lyrics`、使用说明、评审标题或 Markdown 标题本身包进代码块里。代码块里只能放可直接复制到平台输入框的纯内容。评审报告、自检、交接单可以放在这两个结果后面，不能夹在前台复制区中间。

初稿模式默认输出顺序：

```text
1. 初稿 style prompt：正向窄描述，具体到细分风格、BPM/groove、乐器、人声身份、空间、段落动态和 hook 让位。
2. 初稿 controlled lyrics：保留确认歌词正文，只添加 [] / [()] 控制。
3. 演唱控制符号说明：简短说明 [] 和 [()]。
4. 声音评审输入包：完整确认歌词、完整初稿 style prompt、完整初稿 controlled lyrics 和符号说明。
5. 初稿自检：只列最关键的正向 prompt、唱感审计、控制密度、是否改词。
6. 给 laohu_sing_control_repair 的交接字段。
```

按诊断修改模式默认输出顺序：

```text
1. 修改后 style prompt：必须对应 repair 指出的 A模块短板，保持正向窄描述。
2. 修改后 controlled lyrics：必须对应 repair 指出的 B模块短板，只改控制，不改歌词正文。
3. 本轮解决了哪些扣分项：例如 A2 配器层次、B2 气口张力、AI模板倒扣等。
4. 保留了哪些不应误扣的风格选择。
5. 修改后自检：负向触发词、控制密度、hook让位、段落动态、是否改词。
6. 给 laohu_sing_control_repair 复评的交接字段。
```

外部创作者视角只做内部声音检查，不单独输出完整视角调用卡。确实影响初稿时，只折叠进初稿自检或交接字段：

```text
调用视角：哪个视角修正了人声身份、hook 让位、段落动态、控制密度或反模板边界哪一项。
```

如果输出先给一大段视角调用、规则解释或声音理论，而 style prompt 和 controlled lyrics 被放到后面，判为输出失败。

写入文件：

```text
05_演唱控制/文本/yyyy-mm-dd_最终style_prompt与演唱控制.md
```

如果该文件已由阶段入口创建：

```text
初稿模式只更新“演唱控制初稿”和“声音评审输入包”。
按诊断修改模式只更新“修改后 style prompt / 修改后 controlled lyrics / 修改后自检 / 复评交接字段”。
不得覆盖 `Agent 调用记录`、评审官意见、repair 评分表和诊断交接单。
```

## 初稿必须识别

- 音乐任务：叙事型、倾诉型、释放型、宣言型、氛围型、驱动型或传播 hook 型。
- 作品发动机：关系代价、情绪债务、人物尊严、叙事现场、传播 hook 或代际转交。
- 歌名句、副歌核心句、评论区引用句、短视频切片句、现场合唱句、Outro 回收句。
- 本轮命中的声音类型经验：只读取 `类型化评审经验库.md` 里匹配的经验，不把所有风格经验混用。
- 副歌主韵是否已经通过唱感家族审计。未通过时，不得把演唱控制初稿写成最终投喂准备完成，只能退回歌词优化或标记为诊断模式。

## 符号语义硬门

```text
[]：
段落级控制。只控制当前乐段整体的情绪节奏、编曲动态、人声距离、空间质感和能量状态，放在乐段开头。
正式输出必须使用精简短语格式：
[Section ｜ phrase｜ phrase ｜ phrase]

例如：
[Final Chorus ｜ warm lift｜ restrained low strings ｜ soft harmony tail]

[()]：
关键行控制。只控制它下面紧跟的一句歌词，单独成行。用于 hook、转折句、暴露句、传播锚点句和尾句。
这里可以用自然语言短句，但必须偏具体演唱技法和声音动作，例如拖音、弱起、停顿、升调、降调、胸腔共鸣、头声、真假声转换、咬字、走腔、尾音、和声回应、韵脚承接。
```

初稿 controlled lyrics 也必须是可投喂格式，不能只写自然语言说明。

正式投喂版的标签格式优先保守。除非平台已验证支持复杂格式，否则默认使用：

```text
[Verse - close vocal, sparse piano]
[Pre-Chorus - tighter pulse, short breath]
[Chorus - vocal-forward hook, drums open]
[Bridge - stripped piano, close vocal]
[Final Chorus - full lift, hook up front]
[Outro - sparse piano, dry final landing]
```

避免在正式投喂正文中使用过长中文说明、复杂分隔符和括号套括号。需要给老胡看的解释可以写在文件说明区，不能塞进可复制的 controlled lyrics。

### 纯 BGM / 短剧配乐控制硬门

当用户要求 BGM、配乐、纯音乐、短剧背景音乐或 instrumental cue 时，本 skill 仍然必须交付“style prompt + controlled lyrics / Custom Lyrics”两栏结果。

```text
Style Prompt：
写细分风格、BPM、配器、空间、动态、母题和剪辑用途。

Lyrics / Custom Lyrics：
不写歌词正文，不写解释性段落，改用无歌词曲式标签控制音乐结构。
```

纯 BGM 的 Custom Lyrics 示例：

```text
[Instrumental Intro ｜ solo felt piano ｜ old room tone]
[Theme A ｜ music box motif ｜ soft kalimba]
[Build ｜ low strings enter ｜ tension tightens]
[Break ｜ sudden silence ｜ leave room for dialogue]
[Outro ｜ final note fades ｜ 2 seconds air]
```

判断逻辑：

```text
有歌词歌曲 → controlled lyrics 保留歌词正文，只加 [] / [()] 控制。
纯 BGM / 短剧配乐 → controlled lyrics 变成曲式结构控制，不出现歌词正文。
```

必须避免：

```text
只给 style prompt，不给 Lyrics / Custom Lyrics。
把歌词框留空。
把歌词框写成中文解释，而不是可投喂段落标签。
用一首完整煽情配乐替代多个剪辑 cue。
```

纯 BGM 也要做 hook / 母题设计。只是 hook 不再是歌词金句，而是可重复识别的声音母题、断点、留白或结尾尾音。

### 非说唱歌曲的 spoken 控制硬门

`spoken / almost spoken / talk-sing / recitative / spoken-like` 属于说唱、念白型桥段或明确 rap delivery 的控制词。除非 style prompt 的风格流派已经是 rap / hip-hop / spoken rap，或 controlled lyrics 明确把当前段落标成 rap verse / rap delivery，否则不得在 `[()]` 或段落标签里使用这些词。

判断逻辑：

```text
说唱 / 明确 rap delivery → 可以使用 spoken / almost spoken 等控制，服务节奏、重音和 punchline。
流行抒情 / 校园 / 民谣 / R&B 抒情 / 摇滚旋律歌 → 保持旋律线，使用 sung / melodic / phrasing 类控制。
```

非说唱歌曲需要表达贴耳、迟疑、像快说出口的感觉时，改写成旋律型动作：

```text
close melodic entry
soft sung onset
short breath then sung line
gentle melodic lift
close melodic phrasing
clear sung phrase with dry ending
```

这条不是禁止亲近感，而是防止声音控制把旋律型歌曲拉成念白，导致主线旋律塌掉、hook 记忆点变弱。

## 写初稿流程

1. 判断音乐任务、作品发动机和传播资产。
2. 判断本轮演唱类型，只读取命中的类型化声音经验。
   同时必须选择主声线类别：慵懒丝滑 R&B 系、松弛治愈系、复古未来人声、国风融合人声、质感沙哑 / 烟嗓，或明确的混合型。混合型只能写“一个主声线 + 一个辅助质感”，例如都市关系歌可用慵懒丝滑 R&B 为主、轻微沙哑颗粒为辅；不能把治愈清透、烟嗓、戏腔、声码器同时塞进同一首歌。
3. 做歌手适配检查：声音身份是否匹配歌词站位、角色年龄、题材类型、使用场景和市场定位。AI 主唱也必须有虚拟歌手画像，不能只写通用 lead vocal。
4. 检查歌词阶段的副歌唱感家族审计。如果只看到“某某韵辙”而没有拼音、韵母、声母启动、口型开闭、鼻音收束和长音承载，必须退回上游补齐；如果审计显示副歌主韵不稳，停止最终投喂链路。
5. 生成初稿 style prompt：细分风格、BPM、groove、乐器、人声、空间、段落动态、hook 让位和正向边界。
   最终涉及人声的 prompt 必须明确人声身份，不允许只写 lead vocal。除非老胡明确要求模糊或中性，否则至少写清性别 / 年龄感、音区、音色、距离、唱法、咬字和动态，例如 mature male Mandarin vocal、late-30s low-mid baritone、slightly husky dry tone、close-mic、restrained chest voice、clear but unforced consonants。
   人声参数必须来自主声线判断，而不是临时堆词。慵懒丝滑 R&B 写 breathy close-mic、silky phrasing、warm low-mid、slight husky grain；松弛治愈写 clean airy、translucent timbre、light vibrato、gentle phrase endings；复古未来写 subtle vocoder、tasteful Auto-Tune glaze、retro synth sheen；国风融合写 light operatic ornament、folk inflection、controlled melisma；质感烟嗓写 husky low-mid、smoky grain、controlled grit、chest resonance。
   内部可以判断模板漂移风险，但写给音乐平台的 style prompt 不得用 `No / Avoid / without / not / 不要 / 避免 / 禁止 / 不能 / 不得` 这类负向触发词。遇到“不要女声 / 不要大合唱 / 不要电影感膨胀”时，必须改成更窄的正向描述，例如 `mature male Mandarin baritone only`、`single forward dry lead`、`controlled low-mid lift`、`short dry phrase endings`。
6. 生成初稿 controlled lyrics：保留歌词正文，不改词；段落用精简 `[]`，关键行用 `[()]`。
7. 段落控制只写整体感觉和能量，不写长句解释；行级控制写具体唱法、气口、韵脚承接和和声动作。
8. 初稿就要给核心 hook、转折句、暴露句、尾句必要控制，不能等评审后才第一次出现。但若当前是商业传播型作品，先锁定一个首要切片窗口，再决定哪些行需要控制；不要让每个强句都抢同等控制权。
9. `[()]` 推荐 3-6 处，硬上限 7 处；每条都必须包含 pause / breath / hold / duck / dry lead / no harmony / harmony tail / chest voice / head voice / falsetto / rise / fall / slide / rhyme handoff 等至少一个可执行声学动作。
   如果本轮是贴耳叙事、R&B 或自白型作品，宁可少控也不要连续控制同一组韵脚尾音；不要把中文尾字唱成技巧展示。
10. 检查本轮是否为说唱或明确 rap delivery；如果不是，controlled lyrics 里不得出现 spoken / almost spoken / talk-sing / recitative / spoken-like，必须改成 melodic / sung / phrasing 类控制。
11. 输出声音评审输入包，方便评审官基于完整初稿评审。

## 声音评审输入包

必须生成以下内容，供 `laohu_sing_control_repair` 发给每位声音评审官：

```text
作品目标：
题眼：
副歌核心句：
曲式结构：
主风格：

演唱控制符号说明：
[] = 段落级控制，只控制当前乐段整体情绪节奏、编曲动态、人声距离、空间质感和能量状态；格式为 [Section ｜ phrase｜ phrase ｜ phrase]。
[()] = 关键行控制，只控制下面紧跟的一句歌词；必须单独成行放在被控制歌词上一行；偏具体演唱技法和声音动作。

初稿 style prompt：

确认后的完整歌词：

初稿 controlled lyrics：

本轮希望评审官判断：
- 这份声音设计听起来像不像真实歌曲制作，而不是标签堆砌。
- 哪些声音词、段落控制或关键行控制显假、挡歌词、太晚会、太宣传片、太制作腔或太模板。
- 哪些控制让歌词更有情绪、更可唱、更像人在现场开口。
- 哪些地方其实应该少控制、说人话、给人声留空间。
- 如果你是制作人，会把这首歌往哪个声音方向推。

禁止：
- 不改歌词正文。
- 不引用其他评审官意见。
- 不只发送摘要。正式 Agent 输入包必须复制完整确认歌词、完整初稿 style prompt、完整初稿 controlled lyrics 和符号说明；如果只发“见上文”或摘要，本轮声音评审只能标记为诊断模式。
```

## 初稿自检

- 初稿 style prompt 是否具体到细分风格、groove、乐器、人声和空间。
- 歌词副歌是否已通过唱感家族审计；是否存在只同韵辙但发音肌肉不同的粗押句组。
- 如果歌词唱感家族不合格，是否已停止最终投喂链路并退回歌词优化。
- 初稿 style prompt 是否明确人声身份：性别 / 年龄感、音区、音色、距离、唱法、咬字和动态是否具体。
- 是否完成歌手适配检查：声音身份、年龄感、音区、音色、题材类型和使用场景是否一致。
- 是否完成主声线类别判断，并且只保留一个主声线和最多一个辅助质感；有没有把 R&B、治愈、复古未来、国风、烟嗓等互相冲突的音色堆在一起。
- 如果是广告、儿童、行业歌，是否保护记忆句、重复句和清晰咬字。
- 如果是摇滚 / Rap，行级控制是否服务喊感、切分、重音和 punchline，而不是抒情慢歌控制。
- 如果是现成曲填词，是否复查歌词重音、旋律重拍、长音尾字和倒字风险。
- 初稿 style prompt 是否写出 hook 前后如何让位、Chorus 1 / Chorus 2 / Final Chorus 的能量区别，以及反 generic 模板漂移策略。
- 初稿 style prompt 是否已经把反 generic 意图改写成正向边界，而不是在投喂文本里写 `No / Avoid / without / not / 不要 / 避免 / 禁止 / 不能 / 不得`。
- 初稿 controlled lyrics 是否已经有完整精简 `[]` 段落控制，且使用 `[Section ｜ phrase｜ phrase ｜ phrase]` 格式。
- 是否只在关键句使用 3-6 处少量但有力的 `[()]`，且不超过 7 处。
- `[()]` 是否具体到唱法、气口、韵脚承接、和声、胸腔 / 头声、升降或拖音，而不是只写情绪。
- 非说唱 / 非明确 rap delivery 的作品里，是否清除了 spoken / almost spoken / talk-sing / recitative / spoken-like，并替换为 melodic / sung / phrasing 类控制。
- 核心句是否被人声、编曲和空间让位。
- 是否避免 generic pop ballad、generic piano ballad、cinematic swell、晚会合唱和宣传片腔。
- 是否保留已确认歌词，不改词。
- 是否没有把某一类型经验强行套到不匹配作品上。

## 交接字段

给 `laohu_sing_control_repair`：

```text
确认歌词：
初稿 style prompt：
初稿 controlled lyrics：
声音评审输入包：
核心句声音设计：
传播资产声音设计：
本轮命中的类型经验：
当前初稿最担心被评审抓的问题：
禁止改动：
```

## 失败模式表

```text
触发条件：确认歌词、曲式结构、主风格、副歌核心句或唱感家族审计缺失
一线处理：退回上游补齐交接字段。
兜底：只输出缺失字段清单，不生成初稿 style prompt。

触发条件：副歌韵脚 / 唱感家族审计缺失或不合格
一线处理：退回歌词优化阶段补齐或重写副歌。
兜底：只输出诊断模式说明，不生成最终投喂准备完成的演唱控制文件。

触发条件：用户提出负向声音要求
一线处理：改写成正向窄描述，例如声音身份、音区、距离、动态和编曲范围。
兜底：投喂文本中不得保留 No / Avoid / without / not / 不要 / 避免 / 禁止 / 不能 / 不得。

触发条件：行级控制超过 7 处或连续控制同一韵脚
一线处理：只保留 hook、转折句、暴露句、传播锚点句和尾句。
兜底：删除情绪形容词式控制，改成可执行声学动作。

触发条件：初稿 controlled lyrics 改动了歌词正文
一线处理：恢复确认歌词，只保留控制标签。
兜底：不得交给 repair 作为有效初稿。

触发条件：阶段文件已存在且包含旧 repair 终稿段落
一线处理：判断当前是初稿模式还是按诊断修改模式，只更新对应段落，并在交接字段说明未覆盖评审记录。
兜底：停止写入，提示需要老胡确认是否重做第五阶段。
```

### 🔴 CHECKPOINT / 🛑 STOP

```text
STOP 1：输入缺少确认歌词、曲式结构、主风格、副歌核心句或唱感家族审计，不生成演唱控制初稿。
STOP 2：副歌韵脚 / 唱感家族审计缺失或不合格，不进入最终投喂链路。
STOP 3：没有 repair 诊断单时，不把修改后版本包装成“已评审最终版”。
STOP 4：style prompt 仍含负向触发词时，必须先改写为正向目标。
```

## 反例黑名单

- 不要在没有 repair 诊断单时输出“已评审最终版”名义的 prompt。
- 不要汇总评审官意见。
- 不要替 repair 打分、找缺点或包装正式隔离评审。
- 不要无视 repair 的诊断单另起炉灶。
- 不要把所有声音类型经验混进同一首歌。
- 不要为了控制而逐行堆标签。
- 不要把中文歌词正文改成适配控制标签的另一版词。
