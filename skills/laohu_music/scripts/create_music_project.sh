#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "用法: $0 <作品名> [yyyy-mm-dd]"
  exit 1
fi

raw_name="$1"
date_prefix="${2:-$(date +%Y-%m-%d)}"

safe_name="$(printf '%s' "$raw_name" | tr '/:' '__' | sed 's/[[:space:]]\\+/_/g')"
project_dir="$ROOT/01_作品项目/进行中/${date_prefix}_${safe_name}"

if [[ -e "$project_dir" ]]; then
  echo "作品目录已存在: $project_dir"
  exit 1
fi

mkdir -p \
  "$project_dir/00_原始输入/文本" \
  "$project_dir/00_原始输入/图片" \
  "$project_dir/00_原始输入/视频" \
  "$project_dir/00_原始输入/音频" \
  "$project_dir/01_选题题眼/文本" \
  "$project_dir/01_选题题眼/音频" \
  "$project_dir/02_曲式与风格/文本" \
  "$project_dir/02_曲式与风格/音频" \
  "$project_dir/03_歌词/文本" \
  "$project_dir/03_歌词/音频" \
  "$project_dir/04_歌词优化/文本" \
  "$project_dir/04_歌词优化/音频" \
  "$project_dir/05_演唱控制/文本" \
  "$project_dir/05_演唱控制/音频" \
  "$project_dir/06_生成素材/文本" \
  "$project_dir/06_生成素材/图片" \
  "$project_dir/06_生成素材/视频" \
  "$project_dir/06_生成素材/音频" \
  "$project_dir/07_发布包装/文本" \
  "$project_dir/07_发布包装/图片" \
  "$project_dir/07_发布包装/视频" \
  "$project_dir/07_发布包装/音频"

cat > "$project_dir/00_项目总览.md" <<EOF
# ${raw_name}

- 作品名：${raw_name}
- 创建日期：${date_prefix}
- 当前阶段：选题题眼
- 老胡表层输入：
- 真实表达目标：
- 嘴替对象：
- 具体场景：
- 核心情绪：
- 题眼判断：
- 副歌核心句：
- 主风格：
- 曲式结构：
- 当前产物：
- 下一步动作：完成选题角度 / 题眼 / 副歌核心句候选

## 阶段状态

| 阶段 | 状态 | 产物 | 老胡确认 | 下一步 |
|---|---|---|---|---|
| 选题题眼 | 进行中 |  | 待确认 | 曲式与风格 |
| 曲式与风格 | 未开始 |  |  | 填词 |
| 填词 | 未开始 |  |  | 歌词优化 |
| 歌词优化 | 未开始 |  |  | 演唱控制 |
| 演唱控制 | 未开始 |  |  | 审查复盘 |
| 审查复盘 | 未开始 |  |  | 归档 |
EOF

cat > "$project_dir/00_阶段确认记录.md" <<EOF
# 阶段确认记录

## ${date_prefix}｜阶段：项目创建

- 产物文件：00_项目总览.md
- 阶段判断：新音乐作品已创建，下一步进入选题题眼阶段。
- 老胡确认状态：待确认
- 老胡反馈：
- 本轮沉淀：
- 下一步：输出选题角度、嘴替对象、题眼和副歌核心句候选。
EOF

cat > "$project_dir/09_归档复盘.md" <<EOF
# 归档复盘

## 基本信息

- 作品名：${raw_name}
- 创建日期：${date_prefix}
- 当前状态：进行中

## 题眼与副歌

- 题眼：
- 副歌核心句：
- 最终是否兑现：

## 曲式与风格

- 主风格：
- 曲式：
- 是否承载情绪：

## 歌词复盘

- 成立的句子：
- 失败的句子：
- 老胡反馈：

## 演唱控制复盘

- style prompt 是否可用：
- 演唱控制是否突出核心句：
- 生成结果反馈：

## 经验回流

- 写入共享资产：
- 更新 skill：
- 下次避免：
EOF

echo "$project_dir"
