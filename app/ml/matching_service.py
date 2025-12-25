# app/ml/matching_service.py
"""
AIマッチングサービス
ベクトル類似度を使った求人マッチング
"""
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

from .embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class JobRecommendation:
    """求人レコメンデーション結果"""

    def __init__(self, job_id: str, job_data: dict, match_score: float, match_reasons: List[str]):
        self.job_id = job_id
        self.job_data = job_data
        self.match_score = match_score  # 0-100のスコア
        self.match_reasons = match_reasons

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "job_id": self.job_id,
            "job": self.job_data,
            "match_score": round(self.match_score, 2),
            "match_reasons": self.match_reasons
        }


class MatchingService:
    """AIマッチングサービス"""

    def __init__(self):
        self.embedding_service = get_embedding_service()

    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        2つのベクトル間のコサイン類似度を計算

        Args:
            vector1: ベクトル1
            vector2: ベクトル2

        Returns:
            類似度（0-1）
        """
        # ベクトルを2次元配列に変換（sklearn cosine_similarity の要件）
        v1 = vector1.reshape(1, -1)
        v2 = vector2.reshape(1, -1)

        similarity = cosine_similarity(v1, v2)[0][0]
        return float(similarity)

    def filter_by_requirements(
        self,
        jobs: List[dict],
        seeker_profile: dict
    ) -> List[dict]:
        """
        必須条件で求人をフィルタリング

        Args:
            jobs: 求人リスト
            seeker_profile: 求職者プロフィール

        Returns:
            フィルタリング後の求人リスト
        """
        filtered_jobs = []

        # 希望条件（ポジティブ）
        preferred_location = seeker_profile.get("location")
        min_salary = seeker_profile.get("desired_salary_min")
        preferred_employment_types = seeker_profile.get("preferred_employment_types", [])

        # 除外条件（ネガティブ）
        excluded_categories = set(seeker_profile.get("excluded_job_categories", []))
        excluded_skills = set(seeker_profile.get("excluded_skills", []))
        excluded_industries = set(seeker_profile.get("excluded_industries", []))

        logger.debug(f"Seeker preferred_location: {preferred_location}")
        logger.debug(f"Excluded categories: {excluded_categories}")
        logger.debug(f"Excluded skills: {excluded_skills}")

        for job in jobs:
            job_id = job.get("id", "unknown")

            # ステータスチェック（公開中のみ）
            if job.get("status") != "published":
                logger.debug(f"Job {job_id}: Rejected - status is {job.get('status')}")
                continue

            # === 除外条件チェック（ネガティブフィルター） ===

            # 除外職種チェック
            job_category = job.get("job_category", "")
            if excluded_categories:
                # 部分一致でチェック
                is_excluded = any(exc.lower() in job_category.lower() for exc in excluded_categories)
                if is_excluded:
                    logger.debug(f"Job {job_id}: Rejected - job_category '{job_category}' in excluded list")
                    continue

            # 除外スキル・技術チェック
            job_tags = set(job.get("tags", []))
            if excluded_skills and job_tags:
                # 除外スキルと求人タグに重複があるかチェック
                excluded_match = excluded_skills & job_tags
                if excluded_match:
                    logger.debug(f"Job {job_id}: Rejected - has excluded skills: {excluded_match}")
                    continue

            # === 希望条件チェック（ポジティブフィルター） ===

            # 勤務地チェック
            if preferred_location:
                job_location = job.get("location", "")
                if preferred_location not in job_location:
                    logger.debug(f"Job {job_id}: Rejected - location '{preferred_location}' not in '{job_location}'")
                    continue

            # 給与チェック
            if min_salary:
                job_salary_max = job.get("salary_max")
                if job_salary_max and job_salary_max < min_salary:
                    logger.debug(f"Job {job_id}: Rejected - salary_max {job_salary_max} < {min_salary}")
                    continue

            # 雇用形態チェック
            if preferred_employment_types:
                job_employment_type = job.get("employment_type")
                if job_employment_type not in preferred_employment_types:
                    logger.debug(f"Job {job_id}: Rejected - employment_type '{job_employment_type}' not in {preferred_employment_types}")
                    continue

            logger.debug(f"Job {job_id}: PASSED all filters")
            filtered_jobs.append(job)

        logger.info(f"Filtered {len(filtered_jobs)} jobs from {len(jobs)} total jobs")
        return filtered_jobs

    def generate_match_reasons(
        self,
        job: dict,
        seeker_profile: dict,
        match_score: float
    ) -> List[str]:
        """
        マッチング理由を生成

        Args:
            job: 求人情報
            seeker_profile: 求職者プロフィール
            match_score: マッチスコア

        Returns:
            マッチング理由のリスト
        """
        reasons = []

        # スキルマッチ
        seeker_skills = set(seeker_profile.get("skills", []))
        job_tags = set(job.get("tags", []))
        matched_skills = seeker_skills & job_tags

        if matched_skills:
            skills_str = "、".join(list(matched_skills)[:3])  # 最大3つ表示
            reasons.append(f"スキルマッチ: {skills_str}")

        # 勤務地マッチ
        if seeker_profile.get("location") in job.get("location", ""):
            reasons.append(f"希望勤務地: {job.get('location')}")

        # 給与マッチ
        desired_salary = seeker_profile.get("desired_salary_min")
        if desired_salary and job.get("salary_max"):
            if job["salary_max"] >= desired_salary:
                reasons.append(f"希望給与条件を満たしています")

        # 高スコアの場合
        if match_score >= 80:
            reasons.append("プロフィールとの総合的な適合度が高いです")
        elif match_score >= 60:
            reasons.append("プロフィールとの適合度が良好です")

        return reasons if reasons else ["AIによる総合評価"]

    def calculate_skill_match_bonus(self, job: dict, seeker_profile: dict) -> float:
        """
        スキルマッチによるボーナススコアを計算

        Args:
            job: 求人情報
            seeker_profile: 求職者プロフィール

        Returns:
            ボーナススコア（0-20）
        """
        seeker_skills = set(seeker_profile.get("skills", []))
        tech_stack = set(seeker_profile.get("tech_stack", []))
        all_seeker_tech = seeker_skills | tech_stack

        job_tags = set(job.get("tags", []))

        if not all_seeker_tech or not job_tags:
            return 0.0

        # マッチしたスキルの数
        matched_skills = all_seeker_tech & job_tags
        match_count = len(matched_skills)

        # マッチ率
        match_ratio = match_count / len(job_tags) if job_tags else 0

        # ボーナススコア（最大20点）
        # - 1つマッチ: +5点
        # - 2つマッチ: +10点
        # - 3つ以上: +15-20点（マッチ率に応じて）
        if match_count == 0:
            return 0.0
        elif match_count == 1:
            return 5.0
        elif match_count == 2:
            return 10.0
        else:
            return 15.0 + (match_ratio * 5.0)

    def recommend_jobs(
        self,
        seeker_profile: dict,
        available_jobs: List[dict],
        top_k: int = 10
    ) -> List[JobRecommendation]:
        """
        求職者プロフィールに基づいて求人をレコメンド

        Args:
            seeker_profile: 求職者プロフィール
            available_jobs: 利用可能な求人リスト
            top_k: 返す求人の最大数

        Returns:
            レコメンデーション結果のリスト（スコア降順）
        """
        if not available_jobs:
            return []

        # ステップ1: 必須条件でフィルタリング
        filtered_jobs = self.filter_by_requirements(available_jobs, seeker_profile)

        if not filtered_jobs:
            logger.info("No jobs passed required conditions filter")
            return []

        # ステップ2: 求職者プロフィールをベクトル化
        seeker_text = self.embedding_service.create_seeker_text(seeker_profile)
        seeker_embedding = self.embedding_service.encode_text(seeker_text)

        # ステップ3: 各求人とのスコアを計算
        recommendations = []

        for job in filtered_jobs:
            # 求人をベクトル化
            job_text = self.embedding_service.create_job_text(job)
            job_embedding = self.embedding_service.encode_text(job_text)

            # ベクトル類似度計算（0-80点）
            similarity = self.calculate_similarity(seeker_embedding, job_embedding)
            base_score = similarity * 80

            # スキルマッチボーナス（0-20点）
            skill_bonus = self.calculate_skill_match_bonus(job, seeker_profile)

            # 最終スコア
            match_score = base_score + skill_bonus

            # 100点を超えないように制限
            match_score = min(match_score, 100.0)

            logger.debug(f"Job {job.get('id')}: base={base_score:.1f}, skill_bonus={skill_bonus:.1f}, final={match_score:.1f}")

            # マッチング理由を生成
            match_reasons = self.generate_match_reasons(job, seeker_profile, match_score)

            recommendation = JobRecommendation(
                job_id=job.get("id", ""),
                job_data=job,
                match_score=match_score,
                match_reasons=match_reasons
            )
            recommendations.append(recommendation)

        # スコア降順でソート
        recommendations.sort(key=lambda x: x.match_score, reverse=True)

        # Top-K を返す
        return recommendations[:top_k]


# グローバルインスタンス
_matching_service: Optional[MatchingService] = None


def get_matching_service() -> MatchingService:
    """
    マッチングサービスのシングルトンインスタンスを取得

    Returns:
        MatchingServiceインスタンス
    """
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService()
    return _matching_service
