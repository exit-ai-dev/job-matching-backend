# JobMatch AI システム - データベーススキーマ一覧

## データベース概要
- **データベース名**: jobmatch
- **DBMS**: PostgreSQL
- **拡張機能**: pgvector (ベクトル検索用)

---

## 1. ユーザー関連テーブル

### 1.1 personal_date (個人基本情報)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| user_id | SERIAL | PRIMARY KEY | ユーザーID（自動採番） |
| name | VARCHAR(100) | NOT NULL | 氏名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | メールアドレス |
| password | VARCHAR(255) | NOT NULL | パスワード（ハッシュ化） |
| age | INTEGER | | 年齢 |
| gender | VARCHAR(20) | | 性別 |
| phone | VARCHAR(20) | | 電話番号 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 1.2 user_profile (ユーザープロフィール)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | プロフィールID |
| user_id | INTEGER | FOREIGN KEY, UNIQUE | ユーザーID |
| job_title | VARCHAR(200) | | 職種 |
| years_of_experience | INTEGER | | 経験年数 |
| skills | TEXT[] | | スキル（配列） |
| education_level | VARCHAR(50) | | 学歴 |
| location_prefecture | VARCHAR(50) | | 都道府県 |
| location_city | VARCHAR(100) | | 市区町村 |
| salary_min | INTEGER | | 希望年収（下限） |
| salary_max | INTEGER | | 希望年収（上限） |
| work_style_preference | TEXT | | 働き方の希望 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 1.3 user_preferences_profile (ユーザー希望条件プロフィール)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 希望条件ID |
| user_id | INTEGER | FOREIGN KEY, UNIQUE | ユーザーID |
| job_title | VARCHAR(200) | | 希望職種 |
| location_prefecture | VARCHAR(50) | | 希望勤務地（都道府県） |
| location_city | VARCHAR(100) | | 希望勤務地（市区町村） |
| salary_min | INTEGER | | 希望年収（下限） |
| salary_max | INTEGER | | 希望年収（上限） |
| remote_work_preference | VARCHAR(50) | | リモートワーク希望 |
| employment_type | VARCHAR(50) | | 雇用形態 |
| industry_preferences | TEXT[] | | 希望業界（配列） |
| work_hours_preference | VARCHAR(100) | | 勤務時間の希望 |
| company_size_preference | VARCHAR(50) | | 希望企業規模 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 1.4 user_personality_analysis (ユーザー性格分析)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 分析ID |
| user_id | INTEGER | FOREIGN KEY, UNIQUE | ユーザーID |
| personality_traits | JSONB | | 性格特性 |
| work_values | JSONB | | 仕事の価値観 |
| communication_style | VARCHAR(50) | | コミュニケーションスタイル |
| decision_making_style | VARCHAR(50) | | 意思決定スタイル |
| analyzed_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 分析日時 |

### 1.5 user_sessions (ユーザーセッション)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| session_id | VARCHAR(255) | PRIMARY KEY | セッションID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| session_data | JSONB | | セッションデータ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |
| expires_at | TIMESTAMP | | 有効期限 |

---

## 2. 企業・求人関連テーブル

