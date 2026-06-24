# complat-ai-marketplace

コンプラットのAI運用代行（外部AI担当）で使う **共通プラグインの配布リポジトリ**。
全クライアント共通の「頭脳」だけを置く。**クライアント個別の資料はここには入れない**（フォルダ手渡し）。

## 中身
- `gaibu-ai-pack` … 秘書エージェント・ブランドボイス点検スキル・朝タスクコマンド・自動発火フック

## クライアント側の導入（1回だけ）
```
/plugin marketplace add ericakikuchimiyakozawa-lang/complat-ai-marketplace
/plugin install gaibu-ai-pack@complat-ai-marketplace
```
settings.json に `autoUpdate: true` を入れておけば、以後は本リポへのpushで次回起動時に自動更新される。

## 更新の流し方（運用者）
共通機能を直したら本リポに push するだけ。購読中の全クライアントへ自動で行き渡る。
解約クライアントは、本リポの **コラボレーター/アクセスを剥奪** すれば更新が止まる（PCは触らない）。

## 正本
このリポの内容の編集元（マスター）は
`ken_claude/AI運用代行_導入パッケージ/marketplace/` に置く運用。
