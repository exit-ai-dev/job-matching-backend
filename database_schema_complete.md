# データベーススキーマ定義

**プロジェクト名**: AI求人マッチングプラットフォーム（スカウト機能含む）  
**データベース名**: jobmatch  
**DBMS**: PostgreSQL 14+  
**文字コード**: UTF-8  
**最終更新日**: 2024-12-24

---

## 📋 目次

1. [概要](#概要)
2. [テーブル一覧](#テーブル一覧)
3. [ER図](#er図)
4. [詳細テーブル定義](#詳細テーブル定義)
5. [新規追加テーブル](#新規追加テーブル)
6. [漏れていた機能](#漏れていた機能)

---

## 概要

本データベースは、AIを活用した求人マッチングプラットフォームのバックエンドです。
従来の求人マッチング機能に加えて、**企業向けスカウト機能**が追加されています。

### 主要機能

**ユーザー側:**
- ユーザー登録・認証
- AIチャットによる意図抽出
- 動的質問生成と回答収集
- ハイブリッド推薦システム
- ユーザー行動追跡

**企業側:**
- 企業登録・求人管理
- **AIスカウト検索（新機能）**
- **ユーザー性格分析（新機能）**
- **スカウトメッセージ送信・管理（新機能）**

---

## テーブル一覧

### 既存テーブル（10テーブル）

| No | テーブル名 | 説明 | 用途 |
|----|----------|------|------|
| 1 | personal_date | ユーザー基本情報 | 認証・プロファイル |
| 2 | user_profile | ユーザー希望条件 | マッチング条件 |
| 3 | company_date | 企業マスタ | 企業管理 |
| 4 | company_profile | 求人情報 | 求人管理・マッチング |
| 5 | user_interactions | ユーザー行動履歴 | 協調フィルタリング |
| 6 | chat_history | チャット履歴 | 意図抽出・分析 |
| 7 | dynamic_questions | 動的質問マスタ | 質問生成 |
| 8 | user_question_responses | 質問回答 | プロファイル構築 |
| 9 | job_attributes | 求人属性 | 多軸評価 |
| 10 | user_preferences | ユーザープロファイル | 多軸マッチング |

### **新規追加テーブル（2テーブル）**

| No | テーブル名 | 説明 | 用途 |
|----|----------|------|------|
| 11 | **user_personality_analysis** | ユーザー性格分析 | スカウト検索 |
| 12 | **scout_messages** | スカウトメッセージ | スカウト管理 |

### ビュー（3ビュー）

| No | ビュー名 | 説明 |
|----|---------|------|
| 1 | user_interaction_summary | ユーザー行動サマリー |
| 2 | job_stats | 求人統計 |
| 3 | popular_jobs | 人気求人ランキング |

**合計: 12テーブル + 3ビュー**

---

## ER図（完全版）

```mermaid
erDiagram
    personal_date ||--|| user_profile : has
    personal_date ||--o{ user_interactions : performs
    personal_date ||--o{ chat_history : has
    personal_date ||--o{ user_question_responses : answers
    personal_date ||--|| user_preferences : has
    personal_date ||--|| user_personality_analysis : has
    personal_date ||--o{ scout_messages : receives
    
    company_date ||--o{ company_profile : posts
    company_date ||--o{ scout_messages : sends
    
    company_profile ||--o{ user_interactions : receives
    company_profile ||--|| job_attributes : has
    company_profile ||--o{ scout_messages : related_to
    
    dynamic_questions ||--o{ user_question_responses : receives
    
    personal_date {
        INTEGER user_id PK
        VARCHAR email UK
        VARCHAR password_hash
        VARCHAR user_name
        DATE birth_day
        VARCHAR phone_number
        VARCHAR address
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    user_profile {
        INTEGER user_id PK_FK
        VARCHAR job_title
        VARCHAR location_prefecture
        INTEGER salary_min
        TEXT intent_label
        VECTOR embedding
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    user_personality_analysis {
        SERIAL id PK
        INTEGER user_id UK_FK
        JSONB analysis_data
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    scout_messages {
        SERIAL id PK
        UUID company_id FK
        UUID job_id FK
        INTEGER user_id FK
        TEXT message_text
        BOOLEAN auto_generated
        VARCHAR status
        TIMESTAMP read_at
        TIMESTAMP replied_at
        TIMESTAMP created_at
    }
    
    company_date {
        UUID id PK
        UUID company_id
        VARCHAR email UK
        VARCHAR password
        VARCHAR company_name
        VARCHAR address
        VARCHAR phone_number
        VARCHAR website_url
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    company_profile {
        UUID id PK
        UUID company_id FK
        VARCHAR job_title
        TEXT job_summary
        INTEGER salary_min
        INTEGER salary_max
        VARCHAR location_prefecture
        VARCHAR employment_type
        TEXT required_skills
        TEXT preferred_skills
        TEXT benefits
        VARCHAR work_hours
        VARCHAR holidays
        DATE application_deadline
        TEXT intent_labels
        VECTOR embedding
        INTEGER click_count
        INTEGER favorite_count
        INTEGER apply_count
        INTEGER view_count
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    user_interactions {
        SERIAL id PK
        INTEGER user_id FK
        UUID job_id FK
        VARCHAR interaction_type
        FLOAT interaction_value
        JSONB metadata
        TIMESTAMP created_at
    }
    
    chat_history {
        SERIAL id PK
        INTEGER user_id FK
        VARCHAR message_type
        TEXT message_text
        JSONB extracted_intent
        VARCHAR session_id
        TIMESTAMP created_at
    }
    
    user_question_responses {
        SERIAL id PK
        INTEGER user_id FK
        INTEGER question_id FK
        VARCHAR question_key
        TEXT response_text
        TEXT normalized_response
        FLOAT confidence_score
        TIMESTAMP created_at
    }
    
    dynamic_questions {
        SERIAL id PK
        VARCHAR question_key UK
        TEXT question_text
        VARCHAR category
        VARCHAR question_type
        INTEGER usage_count
        INTEGER positive_response_count
        FLOAT effectiveness_score
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    job_attributes {
        SERIAL id PK
        UUID job_id UK_FK
        JSONB company_culture
        JSONB work_flexibility
        JSONB career_path
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    user_preferences {
        SERIAL id PK
        INTEGER user_id UK_FK
        TEXT preference_vector
        TEXT preference_text
        JSONB company_culture_pref
        JSONB work_flexibility_pref
        JSONB career_path_pref
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
```

---

## 詳細テーブル定義

### 既存テーブル（1〜10）

※前回の定義と同様（省略）

---

## 新規追加テーブル

### 11. user_personality_analysis（ユーザー性格分析テーブル）

**用途**: AIによるユーザーの性格・特徴分析結果を保存。企業のスカウト検索に使用。

| カラム名 | データ型 | 長さ | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|------|-----------|------|------|
| id | SERIAL | 4 | NOT NULL | auto | PK | レコード一意ID |
| user_id | INTEGER | 4 | NOT NULL | - | UK, FK | personal_date.user_id参照 |
| analysis_data | JSONB | - | NOT NULL | - | - | 分析結果（JSON形式） |
| created_at | TIMESTAMP | 8 | NOT NULL | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP | 8 | NOT NULL | CURRENT_TIMESTAMP | - | 更新日時 |

**UNIQUE制約**: user_id - 1ユーザーに1分析結果

**analysis_data の JSON構造**:

```json
{
  "personality_traits": ["主要な性格特性を3〜5つ"],
  "work_values": ["仕事で重視する価値観を3〜5つ"],
  "career_orientation": "キャリア志向（安定志向/挑戦志向/バランス志向）",
  "strengths": ["強みと思われる点を3つ"],
  "preferred_work_style": "好む働き方（リモート重視/オフィス重視/柔軟性重視）",
  "preferred_company_culture": "好む企業文化（チームワーク重視/個人裁量重視/成長重視）",
  "salary_importance": "年収の重要度（高/中/低）",
  "location_flexibility": "勤務地の柔軟性（高/中/低）",
  "risk_tolerance": "リスク許容度（高/中/低）",
  "growth_mindset": "成長志向の強さ（高/中/低）",
  "summary": "このユーザーの特徴を2-3文で要約"
}
```

**使用箇所**:
- `company_scout_system.py:156-173` - 分析結果の保存
- `company_scout_system.py:241-257` - スカウト検索での利用
- `comapny_app_enhanced.py:406` - スカウトメッセージ生成

**データ生成方法**:
1. ユーザーのチャット履歴を取得（最新50件）
2. 質問への回答を取得
3. 行動データ（クリック、お気に入り等）を取得
4. お気に入り求人の傾向を分析
5. GPT-4で性格分析を実施
6. 結果をJSONB形式で保存

---

### 12. scout_messages（スカウトメッセージテーブル）

**用途**: 企業からユーザーへのスカウトメッセージを管理。送信履歴、既読状態、返信状況を追跡。

| カラム名 | データ型 | 長さ | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|------|-----------|------|------|
| id | SERIAL | 4 | NOT NULL | auto | PK | メッセージ一意ID |
| company_id | UUID | 16 | NOT NULL | - | FK | company_date.company_id参照 |
| job_id | UUID | 16 | NOT NULL | - | FK | company_profile.id参照 |
| user_id | INTEGER | 4 | NOT NULL | - | FK | personal_date.user_id参照 |
| message_text | TEXT | - | NOT NULL | - | - | スカウトメッセージ本文 |
| auto_generated | BOOLEAN | 1 | NOT NULL | false | - | AI自動生成フラグ |
| status | VARCHAR | 20 | NOT NULL | 'sent' | - | ステータス |
| read_at | TIMESTAMP | 8 | NULL | - | - | 既読日時 |
| replied_at | TIMESTAMP | 8 | NULL | - | - | 返信日時 |
| created_at | TIMESTAMP | 8 | NOT NULL | CURRENT_TIMESTAMP | - | 送信日時 |

**status の値**:
- `sent`: 送信済み（未読）
- `read`: 既読
- `replied`: 返信あり
- `declined`: 辞退

**使用箇所**:
- `company_scout_system.py:467-484` - メッセージ送信
- `company_scout_system.py:550-579` - 送信履歴取得
- `company_scout_system.py:582-623` - ステータス更新
- `comapny_app_enhanced.py:99-125` - ダッシュボード統計表示

**ビジネスロジック**:
1. 企業が求人に対してユーザーを検索
2. マッチスコアの高いユーザーを抽出
3. AIがユーザーの性格分析に基づいてメッセージを自動生成
4. スカウトメッセージを送信（scout_messagesに記録）
5. ユーザーがメッセージを開く → `read_at` 更新
6. ユーザーが返信 → `replied_at` 更新

---

## 漏れていた機能・テーブル

### 1. **スカウト機能関連**

以前のスキーマでは以下が欠落していました:

#### ❌ 欠落していたテーブル:
- `user_personality_analysis` - ユーザー性格分析
- `scout_messages` - スカウトメッセージ管理

#### ❌ 欠落していた機能:
- AIによるユーザー性格分析
- 企業からユーザーへのスカウト検索
- スカウトメッセージの自動生成
- スカウト送信履歴の管理
- スカウトメッセージのステータス追跡

### 2. **user_profile テーブルの拡張**

実際のコードでは `user_profile` にエンベディングカラムがある可能性があります:

```sql
-- company_scout_system.py:249 で参照されている
ALTER TABLE user_profile ADD COLUMN embedding VECTOR(1536);
```

### 3. **job_attributes テーブルの追加カラム**

実際のコードでは以下のカラムも使用されています:

```sql
-- company_scout_system.py:71-72 で参照されている
ALTER TABLE job_attributes 
ADD COLUMN remote_work BOOLEAN,
ADD COLUMN flex_time BOOLEAN,
ADD COLUMN overtime_avg VARCHAR(20);
```

### 4. **company_date テーブルの追加カラム**

実際のコードでは以下のカラムも使用されています:

```sql
-- company_scout_system.py:72 で参照されている
ALTER TABLE company_date 
ADD COLUMN industry VARCHAR(100),
ADD COLUMN company_size VARCHAR(50);
```

---

## 完全版DDL（追加部分のみ）

### user_personality_analysis テーブル作成

```sql
-- ユーザー性格分析テーブル
CREATE TABLE user_personality_analysis (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES personal_date(user_id) ON DELETE CASCADE,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_personality_analysis IS 'AIによるユーザー性格分析結果';
COMMENT ON COLUMN user_personality_analysis.analysis_data IS '性格特性、価値観、キャリア志向などのJSON';

-- インデックス
CREATE INDEX idx_user_personality_analysis_user_id ON user_personality_analysis(user_id);
CREATE INDEX idx_user_personality_analysis_updated_at ON user_personality_analysis(updated_at DESC);

-- トリガー
CREATE TRIGGER update_user_personality_analysis_updated_at
    BEFORE UPDATE ON user_personality_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### scout_messages テーブル作成

```sql
-- スカウトメッセージテーブル
CREATE TABLE scout_messages (
    id SERIAL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES company_date(company_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES company_profile(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES personal_date(user_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    auto_generated BOOLEAN NOT NULL DEFAULT false,
    status VARCHAR(20) NOT NULL DEFAULT 'sent' CHECK (
        status IN ('sent', 'read', 'replied', 'declined')
    ),
    read_at TIMESTAMP,
    replied_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE scout_messages IS '企業からユーザーへのスカウトメッセージ';
COMMENT ON COLUMN scout_messages.auto_generated IS 'AI自動生成フラグ';
COMMENT ON COLUMN scout_messages.status IS 'sent/read/replied/declined';

-- インデックス
CREATE INDEX idx_scout_messages_company_id ON scout_messages(company_id);
CREATE INDEX idx_scout_messages_job_id ON scout_messages(job_id);
CREATE INDEX idx_scout_messages_user_id ON scout_messages(user_id);
CREATE INDEX idx_scout_messages_status ON scout_messages(status);
CREATE INDEX idx_scout_messages_created_at ON scout_messages(created_at DESC);

-- 複合インデックス
CREATE INDEX idx_scout_messages_company_status ON scout_messages(company_id, status);
CREATE INDEX idx_scout_messages_user_status ON scout_messages(user_id, status);
```

### 既存テーブルへのカラム追加

```sql
-- user_profile にエンベディング追加
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS embedding VECTOR(1536);
CREATE INDEX IF NOT EXISTS idx_user_profile_embedding ON user_profile 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- job_attributes に追加カラム
ALTER TABLE job_attributes 
ADD COLUMN IF NOT EXISTS remote_work BOOLEAN,
ADD COLUMN IF NOT EXISTS flex_time BOOLEAN,
ADD COLUMN IF NOT EXISTS overtime_avg VARCHAR(20);

-- company_date に追加カラム
ALTER TABLE company_date 
ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
ADD COLUMN IF NOT EXISTS company_size VARCHAR(50);

COMMENT ON COLUMN job_attributes.remote_work IS 'リモートワーク可否';
COMMENT ON COLUMN job_attributes.flex_time IS 'フレックスタイム制度';
COMMENT ON COLUMN job_attributes.overtime_avg IS '平均残業時間（少/中/多）';
COMMENT ON COLUMN company_date.industry IS '業界';
COMMENT ON COLUMN company_date.company_size IS '企業規模（小/中/大）';
```

---

## テーブル関連図（完全版）

```
[ユーザー側]
personal_date (ユーザー基本情報)
    │
    ├─→ user_profile (希望条件) ★embedding追加
    │
    ├─→ user_interactions (行動履歴)
    │       └─→ company_profile (求人情報)
    │
    ├─→ chat_history (会話履歴)
    │
    ├─→ user_question_responses (質問への回答)
    │       └─→ dynamic_questions (質問マスタ)
    │
    ├─→ user_preferences (プロファイル)
    │
    ├─→ user_personality_analysis (性格分析) ★NEW★
    │
    └─→ scout_messages (受信したスカウト) ★NEW★

[企業側]
company_date (企業基本情報) ★industry, company_size追加
    │
    ├─→ company_profile (求人情報)
    │       │
    │       └─→ job_attributes (求人属性) ★remote_work等追加
    │
    └─→ scout_messages (送信したスカウト) ★NEW★
            │
            ├─→ job_id → company_profile
            └─→ user_id → personal_date
```

---

## データフロー（スカウト機能）

### 1. ユーザー性格分析の流れ

```
[ステップ1: データ収集]
personal_date (基本情報)
    ↓
chat_history (会話履歴) ← 最新50件
    ↓
user_question_responses (質問回答)
    ↓
user_interactions (行動データ)
    ↓
お気に入り求人の傾向分析

[ステップ2: AI分析]
GPT-4による性格分析
    ↓
- personality_traits (性格特性)
- work_values (価値観)
- career_orientation (キャリア志向)
- strengths (強み)
- preferred_work_style (働き方の好み)
等を抽出

[ステップ3: 保存]
user_personality_analysis (JSONB形式で保存)
    ↓
定期的に更新（7日以上経過した場合）
```

### 2. スカウト検索の流れ

```
[企業側の操作]
求人を選択
    ↓
スカウト検索を実行
    ↓
    
[システム側の処理]
1. 求人情報取得（company_profile）
2. 求人のエンベディング取得
3. 全ユーザーのプロファイル取得
4. ユーザーのエンベディング取得
5. 性格分析データ取得（user_personality_analysis）

[マッチング計算]
- エンベディング類似度（40%）
- 職種マッチ（30%）
- 勤務地マッチ（15%）
- 年収マッチ（15%）
    ↓
マッチスコアでソート
    ↓
上位候補者を表示

[フィルター適用]
- 性格特性フィルター
- キャリア志向フィルター
- 最低マッチスコア
    ↓
最終候補者リスト
```

### 3. スカウトメッセージ送信の流れ

```
[候補者選択]
企業がマッチした候補者を選択
    ↓
    
[メッセージ生成]
- 求人情報
- ユーザープロファイル
- ユーザー性格分析
    ↓
GPT-4でパーソナライズされたメッセージ生成
    ↓
企業が確認・編集
    ↓
    
[送信]
scout_messages テーブルに記録
    - company_id
    - job_id
    - user_id
    - message_text
    - auto_generated (true/false)
    - status ('sent')
    ↓
    
[ユーザー側]
スカウト受信通知
    ↓
メッセージ閲覧 → status = 'read', read_at更新
    ↓
返信 → status = 'replied', replied_at更新
```

---

## 統計・分析クエリ

### スカウト成功率の計算

```sql
-- 企業別のスカウト成功率
SELECT 
    cd.company_name,
    COUNT(*) as total_scouts,
    COUNT(*) FILTER (WHERE status = 'read') as read_count,
    COUNT(*) FILTER (WHERE status = 'replied') as replied_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'replied') / COUNT(*), 2) as reply_rate
FROM scout_messages sm
JOIN company_date cd ON sm.company_id = cd.company_id
GROUP BY cd.company_name
ORDER BY reply_rate DESC;
```

### 人気のある性格特性

```sql
-- 最も多く応募されている求人のユーザー性格特性
SELECT 
    trait,
    COUNT(*) as count
FROM (
    SELECT 
        jsonb_array_elements_text(upa.analysis_data->'personality_traits') as trait
    FROM user_interactions ui
    JOIN user_personality_analysis upa ON ui.user_id = upa.user_id
    WHERE ui.interaction_type = 'apply'
) subq
GROUP BY trait
ORDER BY count DESC
LIMIT 10;
```

### スカウトメッセージの効果測定

```sql
-- AI生成メッセージ vs 手動作成メッセージの効果比較
SELECT 
    auto_generated,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'replied') as replied,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'replied') / COUNT(*), 2) as reply_rate,
    AVG(EXTRACT(EPOCH FROM (replied_at - created_at)) / 3600) as avg_response_hours
FROM scout_messages
WHERE replied_at IS NOT NULL
GROUP BY auto_generated;
```

---

## まとめ

### 最終的なデータベース構成

| 項目 | 数 |
|-----|---|
| **テーブル** | **12** |
| ビュー | 3 |
| インデックス | 35+ |
| トリガー | 8 |
| CHECK制約 | 3 |
| 外部キー制約 | 15 |

### 主要な追加機能

1. **ユーザー性格分析** (`user_personality_analysis`)
   - GPT-4による自動分析
   - 定期的な再分析（7日ごと）
   - JSONB形式で柔軟なデータ構造

2. **スカウトメッセージ管理** (`scout_messages`)
   - AIによる自動メッセージ生成
   - ステータス追跡（送信/既読/返信/辞退）
   - 送信履歴管理

3. **エンベディングベースのマッチング**
   - ユーザーと求人の双方向マッチング
   - ベクトル類似度検索
   - 多軸評価との組み合わせ

### 今後の拡張可能性

- スカウトメッセージのテンプレート管理
- A/Bテストによるメッセージ最適化
- ユーザーのスカウト受信設定
- スカウト送信のレート制限
- スカウトのリマインダー機能

---

**END OF DOCUMENT**