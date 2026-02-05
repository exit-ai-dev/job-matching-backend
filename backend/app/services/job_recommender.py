"""
求人推薦サービス
Iizumiロジック移植版（テーブルマッピング適用）
"""

from typing import List, Dict, Any, Tuple
from app.config.database import get_db_conn
from app.models.chat_models import JobRecommendation


class JobRecommender:
    """求人推薦ロジック"""

    @staticmethod
    def should_show_jobs(
        turn_count: int,
        current_score: float,
        user_message: str,
        score_history: List[float] = None
    ) -> tuple[bool, str]:
        # トリガー1: スコアが80%以上
        if current_score >= 80.0:
            return True, "match_score_high"

        # トリガー2: ユーザーが明示的にリクエスト
        request_keywords = [
            '求人', '案件', '仕事', '見せて', '教えて', '出して',
            '紹介', 'おすすめ', '探して', '検索', '提案'
        ]
        if any(keyword in user_message for keyword in request_keywords):
            return True, "user_request"

        # トリガー3: 10ターン経過
        if turn_count >= 10:
            return True, "turn_limit"

        # トリガー4: スコア停滞
        if score_history and len(score_history) >= 4:
            recent_scores = score_history[-4:]
            if max(recent_scores) - min(recent_scores) <= 5.0 and turn_count >= 5:
                return True, "score_stagnant"

        return False, "continue_chat"

    @staticmethod
    def get_recommendations(
        user_preferences: Dict[str, Any],
        conversation_keywords: List[str],
        limit: int = 5
    ) -> List[JobRecommendation]:
        """
        求人を推薦（0件なら条件を緩めて必ず返す）

        テーブルマッピング:
        - Iizumi company_profile → 現リポジトリ jobs
        - job_title → title
        - location_prefecture → location
        - status = 'active' → status = 'published'
        - remote_option → remote (boolean)
        - company_date.company_name → jobs.company
        """

        conn = get_db_conn()
        from psycopg2.extras import RealDictCursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            job_title = (user_preferences.get('job_title') or '').strip()
            location = (user_preferences.get('location') or '').strip()
            salary_min = user_preferences.get('salary_min') or 0

            # salary_min の単位補正（万円が入ってくる可能性があるため）
            # 例: 400(万円) -> 4,000,000(円)
            if isinstance(salary_min, (int, float)) and 0 < salary_min < 100000:  # 10万未満なら「万円」っぽい
                salary_min = int(salary_min * 10000)

            # --- 段階的に条件を緩める検索プラン ---
            # (title, location, salary) の順で緩める
            search_plans: List[Tuple[bool, bool, bool, str]] = [
                (True, True, True,  "strict"),           # 全条件
                (True, False, True, "no_location"),      # 場所なし
                (True, False, False,"no_loc_no_salary"), # 場所なし + 年収なし
                (False, False, False,"latest_active"),   # 何もなし（active新着）
            ]

            jobs: List[Dict[str, Any]] = []

            for use_title, use_location, use_salary, plan_name in search_plans:
                # テーブル: jobs（Iizumiではcompany_profile）
                # カラムマッピング: job_title→title, location_prefecture→location
                # status: 'active'→'published'
                query = """
                    SELECT
                        j.id as job_id,
                        j.title as job_title,
                        j.company as company_name,
                        j.salary_min,
                        j.salary_max,
                        j.location,
                        j.remote,
                        j.description,
                        j.required_skills,
                        j.status,
                        j.employer_id
                    FROM jobs j
                    WHERE j.status::text = 'published'
                """
                params: List[Any] = []

                if use_title and job_title:
                    query += " AND j.title ILIKE %s"
                    params.append(f"%{job_title}%")

                if use_location and location:
                    query += " AND j.location ILIKE %s"
                    params.append(f"%{location}%")

                if use_salary and salary_min and salary_min > 0:
                    query += " AND j.salary_max >= %s"
                    params.append(int(salary_min))

                query += f" ORDER BY j.created_at DESC LIMIT {limit * 5}"

                print(f"[JobRecommender] Search plan={plan_name}")
                print(f"[JobRecommender] Query: {query}")
                print(f"[JobRecommender] Params: {params}")

                cur.execute(query, params)
                jobs = cur.fetchall()
                print(f"[JobRecommender] Found jobs: {len(jobs)}")

                if jobs:
                    break

            if not jobs:
                return []

            # スコアリングして上位だけ返す
            scored_jobs = []
            for job in jobs:
                score = JobRecommender._calculate_job_score(
                    job,
                    user_preferences,
                    conversation_keywords
                )
                scored_jobs.append({'job': job, 'score': score})

            scored_jobs.sort(key=lambda x: x['score'], reverse=True)

            recommendations: List[JobRecommendation] = []
            for item in scored_jobs[:limit]:
                job = item['job']
                score = item['score']

                # remote: boolean → string変換
                remote_option = "リモート可" if job.get('remote', False) else "出社"

                recommendations.append(JobRecommendation(
                    job_id=str(job['job_id']),
                    job_title=job.get('job_title', ''),
                    company_name=job.get('company_name', '非公開'),
                    match_score=score,
                    match_reasoning=JobRecommender._generate_reasoning(job, conversation_keywords),
                    salary_min=job.get('salary_min', 0) or 0,
                    salary_max=job.get('salary_max', 0) or 0,
                    location=(job.get('location') or '未設定'),
                    remote_option=remote_option
                ))

            return recommendations

        except Exception as e:
            print(f"[JobRecommender] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def _calculate_job_score(
        job: Dict[str, Any],
        user_preferences: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        score = 50.0

        job_title = (job.get('job_title') or '')
        description = (job.get('required_skills') or job.get('description') or '')
        salary_min = job.get('salary_min') or 0
        salary_max = job.get('salary_max') or 0
        location = (job.get('location') or '')
        remote = job.get('remote', False)

        # 職種マッチ
        pref_title = (user_preferences.get('job_title') or '')
        if pref_title and pref_title.lower() in job_title.lower():
            score += 15

        # 勤務地マッチ
        pref_loc = (user_preferences.get('location') or '')
        if pref_loc and pref_loc.lower() in location.lower():
            score += 10
        elif remote:
            score += 8

        # 年収マッチ
        user_salary = user_preferences.get('salary_min') or 0
        if isinstance(user_salary, (int, float)) and 0 < user_salary < 100000:
            user_salary = int(user_salary * 10000)

        if user_salary and salary_max and salary_max >= user_salary:
            if salary_min and salary_min >= user_salary * 0.9:
                score += 10
            else:
                score += 5

        # キーワードマッチ
        matched_keywords = 0
        for keyword in keywords:
            k = (keyword or '').lower()
            if not k:
                continue
            if k in (description or '').lower() or k in job_title.lower():
                matched_keywords += 1
        score += min(matched_keywords * 3, 15)

        return min(score, 95.0)

    @staticmethod
    def _generate_reasoning(job: Dict[str, Any], keywords: List[str]) -> str:
        reasons = []
        job_title = (job.get('job_title') or '')
        description = (job.get('required_skills') or job.get('description') or '')
        remote = job.get('remote', False)

        matched = [k for k in keywords if (k or '').lower() in (description or '').lower() or (k or '').lower() in job_title.lower()]
        if matched:
            reasons.append(f"スキルマッチ: {', '.join(matched[:3])}")

        if remote:
            reasons.append("リモートワーク可")

        if not reasons:
            reasons.append("条件に近い求人")

        return " / ".join(reasons)
