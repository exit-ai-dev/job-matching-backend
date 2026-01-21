"""
JobMatch AI システム - ダミーデータ生成スクリプト

このスクリプトは、各テーブルにリアルなダミーデータを生成します。
使用方法:
    python generate_dummy_data.py --host localhost --database jobmatch --user postgres --password your_password
"""

import psycopg2
from psycopg2.extras import execute_values, Json
import random
from datetime import datetime, timedelta
import argparse
import uuid
from faker import Faker

# Fakerの初期化（日本語対応）
fake = Faker('ja_JP')
Faker.seed(42)
random.seed(42)


class DummyDataGenerator:
    def __init__(self, connection_params):
        """データベース接続の初期化"""
        self.conn = psycopg2.connect(**connection_params)
        self.cur = self.conn.cursor()
        print("✅ データベースに接続しました")
    
    def generate_all_data(self):
        """全てのダミーデータを生成"""
        try:
            print("\n📊 ダミーデータ生成を開始します...\n")
            
            # 1. ユーザー関連
            print("👤 ユーザーデータを生成中...")
            user_ids = self.generate_users(50)
            self.generate_user_profiles(user_ids)
            self.generate_user_preferences(user_ids)
            self.generate_user_personality_analysis(user_ids)
            
            # 2. 企業・求人関連
            print("\n🏢 企業・求人データを生成中...")
            company_ids = self.generate_companies(20)
            job_ids = self.generate_jobs(company_ids, 100)
            self.generate_job_attributes(job_ids)
            self.generate_job_additional_answers(job_ids)
            
            # 3. 会話・マッチング関連
            print("\n💬 会話データを生成中...")
            session_ids = self.generate_conversation_sessions(user_ids, 30)
            self.generate_conversation_logs(session_ids, user_ids)
            self.generate_conversation_turns(session_ids, user_ids)
            self.generate_user_insights(session_ids, user_ids)
            self.generate_score_history(session_ids, user_ids, job_ids)
            self.generate_chat_history(session_ids, user_ids)
            
            # 4. ユーザー行動追跡
            print("\n📈 ユーザー行動データを生成中...")
            self.generate_user_interactions(user_ids, job_ids, 500)
            self.generate_search_history(user_ids, 200)
            
            # 5. エンリッチメント・トレンド
            print("\n🔍 エンリッチメント・トレンドデータを生成中...")
            self.generate_missing_job_info_log(job_ids, user_ids, 100)
            self.generate_company_enrichment_requests(job_ids, company_ids, 50)
            self.generate_global_preference_trends(100)
            self.generate_current_weekly_trends(4)
            
            # 6. 基本項目管理
            print("\n⚙️ 基本項目データを生成中...")
            self.generate_baseline_job_fields()
            
            # 7. スカウト関連
            print("\n📧 スカウトメッセージを生成中...")
            self.generate_scout_messages(company_ids, job_ids, user_ids, 80)
            
            # 8. 動的質問関連
            print("\n❓ 動的質問データを生成中...")
            question_ids = self.generate_dynamic_questions(30)
            self.generate_user_question_responses(user_ids, question_ids, session_ids)
            
            # 9. チャットセッション
            print("\n💬 チャットセッションを生成中...")
            self.generate_chat_sessions(user_ids, 40)
            
            self.conn.commit()
            print("\n✅ 全てのダミーデータの生成が完了しました！")
            
        except Exception as e:
            self.conn.rollback()
            print(f"\n❌ エラーが発生しました: {e}")
            raise
    
    # ====================================
    # 1. ユーザー関連データ生成
    # ====================================
    
    def generate_users(self, count=50):
        """ユーザー基本情報を生成"""
        users = []
        for i in range(count):
            users.append((
                fake.name(),
                fake.email(),
                fake.password(length=12),  # 実際はハッシュ化が必要
                random.randint(22, 60),
                random.choice(['男性', '女性', 'その他', None]),
                fake.phone_number() if random.random() > 0.3 else None,
            ))
        
        query = """
        INSERT INTO personal_date (name, email, password, age, gender, phone)
        VALUES %s
        RETURNING user_id
        """
        user_ids = []
        execute_values(self.cur, query, users, fetch=True)
        user_ids = [row[0] for row in self.cur.fetchall()]
        print(f"  ✓ {len(user_ids)}件のユーザーを作成")
        return user_ids
    
    def generate_user_profiles(self, user_ids):
        """ユーザープロフィールを生成"""
        job_titles = ['ソフトウェアエンジニア', 'プロダクトマネージャー', 'データサイエンティスト', 
                     'UIデザイナー', 'マーケティング', '営業', 'コンサルタント']
        skills = ['Python', 'Java', 'JavaScript', 'React', 'AWS', 'Docker', 'SQL', 
                 'プロジェクト管理', 'データ分析', 'UI/UX', 'マーケティング戦略']
        
        profiles = []
        for user_id in user_ids:
            num_skills = random.randint(3, 7)
            user_skills = random.sample(skills, num_skills)
            
            profiles.append((
                user_id,
                random.choice(job_titles),
                random.randint(1, 15),
                user_skills,
                random.choice(['学士', '修士', '博士', '高卒']),
                fake.prefecture(),
                fake.city(),
                random.randint(300, 600) * 10000,
                random.randint(400, 1000) * 10000,
                random.choice(['フルリモート希望', 'ハイブリッド', '出社メイン', 'フレックス希望']),
            ))
        
        query = """
        INSERT INTO user_profile 
        (user_id, job_title, years_of_experience, skills, education_level, 
         location_prefecture, location_city, salary_min, salary_max, work_style_preference)
        VALUES %s
        """
        execute_values(self.cur, query, profiles)
        print(f"  ✓ {len(profiles)}件のプロフィールを作成")
    
    def generate_user_preferences(self, user_ids):
        """ユーザー希望条件を生成"""
        preferences = []
        industries = ['IT', '金融', 'コンサルティング', '製造業', 'ヘルスケア', '教育', 'エンターテイメント']
        
        for user_id in user_ids:
            num_industries = random.randint(1, 3)
            
            preferences.append((
                user_id,
                random.choice(['エンジニア', 'マネージャー', 'デザイナー', 'コンサルタント']),
                fake.prefecture(),
                fake.city() if random.random() > 0.3 else None,
                random.randint(400, 600) * 10000,
                random.randint(600, 1200) * 10000,
                random.choice(['完全リモート', '週2-3日', '月数回', 'オフィス勤務']),
                random.choice(['正社員', '契約社員', '業務委託']),
                random.sample(industries, num_industries),
                random.choice(['9-18時', 'フレックス', '裁量労働', 'シフト制']),
                random.choice(['スタートアップ', '中小企業', '大企業', '外資系']),
            ))
        
        query = """
        INSERT INTO user_preferences_profile 
        (user_id, job_title, location_prefecture, location_city, salary_min, salary_max,
         remote_work_preference, employment_type, industry_preferences, 
         work_hours_preference, company_size_preference)
        VALUES %s
        """
        execute_values(self.cur, query, preferences)
        print(f"  ✓ {len(preferences)}件の希望条件を作成")
    
    def generate_user_personality_analysis(self, user_ids):
        """ユーザー性格分析を生成"""
        analyses = []
        for user_id in random.sample(user_ids, len(user_ids) // 2):  # 半数のユーザーのみ
            personality_traits = {
                "外向性": random.randint(1, 10),
                "協調性": random.randint(1, 10),
                "誠実性": random.randint(1, 10),
                "神経症傾向": random.randint(1, 10),
                "開放性": random.randint(1, 10)
            }
            
            work_values = {
                "成長志向": random.randint(1, 10),
                "ワークライフバランス": random.randint(1, 10),
                "報酬重視": random.randint(1, 10),
                "社会貢献": random.randint(1, 10),
                "安定志向": random.randint(1, 10)
            }
            
            analyses.append((
                user_id,
                Json(personality_traits),
                Json(work_values),
                random.choice(['積極的', '控えめ', 'バランス型']),
                random.choice(['論理的', '直感的', '協調型']),
            ))
        
        query = """
        INSERT INTO user_personality_analysis 
        (user_id, personality_traits, work_values, communication_style, decision_making_style)
        VALUES %s
        """
        execute_values(self.cur, query, analyses)
        print(f"  ✓ {len(analyses)}件の性格分析を作成")
    
    # ====================================
    # 2. 企業・求人関連データ生成
    # ====================================
    
    def generate_companies(self, count=20):
        """企業基本情報を生成"""
        companies = []
        industries = ['IT・ソフトウェア', '金融', 'コンサルティング', '製造業', 
                     'ヘルスケア', 'EC・小売', '教育', 'エンターテイメント']
        
        for i in range(count):
            companies.append((
                fake.company(),
                fake.company_email(),
                fake.password(length=12),
                random.choice(industries),
                random.choice(['1-10名', '11-50名', '51-200名', '201-500名', '501名以上']),
                random.randint(1990, 2020),
                fake.url(),
                fake.catch_phrase() + '。' + fake.text(max_nb_chars=200),
            ))
        
        query = """
        INSERT INTO company_date 
        (company_name, email, password, industry, company_size, founded_year, website_url, description)
        VALUES %s
        RETURNING company_id
        """
        execute_values(self.cur, query, companies, fetch=True)
        company_ids = [row[0] for row in self.cur.fetchall()]
        print(f"  ✓ {len(company_ids)}件の企業を作成")
        return company_ids
    
    def generate_jobs(self, company_ids, count=100):
        """求人情報を生成"""
        job_titles = [
            'バックエンドエンジニア', 'フロントエンドエンジニア', 'データサイエンティスト',
            'プロダクトマネージャー', 'UIUXデザイナー', 'DevOpsエンジニア',
            'マーケティングマネージャー', 'セールスマネージャー', '人事マネージャー'
        ]
        
        tech_stacks = [
            {"backend": ["Python", "Django"], "frontend": ["React", "TypeScript"], "infra": ["AWS", "Docker"]},
            {"backend": ["Java", "Spring"], "frontend": ["Vue.js"], "infra": ["GCP", "Kubernetes"]},
            {"backend": ["Node.js", "Express"], "frontend": ["Next.js"], "infra": ["Azure", "CI/CD"]},
        ]
        
        jobs = []
        for i in range(count):
            company_id = random.choice(company_ids)
            
            jobs.append((
                company_id,
                # Layer 1: 基本情報
                random.choice(job_titles),
                fake.text(max_nb_chars=500),
                fake.prefecture(),
                fake.city(),
                random.randint(400, 600) * 10000,
                random.randint(600, 1200) * 10000,
                random.choice(['正社員', '契約社員', '業務委託']),
                # Layer 2: 構造化データ
                random.choice(['完全リモート', '週2-3日出社', '出社メイン', 'ハイブリッド']),
                random.choice([True, False]),
                f"{random.randint(9, 11)}:00:00" if random.random() > 0.5 else None,
                random.choice([True, False]),
                random.choice(['3-5名', '6-10名', '11-20名', '21名以上']),
                random.choice(['アジャイル', 'ウォーターフォール', 'スクラム', 'カンバン']),
                Json(random.choice(tech_stacks)),
                random.sample(['Python', 'JavaScript', 'SQL', 'AWS', 'Docker'], k=random.randint(2, 4)),
                random.sample(['機械学習', 'CI/CD', 'マイクロサービス', 'TDD'], k=random.randint(1, 3)),
                random.sample(['フレックスタイム', '社員食堂', '書籍購入補助', 'リモート手当'], k=random.randint(2, 4)),
                # Layer 3: 自由記述
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                fake.text(max_nb_chars=300) if random.random() > 0.3 else None,
                # AI処理済みデータ
                Json({"keywords": random.sample(['成長', 'イノベーション', 'グローバル'], k=2)}),
                Json([{"question": "プロジェクトの規模は？", "type": "text"}]) if random.random() > 0.5 else None,
                # メタデータ
                random.choice(['active', 'draft', 'closed']),
                random.randint(0, 1000),
                random.randint(0, 300),
                random.randint(0, 100),
                random.randint(0, 50),
            ))
        
        query = """
        INSERT INTO company_profile 
        (company_id, job_title, job_description, location_prefecture, location_city,
         salary_min, salary_max, employment_type, remote_option, flex_time,
         latest_start_time, side_job_allowed, team_size, development_method,
         tech_stack, required_skills, preferred_skills, benefits,
         work_style_details, team_culture_details, growth_opportunities_details,
         benefits_details, office_environment_details, project_details,
         company_appeal_text, ai_extracted_features, additional_questions,
         status, view_count, click_count, favorite_count, apply_count)
        VALUES %s
        RETURNING id
        """
        execute_values(self.cur, query, jobs, fetch=True)
        job_ids = [row[0] for row in self.cur.fetchall()]
        print(f"  ✓ {len(job_ids)}件の求人を作成")
        return job_ids
    
    def generate_job_attributes(self, job_ids):
        """求人属性を生成"""
        attributes = []
        attribute_names = ['certification', 'language', 'tool', 'framework']
        
        for job_id in random.sample(job_ids, len(job_ids) // 2):
            for _ in range(random.randint(1, 3)):
                attributes.append((
                    job_id,
                    random.choice(attribute_names),
                    fake.word(),
                    random.choice(['required', 'preferred', 'optional']),
                ))
        
        query = """
        INSERT INTO job_attributes (job_id, attribute_name, attribute_value, attribute_type)
        VALUES %s
        """
        execute_values(self.cur, query, attributes)
        print(f"  ✓ {len(attributes)}件の求人属性を作成")
    
    def generate_job_additional_answers(self, job_ids):
        """動的質問の回答を生成"""
        answers = []
        questions = [
            "チームの平均年齢は？",
            "リモートワークの頻度は？",
            "評価制度について教えてください",
            "キャリアパスはどうなっていますか？"
        ]
        
        for job_id in random.sample(job_ids, len(job_ids) // 3):
            for i, question in enumerate(random.sample(questions, k=random.randint(1, 3))):
                answers.append((
                    job_id,
                    question,
                    fake.text(max_nb_chars=200),
                    i + 1,
                ))
        
        query = """
        INSERT INTO job_additional_answers (job_id, question_text, answer_text, question_order)
        VALUES %s
        """
        execute_values(self.cur, query, answers)
        print(f"  ✓ {len(answers)}件の追加回答を作成")
    
    # ====================================
    # 3. 会話・マッチング関連データ生成
    # ====================================
    
    def generate_conversation_sessions(self, user_ids, count=30):
        """会話セッションを生成"""
        sessions = []
        session_ids = []
        
        for _ in range(count):
            session_id = str(uuid.uuid4())
            session_ids.append(session_id)
            sessions.append((
                random.choice(user_ids),
                session_id,
                random.randint(3, 15),
                random.choice(['completed', 'abandoned', 'ongoing']),
                random.uniform(60.0, 95.0),
                Json([str(uuid.uuid4()) for _ in range(random.randint(1, 5))]),
                datetime.now() - timedelta(days=random.randint(1, 30)),
                datetime.now() - timedelta(hours=random.randint(1, 24)),
            ))
        
        query = """
        INSERT INTO conversation_sessions 
        (user_id, session_id, total_turns, end_reason, final_match_percentage, 
         presented_jobs, started_at, ended_at)
        VALUES %s
        """
        execute_values(self.cur, query, sessions)
        print(f"  ✓ {len(sessions)}件の会話セッションを作成")
        return session_ids
    
    def generate_conversation_logs(self, session_ids, user_ids):
        """会話ログを生成"""
        logs = []
        messages = [
            "エンジニアの仕事を探しています",
            "リモートワークできる企業がいいです",
            "年収は600万円以上希望です",
            "成長できる環境を探しています"
        ]
        
        for session_id in session_ids:
            user_id = random.choice(user_ids)
            for turn in range(random.randint(3, 10)):
                logs.append((
                    session_id,
                    user_id,
                    turn + 1,
                    random.choice(messages),
                    fake.text(max_nb_chars=200),
                    Json({"intent": "job_search", "entities": {"job_type": "engineer"}}),
                ))
        
        query = """
        INSERT INTO conversation_logs 
        (session_id, user_id, turn_number, user_message, ai_response, extracted_intent)
        VALUES %s
        """
        execute_values(self.cur, query, logs)
        print(f"  ✓ {len(logs)}件の会話ログを作成")
    
    def generate_conversation_turns(self, session_ids, user_ids):
        """会話ターン詳細を生成"""
        turns = []
        
        for session_id in session_ids:
            user_id = random.choice(user_ids)
            for turn_num in range(random.randint(3, 8)):
                turns.append((
                    user_id,
                    session_id,
                    turn_num + 1,
                    fake.text(max_nb_chars=100),
                    fake.text(max_nb_chars=150),
                    Json({"skills": ["Python", "AWS"], "location": "東京都"}),
                    random.uniform(70.0, 95.0),
                    random.uniform(75.0, 98.0),
                    random.randint(5, 20),
                ))
        
        query = """
        INSERT INTO conversation_turns 
        (user_id, session_id, turn_number, user_message, bot_message, 
         extracted_info, top_score, top_match_percentage, candidate_count)
        VALUES %s
        """
        execute_values(self.cur, query, turns)
        print(f"  ✓ {len(turns)}件の会話ターンを作成")
    
    def generate_user_insights(self, session_ids, user_ids):
        """ユーザー洞察を生成"""
        insights = []
        
        for session_id in random.sample(session_ids, len(session_ids) // 2):
            user_id = random.choice(user_ids)
            insight_data = {
                "preferences": {
                    "remote_work": "重視",
                    "salary": "やや重視",
                    "growth": "非常に重視"
                },
                "concerns": ["ワークライフバランス", "キャリアパス"],
                "strengths": ["技術力", "コミュニケーション能力"]
            }
            
            insights.append((
                user_id,
                session_id,
                Json(insight_data),
            ))
        
        query = """
        INSERT INTO user_insights (user_id, session_id, insights)
        VALUES %s
        """
        execute_values(self.cur, query, insights)
        print(f"  ✓ {len(insights)}件のユーザー洞察を作成")
    
    def generate_score_history(self, session_ids, user_ids, job_ids):
        """スコア履歴を生成"""
        scores = []
        
        for session_id in session_ids:
            user_id = random.choice(user_ids)
            for turn_num in range(random.randint(3, 8)):
                for _ in range(random.randint(3, 7)):
                    job_id = str(random.choice(job_ids))
                    score = random.uniform(60.0, 98.0)
                    scores.append((
                        user_id,
                        session_id,
                        turn_num + 1,
                        job_id,
                        score,
                        score * 1.02,  # match_percentage
                        Json({
                            "skill_match": random.uniform(70, 100),
                            "location_match": random.uniform(80, 100),
                            "salary_match": random.uniform(60, 100)
                        }),
                    ))
        
        query = """
        INSERT INTO score_history 
        (user_id, session_id, turn_number, job_id, score, match_percentage, score_details)
        VALUES %s
        """
        execute_values(self.cur, query, scores)
        print(f"  ✓ {len(scores)}件のスコア履歴を作成")
    
    def generate_chat_history(self, session_ids, user_ids):
        """チャット履歴を生成"""
        chats = []
        
        for session_id in session_ids:
            user_id = random.choice(user_ids)
            for _ in range(random.randint(5, 15)):
                sender = random.choice(['user', 'bot'])
                chats.append((
                    user_id,
                    session_id,
                    sender,
                    fake.text(max_nb_chars=150),
                ))
        
        query = """
        INSERT INTO chat_history (user_id, session_id, sender, message)
        VALUES %s
        """
        execute_values(self.cur, query, chats)
        print(f"  ✓ {len(chats)}件のチャット履歴を作成")
    
    # ====================================
    # 4. ユーザー行動追跡データ生成
    # ====================================
    
    def generate_user_interactions(self, user_ids, job_ids, count=500):
        """ユーザーインタラクションを生成"""
        interactions = []
        interaction_types = ['view', 'click', 'favorite', 'apply']
        
        for _ in range(count):
            interaction_type = random.choice(interaction_types)
            interactions.append((
                random.choice(user_ids),
                random.choice(job_ids),
                interaction_type,
                str(uuid.uuid4()),
                Json({"duration": random.randint(10, 300), "device": random.choice(["PC", "Mobile"])}),
            ))
        
        query = """
        INSERT INTO user_interactions 
        (user_id, job_id, interaction_type, session_id, interaction_data)
        VALUES %s
        """
        execute_values(self.cur, query, interactions)
        print(f"  ✓ {len(interactions)}件のインタラクションを作成")
    
    def generate_search_history(self, user_ids, count=200):
        """検索履歴を生成"""
        searches = []
        queries = ["エンジニア 東京", "リモート 開発", "Python データサイエンス", "マネージャー 大阪"]
        
        for _ in range(count):
            searches.append((
                random.choice(user_ids),
                random.choice(queries),
                Json({
                    "location": random.choice(["東京都", "大阪府", "福岡県"]),
                    "salary_min": random.randint(400, 600) * 10000,
                    "remote": random.choice([True, False])
                }),
                random.randint(5, 50),
            ))
        
        query = """
        INSERT INTO search_history (user_id, search_query, filters, results_count)
        VALUES %s
        """
        execute_values(self.cur, query, searches)
        print(f"  ✓ {len(searches)}件の検索履歴を作成")
    
    # ====================================
    # 5. エンリッチメント・トレンドデータ生成
    # ====================================
    
    def generate_missing_job_info_log(self, job_ids, user_ids, count=100):
        """不足情報ログを生成"""
        logs = []
        missing_fields = ['remote_option', 'benefits', 'team_culture', 'growth_opportunities']
        
        for _ in range(count):
            logs.append((
                random.choice(job_ids),
                random.choice(user_ids) if random.random() > 0.5 else None,
                random.choice(missing_fields),
                random.choice(['conversation', 'search', 'profile']),
            ))
        
        query = """
        INSERT INTO missing_job_info_log (job_id, user_id, missing_field, detected_from)
        VALUES %s
        """
        execute_values(self.cur, query, logs)
        print(f"  ✓ {len(logs)}件の不足情報ログを作成")
    
    def generate_company_enrichment_requests(self, job_ids, company_ids, count=50):
        """企業への追加質問リクエストを生成"""
        requests = []
        
        for _ in range(count):
            job_id = random.choice(job_ids)
            # job_idから対応するcompany_idを取得する必要があるが、簡略化のためランダムに選択
            requests.append((
                job_id,
                random.choice(company_ids),
                random.choice(['remote_option', 'team_culture', 'benefits']),
                fake.text(max_nb_chars=100),
                random.choice(['single_select', 'multi_select', 'text']),
                random.randint(1, 10),
                random.randint(1, 20),
                random.choice(['pending', 'responded', 'declined']),
            ))
        
        query = """
        INSERT INTO company_enrichment_requests 
        (job_id, company_id, missing_field, question_text, question_type, 
         priority_score, detection_count, status)
        VALUES %s
        """
        execute_values(self.cur, query, requests)
        print(f"  ✓ {len(requests)}件のエンリッチメントリクエストを作成")
    
    def generate_global_preference_trends(self, count=100):
        """グローバル嗜好トレンドを生成"""
        trends = []
        preference_keys = ['remote_work', 'flex_time', 'side_job', 'growth_opportunity', 
                          'work_life_balance', 'tech_stack', 'team_size']
        
        for _ in range(count):
            key = random.choice(preference_keys)
            value = fake.word()
            trends.append((
                key,
                value,
                random.randint(1, 50),
                random.randint(1, 30),
                random.uniform(0.5, 10.0),
                random.choice(['work_style', 'benefits', 'tech', 'culture']),
            ))
        
        query = """
        INSERT INTO global_preference_trends 
        (preference_key, preference_value, occurrence_count, unique_users, trend_score, category)
        VALUES %s
        ON CONFLICT (preference_key, preference_value) DO NOTHING
        """
        execute_values(self.cur, query, trends)
        print(f"  ✓ グローバル嗜好トレンドを作成")
    
    def generate_current_weekly_trends(self, weeks=4):
        """週次トレンドを生成"""
        trends = []
        
        for i in range(weeks):
            week_start = datetime.now().date() - timedelta(weeks=i)
            trend_data = {
                "top_preferences": [
                    {"key": "remote_work", "value": "完全リモート", "count": random.randint(20, 50)},
                    {"key": "flex_time", "value": "フレックス", "count": random.randint(15, 40)},
                ],
                "emerging_trends": [
                    {"key": "side_job", "value": "副業可", "growth_rate": random.uniform(1.2, 2.0)}
                ]
            }
            trends.append((
                week_start,
                Json(trend_data),
            ))
        
        query = """
        INSERT INTO current_weekly_trends (week_start, trend_data)
        VALUES %s
        ON CONFLICT (week_start) DO NOTHING
        """
        execute_values(self.cur, query, trends)
        print(f"  ✓ {len(trends)}週分の週次トレンドを作成")
    
    # ====================================
    # 6. 基本項目管理データ生成
    # ====================================
    
    def generate_baseline_job_fields(self):
        """基本項目定義を生成"""
        fields = [
            ('job_title', 'text', '職種', None, None, '例: ソフトウェアエンジニア', True, 10, 'basic'),
            ('location', 'text', '勤務地', None, None, '例: 東京都渋谷区', True, 9, 'basic'),
            ('salary_range', 'range', '年収', None, None, None, True, 8, 'basic'),
            ('remote_option', 'select', 'リモートワーク', None, 
             Json(['完全リモート', '週2-3日', '出社メイン']), None, False, 7, 'work_style'),
            ('flex_time', 'boolean', 'フレックスタイム', None, None, None, False, 6, 'work_style'),
            ('tech_stack', 'multi_select', '技術スタック', None, 
             Json(['Python', 'Java', 'JavaScript', 'Go', 'Ruby']), None, False, 5, 'tech'),
        ]
        
        query = """
        INSERT INTO baseline_job_fields 
        (field_name, field_type, label, question_template, options, placeholder, 
         required, priority, category)
        VALUES %s
        ON CONFLICT (field_name) DO NOTHING
        """
        execute_values(self.cur, query, fields)
        print(f"  ✓ {len(fields)}件の基本項目定義を作成")
    
    # ====================================
    # 7. スカウト関連データ生成
    # ====================================
    
    def generate_scout_messages(self, company_ids, job_ids, user_ids, count=80):
        """スカウトメッセージを生成"""
        messages = []
        
        for _ in range(count):
            match_score = random.uniform(70.0, 98.0)
            messages.append((
                random.choice(company_ids),
                random.choice(job_ids),
                random.choice(user_ids),
                fake.catch_phrase(),
                fake.text(max_nb_chars=300),
                match_score,
                Json({
                    "skill_match": random.uniform(70, 100),
                    "experience_match": random.uniform(60, 100),
                    "culture_match": random.uniform(70, 95)
                }),
                random.choice(['sent', 'read', 'replied']),
                datetime.now() - timedelta(days=random.randint(1, 30)),
                datetime.now() - timedelta(days=random.randint(0, 20)) if random.random() > 0.3 else None,
                datetime.now() - timedelta(days=random.randint(0, 15)) if random.random() > 0.5 else None,
            ))
        
        query = """
        INSERT INTO scout_messages 
        (company_id, job_id, user_id, message_title, message_body, match_score,
         match_reasons, status, sent_at, read_at, replied_at)
        VALUES %s
        """
        execute_values(self.cur, query, messages)
        print(f"  ✓ {len(messages)}件のスカウトメッセージを作成")
    
    # ====================================
    # 8. 動的質問関連データ生成
    # ====================================
    
    def generate_dynamic_questions(self, count=30):
        """動的質問定義を生成"""
        questions = []
        question_texts = [
            "リモートワークの頻度について教えてください",
            "チームの雰囲気はどうですか？",
            "技術的な成長機会はありますか？",
            "評価制度について教えてください",
            "ワークライフバランスはどうですか？"
        ]
        
        for text in question_texts[:count]:
            questions.append((
                text,
                random.choice(['single_select', 'multi_select', 'text', 'rating']),
                random.choice(['job_search', 'profile', 'matching']),
                Json(['選択肢1', '選択肢2', '選択肢3']) if random.random() > 0.5 else None,
            ))
        
        query = """
        INSERT INTO dynamic_questions (question_text, question_type, target_context, options)
        VALUES %s
        RETURNING id
        """
        execute_values(self.cur, query, questions, fetch=True)
        question_ids = [row[0] for row in self.cur.fetchall()]
        print(f"  ✓ {len(question_ids)}件の動的質問を作成")
        return question_ids
    
    def generate_user_question_responses(self, user_ids, question_ids, session_ids):
        """ユーザー回答を生成"""
        responses = []
        
        for user_id in random.sample(user_ids, len(user_ids) // 2):
            for question_id in random.sample(question_ids, random.randint(1, 5)):
                responses.append((
                    user_id,
                    question_id,
                    fake.text(max_nb_chars=100),
                    Json({"rating": random.randint(1, 5)}),
                    random.choice(session_ids),
                ))
        
        query = """
        INSERT INTO user_question_responses 
        (user_id, question_id, response_text, response_data, session_id)
        VALUES %s
        """
        execute_values(self.cur, query, responses)
        print(f"  ✓ {len(responses)}件のユーザー回答を作成")
    
    # ====================================
    # 9. チャットセッションデータ生成
    # ====================================
    
    def generate_chat_sessions(self, user_ids, count=40):
        """チャットセッションを生成"""
        sessions = []
        
        for _ in range(count):
            session_data = {
                "messages": [
                    {"sender": "user", "message": "こんにちは"},
                    {"sender": "bot", "message": "いらっしゃいませ！"}
                ],
                "context": {"current_step": random.randint(1, 5)}
            }
            
            sessions.append((
                str(uuid.uuid4()),
                str(random.choice(user_ids)),
                Json(session_data),
                datetime.now() - timedelta(days=random.randint(1, 30)),
            ))
        
        query = """
        INSERT INTO chat_sessions (session_id, user_id, session_data, updated_at)
        VALUES %s
        """
        execute_values(self.cur, query, sessions)
        print(f"  ✓ {len(sessions)}件のチャットセッションを作成")
    
    def close(self):
        """データベース接続をクローズ"""
        self.cur.close()
        self.conn.close()
        print("\n✅ データベース接続をクローズしました")


def main():
    parser = argparse.ArgumentParser(description='JobMatch AI システムのダミーデータ生成')
    parser.add_argument('--host', default='localhost', help='データベースホスト')
    parser.add_argument('--database', default='jobmatch', help='データベース名')
    parser.add_argument('--user', default='postgres', help='データベースユーザー')
    parser.add_argument('--password', required=True, help='データベースパスワード')
    parser.add_argument('--port', default='5432', help='データベースポート')
    
    args = parser.parse_args()
    
    connection_params = {
        'host': args.host,
        'database': args.database,
        'user': args.user,
        'password': args.password,
        'port': args.port
    }
    
    print("=" * 60)
    print("JobMatch AI システム - ダミーデータ生成スクリプト")
    print("=" * 60)
    
    try:
        generator = DummyDataGenerator(connection_params)
        generator.generate_all_data()
        generator.close()
        
        print("\n" + "=" * 60)
        print("🎉 全ての処理が正常に完了しました！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
