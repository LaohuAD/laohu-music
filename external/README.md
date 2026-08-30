# 外部参考资产

这里保存从外部项目引入、但不属于老胡音乐 V4 权威规则的只读参考资产。

## MiniMax Music 3

`MiniMax-Music3/` 来自 `https://github.com/MiniMax-AI/MiniMax-Music3`。当前保留它的原始仓库结构、路由索引和完整模板库，供 V4 的谱曲 Skill 按需检索：

```text
MiniMax-Music3/
└── skills/music-caption-rewriter/
    ├── SKILL.md
    ├── references/genre-router.md
    ├── references/index-*.md
    └── templates/*.txt
```

V4 不复制约 1,000 个模板，也不把外部 Skill 当作 V4 的执行入口。真正生效的规则在：

- `.agents/skills/laohu-lyric-composing/SKILL.md`
- `.agents/references/laohu-lyric-composing/音乐风格路由与提示词生成.md`
- `.agents/references/laohu-lyric-composing/演唱控制与Controlled Lyrics.md`

外部项目负责提供经过整理的风格卡和模板证据；V4 适配层负责作品总线、唯一声音中心、中文歌词词曲接口、演唱控制、字符上限和试听回填。两者职责不同，不能直接覆盖。

## 更新边界

需要同步外部仓库时，在该目录内执行普通 Git 更新，然后重新检查路由文件、模板路径和许可证。更新外部仓库不等于自动接受其新规则；只有经过 V4 适配层审查的变化，才写入本项目 Skill 或 reference。
