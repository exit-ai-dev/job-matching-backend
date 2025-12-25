"""
ダミーデータ生成スクリプト（1万件）

このスクリプトは以下のデータを生成します:
- ユーザー: 1,000人
- 企業: 100社
- 求人: 1,000件
- ユーザー行動: 10,000件
- チャット履歴: 3,000件
- 質問回答: 2,000件
- 求人属性: 1,000件
- ユーザープロファイル: 500件
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import numpy as np
from werkzeug.security import generate_password_hash
import uuid

# 日本語対応
fake = Faker('ja_JP')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# データベース接続情報
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'jobmatch',
    'user': 'devuser',
    'password': 'devpass'
}


def get_db_conn():
    """データベース接続を取得"""
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# マスターデータ
# ============================================================

# 職種リスト
JOB_TITLES = [
    'Webエンジニア', 'バックエンドエンジニア', 'フロントエンドエンジニア',
    'モバイルアプリエンジニア', 'インフラエンジニア', 'データサイエンティスト',
    'データアナリスト', 'プロジェクトマネージャー', 'プロダクトマネージャー',
    'デザイナー', 'UIUXデザイナー', 'Webデザイナー',
    '営業', '企画', 'マーケティング', '人事', '経理', '法務',
    'カスタマーサポート', 'QAエンジニア', 'セキュリティエンジニア',
    'システムアーキテクト', 'DevOpsエンジニア', 'SRE',
    '機械学習エンジニア', 'AIエンジニア', 'ブロックチェーンエンジニア'
]

# 都道府県リスト
PREFECTURES = [
    '東京都', '神奈川県', '千葉県', '埼玉県', '大阪府', '京都府', '兵庫県',
    '愛知県', '福岡県', '北海道', '宮城県', '広島県', '静岡県', '茨城県',
    '栃木県', '群馬県', '長野県', '新潟県', '石川県', '富山県', '岐阜県',
    '三重県', '滋賀県', '奈良県', '和歌山県', '岡山県', '山口県', '徳島県',
    '香川県', '愛媛県', '高知県', '佐賀県', '長崎県', '熊本県', '大分県',
    '宮崎県', '鹿児島県', '沖縄県'
]

# 企業名プレフィックス/サフィックス
COMPANY_PREFIXES = ['株式会社', '有限会社', '']
COMPANY_NAMES = [
    'テックイノベーション', 'デジタルソリューションズ', 'クリエイティブワークス',
    'フューチャーシステムズ', 'スマートテクノロジー', 'グローバルネット',
    'ネクストジェネレーション', 'アドバンスドソフト', 'ダイナミックラボ',
    'インテリジェントシステム', 'ブライトフューチャー', 'サクセスパートナーズ',
    'プレミアムソリューション', 'エクセレントワークス', 'プログレッシブテック',
    'イノベーティブラボ', 'クリエイティブスタジオ', 'テクノロジーパートナー',
    'デジタルクリエイト', 'スマートイノベーション'
]

# 雇用形態
EMPLOYMENT_TYPES = ['正社員', '契約社員', '派遣社員', '業務委託', 'アルバイト・パート']

# 企業文化タイプ
COMPANY_CULTURE_TYPES = ['startup', 'venture', 'mid-size', 'large-enterprise']
ATMOSPHERES = ['flat', 'hierarchical', 'challenging', 'stable']
COMPANY_SIZES = ['small', 'medium', 'large']

# インタラクションタイプ
INTERACTION_TYPES = ['click', 'favorite', 'apply', 'view', 'chat_mention']

# メッセージテンプレート
USER_MESSAGES = [
    'リモートワークが可能な求人を探しています',
    'フレックスタイム制度のある会社を希望します',
    '年収500万円以上の求人を教えてください',
    'エンジニアの求人を探しています',
    '残業が少ない職場を希望します',
    'スタートアップで働きたいです',
    '福利厚生が充実している会社を探しています',
    'キャリアアップできる環境を求めています',
    '東京で働ける求人を教えてください',
    'データサイエンティストの求人はありますか？'
]

BOT_MESSAGES = [
    'かしこまりました。条件に合う求人を検索します。',
    'いくつか候補が見つかりました。詳細をご覧ください。',
    'もう少し条件を詳しく教えていただけますか？',
    'こちらの求人はいかがでしょうか？',
    '他にご希望の条件はありますか？'
]


# ============================================================
# データ生成関数
# ============================================================

def generate_random_embedding(dim=1536):
    """ランダムなエンベディングベクトルを生成"""
    vec = np.random.randn(dim)
    vec = vec / np.linalg.norm(vec)  # 正規化
    return vec.tolist()


def generate_personal_date(conn, num_users=1000):
    """ユーザー基本情報を生成"""
    print(f"\n📝 personal_date: {num_users}件のユーザーを生成中...")
    
    cur = conn.cursor()
    users = []
    
    for i in range(1, num_users + 1):
        email = f"user{i}@example.com"
        password_hash = generate_password_hash("password123")
        user_name = fake.name()
        birth_day = fake.date_of_birth(minimum_age=20, maximum_age=60)
        phone_number = fake.phone_number()
        address = fake.address().replace('\n', ' ')
        
        users.append((
            i,  # user_id
            email,
            password_hash,
            user_name,
            birth_day,
            phone_number,
            address
        ))
    
    execute_batch(cur, """
        INSERT INTO personal_date 
        (user_id, email, password_hash, user_name, birth_day, phone_number, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, users)
    
    conn.commit()
    print(f"✅ {len(users)}件のユーザーを作成しました")


