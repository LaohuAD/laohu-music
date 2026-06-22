# 音乐候选池 Schema

本文件借鉴 `cheat-on-content` 的 Candidate Schema，改写为老胡音乐项目的候选池协议。

候选池不只放选题，也可以放：

```text
灵感
热点
参考歌
参考歌词片段
观点句
副歌 hook 候选
发布标题
短视频切片句
课程化主题
老胡反馈里的可复用规则
```

## 1. 必填字段

```text
id：
标题：
来源：
快照文本：
录入时间：
类别：
状态：
```

字段说明：

```text
id：
稳定 hash，可用 source + normalized_title + snapshot_text 前部生成。

标题：
人类可读标题。

来源：
manual / 老胡口述 / 热点 / 参考歌 / 评论反馈 / 生成失败样本 / 外部项目。

快照文本：
候选项真正用于判断的内容，不只是链接。

录入时间：
ISO 或 yyyy-mm-dd。

类别：
选题 / 题眼 / 副歌 / 歌词句 / 曲风 / 发布包装 / 课程化 / 经验规则。

状态：
unread / skimmed / scored / selected / rejected / done / archived。
```

## 2. 可选字段

```text
url：
作品归属：
阶段归属：
composite_score：
dimension_scores：
scored_under_rubric_version：
predicted_bucket：
predicted_reason：
risk_level：
rejected_reason：
note：
```

## 3. Markdown 表示

```text
### [selected] 粉笔还没写完
- id:
- source:
- snapshot_at:
- category:
- work:
- stage:
- composite:
- predicted bucket:
- risk:
- note:

> 快照文本
```

## 4. 去重规则

进入候选池前必须检查：

```text
同一 id 是否已存在。
是否已经进入某个作品。
是否已被老胡否定。
是否只是同一想法换了标题。
是否属于一次性聊天反馈，不值得入池。
```

## 5. Tier 语义

```text
tier1：
强候选，应优先进入创作或复盘。

tier2：
中等候选，可作为备用。

tier3：
弱候选，只保留观察。

risky：
方向有潜力，但存在口味、版权、表达、平台或生成风险。

skip：
老胡明确跳过，短期不要再推。

done：
已经进入作品或沉淀规则。
```

## 6. 推荐策略

每次推荐候选时，不只按高分排序。

推荐两类：

```text
1 稳：
综合分高、风险低、能直接服务当前作品。

1 实验：
不一定最高分，但能验证一个待验证假设，或者能补当前项目缺失的样本类型。
```

如果当前作品已经处在韵脚、歌词或生成风险未解决状态，不推荐新题材，先解决当前阻塞。
