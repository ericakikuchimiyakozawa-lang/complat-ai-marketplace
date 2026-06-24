#!/usr/bin/env bash
# UserPromptSubmit フック：ユーザー発話のキーワードを検知し、対応スキル/ルールの起動を促す。
# CLAUDE.md の「自動判定トリガー」を、CLAUDE.md頼みではなくハーネス側で強制する仕組み。
#
# stdin から JSON（.prompt にユーザー入力）を受け取り、
# 標準出力に出した文字列がコンテキストとして注入される。

set -euo pipefail

INPUT="$(cat)"
PROMPT="$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null || true)"

HINTS=""

case "$PROMPT" in
  *文体*|*ブランドボイス*|*トーン*) HINTS="$HINTS\n- 文章の品質に関わる依頼です。brand-voice-check スキルの使用を検討してください。" ;;
esac
case "$PROMPT" in
  *メルマガ*|*note*|*LP*|*セールスレター*|*コピー*) HINTS="$HINTS\n- 文章成果物です。着手前に brand-voice.md を読み、文体を揃えてください。" ;;
esac
case "$PROMPT" in
  *今日*|*タスク*|*朝*) HINTS="$HINTS\n- タスク確認の文脈です。/朝タスク コマンドが使えます。" ;;
esac

if [ -n "$HINTS" ]; then
  CTX="【自動トリガー検知】$(printf "$HINTS")"
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":%s}}\n' \
    "$(printf '%s' "$CTX" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
fi
exit 0
