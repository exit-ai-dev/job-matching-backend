"""
企業向け候補者検索チャットサービス（OR検索版）
職種、スキル、勤務地のいずれかに該当すれば表示
"""

from typing import Optional, List, Dict, Any
import json
import os
import re
from app.models.chat_models import ChatTurnResult
from app.utils.session_manager import SessionManager
from openai import OpenAI


class EmployerChatService:
    """企業向け候補者検索チャットサービス"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def start_chat(self, user_id: str) -> ChatTurnResult: 
        """候補者検索チャット開始"""
        session = SessionManager.create_session(user_id, {})  

        initial_message = (
            "こんにちは！候補者検索をサポートします。\n\n"
            "どのようなスキルや経験をお持ちの方をお探しですか？\n"
            "例えば、以下のような情報をお聞かせください：\n"
            "• 必要なスキル（プログラミング言語、ツールなど）\n"
            "• 経験年数\n"
            "• 希望する勤務形態（リモート可否など）\n"
            "• その他の条件"
        )

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
        user_id: str,
        user_message: str,
        session_id: Optional[str] = None
    ) -> ChatTurnResult:
        """企業のメッセージを処理して候補者を検索"""
        try:
            if session_id:
                session = SessionManager.get_session(session_id)
                if not session:
                    return self.start_chat(user_id)
            else:
                return self.start_chat(user_id)

            print(f"\n{'='*60}")
            print(f"[EmployerChatService] Processing employer message")
            print(f"   Employer ID: {user_id}")
            print(f"   Message: {user_message[:100]}...")

            # 1. AIで企業の要求を分析
            requirements = self._extract_requirements(user_message, session)
            print(f"[EmployerChatService] Extracted requirements: {requirements}")

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

            return ChatTurnResult(
                ai_message=ai_message,
                current_score=0.0,
                turn_count=session.turn_count,
                should_show_jobs=len(candidates) > 0,
                jobs=candidates,
                session_id=session.session_id
            )
        except Exception as e:
            print(f"[EmployerChatService] ERROR in process_message: {e}")
            import traceback
            traceback.print_exc()
            return ChatTurnResult(
                ai_message="申し訳ございません。エラーが発生しました。もう一度お試しください。",
                current_score=0.0,
                turn_count=1,
                should_show_jobs=False,
                jobs=[],
                session_id=session_id or "error"
            )

    def _extract_requirements(self, user_message: str, session) -> Dict[str, Any]:
        """企業のメッセージから求める候補者の要件を抽出"""
        conversation_history = []
        for turn in session.conversation_history[-5:]:
            if turn.get("user"):
                conversation_history.append({"role": "user", "content": turn["user"]})
            if turn.get("ai"):
                conversation_history.append({"role": "assistant", "content": turn["ai"]})

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

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}] + 
                         conversation_history + 
                         [{"role": "user", "content": user_message}],
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            requirements = json.loads(content)
            return requirements

        except Exception as e:
            print(f"[EmployerChatService] Error extracting requirements: {e}")
            return {
                "skills": [],
                "experience_years": None,
                "job_title": None,
                "location": None,
                "remote_preference": None,
                "keywords": user_message.split(),
                "other_requirements": user_message
            }

    def _search_candidates(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """要件に基づいて候補者を検索（OR検索版）"""
        from app.db.session import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        
        try:
            # 基本クエリ
            query = """
                SELECT 
                    u.id,
                    u.name,
                    u.skills as user_skills,
                    upp.job_title,
                    upp.location_prefecture,
                    upp.location_city,
                    upp.remote_work_preference,
                    u.experience_years
                FROM users u
                LEFT JOIN user_preferences_profile upp ON u.id = upp.user_id
                WHERE u.role = 'SEEKER'
                  AND u.is_active = true
            """

            params = {}
            or_conditions = []  # ← OR条件を格納

            # 1. スキルまたは職種で検索（どちらか該当すればOK）
            search_keywords = []
            
            if requirements.get("skills") and len(requirements["skills"]) > 0:
                search_keywords.extend(requirements["skills"][:3])
            
            if requirements.get("job_title"):
                search_keywords.append(requirements["job_title"])
            
            # スキル・職種のOR検索
            if search_keywords:
                skill_conditions = []
                for i, keyword in enumerate(search_keywords[:5]):
                    skill_conditions.append(
                        f"(u.skills::text ILIKE %(keyword_{i})s OR upp.job_title::text ILIKE %(keyword_{i})s)"
                    )
                    params[f"keyword_{i}"] = f"%{keyword}%"
                
                if skill_conditions:
                    or_conditions.append(f"({' OR '.join(skill_conditions)})")

            # 2. 勤務地で検索（該当すればOK）
            if requirements.get("location"):
                or_conditions.append(
                    "(upp.location_prefecture ILIKE %(location)s OR upp.location_city ILIKE %(location)s)"
                )
                params["location"] = f"%{requirements['location']}%"

            # 3. リモートワークで検索（該当すればOK）
            if requirements.get("remote_preference"):
                remote_pref = requirements["remote_preference"].lower()
                if "リモート" in remote_pref or "在宅" in remote_pref or "remote" in remote_pref:
                    or_conditions.append(
                        "upp.remote_work_preference IN ('フルリモート', 'リモート可')"
                    )

            # OR条件を結合（いずれか1つでも該当すればOK）
            if or_conditions:
                query += f" AND ({' OR '.join(or_conditions)})"
            
            query += " LIMIT 20"

            print(f"[EmployerChatService] Search keywords: {search_keywords}")
            print(f"[EmployerChatService] OR conditions count: {len(or_conditions)}")
            print(f"[EmployerChatService] Query params: {params}")
            print(f"[EmployerChatService] Full query:\n{query}")
            
            result = db.execute(text(query), params)
            candidates = []

            for row in result:
                try:
                    # スキルの解析
                    skills = []
                    skills_source = getattr(row, 'user_skills', None)
                    if skills_source:
                        try:
                            skills = json.loads(skills_source) if isinstance(skills_source, str) else skills_source
                            if not isinstance(skills, list):
                                skills = [str(skills_source)]
                        except:
                            skills = [s.strip() for s in str(skills_source).split(',') if s.strip()]

                    # 経験年数の推定
                    experience_years = 0
                    exp_years_field = getattr(row, 'experience_years', None)
                    if exp_years_field:
                        try:
                            exp_str = str(exp_years_field)
                            if exp_str.isdigit():
                                experience_years = int(exp_str)
                            else:
                                years_match = re.search(r'(\d+)', exp_str)
                                if years_match:
                                    experience_years = int(years_match.group(1))
                        except:
                            pass

                    # 経験年数フィルター（これはANDで適用）
                    if requirements.get("experience_years"):
                        if experience_years > 0 and experience_years < requirements["experience_years"]:
                            continue  # 経験年数が足りない場合はスキップ

                    # マッチスコア計算
                    match_score = self._calculate_match_score(
                        {
                            "skills": skills,
                            "job_title": getattr(row, 'job_title', None),
                            "experience_years": experience_years,
                            "remote_work_preference": getattr(row, 'remote_work_preference', None),
                            "location_prefecture": getattr(row, 'location_prefecture', None),
                            "location_city": getattr(row, 'location_city', None)
                        },
                        requirements
                    )

                    # 勤務地
                    location_parts = []
                    if getattr(row, 'location_prefecture', None):
                        location_parts.append(row.location_prefecture)
                    if getattr(row, 'location_city', None):
                        location_parts.append(row.location_city)
                    location = "".join(location_parts) if location_parts else "未設定"

                    candidate = {
                        "id": str(getattr(row, 'id', 'unknown')),
                        "name": getattr(row, 'name', None) or "名前未設定",
                        "job_title": getattr(row, 'job_title', None) or "職種未設定",
                        "experience_years": experience_years,
                        "skills": skills,
                        "location": location,
                        "remote_option": getattr(row, 'remote_work_preference', None) or "未設定",
                        "matchScore": match_score,
                        "matchReasoning": self._generate_match_reasoning(
                            {
                                "skills": skills,
                                "job_title": getattr(row, 'job_title', None),
                                "experience_years": experience_years,
                                "location_prefecture": getattr(row, 'location_prefecture', None),
                                "location_city": getattr(row, 'location_city', None)
                            },
                            requirements
                        )
                    }
                    candidates.append(candidate)
                    
                except Exception as row_error:
                    print(f"[EmployerChatService] Error processing row: {row_error}")
                    continue

            candidates.sort(key=lambda x: x["matchScore"], reverse=True)
            
            print(f"[EmployerChatService] Found {len(candidates)} candidates")
            return candidates[:10]

        except Exception as e:
            print(f"[EmployerChatService] Error in _search_candidates: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            db.close()

    def _calculate_match_score(self, candidate: Dict[str, Any], requirements: Dict[str, Any]) -> int:
        """候補者のマッチスコアを計算"""
        try:
            score = 50  # ベーススコア（少し下げる）
            
            # スキルマッチ（最大30点）
            if requirements.get("skills") and candidate.get("skills"):
                required_skills = set(s.lower() for s in requirements["skills"])
                candidate_skills = set(s.lower() for s in candidate["skills"])
                matched_skills = required_skills & candidate_skills
                
                if matched_skills:
                    score += min(len(matched_skills) * 10, 30)

            # 職種マッチ（20点）
            if requirements.get("job_title") and candidate.get("job_title"):
                if requirements["job_title"].lower() in candidate["job_title"].lower():
                    score += 20

            # 経験年数マッチ（15点）
            if requirements.get("experience_years") and candidate.get("experience_years"):
                if candidate["experience_years"] >= requirements["experience_years"]:
                    score += 15

            # 勤務地マッチ（10点）
            if requirements.get("location"):
                location = requirements["location"].lower()
                cand_pref = (candidate.get("location_prefecture") or "").lower()
                cand_city = (candidate.get("location_city") or "").lower()
                if location in cand_pref or location in cand_city:
                    score += 10

            # リモートマッチ（10点）
            if requirements.get("remote_preference"):
                remote_pref = requirements["remote_preference"].lower()
                cand_remote = (candidate.get("remote_work_preference") or "").lower()
                if ("リモート" in remote_pref or "remote" in remote_pref) and "リモート" in cand_remote:
                    score += 10

            return min(score, 100)
        except Exception as e:
            print(f"[EmployerChatService] Error calculating score: {e}")
            return 50

    def _generate_match_reasoning(self, candidate: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """マッチング理由を生成"""
        try:
            reasons = []

            # スキルマッチ
            if requirements.get("skills") and candidate.get("skills"):
                required_skills = set(s.lower() for s in requirements["skills"])
                candidate_skills = set(s.lower() for s in candidate["skills"])
                matched_skills = required_skills & candidate_skills
                
                if matched_skills:
                    reasons.append(f"スキル一致: {', '.join(list(matched_skills)[:3])}")

            # 職種マッチ
            if requirements.get("job_title") and candidate.get("job_title"):
                if requirements["job_title"].lower() in candidate["job_title"].lower():
                    reasons.append("職種一致")

            # 経験年数
            if requirements.get("experience_years") and candidate.get("experience_years"):
                if candidate["experience_years"] >= requirements["experience_years"]:
                    reasons.append(f"経験年数: {candidate['experience_years']}年")

            # 勤務地
            if requirements.get("location"):
                location = requirements["location"].lower()
                cand_pref = (candidate.get("location_prefecture") or "").lower()
                cand_city = (candidate.get("location_city") or "").lower()
                if location in cand_pref or location in cand_city:
                    reasons.append("勤務地一致")

            return " / ".join(reasons) if reasons else "候補者として推薦"
        except Exception as e:
            print(f"[EmployerChatService] Error generating reasoning: {e}")
            return "候補者として推薦"

    def _generate_response(self, requirements: Dict[str, Any], candidates: List[Dict[str, Any]], candidate_count: int) -> str:
        """AIの応答メッセージを生成"""
        try:
            if candidate_count == 0:
                return (
                    "申し訳ございません。現在、ご指定の条件に完全に一致する候補者が見つかりませんでした。\n\n"
                    "条件を少し緩和していただくか、別の条件を追加していただけますか？"
                )

            requirements_summary = []
            if requirements.get("skills"):
                requirements_summary.append(f"スキル: {', '.join(requirements['skills'][:3])}")
            if requirements.get("experience_years"):
                requirements_summary.append(f"経験: {requirements['experience_years']}年以上")
            if requirements.get("job_title"):
                requirements_summary.append(f"職種: {requirements['job_title']}")
            if requirements.get("location"):
                requirements_summary.append(f"勤務地: {requirements['location']}")

            message = f"以下の条件で{candidate_count}名の候補者が見つかりました：\n"
            if requirements_summary:
                message += "• " + "\n• ".join(requirements_summary) + "\n\n"

            message += (
                f"マッチスコアの高い順に{min(candidate_count, 10)}名を表示しています。\n"
                "各候補者の詳細を確認して、スカウトメッセージを送信することができます。\n\n"
                "さらに条件を絞り込みたい場合は、追加の要件をお聞かせください。"
            )

            return message
        except Exception as e:
            print(f"[EmployerChatService] Error generating response: {e}")
            return "候補者を検索しました。"