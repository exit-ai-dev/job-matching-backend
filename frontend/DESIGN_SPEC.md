# exitotrinity - 画面デザイン仕様書

## 1. プロジェクト概要

**プロジェクト名**: exitotrinity（エグジトトリニティ）
**種別**: AI求人マッチングプラットフォーム
**対象ユーザー**: 求職者（seeker）と企業（employer）
**技術スタック**: React 19, TypeScript, Tailwind CSS 4, Vite

---

## 2. デザインコンセプト

**テーマ**: 金融系コーポレート × シンプル × 信頼性
**参考**: トヨタファイナンスデザインシステム
**禁止事項**:
- グラデーション背景、斜め区切り、曲線セクション
- 4色以上のビビッドカラー使用
- 強いshadow（shadow-lgやdrop-shadow-xl）
- rounded-3xl以上の極端な角丸
- カード1枚ごとに別配色・別スタイル
- アイコンや装飾イラストの多用

---

## 3. カラーシステム

### 3.1 カラートークン定義

```css
/* 背景 */
--color-page: #fafafa          /* ページ全体の背景 */
--color-surface: #ffffff       /* カード、フォームの背景 */
--color-subtle: #f5f5f5        /* 薄い背景アクセント */

/* テキスト */
--color-main: #1a1a1a          /* メインテキスト */
--color-muted: #666666         /* 補足テキスト */
--color-strong: #000000        /* 強調テキスト */

/* 枠線 */
--color-border-subtle: #e0e0e0 /* 控えめなボーダー */

/* ブランド */
--color-brand-primary: #1e3a8a   /* プライマリカラー（紺） */
--color-brand-secondary: #3b82f6 /* セカンダリカラー（青） */

/* 状態 */
--color-state-info: #0ea5e9
--color-state-success: #10b981
--color-state-warning: #f59e0b
--color-state-error: #dc2626
```

### 3.2 Tailwindカスタムクラス

```css
.bg-page { background-color: var(--color-page); }
.bg-surface { background-color: var(--color-surface); }
.bg-subtle { background-color: var(--color-subtle); }
.text-main { color: var(--color-main); }
.text-muted { color: var(--color-muted); }
.text-strong { color: var(--color-strong); }
.border-subtle { border-color: var(--color-border-subtle); }
.brand-primary { color: var(--color-brand-primary); }
.bg-brand-primary { background-color: var(--color-brand-primary); }
.border-brand-primary { border-color: var(--color-brand-primary); }
```

**使用ルール**:
- 1画面で使う鮮やかな色は、brand-primary / brand-secondary / 状態色1〜2種類まで
- brand-primaryで大きな背景セクションを塗りつぶさない

---

## 4. タイポグラフィ

### 4.1 フォント

**フォントファミリー**:
```css
font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
```

### 4.2 サイズとウェイト

| 用途 | クラス | サイズ | ウェイト |
|------|--------|--------|----------|
| H1（ページタイトル） | `text-3xl md:text-4xl font-semibold` | 30px/36px | 600 |
| H2（セクションタイトル） | `text-2xl md:text-3xl font-semibold` | 24px/30px | 600 |
| セクション小見出し | `text-xl md:text-2xl font-semibold` | 20px/24px | 600 |
| カードタイトル | `text-base md:text-lg font-medium` | 16px/18px | 500 |
| 本文 | `text-sm md:text-base` | 14px/16px | 400 |
| 補足・ラベル | `text-xs text-muted` | 12px | 400 |

### 4.3 行間

- 本文: `leading-relaxed` (1.625)
- 見出し: `leading-tight` (1.25) または `leading-snug` (1.375)

### 4.4 テキスト配置

- 基本は左揃え
- ヒーローセクションのH1＋説明文のみ中央揃え可
- 強調は「太字」または「色変更」のどちらか片方のみ（同時使用禁止）

---

## 5. レイアウトシステム

### 5.1 コンテナ

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* または Tailwind */
max-w-[1120px] mx-auto px-6 md:px-8
```

### 5.2 ブレイクポイント

- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

### 5.3 グリッド

**12カラムシステム**:
- メイン＋サイド: `lg:col-span-8` + `lg:col-span-4`
- 検索＋結果: `lg:col-span-5` + `lg:col-span-7`
- カード3枚: `grid-cols-1 md:grid-cols-3 gap-6`
- カード2枚: `grid-cols-1 md:grid-cols-2 gap-6`

**モバイル**: 必ず1カラム（`grid-cols-1`）

### 5.4 セクション余白

- モバイル: `py-8`
- PC: `py-12` または `py-16`
- セクション内の要素間: `mb-6` または `mb-8`

---

## 6. コンポーネント仕様

### 6.1 ボタン

**Primary ボタン**:
```html
<button class="w-full bg-brand-primary text-white py-2.5 px-5 md:px-6 rounded-full text-sm md:text-base font-medium hover:opacity-90 transition disabled:opacity-50">
  ボタンテキスト
