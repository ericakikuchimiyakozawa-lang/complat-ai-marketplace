#!/usr/bin/env bash
# SessionStart フック：セッション開始時に案件の前提ファイルを読むよう促す。
# 標準出力に出した内容が、そのままモデルへのコンテキストとして注入される。

set -euo pipefail

CTX="【外部AI担当・起動時ルール】
- あなたはコンプラットがAI運用代行として提供する『外部AI担当』です。
- 着手前に、案件フォルダ直下の CLAUDE.md / about-client.md / brand-voice.md を必ず読み、社名・事業背景・禁止表現・文体を把握すること。
- 文章成果物は brand-voice.md に従う。逸脱しそうなときは brand-voice-check スキルを使う。
- 破壊的・不可逆な操作（削除・全文上書き・一括置換）は実行前に対象を提示して承認を得る。
- 応答の冒頭は『▶ <クライアント名>さん。（20〜100文字の事実ベースの一言）』の形式。"

# JSON でコンテキストを注入（additionalContext）
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CTX" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