### 2.1 company_date (企業基本情報)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| company_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 企業ID |
| company_name | VARCHAR(255) | NOT NULL | 企業名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | メールアドレス |
| password | VARCHAR(255) | NOT NULL | パスワード（ハッシュ化） |
| industry | VARCHAR(100) | | 業種 |
| company_size | VARCHAR(50) | | 企業規模 |
| founded_year | INTEGER | | 設立年 |
| website_url | VARCHAR(500) | | ウェブサイトURL |
| description | TEXT | | 企業説明 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 2.2 company_profile (求人情報)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 求人ID |
| company_id | UUID | FOREIGN KEY | 企業ID |
| **Layer 1: 基本情報（必須）** |
| job_title | VARCHAR(200) | NOT NULL | 求人タイトル |
| job_description | TEXT | NOT NULL | 求人詳細 |
| location_prefecture | VARCHAR(50) | NOT NULL | 勤務地（都道府県） |
| location_city | VARCHAR(100) | | 勤務地（市区町村） |
| salary_min | INTEGER | NOT NULL | 年収（下限） |
| salary_max | INTEGER | NOT NULL | 年収（上限） |
| employment_type | VARCHAR(50) | DEFAULT '正社員' | 雇用形態 |
| **Layer 2: 構造化データ（オプション）** |
| remote_option | VARCHAR(50) | | リモートワークオプション |
| flex_time | BOOLEAN | DEFAULT FALSE | フレックスタイム |
| latest_start_time | TIME | | 最遅出社時刻 |
| side_job_allowed | BOOLEAN | DEFAULT FALSE | 副業可否 |
| team_size | VARCHAR(50) | | チーム規模 |
| development_method | VARCHAR(100) | | 開発手法 |
| tech_stack | JSONB | | 技術スタック |
| required_skills | TEXT[] | | 必須スキル（配列） |
| preferred_skills | TEXT[] | | 歓迎スキル（配列） |
| benefits | TEXT[] | | 福利厚生（配列） |
| **Layer 3: 自由記述（AI抽出対象）** |
| work_style_details | TEXT | | 働き方詳細 |
| team_culture_details | TEXT | | チーム文化詳細 |
| growth_opportunities_details | TEXT | | 成長機会詳細 |
| benefits_details | TEXT | | 福利厚生詳細 |
| office_environment_details | TEXT | | オフィス環境詳細 |
| project_details | TEXT | | プロジェクト詳細 |
| company_appeal_text | TEXT | | 企業の魅力 |
| **AI処理済みデータ** |
| ai_extracted_features | JSONB | | AI抽出特徴 |
| additional_questions | JSONB | | 追加質問 |
| embedding | VECTOR(1536) | | ベクトル埋め込み |
| **メタデータ** |
| status | VARCHAR(20) | DEFAULT 'active' | ステータス |
| view_count | INTEGER | DEFAULT 0 | 閲覧数 |
| click_count | INTEGER | DEFAULT 0 | クリック数 |
| favorite_count | INTEGER | DEFAULT 0 | お気に入り数 |
| apply_count | INTEGER | DEFAULT 0 | 応募数 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 2.3 job_attributes (求人属性)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 属性ID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| attribute_name | VARCHAR(100) | NOT NULL | 属性名 |
| attribute_value | TEXT | | 属性値 |
| attribute_type | VARCHAR(50) | | 属性タイプ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 2.4 job_additional_answers (動的質問の回答)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 回答ID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| question_text | TEXT | NOT NULL | 質問文 |
| answer_text | TEXT | | 回答文 |
| question_order | INTEGER | | 質問順序 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

---

## 3. 会話・マッチング関連テーブル

### 3.1 conversation_logs (会話ログ)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | ログID |
| session_id | VARCHAR(100) | NOT NULL | セッションID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| turn_number | INTEGER | NOT NULL | ターン番号 |
| user_message | TEXT | | ユーザーメッセージ |
| ai_response | TEXT | | AI応答 |
| extracted_intent | JSONB | | 抽出意図 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.2 conversation_sessions (会話セッション)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | セッションID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| session_id | VARCHAR(100) | NOT NULL, UNIQUE | セッション識別子 |
| total_turns | INTEGER | | 総ターン数 |
| end_reason | VARCHAR(50) | | 終了理由 |
| final_match_percentage | FLOAT | | 最終マッチ率 |
| presented_jobs | JSONB | | 提示された求人 |
| started_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 開始日時 |
| ended_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 終了日時 |

### 3.3 conversation_turns (会話ターン詳細)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | ターンID |
| user_id | INTEGER | NOT NULL | ユーザーID |
| session_id | VARCHAR(100) | NOT NULL | セッションID |
| turn_number | INTEGER | NOT NULL | ターン番号 |
| user_message | TEXT | | ユーザーメッセージ |
| bot_message | TEXT | | ボットメッセージ |
| extracted_info | JSONB | | 抽出情報 |
| top_score | FLOAT | | トップスコア |
| top_match_percentage | FLOAT | | トップマッチ率 |
| candidate_count | INTEGER | | 候補数 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.4 user_insights (ユーザー洞察蓄積)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 洞察ID |
| user_id | INTEGER | NOT NULL | ユーザーID |
| session_id | VARCHAR(100) | NOT NULL | セッションID |
| insights | JSONB | | 洞察データ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |
| | | UNIQUE(user_id, session_id) | 複合ユニーク制約 |