</button>
```

**Secondary ボタン**:
```html
<button class="w-full border border-brand-primary brand-primary py-2.5 px-5 md:px-6 rounded-full text-sm md:text-base font-medium hover:bg-brand-primary hover:text-white transition">
  ボタンテキスト
</button>
```

**サイズ**:
- パディング: `py-2.5 px-5 md:px-6`
- 角丸: `rounded-full`（完全な丸）
- 最小幅: `min-width: 120px`（.btnクラス使用時）

### 6.2 カード

```html
<div class="bg-surface border border-subtle rounded-lg p-4 md:p-6 shadow-sm">
  <h3 class="text-base md:text-lg font-medium text-main mb-2">カードタイトル</h3>
  <p class="text-sm md:text-base text-muted">カード本文</p>
</div>
```

**ルール**:
- 背景: `bg-surface`
- 枠線: `border border-subtle`
- 角丸: `rounded-lg` (8px)
- 影: `shadow-sm` または影なし
- パディング: `p-4 md:p-6`
- 全カードで統一スタイル（個別に色変更禁止）

### 6.3 フォーム入力

**テキスト入力**:
```html
<div>
  <label class="block text-xs text-muted mb-1">メールアドレス</label>
  <input
    type="email"
    class="w-full h-10 md:h-11 px-3 md:px-4 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20"
    placeholder="example@email.com"
  />
</div>
```

**ルール**:
- ラベル: 必ず入力欄の上に配置（`text-xs text-muted mb-1`）
- 入力欄高さ: `h-10 md:h-11`
- 角丸: `rounded-md`
- フォーカス: `focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20`
- 左右並びレイアウト禁止

**テキストエリア**:
```html
<textarea
  class="w-full h-32 md:h-40 px-3 md:px-4 py-3 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20 resize-none leading-relaxed"
></textarea>
```

**セレクトボックス**:
```html
<select class="w-full h-10 md:h-11 px-3 md:px-4 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20">
  <option value="">選択してください</option>
</select>
```

### 6.4 テーブル

```html
<table class="w-full">
  <thead>
    <tr class="bg-subtle h-10">
      <th class="px-3 md:px-4 py-2 text-xs md:text-sm text-muted text-left">カラム1</th>
    </tr>
  </thead>
  <tbody>
    <tr class="border-b border-subtle">
      <td class="px-3 md:px-4 py-2 md:py-3 text-sm text-main">データ</td>
    </tr>
  </tbody>
</table>
```

**ルール**:
- ヘッダ: `bg-subtle h-10`
- 行区切り: `border-b border-subtle`（横線のみ、縦線なし）
- モバイル: 水平スクロール可能（カード表示変換禁止）

---

## 7. 画面別仕様

### 7.1 LandingPage（ランディングページ）

**URL**: `/`

**セクション構成**:
1. ヘッダー（sticky）
2. ヒーロー（左テキスト＋右ビジュアル）
3. 特徴（3カラムカード）
4. 詳細説明（2カラム：左説明文＋右FAQ）
5. フッター

**詳細**:

```html
<!-- ヘッダー -->
<header class="top-header">
  <div class="container">
    <div class="top-header-inner">
      <div class="top-header-logo"><h1>exitotrinity</h1></div>
      <nav class="top-header-nav">
        <ul class="nav-list">
          <li><a href="#features" class="nav-link">機能</a></li>
          <li><a href="#benefits" class="nav-link">特徴</a></li>
          <li><a href="/login" class="nav-link">ログイン</a></li>
        </ul>
      </nav>
      <div class="top-header-actions">
        <a href="/register" class="btn btn-primary">無料で始める</a>
      </div>
    </div>
  </div>
</header>

<!-- ヒーロー -->
<section class="hero">
  <div class="container">
    <div class="hero-content">
      <div>
        <h2 class="hero-title">AIキャリアアドバイザーが<br/>転職活動を完全サポート</h2>
        <p class="hero-description">求人提案・書類添削・模擬面接をチャット一つで。</p>
        <div class="hero-buttons">
          <a href="/register" class="btn btn-primary">今すぐはじめる</a>
          <a href="#features" class="btn btn-secondary">機能を見る</a>
        </div>
      </div>
      <div class="hero-visual">
        <!-- チャットプレビュー等のビジュアル -->
      </div>
    </div>
  </div>
