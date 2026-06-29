#!/usr/bin/env python3
"""AI運用代行 禁止事項ガード（PreToolUse: Bash）

CLAUDE.md の禁止事項のうち、決定論的に判定できる危険コマンドをブロックする。
共通プラグイン gaibu-ai-pack に同梱され、全クライアント環境へ自動配布される。
- ブロック時: exit code 2 + stderr で理由を Claude に返す（承認を促す）
- 判定不能・パース失敗時: fail-open（通す）。ガード自身の不具合で全作業を止めない。
"""
import sys
import json
import re


def block(reason: str):
    sys.stderr.write(
        f"🛑 ブロック: {reason}\n"
        "CLAUDE.md の禁止事項に該当します。実行前にご担当者さまへ対象を提示し、"
        "承認を得てから実行してください（承認済みなら、その旨を添えて再実行を依頼してください）。\n"
    )
    sys.exit(2)


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # fail-open

cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""

# --- 誤検知対策 ---------------------------------------------------------
# git commit のメッセージ本文（-m "..." / -m '...' / ヒアドキュメント）は
# 「実行されるコマンド」ではなく単なる文字列。そこに .env や git push 等の語が
# 含まれても誤ブロックしないよう、git commit のときだけ本文を除去して判定する。
# （bash -c "..." 等の引用符は除去しないので、引用符内に隠した破壊コマンドは検知可能）
scan = cmd
if re.search(r"\bgit\b[^&|;]*\bcommit\b", cmd):
    scan = re.sub(r"<<-?\s*'?(\w+)'?.*?^\s*\1", " ", scan, flags=re.S | re.M)  # heredoc本文
    scan = re.sub(r"-m\s+'[^']*'", "-m ''", scan)   # -m '...'
    scan = re.sub(r'-m\s+"[^"]*"', '-m ""', scan)   # -m "..."

# コマンド境界（行頭／パイプ・連結・サブシェルの直後）。外部送信・公開系は
# 実際にコマンドとして起動される位置に限定し、文字列中の言及では発火させない。
SEP = r"(?:^|[;&|(]|&&|\|\|)\s*"
# -----------------------------------------------------------------------

# 1) 再帰 / 強制削除（rm -r / -f / -rf …）
if re.search(r"\brm\s+-\S*[rRf]", scan):
    block("rm の再帰/強制削除（-r / -f / -rf）")

# 2) git reset --hard（作業内容の破棄）
if re.search(r"\bgit\s+reset\s+--hard\b", scan):
    block("git reset --hard（コミット前の変更を破棄）")

# 3) git push --force / -f（リモート履歴の上書き）
if re.search(SEP + r"git\s+push\b", scan) and re.search(r"(--force\b|\s-f\b)", scan):
    block("git push --force（リモート履歴の上書き）")

# 4) git clean -f（未追跡ファイルの削除）
if re.search(r"\bgit\s+clean\b", scan) and re.search(r"\s-\w*f", scan):
    block("git clean -f（未追跡ファイルの削除）")

# 5) .env / 鍵ファイルの git add / commit
if re.search(r"\bgit\s+(add|commit)\b", scan) and re.search(r"(\.env(\.\w+)?|\.key|\.pem)\b", scan):
    block(".env / 鍵ファイル（*.key / *.pem）のGitコミット")

# 6) python / node 経由のファイル削除（rm ガードを迂回する削除）
#    ※ コマンド行に直接書かれた削除のみ検知。スクリプト内部の削除は検知できない。
if re.search(
    r"(shutil\.rmtree|os\.remove|os\.unlink|os\.rmdir|\.unlink\(|"
    r"\.rmSync\(|\.unlinkSync\(|\.rmdirSync\(|fs\.rm\()",
    scan,
):
    block("python/node 経由のファイル削除（rm ガードを迂回する削除）")

# 7) curl / wget による外部送信（POST・データアップロード＝情報漏洩の経路）
#    単純なGET取得は通す。データ送信フラグがある場合のみ承認を要求する。
if re.search(SEP + r"(curl|wget)\b", scan) and re.search(
    r"(\s-d\b|--data(-binary|-raw)?\b|\s-F\b|--form\b|\s-T\b|--upload-file\b|"
    r"-X\s*(POST|PUT|DELETE)|--request\s+(POST|PUT|DELETE))",
    scan,
):
    block("curl/wget による外部送信（POST/データアップロード）")

# 8) git push（リモートへの公開）
if re.search(SEP + r"git\s+push\b", scan):
    block("git push（リモートへの公開）")

# 9) デプロイ / 公開コマンド（本番反映・パッケージ公開）
if re.search(
    SEP + r"(wrangler\s+(deploy|publish)|vercel\s+(deploy|--prod)|netlify\s+deploy|"
    r"firebase\s+deploy|(npm|pnpm|yarn)\s+publish|gh\s+release\s+create)",
    scan,
):
    block("デプロイ/公開コマンド（本番反映・パッケージ公開）")

# 10) 課金 / 本番サービスCLI（Stripe / Supabase / AWS の本番操作）
if (
    re.search(SEP + r"stripe\b", scan)
    or re.search(SEP + r"supabase\s+db\b", scan)
    or (
        re.search(SEP + r"aws\b", scan)
        and re.search(r"\b(rm|delete|terminate|remove|delete-object)\b", scan)
    )
):
    block("課金/本番サービス操作（Stripe / Supabase / AWS の本番反映）")

sys.exit(0)