### 3.5 score_history (スコア履歴)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 履歴ID |
| user_id | INTEGER | NOT NULL | ユーザーID |
| session_id | VARCHAR(100) | NOT NULL | セッションID |
| turn_number | INTEGER | NOT NULL | ターン番号 |
| job_id | VARCHAR(100) | NOT NULL | 求人ID |
| score | FLOAT | | スコア |
| match_percentage | FLOAT | | マッチ率 |
| score_details | JSONB | | スコア詳細 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.6 chat_history (チャット履歴)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 履歴ID |
| user_id | INTEGER | NOT NULL | ユーザーID |
| session_id | VARCHAR(100) | NOT NULL | セッションID |
| sender | VARCHAR(10) | NOT NULL | 送信者（user/bot） |
| message | TEXT | NOT NULL | メッセージ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.7 chat_sessions (チャットセッション管理)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| session_id | VARCHAR(255) | PRIMARY KEY | セッションID |
| user_id | VARCHAR(255) | NOT NULL | ユーザーID |
| session_data | JSONB | NOT NULL | セッションデータ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

---

## 4. ユーザー行動追跡テーブル

### 4.1 user_interactions (ユーザーインタラクション)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | インタラクションID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| interaction_type | VARCHAR(50) | NOT NULL | インタラクションタイプ |
| session_id | VARCHAR(100) | | セッションID |
| interaction_data | JSONB | | インタラクションデータ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 4.2 user_interaction_summary (ビュー)
ユーザーと求人のインタラクション集計ビュー
- view_count: 閲覧数
- click_count: クリック数
- favorite_count: お気に入り数
- apply_count: 応募数
- last_interaction: 最終インタラクション日時

### 4.3 search_history (検索履歴)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 履歴ID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| search_query | TEXT | | 検索クエリ |
| filters | JSONB | | フィルター条件 |
| results_count | INTEGER | | 結果件数 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

---

## 5. エンリッチメント・トレンド関連テーブル

### 5.1 missing_job_info_log (不足情報ログ)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | ログID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| missing_field | VARCHAR(100) | NOT NULL | 不足フィールド |
| detected_from | VARCHAR(50) | | 検出元 |
| detected_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 検出日時 |

### 5.2 company_enrichment_requests (企業への追加質問リクエスト)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | リクエストID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| company_id | UUID | FOREIGN KEY | 企業ID |
| missing_field | VARCHAR(100) | NOT NULL | 不足フィールド |
| question_text | TEXT | NOT NULL | 質問文 |
| question_type | VARCHAR(50) | | 質問タイプ |
| priority_score | INTEGER | | 優先度スコア |
| detection_count | INTEGER | DEFAULT 1 | 検出回数 |
| status | VARCHAR(50) | DEFAULT 'pending' | ステータス |
| requested_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | リクエスト日時 |
| responded_at | TIMESTAMP | | 回答日時 |
| response_text | TEXT | | 回答テキスト |

### 5.3 global_preference_trends (グローバル嗜好トレンド)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | トレンドID |
| preference_key | VARCHAR(100) | NOT NULL | 嗜好キー |
| preference_value | TEXT | | 嗜好値 |
| occurrence_count | INTEGER | DEFAULT 1 | 出現回数 |
| unique_users | INTEGER | DEFAULT 1 | ユニークユーザー数 |
| last_detected | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 最終検出日時 |
| trend_score | FLOAT | | トレンドスコア |
| category | VARCHAR(50) | | カテゴリ |
| | | UNIQUE(preference_key, preference_value) | 複合ユニーク制約 |

### 5.4 trend_thresholds (トレンド閾値)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 閾値ID |
| threshold_name | VARCHAR(100) | UNIQUE, NOT NULL | 閾値名 |
| threshold_value | INTEGER | NOT NULL | 閾値 |
| description | TEXT | | 説明 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新日時 |

### 5.5 current_weekly_trends (週次トレンド)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | トレンドID |
| week_start | DATE | NOT NULL, UNIQUE | 週開始日 |
| trend_data | JSONB | NOT NULL | トレンドデータ |
| generated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 生成日時 |

---

## 6. 基本項目管理テーブル

### 6.1 baseline_job_fields (基本項目定義)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| field_id | SERIAL | PRIMARY KEY | フィールドID |
| field_name | VARCHAR(100) | UNIQUE, NOT NULL | フィールド名 |
| field_type | VARCHAR(50) | NOT NULL | フィールドタイプ |
| label | VARCHAR(200) | NOT NULL | ラベル |
| question_template | TEXT | | 質問テンプレート |
| options | JSONB | | 選択肢 |
| placeholder | TEXT | | プレースホルダー |
| required | BOOLEAN | DEFAULT FALSE | 必須フラグ |
| priority | INTEGER | DEFAULT 0 | 優先度 |
| category | VARCHAR(50) | | カテゴリ |
| promoted_at | TIMESTAMP | | 昇格日時 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