</section>

<!-- 特徴 -->
<section class="features">
  <div class="container">
    <h2 class="section-title">exitotrinity の特徴</h2>
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon"><!-- SVGアイコン --></div>
        <h3 class="feature-title">AI書類添削</h3>
        <p class="feature-description">説明文</p>
      </div>
      <!-- 以下同様に3枚 -->
    </div>
  </div>
</section>

<!-- 詳細 -->
<section class="details">
  <div class="container">
    <div class="details-grid">
      <div class="detail-content">
        <div class="info-item">
          <h3>見出し</h3>
          <p>説明</p>
        </div>
      </div>
      <div class="info-card">
        <h4>よくある質問</h4>
        <ul class="faq-list">
          <li>
            <strong>Q. 質問</strong>
            <p>回答</p>
          </li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- フッター -->
<footer class="footer">
  <div class="container">
    <div class="footer-content">
      <div class="footer-info">
        <h3>exitotrinity</h3>
        <p>説明文</p>
      </div>
      <nav>
        <ul class="footer-nav-list">
          <li><a href="#">リンク</a></li>
        </ul>
      </nav>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2025 exitotrinity. All rights reserved.</p>
    </div>
  </div>
</footer>
```

---

### 7.2 LoginPage（ログインページ）

**URL**: `/login`

**レイアウト**: 中央配置フォーム（max-w-md）

**構成**:
1. ロゴ（brand-primary、text-3xl md:text-4xl）
2. ページタイトル（text-2xl md:text-3xl）
3. エラー表示（border-state-error）
4. LINEログインボタン（緑 #06C755、rounded-full）
5. 区切り線
6. メールアドレス入力
7. パスワード入力
8. ログインボタン（Primary）
9. 新規登録リンク

**コード例**:
```html
<div class="min-h-screen bg-page flex items-center justify-center px-6 py-12">
  <div class="w-full max-w-md bg-surface border border-subtle rounded-lg p-6 md:p-8 shadow-sm">
    <!-- ロゴ -->
    <div class="mb-8">
      <h1 class="text-3xl md:text-4xl font-semibold brand-primary leading-tight">exitotrinity</h1>
      <p class="text-xs text-muted mt-1">for Business</p>
    </div>

    <!-- タイトル -->
    <h2 class="text-2xl md:text-3xl font-semibold text-main mb-6 leading-snug">ログイン</h2>

    <!-- エラー表示 -->
    <div class="mb-6 p-3 bg-surface border border-state-error rounded-md">
      <p class="text-sm state-error">エラーメッセージ</p>
    </div>

    <!-- LINEログインボタン -->
    <div class="mb-6">
      <button class="w-full bg-[#06C755] text-white py-2.5 px-5 md:px-6 rounded-full text-sm md:text-base font-medium hover:opacity-90 transition">
        LINEでログイン
      </button>

      <!-- 区切り線 -->
      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-subtle"></div>
        </div>
        <div class="relative flex justify-center">
          <span class="px-3 bg-surface text-xs text-muted">または</span>
        </div>
      </div>
    </div>

    <!-- フォーム -->
    <form class="space-y-4">
      <div>
        <label class="block text-xs text-muted mb-1">メールアドレス</label>
        <input type="email" class="w-full h-10 md:h-11 px-3 md:px-4 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20" placeholder="example@email.com" />
      </div>

      <div>
        <label class="block text-xs text-muted mb-1">パスワード</label>
        <input type="password" class="w-full h-10 md:h-11 px-3 md:px-4 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20" />
      </div>

      <button type="submit" class="w-full bg-brand-primary text-white py-2.5 px-5 md:px-6 rounded-full text-sm md:text-base font-medium hover:opacity-90 transition mt-6">
        ログイン
      </button>
    </form>

    <!-- 新規登録リンク -->
    <div class="mt-6 text-center">
      <p class="text-xs text-muted">
        アカウントをお持ちでない方は <a href="/register" class="brand-primary hover:opacity-80 font-medium">新規登録</a>
      </p>
    </div>
  </div>
