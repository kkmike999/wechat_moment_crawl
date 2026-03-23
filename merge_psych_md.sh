#!/usr/bin/env bash
# 将 temp/550篇心理分析与精神分析译文目录 下所有 .md 按路径排序拼接为一个文件。
# 用法:
#   ./merge_psych_md.sh
#   ./merge_psych_md.sh "源目录" "输出.md"

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SRC="$ROOT/temp/550篇心理分析与精神分析译文目录"
DEFAULT_OUT="$ROOT/temp/550篇心理分析与精神分析译文_合并.md"

SRC="${1:-$DEFAULT_SRC}"
OUT="${2:-$DEFAULT_OUT}"

if [[ ! -d "$SRC" ]]; then
  echo "错误: 源目录不存在: $SRC" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
: >"$OUT"

count=0
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  {
    printf '\n\n---\n\n## %s\n\n' "$rel"
    cat -- "$f"
  } >>"$OUT"
  count=$((count + 1))
done < <(find "$SRC" -type f -name '*.md' -print0 | LC_ALL=C sort -z)

echo "已合并 $count 个 .md -> $OUT"