def generate_user_profile(conn, num_users=1000):
    """ユーザープロファイルを生成"""
    print(f"\n📝 user_profile: {num_users}件のプロファイルを生成中...")
    
    cur = conn.cursor()
    profiles = []
    
    for i in range(1, num_users + 1):
        job_title = random.choice(JOB_TITLES)
        location_prefecture = random.choice(PREFECTURES)
        salary_min = random.choice([300, 400, 500, 600, 700, 800, 900, 1000])
        
        intent_labels = []
        if random.random() > 0.5:
            intent_labels.append('リモートワーク')
        if random.random() > 0.5:
            intent_labels.append('フレックスタイム')
        if random.random() > 0.7:
            intent_labels.append('副業OK')
        
        intent_label = ','.join(intent_labels) if intent_labels else None
        
        profiles.append((i, job_title, location_prefecture, salary_min, intent_label))
    
    execute_batch(cur, """
        INSERT INTO user_profile 
        (user_id, job_title, location_prefecture, salary_min, intent_label)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, profiles)
    
    conn.commit()
    print(f"✅ {len(profiles)}件のプロファイルを作成しました")


def generate_company_date(conn, num_companies=100):
    """企業マスタを生成"""
    print(f"\n📝 company_date: {num_companies}社の企業を生成中...")
    
    cur = conn.cursor()
    companies = []
    company_ids = []
    
    for i in range(1, num_companies + 1):
        company_id = str(uuid.uuid4())
        company_ids.append(company_id)
        
        prefix = random.choice(COMPANY_PREFIXES)
        name = random.choice(COMPANY_NAMES)
        company_name = f"{prefix}{name}" if prefix else name
        
        email = f"company{i}@example.com"
        password = generate_password_hash("password123")
        address = fake.address().replace('\n', ' ')
        phone_number = fake.phone_number()
        website_url = f"https://company{i}.example.com"
        
        companies.append((
            company_id,
            email,
            password,
            company_name,
            address,
            phone_number,
            website_url
        ))
    
    execute_batch(cur, """
        INSERT INTO company_date 
        (company_id, email, password, company_name, address, phone_number, website_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, companies)
    
    conn.commit()
    print(f"✅ {len(companies)}社の企業を作成しました")
    
    return company_ids


def generate_company_profile(conn, company_ids, num_jobs=1000):
    """求人情報を生成"""
    print(f"\n📝 company_profile: {num_jobs}件の求人を生成中...")
    
    cur = conn.cursor()
    jobs = []
    job_ids = []
    
    for i in range(num_jobs):
        job_id = str(uuid.uuid4())
        job_ids.append(job_id)
        
        company_id = random.choice(company_ids)
        job_title = random.choice(JOB_TITLES)
        
        # 求人概要を生成
        job_summary = f"{job_title}として、最先端の技術を用いた開発に携わっていただきます。" \
                     f"チームで協力しながら、高品質なサービスを提供します。"
        
        salary_min = random.choice([300, 400, 500, 600, 700, 800])
        salary_max = salary_min + random.choice([100, 200, 300, 400])
        location_prefecture = random.choice(PREFECTURES)
        employment_type = random.choice(EMPLOYMENT_TYPES)
        
        required_skills = f"{job_title}の実務経験3年以上"
        preferred_skills = "チームリーダー経験、英語力"
        benefits = "各種社会保険完備、交通費全額支給、リモートワーク可"
        work_hours = "9:00-18:00（フレックスタイム制）"
        holidays = "完全週休2日制（土日祝）、年間休日125日"
        
        # 応募締切（1-3ヶ月後）
        application_deadline = datetime.now() + timedelta(days=random.randint(30, 90))
        
        # ラベル生成
        labels = []
        if random.random() > 0.5:
            labels.append('リモートワーク可')
        if random.random() > 0.5:
            labels.append('フレックスタイム')
        if random.random() > 0.7:
            labels.append('残業少なめ')
        if random.random() > 0.6:
            labels.append('ボーナスあり')
        
        intent_labels = ','.join(labels) if labels else None
        
        # エンベディング生成
        embedding = generate_random_embedding()
        
        jobs.append((
            job_id,
            company_id,
            job_title,
            job_summary,
            salary_min,
            salary_max,
            location_prefecture,
            employment_type,
            required_skills,
            preferred_skills,
            benefits,
            work_hours,
            holidays,
            application_deadline,
            intent_labels,
            embedding
        ))
    
    execute_batch(cur, """
        INSERT INTO company_profile 
        (id, company_id, job_title, job_summary, salary_min, salary_max, 
         location_prefecture, employment_type, required_skills, preferred_skills,
         benefits, work_hours, holidays, application_deadline, intent_labels, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, jobs)
    
    conn.commit()
    print(f"✅ {len(jobs)}件の求人を作成しました")
    
    return job_ids


def generate_user_interactions(conn, num_users, job_ids, num_interactions=10000):
    """ユーザー行動履歴を生成"""
    print(f"\n📝 user_interactions: {num_interactions}件の行動を生成中...")
    
    cur = conn.cursor()
    interactions = []
    
    for _ in range(num_interactions):
        user_id = random.randint(1, num_users)
        job_id = random.choice(job_ids)
        interaction_type = random.choice(INTERACTION_TYPES)
        interaction_value = random.uniform(0, 60) if interaction_type == 'view' else 0.0
        
        metadata = None
        if random.random() > 0.7:
            metadata = json.dumps({
                'source': random.choice(['search', 'recommendation', 'chat']),
                'device': random.choice(['desktop', 'mobile', 'tablet'])
            })
        
        # 作成日時（過去30日以内）
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        interactions.append((
            user_id,
            job_id,
            interaction_type,
            interaction_value,
            metadata,
            created_at
        ))
    
    execute_batch(cur, """
        INSERT INTO user_interactions 
        (user_id, job_id, interaction_type, interaction_value, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, interactions)
    
    conn.commit()
    print(f"✅ {len(interactions)}件の行動を記録しました")


def generate_chat_history(conn, num_users, num_messages=3000):
    """チャット履歴を生成"""
    print(f"\n📝 chat_history: {num_messages}件のメッセージを生成中...")
    
    cur = conn.cursor()
    messages = []
    
    # セッションごとに複数メッセージを生成
    num_sessions = num_messages // 3
    
    for _ in range(num_sessions):
        user_id = random.randint(1, num_users)
        session_id = str(uuid.uuid4())
        
        # ユーザーメッセージ
        user_message = random.choice(USER_MESSAGES)
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        messages.append((
            user_id,
            'user',
            user_message,
            None,
            session_id,
            created_at
        ))
        
        # ボット応答1
        bot_message1 = random.choice(BOT_MESSAGES)
        intent = json.dumps({
            'job_title': random.choice(JOB_TITLES),
            'location': random.choice(PREFECTURES),
            'remote': random.choice([True, False])
        })
        created_at += timedelta(seconds=2)
        
        messages.append((
            user_id,
            'bot',
            bot_message1,
            intent,
            session_id,
            created_at
        ))
        
        # ボット応答2
        if random.random() > 0.5:
            bot_message2 = random.choice(BOT_MESSAGES)
            created_at += timedelta(seconds=1)
            
            messages.append((
                user_id,
                'bot',
                bot_message2,
                None,
                session_id,
                created_at
            ))
    
    execute_batch(cur, """
        INSERT INTO chat_history 
        (user_id, message_type, message_text, extracted_intent, session_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, messages)
    
    conn.commit()
    print(f"✅ {len(messages)}件のメッセージを作成しました")


def generate_user_question_responses(conn, num_users, num_responses=2000):
    """質問への回答を生成"""
    print(f"\n📝 user_question_responses: {num_responses}件の回答を生成中...")
    
    cur = conn.cursor()
    
    # 質問を取得
    cur.execute("SELECT id, question_key FROM dynamic_questions")
    questions = cur.fetchall()
    
    if not questions:
        print("⚠️  dynamic_questionsにデータがありません")
        return
    
    responses = []
    
    for _ in range(num_responses):
        user_id = random.randint(1, num_users)
        question_id, question_key = random.choice(questions)
        
        # ランダムな回答を生成
        response_texts = ['はい', 'いいえ', '重視します', '重視しません', 'どちらでも']
        response_text = random.choice(response_texts)
        
        normalized_responses = ['true', 'false', 'high', 'low', 'medium']
        normalized_response = random.choice(normalized_responses)
        
        confidence_score = random.uniform(0.7, 1.0)
        
        responses.append((
            user_id,
            question_id,
            question_key,
            response_text,
            normalized_response,
            confidence_score
        ))
    
    execute_batch(cur, """
        INSERT INTO user_question_responses 
        (user_id, question_id, question_key, response_text, normalized_response, confidence_score)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, question_id) DO NOTHING
    """, responses)
    
    conn.commit()
    print(f"✅ {len(responses)}件の回答を作成しました")


def generate_job_attributes(conn, job_ids):
    """求人属性を生成"""
    print(f"\n📝 job_attributes: {len(job_ids)}件の属性を生成中...")
    
    cur = conn.cursor()
    attributes = []
    
    for job_id in job_ids:
        # 企業文化
        company_culture = json.dumps({
            'type': random.choice(COMPANY_CULTURE_TYPES),
            'atmosphere': random.choice(ATMOSPHERES),
            'size': random.choice(COMPANY_SIZES)
        })
        
        # 働き方の柔軟性
        work_flexibility = json.dumps({
            'remote': random.choice([True, False]),
            'flex_time': random.choice([True, False]),
            'side_job': random.choice([True, False]),
            'overtime': random.choice(['low', 'medium', 'high'])
        })
        
        # キャリアパス
        career_path = json.dumps({
            'growth_opportunities': random.choice([True, False]),
            'training': random.choice([True, False]),
            'promotion_speed': random.choice(['fast', 'normal', 'slow']),
            'skill_support': random.choice([True, False])
        })
        
        attributes.append((
            job_id,
            company_culture,
            work_flexibility,
            career_path
        ))
    
    execute_batch(cur, """
        INSERT INTO job_attributes 
        (job_id, company_culture, work_flexibility, career_path)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (job_id) DO NOTHING
    """, attributes)
    
    conn.commit()
    print(f"✅ {len(attributes)}件の属性を作成しました")


def generate_user_preferences(conn, num_users, num_preferences=500):
    """ユーザープロファイルを生成"""
    print(f"\n📝 user_preferences: {num_preferences}件のプロファイルを生成中...")
    
    cur = conn.cursor()
    preferences = []
    
    for _ in range(num_preferences):
        user_id = random.randint(1, num_users)
        
        # プロファイルテキスト
        preference_text = f"希望職種: {random.choice(JOB_TITLES)}\n" \
                         f"希望勤務地: {random.choice(PREFECTURES)}\n" \
                         f"リモートワーク: {'希望する' if random.random() > 0.5 else '希望しない'}"
        
        # エンベディングベクトル
        preference_vector = str(generate_random_embedding())
        
        # カテゴリ別の好み
        company_culture_pref = json.dumps({
            'type': random.choice(COMPANY_CULTURE_TYPES),
            'atmosphere': random.choice(ATMOSPHERES)
        })
        
        work_flexibility_pref = json.dumps({
            'remote': str(random.choice([True, False])).lower(),
            'flex_time': str(random.choice([True, False])).lower()
        })
        
        career_path_pref = json.dumps({
            'growth_opportunities': str(random.choice([True, False])).lower(),
            'training': str(random.choice([True, False])).lower()
        })
        
        preferences.append((
            user_id,
            preference_vector,
            preference_text,
            company_culture_pref,
            work_flexibility_pref,
            career_path_pref
        ))
    
    execute_batch(cur, """
        INSERT INTO user_preferences 
        (user_id, preference_vector, preference_text, company_culture_pref, 
         work_flexibility_pref, career_path_pref)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, preferences)
    
    conn.commit()
    print(f"✅ {len(preferences)}件のプロファイルを作成しました")


def generate_user_personality_analysis(conn, num_users, num_analyses=300):
    """ユーザー性格分析データを生成"""
    print(f"\n📝 user_personality_analysis: {num_analyses}件の性格分析を生成中...")
    
    cur = conn.cursor()
    analyses = []
    
    # 性格特性の例
    personality_traits_options = [
        ['協調性が高い', 'コミュニケーション能力が高い', '責任感が強い'],
        ['論理的思考', '問題解決能力', '分析力が高い'],
        ['創造性豊か', '柔軟な思考', '好奇心旺盛'],
        ['リーダーシップ', '決断力', '行動力がある'],
        ['几帳面', '計画性がある', '粘り強い']
    ]
    
    work_values_options = [
        ['ワークライフバランス', '柔軟な働き方', '自由度'],
        ['成長機会', 'スキルアップ', 'チャレンジ'],
        ['安定性', '福利厚生', '長期的なキャリア'],
        ['チームワーク', '良好な人間関係', '協力体制'],
        ['高い報酬', '評価制度', 'インセンティブ']
    ]
    
    career_orientations = ['安定志向', '挑戦志向', 'バランス志向', '成長志向', '専門性志向']
    
    strengths_options = [
        ['プログラミングスキル', 'システム設計', 'データ分析'],
        ['プロジェクト管理', 'チームマネジメント', '進捗管理'],
        ['デザインセンス', 'UI/UX設計', 'クリエイティビティ'],
        ['コミュニケーション', 'プレゼン能力', '交渉力'],
        ['問題解決', '分析力', 'ロジカルシンキング']
    ]
    
    for _ in range(num_analyses):
        user_id = random.randint(1, num_users)
        
        analysis_data = json.dumps({
            'personality_traits': random.choice(personality_traits_options),
            'work_values': random.choice(work_values_options),
            'career_orientation': random.choice(career_orientations),
            'strengths': random.choice(strengths_options),
            'preferred_work_style': random.choice(['リモート重視', 'オフィス重視', '柔軟性重視']),
            'preferred_company_culture': random.choice(['チームワーク重視', '個人裁量重視', '成長重視']),
            'salary_importance': random.choice(['高', '中', '低']),
            'location_flexibility': random.choice(['高', '中', '低']),
            'risk_tolerance': random.choice(['高', '中', '低']),
            'growth_mindset': random.choice(['高', '中', '低']),
            'summary': 'このユーザーは協調性が高く、チームで働くことを好みます。安定したキャリアを求めており、ワークライフバランスを重視します。'
        }, ensure_ascii=False)
        
        analyses.append((user_id, analysis_data))
    
    execute_batch(cur, """
        INSERT INTO user_personality_analysis 
        (user_id, analysis_data)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, analyses)
    
    conn.commit()
    print(f"✅ {len(analyses)}件の性格分析を作成しました")


def generate_scout_messages(conn, company_ids, job_ids, num_users, num_messages=200):
    """スカウトメッセージを生成"""
    print(f"\n📝 scout_messages: {num_messages}件のスカウトを生成中...")
    
    cur = conn.cursor()
    messages = []
    
    message_templates = [
        "あなたの経歴とスキルを拝見し、弊社の求人にマッチすると感じご連絡いたしました。ぜひ一度カジュアル面談でお話しさせていただけませんか？",
        "現在のご経験を活かせるポジションがございます。弊社の事業内容や働き方について、まずはお気軽にお話しできればと思います。",
        "あなたの専門性が弊社のプロジェクトに最適だと考えております。詳細についてご説明させていただきたいので、ぜひご検討ください。",
        "弊社では現在、あなたのようなスキルセットを持つ方を求めております。キャリアアップのチャンスとして、ぜひご検討いただければ幸いです。"
    ]
    
    statuses = ['sent', 'read', 'replied']
    
    for _ in range(num_messages):
        company_id = random.choice(company_ids)
        job_id = random.choice(job_ids)
        user_id = random.randint(1, num_users)
        message_text = random.choice(message_templates)
        auto_generated = random.choice([True, False])
        status = random.choice(statuses)
        
        # 作成日時（過去30日以内）
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # read_at と replied_at
        read_at = None
        replied_at = None
        
        if status in ['read', 'replied']:
            read_at = created_at + timedelta(hours=random.randint(1, 48))
        
        if status == 'replied':
            replied_at = read_at + timedelta(hours=random.randint(1, 72))
        
        messages.append((
            company_id,
            job_id,
            user_id,
            message_text,
            auto_generated,
            status,
            read_at,
            replied_at,
            created_at
        ))
    
    execute_batch(cur, """
        INSERT INTO scout_messages 
        (company_id, job_id, user_id, message_text, auto_generated, status, read_at, replied_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, messages)
    
    conn.commit()
    print(f"✅ {len(messages)}件のスカウトメッセージを作成しました")


def generate_user_preferences(conn, num_users, num_preferences=500):
    """ユーザープロファイルを生成"""
    print(f"\n📝 user_preferences: {num_preferences}件のプロファイルを生成中...")
    
    cur = conn.cursor()
    preferences = []
    
    for _ in range(num_preferences):
        user_id = random.randint(1, num_users)
        
        # プロファイルテキスト
        preference_text = f"希望職種: {random.choice(JOB_TITLES)}\n" \
                         f"希望勤務地: {random.choice(PREFECTURES)}\n" \
                         f"リモートワーク: {'希望する' if random.random() > 0.5 else '希望しない'}"
        
        # エンベディングベクトル
        preference_vector = str(generate_random_embedding())
        
        # カテゴリ別の好み
        company_culture_pref = json.dumps({
            'type': random.choice(COMPANY_CULTURE_TYPES),
            'atmosphere': random.choice(ATMOSPHERES)
        })
        
        work_flexibility_pref = json.dumps({
            'remote': str(random.choice([True, False])).lower(),
            'flex_time': str(random.choice([True, False])).lower()
        })
        
        career_path_pref = json.dumps({
            'growth_opportunities': str(random.choice([True, False])).lower(),
            'training': str(random.choice([True, False])).lower()
        })
        
        preferences.append((
            user_id,
            preference_vector,
            preference_text,
            company_culture_pref,
            work_flexibility_pref,
            career_path_pref
        ))
    
    execute_batch(cur, """
        INSERT INTO user_preferences 
        (user_id, preference_vector, preference_text, company_culture_pref, 
         work_flexibility_pref, career_path_pref)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, preferences)
    
    conn.commit()
    print(f"✅ {len(preferences)}件のプロファイルを作成しました")


def update_job_counters(conn, job_ids):
    """求人のカウンターを更新（user_interactionsから集計）"""
    print(f"\n🔄 求人のカウンターを更新中...")
    
    cur = conn.cursor()
    
    for job_id in job_ids:
        cur.execute("""
            UPDATE company_profile
            SET 
                click_count = (SELECT COUNT(*) FROM user_interactions WHERE job_id = %s AND interaction_type = 'click'),
                favorite_count = (SELECT COUNT(*) FROM user_interactions WHERE job_id = %s AND interaction_type = 'favorite'),
                apply_count = (SELECT COUNT(*) FROM user_interactions WHERE job_id = %s AND interaction_type = 'apply'),
                view_count = (SELECT COUNT(*) FROM user_interactions WHERE job_id = %s AND interaction_type = 'view')
            WHERE id = %s
        """, (job_id, job_id, job_id, job_id, job_id))
    
    conn.commit()
    print(f"✅ {len(job_ids)}件の求人カウンターを更新しました")


def print_statistics(conn):
    """データ統計を表示"""
    print("\n" + "="*60)
    print("📊 データ生成完了 - 統計情報")
    print("="*60)
    
    cur = conn.cursor()
    
    tables = [
        'personal_date',
        'user_profile',
        'company_date',
        'company_profile',
        'user_interactions',
        'chat_history',
        'dynamic_questions',
        'user_question_responses',
        'job_attributes',
        'user_preferences',
        'user_personality_analysis',
        'scout_messages'
    ]
    
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table:30s}: {count:>6,}件")
    
    print("="*60)
    
    # 追加統計
    print("\n📈 追加統計:")
    
    # 職種別求人数
    cur.execute("""
        SELECT job_title, COUNT(*) as count
        FROM company_profile
        GROUP BY job_title
        ORDER BY count DESC
        LIMIT 5
    """)
    print("\n  人気職種 TOP5:")
    for row in cur.fetchall():
        print(f"    {row[0]:30s}: {row[1]:>4}件")
    
    # 都道府県別求人数
    cur.execute("""
        SELECT location_prefecture, COUNT(*) as count
        FROM company_profile
        GROUP BY location_prefecture
        ORDER BY count DESC
        LIMIT 5
    """)
    print("\n  求人数が多い都道府県 TOP5:")
    for row in cur.fetchall():
        print(f"    {row[0]:30s}: {row[1]:>4}件")
    
    # インタラクションタイプ別集計
    cur.execute("""
        SELECT interaction_type, COUNT(*) as count
        FROM user_interactions
        GROUP BY interaction_type
        ORDER BY count DESC
    """)
    print("\n  行動タイプ別集計:")
    for row in cur.fetchall():
        print(f"    {row[0]:30s}: {row[1]:>6,}件")


# ============================================================
# メイン処理
# ============================================================

def main():
    """メイン処理"""
    print("="*60)
    print("🚀 ダミーデータ生成スクリプト")
    print("="*60)
    print()
    
    try:
        # データベース接続
        print("📡 データベースに接続中...")
        conn = get_db_conn()
        print("✅ 接続成功")
        
        # データ生成
        NUM_USERS = 1000
        NUM_COMPANIES = 100
        NUM_JOBS = 1000
        NUM_INTERACTIONS = 10000
        NUM_MESSAGES = 3000
        NUM_RESPONSES = 2000
        NUM_PREFERENCES = 500
        
        # 1. ユーザー生成
        generate_personal_date(conn, NUM_USERS)
        generate_user_profile(conn, NUM_USERS)
        
        # 2. 企業・求人生成
        company_ids = generate_company_date(conn, NUM_COMPANIES)
        job_ids = generate_company_profile(conn, company_ids, NUM_JOBS)
        
        # 3. 行動履歴生成
        generate_user_interactions(conn, NUM_USERS, job_ids, NUM_INTERACTIONS)
        
        # 4. チャット履歴生成
        generate_chat_history(conn, NUM_USERS, NUM_MESSAGES)
        
        # 5. 質問回答生成
        generate_user_question_responses(conn, NUM_USERS, NUM_RESPONSES)
        
        # 6. 求人属性生成
        generate_job_attributes(conn, job_ids)
        
        # 7. ユーザープロファイル生成
        generate_user_preferences(conn, NUM_USERS, NUM_PREFERENCES)
        
        # 8. ユーザー性格分析データ生成（新規）
        generate_user_personality_analysis(conn, NUM_USERS, 300)
        
        # 9. スカウトメッセージ生成（新規）
        generate_scout_messages(conn, company_ids, job_ids, NUM_USERS, 200)
        
        # 10. 求人カウンター更新
        update_job_counters(conn, job_ids)
        
        # 統計表示
        print_statistics(conn)
        
        # 接続クローズ
        conn.close()
        
        print("\n✅ すべてのダミーデータ生成が完了しました！")
        print("\n次のステップ:")
        print("  1. データ確認: psql -d jobmatch -c 'SELECT COUNT(*) FROM personal_date;'")
        print("  2. アプリ起動: python app.py")
        print()
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()