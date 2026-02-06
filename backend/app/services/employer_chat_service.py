"""
企業向け候補者検索チャットサービス
"""

from typing import Optional, List, Dict, Any
import json
import os
from app.models.chat_models import ChatTurnResult
from app.utils.session_manager import SessionManager
from openai import OpenAI


class EmployerChatService:
    """企業向け候補者検索チャットサービス"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def start_chat(self, employer_id: str) -> ChatTurnResult:
        """
        候補者検索チャット開始

        Args:
            employer_id: 企業ID

        Returns:
            ChatTurnResult: 初回メッセージ
        """
        # セッション作成
        session = SessionManager.create_session(employer_id, {})

        initial_message = (
            "こんにちは！候補者検索をサポートします。\n\n"
            "どのようなスキルや経験をお持ちの方をお探しですか？\n"
            "例えば、以下のような情報をお聞かせください：\n"
            "• 必要なスキル（プログラミング言語、ツールなど）\n"
            "• 経験年数\n"
            "• 希望する勤務形態（リモート可否など）\n"
            "• その他の条件"
        )

        # セッションに記録
        SessionManager.add_turn(
            session=session,
            user_message="[初回接続]",
            ai_message=initial_message,
            is_deep_dive=False,
            new_score=0.0
        )

        return ChatTurnResult(
            ai_message=initial_message,
            current_score=0.0,
            turn_count=1,
            should_show_jobs=False,
            jobs=None,
            session_id=session.session_id
        )

    def process_message(
        self,
        employer_id: str,
        user_message: str,
        session_id: Optional[str] = None
    ) -> ChatTurnResult:
        """
        企業のメッセージを処理して候補者を検索

        Args:
            employer_id: 企業ID
            user_message: 企業のメッセージ
            session_id: セッションID

        Returns:
            ChatTurnResult: 候補者リストと応答
        """
        # セッション取得または作成
        if session_id:
            session = SessionManager.get_session(session_id)
            if not session:
                return self.start_chat(employer_id)
        else:
            return self.start_chat(employer_id)

        print(f"\n{'='*60}")
        print(f"[EmployerChatService] Processing employer message")
        print(f"   Employer ID: {employer_id}")
        print(f"   Message: {user_message[:100]}...")

        # 1. AIで企業の要求を分析
        requirements = self._extract_requirements(user_message, session)

        # 2. 候補者を検索
        candidates = self._search_candidates(requirements)

        # 3. AIで応答メッセージを生成
        ai_message = self._generate_response(requirements, candidates, len(candidates))

        # 4. セッションに記録
        SessionManager.add_turn(
            session=session,
            user_message=user_message,
            ai_message=ai_message,
            is_deep_dive=False,
            new_score=0.0
        )

        # 5. 結果を返す
        return ChatTurnResult(
            ai_message=ai_message,
            current_score=0.0,
            turn_count=session.turn_count,
            should_show_jobs=len(candidates) > 0,
            jobs=candidates,
            session_id=session.session_id
        )

    def _extract_requirements(
        self,
        user_message: str,
        session
    ) -> Dict[str, Any]:
        """
        企業のメッセージから求める候補者の要件を抽出

        Args:
            user_message: ユーザーメッセージ
            session: セッション

        Returns:
            Dict: 抽出された要件
        """
        # 会話履歴を構築
        conversation_history = []
        for turn in session.conversation_history[-5:]:  # 直近5ターン
            if turn.get("user"):
                conversation_history.append({
                    "role": "user",
                    "content": turn["user"]
                })
            if turn.get("ai"):
                conversation_history.append({
                    "role": "assistant",
                    "content": turn["ai"]
                })

        # AIで要件抽出
        system_prompt = """あなたは採用担当者のアシスタントです。
企業が求める候補者の要件を分析してください。