---

## 7. スカウト関連テーブル

### 7.1 scout_messages (スカウトメッセージ)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | メッセージID |
| company_id | UUID | FOREIGN KEY | 企業ID |
| job_id | UUID | FOREIGN KEY | 求人ID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| message_title | VARCHAR(255) | NOT NULL | メッセージタイトル |
| message_body | TEXT | NOT NULL | メッセージ本文 |
| match_score | FLOAT | | マッチスコア |
| match_reasons | JSONB | | マッチ理由 |
| status | VARCHAR(50) | DEFAULT 'sent' | ステータス |
| sent_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 送信日時 |
| read_at | TIMESTAMP | | 既読日時 |
| replied_at | TIMESTAMP | | 返信日時 |

---

## 8. 動的質問関連テーブル

### 8.1 dynamic_questions (動的質問定義)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 質問ID |
| question_text | TEXT | NOT NULL | 質問文 |
| question_type | VARCHAR(50) | | 質問タイプ |
| target_context | VARCHAR(100) | | 対象コンテキスト |
| options | JSONB | | 選択肢 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 8.2 user_question_responses (ユーザー回答)
| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | SERIAL | PRIMARY KEY | 回答ID |
| user_id | INTEGER | FOREIGN KEY | ユーザーID |
| question_id | INTEGER | FOREIGN KEY | 質問ID |
| response_text | TEXT | | 回答テキスト |
| response_data | JSONB | | 回答データ |
| session_id | VARCHAR(100) | | セッションID |
| answered_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 回答日時 |

---

## インデックス一覧

### パフォーマンス最適化用インデックス

#### 求人検索用
- `idx_company_profile_job_title`: job_title
- `idx_company_profile_location`: location_prefecture, location_city
- `idx_company_profile_salary`: salary_min, salary_max
- `idx_company_profile_status`: status
- `idx_company_profile_company_id`: company_id

#### ユーザー行動分析用
- `idx_user_interactions_user_job`: user_id, job_id
- `idx_user_interactions_type`: interaction_type

#### 会話ログ分析用
- `idx_conversation_logs_session`: session_id
- `idx_conversation_logs_user`: user_id
- `idx_conversation_turns_session`: user_id, session_id
- `idx_score_history_session`: user_id, session_id, turn_number

#### エンリッチメント用
- `idx_missing_job_info_job`: job_id
- `idx_missing_job_info_field`: missing_field

#### トレンド分析用
- `idx_global_trends_key`: preference_key
- `idx_global_trends_score`: trend_score DESC

#### チャットセッション用
- `idx_chat_sessions_user_id`: user_id
- `idx_chat_sessions_updated_at`: updated_at

---

## テーブル関係図（主要な関連）

```
personal_date (ユーザー)
  ├── user_profile
  ├── user_preferences_profile
  ├── user_personality_analysis
  ├── user_sessions
  ├── conversation_logs
  ├── conversation_sessions
  ├── user_interactions
  └── scout_messages

company_date (企業)
  ├── company_profile (求人)
  │   ├── job_attributes
  │   ├── job_additional_answers
  │   ├── user_interactions
  │   └── scout_messages
  └── company_enrichment_requests

conversation_sessions
  ├── conversation_logs
  ├── conversation_turns
  ├── score_history
  └── chat_history
```

---

## 初期データ

### trend_thresholds (トレンド閾値)
| threshold_name | threshold_value | description |
|---------------|-----------------|-------------|
| high_demand_threshold | 10 | 高需要と判断する最小出現回数 |
| medium_demand_threshold | 5 | 中需要と判断する最小出現回数 |
| question_generation_threshold | 3 | 動的質問を生成する最小出現回数 |

---

## 注意事項

1. **外部キー制約**: ON DELETE CASCADE/SET NULLが設定されており、親レコード削除時の動作が定義されています
2. **JSONB型**: 柔軟なデータ構造に対応するため、多くのテーブルでJSONB型を使用しています
3. **配列型**: スキルや福利厚生など、複数値を持つカラムにはTEXT[]を使用しています
4. **ベクトル型**: AI埋め込みにVECTOR(1536)型を使用（pgvector拡張が必要）
5. **タイムスタンプ**: 全テーブルにcreated_at/updated_atが設定されています
