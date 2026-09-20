# 外部参考资产

外部项目提供风格卡与模板证据，不属于 V4 权威规则，也不是必须执行的第三方 Skill。V4 按需读取，不能让外部默认参数、输出格式或流程覆盖用户目标。

## MiniMax Music 3

- 来源：[MiniMax-AI/MiniMax-Music3](https://github.com/MiniMax-AI/MiniMax-Music3)
- 当前参考版本：`945655064d59b98004dd70002e7eb5c8c6e11373`
- 安装位置：项目内 `external/MiniMax-Music3/`
- 状态：本地可选依赖，目录由 `.gitignore` 排除，不随主仓库自动下载。

在项目根目录、确认外接工作盘可用后获取；已有同名目录时先查看来源、版本和工作区状态，不覆盖它：

```sh
git clone https://github.com/MiniMax-AI/MiniMax-Music3.git external/MiniMax-Music3
git -C external/MiniMax-Music3 checkout --detach 945655064d59b98004dd70002e7eb5c8c6e11373
git -C external/MiniMax-Music3 rev-parse HEAD
```

版本须与上面的参考版本一致。网络或该提交不可用时停在获取步骤，不能换到未核验版本后声称已复现。

读取入口为 `skills/music-caption-rewriter/` 下的 `references/genre-router.md`、`references/index-*.md` 和 `templates/*.txt`。不复制整套模板到 `.agents`。

V4 的执行入口与适配方法：

- [谱曲 Skill](../.agents/skills/laohu-lyric-composing/SKILL.md)
- [音乐风格路由与提示词生成](../.agents/references/laohu-lyric-composing/音乐风格路由与提示词生成.md)
- [演唱控制与歌词接口](../.agents/references/laohu-lyric-composing/vocal-control.md)

## 缺失与更新

没有外部目录时，继续用 V4 已有谱曲方法、用户声音参考和经过核实的资料完成方案；模板证据标为缺失，不捏造读取记录。只有任务明确依赖某张模板时才需要先获取依赖。依赖缺失不等于不能创作。

更新前记录当前提交并检查本地改动，随后获取候选版本，核验路由、模板结构和许可证；通过项目适配与代表任务检查后，再同时更新本文件参考版本和本地检出。普通 `git pull` 不自动代表接受新规则；不对有本地改动的依赖强制重置。