</div>
```

---

### 7.3 RegisterPage（新規登録ページ）

**URL**: `/register`

**レイアウト**: LoginPageと同様、中央配置フォーム

**構成**:
1. ロゴ＋タイトル
2. エラー表示
3. お名前入力
4. メールアドレス入力
5. パスワード入力
6. パスワード確認入力
7. 利用目的セレクト（求職者/企業）
8. 登録ボタン（Primary）
9. ログインリンク

**コード**: LoginPageと同じスタイルを適用（フィールドが増えただけ）

---

### 7.4 ChatPage（検索・会話ページ）

**URL**: `/chat`

**レイアウト**: 2カラム（左5列: トーク、右7列: 検索結果）

**構成**:

**左カラム（トーク画面）**:
- 固定高さ: `h-[calc(100vh-280px)]`
- メッセージエリア（overflow-y-auto）
- 入力エリア（下部固定、border-t）

**右カラム（検索結果）**:
- タイトル（text-xl md:text-2xl）
- 結果カード（bg-surface, border, rounded-lg, p-4 md:p-6）
- マッチ度表示（右上、brand-primary）

**コード例**:
```html
<div class="bg-page min-h-[calc(100vh-120px)]">
  <div class="max-w-[1120px] mx-auto px-6 md:px-8 py-8 md:py-12">
    <h1 class="text-3xl md:text-4xl font-semibold text-main mb-8 md:mb-12 leading-tight">求人検索</h1>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8">
      <!-- 左カラム: トーク -->
      <div class="lg:col-span-5">
        <div class="bg-surface border border-subtle rounded-lg flex flex-col" style="height: calc(100vh - 280px)">
          <!-- メッセージエリア -->
          <div class="flex-1 overflow-y-auto p-4 md:p-6">
            <div class="space-y-4">
              <!-- アシスタントメッセージ -->
              <div class="bg-subtle border border-subtle rounded-md p-3 md:p-4">
                <div class="flex items-baseline gap-2 mb-1">
                  <span class="text-xs font-medium text-main">exitotrinity</span>
                  <span class="text-xs text-muted">10:30</span>
                </div>
                <p class="text-sm md:text-base text-main leading-relaxed">メッセージ内容</p>
              </div>

              <!-- ユーザーメッセージ -->
              <div class="bg-surface border border-subtle rounded-md p-3 md:p-4">
                <div class="flex items-baseline gap-2 mb-1">
                  <span class="text-xs font-medium text-main">ユーザー名</span>
                  <span class="text-xs text-muted">10:31</span>
                </div>
                <p class="text-sm md:text-base text-main leading-relaxed">メッセージ内容</p>
              </div>
            </div>
          </div>

          <!-- 入力エリア -->
          <div class="border-t border-subtle p-4 md:p-6">
            <form class="flex gap-2">
              <input type="text" class="flex-1 h-10 md:h-11 px-3 md:px-4 border border-subtle bg-surface text-main text-sm md:text-base rounded-md focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20" placeholder="例：年収500万円以上、リモート可能" />
              <button type="submit" class="py-2.5 px-5 md:px-6 bg-brand-primary text-white text-sm md:text-base font-medium rounded-full hover:opacity-90 transition whitespace-nowrap">送信</button>
            </form>
          </div>
        </div>
      </div>

      <!-- 右カラム: 検索結果 -->
      <div class="lg:col-span-7">
        <h2 class="text-xl md:text-2xl font-semibold text-main mb-4 md:mb-6 leading-snug">検索結果</h2>

        <div class="space-y-4">
          <!-- 結果カード -->
          <div class="bg-surface border border-subtle rounded-lg p-4 md:p-6 shadow-sm">
            <div class="flex items-start justify-between mb-3 md:mb-4">
              <div class="flex-1">
                <h3 class="text-base md:text-lg font-medium text-main mb-1 leading-snug">フロントエンドエンジニア</h3>
                <p class="text-sm md:text-base text-main">株式会社テックカンパニー</p>
              </div>
              <div class="text-right ml-4">
                <div class="text-xl md:text-2xl font-semibold brand-primary">92%</div>
                <div class="text-xs text-muted">マッチ度</div>
              </div>
            </div>

            <div class="space-y-0.5 mb-3 md:mb-4">
              <p class="text-xs md:text-sm text-muted">年収: 500-800万円</p>
              <p class="text-xs md:text-sm text-muted">勤務地: 東京都渋谷区</p>
            </div>

            <div class="flex flex-wrap gap-2 mb-3 md:mb-4">
              <span class="px-2 md:px-3 py-1 bg-subtle border border-subtle text-main text-xs rounded-full">React</span>
              <span class="px-2 md:px-3 py-1 bg-subtle border border-subtle text-main text-xs rounded-full">TypeScript</span>
            </div>

            <button class="w-full py-2 px-4 border border-brand-primary brand-primary text-sm font-medium rounded-full hover:bg-brand-primary hover:text-white transition">詳細を見る</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