以下の形式でJSONを返してください：
{
  "skills": ["スキル1", "スキル2", ...],
  "experience_years": 数値または null,
  "job_title": "希望職種" または null,
  "location": "勤務地" または null,
  "remote_preference": "リモート可否の希望" または null,
  "keywords": ["キーワード1", "キーワード2", ...],
  "other_requirements": "その他の要件の説明"
}"""

        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt}
                ] + messages,
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            
            # JSONを抽出（```json ``` で囲まれている場合に対応）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            requirements = json.loads(content)
            print(f"[EmployerChatService] Extracted requirements: {requirements}")
            return requirements

        except Exception as e:
            print(f"[EmployerChatService] Error extracting requirements: {e}")
            # フォールバック：基本的なキーワード抽出
            return {
                "skills": [],
                "experience_years": None,
                "job_title": None,
                "location": None,
                "remote_preference": None,
                "keywords": user_message.split(),
                "other_requirements": user_message
            }

    def _search_candidates(
        self,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        要件に基づいて候補者を検索

        Args:
            requirements: 抽出された要件

        Returns:
            List[Dict]: 候補者リスト
        """
        from app.db.session import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        
        try:
            # 基本的な候補者検索クエリ
            query = """
                SELECT 
                    pd.user_id as id,
                    pd.name,
                    up.job_title,
                    up.years_of_experience as experience_years,
                    up.skills,
                    CONCAT(up.location_prefecture, up.location_city) as location,
                    upp.remote_work_preference
                FROM personal_date pd
                LEFT JOIN user_profile up ON pd.user_id = up.user_id
                LEFT JOIN user_preferences_profile upp ON pd.user_id = upp.user_id
                WHERE 1=1
            """

            params = {}

            # スキルフィルター
            if requirements.get("skills"):
                # スキル配列に対する検索（PostgreSQL配列演算子使用）
                skill_conditions = []
                for i, skill in enumerate(requirements["skills"][:5]):  # 最大5つ
                    param_name = f"skill_{i}"
                    skill_conditions.append(f"%({param_name})s = ANY(up.skills)")
                    params[param_name] = skill
                
                if skill_conditions:
                    query += f" AND ({' OR '.join(skill_conditions)})"

            # 経験年数フィルター
            if requirements.get("experience_years"):
                query += " AND up.years_of_experience >= %(min_years)s"
                params["min_years"] = requirements["experience_years"]

            # 職種フィルター
            if requirements.get("job_title"):
                query += " AND up.job_title ILIKE %(job_title)s"
                params["job_title"] = f"%{requirements['job_title']}%"

            # リモートワークフィルター
            if requirements.get("remote_preference"):
                remote_pref = requirements["remote_preference"].lower()
                if "リモート" in remote_pref or "在宅" in remote_pref or "remote" in remote_pref:
                    query += " AND upp.remote_work_preference IN ('フルリモート', 'リモート可')"

            query += " LIMIT 20"

            print(f"[EmployerChatService] Executing query with params: {params}")
            result = db.execute(text(query), params)
            candidates = []

            for row in result:
                # マッチスコアを計算（簡易版）
                match_score = self._calculate_match_score(
                    dict(row._mapping),
                    requirements
                )

                candidate = {
                    "id": str(row.id),
                    "name": row.name or "名前未設定",
                    "job_title": row.job_title or "職種未設定",
                    "experience_years": row.experience_years,
                    "skills": row.skills if row.skills else [],
                    "location": row.location or "未設定",
                    "remote_option": row.remote_work_preference or "未設定",
                    "matchScore": match_score,
                    "matchReasoning": self._generate_match_reasoning(
                        dict(row._mapping),
                        requirements
                    )
                }
                candidates.append(candidate)

            # マッチスコア順にソート
            candidates.sort(key=lambda x: x["matchScore"], reverse=True)
            
            print(f"[EmployerChatService] Found {len(candidates)} candidates")
            return candidates[:10]  # 上位10名

        except Exception as e:
            print(f"[EmployerChatService] Error searching candidates: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            db.close()

    def _calculate_match_score(
        self,
        candidate: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> int:
        """
        候補者のマッチスコアを計算

        Args:
            candidate: 候補者情報
            requirements: 要件

        Returns:
            int: マッチスコア（0-100）
        """
        score = 60  # ベーススコア

        # スキルマッチ
        if requirements.get("skills") and candidate.get("skills"):
            required_skills = set(s.lower() for s in requirements["skills"])
            candidate_skills = set(s.lower() for s in candidate["skills"])
            matched_skills = required_skills & candidate_skills
            
            if matched_skills:
                score += min(len(matched_skills) * 10, 30)

        # 経験年数マッチ
        if requirements.get("experience_years") and candidate.get("experience_years"):
            if candidate["experience_years"] >= requirements["experience_years"]:
                score += 10

        # 職種マッチ
        if requirements.get("job_title") and candidate.get("job_title"):
            if requirements["job_title"].lower() in candidate["job_title"].lower():
                score += 15

        return min(score, 100)

    def _generate_match_reasoning(
        self,
        candidate: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """
        マッチング理由を生成

        Args:
            candidate: 候補者情報
            requirements: 要件

        Returns:
            str: マッチング理由
        """
        reasons = []

        # スキルマッチ
        if requirements.get("skills") and candidate.get("skills"):
            required_skills = set(s.lower() for s in requirements["skills"])
            candidate_skills = set(s.lower() for s in candidate["skills"])
            matched_skills = required_skills & candidate_skills
            
            if matched_skills:
                reasons.append(f"スキル一致: {', '.join(list(matched_skills)[:3])}")

        # 経験年数
        if requirements.get("experience_years") and candidate.get("experience_years"):
            if candidate["experience_years"] >= requirements["experience_years"]:
                reasons.append(f"経験年数: {candidate['experience_years']}年")

        # 職種
        if requirements.get("job_title") and candidate.get("job_title"):
            if requirements["job_title"].lower() in candidate["job_title"].lower():
                reasons.append(f"職種一致")

        if not reasons:
            return "候補者として推薦"

        return " / ".join(reasons)

    def _generate_response(
        self,
        requirements: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        candidate_count: int
    ) -> str:
        """
        AIの応答メッセージを生成

        Args:
            requirements: 抽出された要件
            candidates: 候補者リスト
            candidate_count: 候補者数

        Returns:
            str: 応答メッセージ
        """
        if candidate_count == 0:
            return (
                "申し訳ございません。現在、ご指定の条件に完全に一致する候補者が見つかりませんでした。\n\n"
                "条件を少し緩和していただくか、別の条件を追加していただけますか？"
            )

        # 要件のサマリー
        requirements_summary = []
        if requirements.get("skills"):
            requirements_summary.append(f"スキル: {', '.join(requirements['skills'][:3])}")
        if requirements.get("experience_years"):
            requirements_summary.append(f"経験: {requirements['experience_years']}年以上")
        if requirements.get("job_title"):
            requirements_summary.append(f"職種: {requirements['job_title']}")

        message = f"以下の条件で{candidate_count}名の候補者が見つかりました：\n"
        if requirements_summary:
            message += "• " + "\n• ".join(requirements_summary) + "\n\n"

        message += (
            f"マッチスコアの高い順に{min(candidate_count, 10)}名を表示しています。\n"
            "各候補者の詳細を確認して、スカウトメッセージを送信することができます。\n\n"
            "さらに条件を絞り込みたい場合は、追加の要件をお聞かせください。"
        )

        return message