### 7.5 HomePage（ホーム/ダッシュボード）

**URL**: `/home`

**レイアウト**: サイドバー付きレイアウト（Layout コンポーネント使用）

**構成**:
1. ウェルカムセクション（bg-surface, border, rounded, shadow-sm）
2. 統計カード（4カラムグリッド）
3. おすすめ求人 or 候補者リスト

**役割分岐**:
- 求職者（seeker）: 求人カード表示
- 企業（employer）: 候補者カード表示

**統計カードスタイル**:
```html
<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
  <div class="bg-surface rounded border border-subtle p-4 shadow-sm">
    <div class="text-sm text-muted mb-1">マッチング求人</div>
    <div class="text-2xl font-semibold text-main">12件</div>
  </div>
</div>
```

---

## 8. レスポンシブ対応

### 8.1 モバイル優先

- デフォルトはモバイル（1カラム）
- md以上でPC表示（2〜3カラム）

### 8.2 ブレイクポイント別レイアウト

**768px未満（モバイル）**:
- ヘッダーナビ: 縦並び or ハンバーガーメニュー
- グリッド: すべて1カラム
- パディング: px-4, py-8
- フォントサイズ: 小サイズ（text-sm, text-base等）

**768px以上（PC）**:
- ヘッダーナビ: 横並び
- グリッド: 2〜4カラム
- パディング: px-6~px-8, py-12~py-16
- フォントサイズ: 大サイズ（md:text-lg, md:text-xl等）

---

## 9. アニメーション・インタラクション

### 9.1 ホバー効果

- ボタン: `hover:opacity-90`
- リンク: `hover:text-brand-primary`
- カード: `hover:shadow` (shadow-sm → shadow)

### 9.2 トランジション

すべてのインタラクティブ要素に `transition` を追加

```css
transition: all 0.2s ease;
```

### 9.3 禁止事項

- アニメーション（@keyframes）の多用禁止
- 回転、拡大縮小等の派手な効果禁止
- ローディングスピナーはシンプルなもののみ

---

## 10. アイコン使用

### 10.1 SVGアイコン

Heroicons（outline）を推奨

```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="..." />
</svg>
```

### 10.2 サイズ

- 小: `w-4 h-4` (16px)
- 中: `w-5 h-5` (20px)
- 大: `w-6 h-6` (24px)
- 特大: `w-12 h-12` (48px) - feature-icon等

---

## 11. アクセシビリティ

- すべてのフォーム要素にラベル必須
- ボタンは明確なテキスト（「送信」「登録」等）
- コントラスト比: 最低4.5:1（WCAG AA準拠）
- フォーカス表示: `focus:outline-none focus:ring-1`

---

## 12. 実装時の注意事項

1. **Tailwind CSS 4の使用**: `@import "tailwindcss";` を先頭に記述
2. **カスタムCSSクラスとの併用**: `.btn`, `.hero`, `.features`等のクラスはindex.cssで定義済み
3. **カラートークンの厳守**: 直接色コード記述禁止（例外: LINEボタンの#06C755のみ）
4. **レスポンシブ確認必須**: モバイル（375px）、タブレット（768px）、PC（1280px）で動作確認
5. **グラデーション禁止**: `bg-gradient-*` クラス使用禁止
6. **影は控えめに**: `shadow-sm` のみ使用可、`shadow-lg`等禁止

---

## 13. 参考リソース

- トヨタファイナンスデザイン: https://design.toyota-finance.co.jp/
- Tailwind CSS 4: https://tailwindcss.com/
- Heroicons: https://heroicons.com/

---

## 14. 画面一覧サマリー

| 画面名 | URL | レイアウト | 主要コンポーネント |
|--------|-----|------------|-------------------|
| LandingPage | `/` | セクション型（ヘッダー→ヒーロー→特徴→詳細→フッター） | .hero, .features, .details |
| LoginPage | `/login` | 中央フォーム（max-w-md） | フォーム、ボタン、区切り線 |
| RegisterPage | `/register` | 中央フォーム（max-w-md） | フォーム、セレクト、ボタン |
| ChatPage | `/chat` | 2カラム（5:7） | トークUI、検索結果カード |
| HomePage | `/home` | サイドバー付き | 統計カード、求人/候補者リスト |

---

**この仕様書に基づいて、金融系コーポレートデザインに準拠した、シンプルで信頼性の高いUI画面を作成してください。**
