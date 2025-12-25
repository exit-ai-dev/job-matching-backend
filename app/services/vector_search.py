# app/services/vector_search.py
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VectorSearchService:
    """ベクトル検索サービス"""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        コサイン類似度を計算

        Args:
            vec1: ベクトル1
            vec2: ベクトル2

        Returns:
            コサイン類似度（0〜1）
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # -1〜1の範囲を0〜1に正規化
            return float((similarity + 1) / 2)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """
        ユークリッド距離を計算

        Args:
            vec1: ベクトル1
            vec2: ベクトル2

        Returns:
            ユークリッド距離
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            return float(np.linalg.norm(v1 - v2))

        except Exception as e:
            logger.error(f"Error calculating euclidean distance: {e}")
            return float('inf')

    @staticmethod
    def search_similar_jobs(
        query_embedding: List[float],
        job_embeddings: List[Dict[str, Any]],
        top_k: int = 10,
        min_similarity: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        クエリに類似した求人を検索

        Args:
            query_embedding: 検索クエリのエンベディング
            job_embeddings: 求人エンベディングのリスト
            top_k: 上位K件を返す
            min_similarity: 最小類似度閾値

        Returns:
            (job_id, similarity)のリスト
        """
        try:
            similarities = []

            for job_emb in job_embeddings:
                job_id = job_emb.get("job_id")
                embedding = job_emb.get("embedding")

                if not job_id or not embedding:
                    continue

                similarity = VectorSearchService.cosine_similarity(
                    query_embedding,
                    embedding
                )

                if similarity >= min_similarity:
                    similarities.append((job_id, similarity))

            # 類似度で降順ソート
            similarities.sort(key=lambda x: x[1], reverse=True)

            # 上位K件を返す
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Error searching similar jobs: {e}")
            return []

    @staticmethod
    def weighted_search(
        query_embedding: List[float],
        job_embeddings: List[Dict[str, Any]],
        job_data_list: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        重み付きベクトル検索

        Args:
            query_embedding: 検索クエリのエンベディング
            job_embeddings: 求人エンベディングのリスト
            job_data_list: 求人データのリスト
            preferences: ユーザーの条件・重み
            top_k: 上位K件を返す

        Returns:
            スコア付き求人のリスト
        """
        try:
            results = []
            job_data_map = {job["id"]: job for job in job_data_list}

            for job_emb in job_embeddings:
                job_id = job_emb.get("job_id")
                embedding = job_emb.get("embedding")

                if not job_id or not embedding or job_id not in job_data_map:
                    continue

                job_data = job_data_map[job_id]

                # ベクトル類似度スコア（0〜100）
                vector_similarity = VectorSearchService.cosine_similarity(
                    query_embedding,
                    embedding
                ) * 100

                # 条件による追加スコア
                condition_score = VectorSearchService._calculate_condition_score(
                    job_data,
                    preferences
                )

                # 重み付き合計スコア
                # ベクトル類似度: 60%、条件マッチ: 40%
                total_score = (vector_similarity * 0.6) + (condition_score * 0.4)

                results.append({
                    "job_id": job_id,
                    "job_data": job_data,
                    "vector_similarity": round(vector_similarity, 2),
                    "condition_score": round(condition_score, 2),
                    "total_score": round(total_score, 2)
                })

            # トータルスコアで降順ソート
            results.sort(key=lambda x: x["total_score"], reverse=True)

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error in weighted search: {e}")
            return []

    @staticmethod
    def _calculate_condition_score(
        job_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> float:
        """
        条件マッチングスコアを計算

        Args:
            job_data: 求人データ
            preferences: ユーザーの条件

        Returns:
            条件スコア（0〜100）
        """
        score = 0.0
        max_score = 0.0

        # 勤務地マッチング（20点）
        max_score += 20
        preferred_locations = preferences.get("location", [])
        if preferred_locations and job_data.get("location"):
            if any(loc in job_data["location"] for loc in preferred_locations):
                score += 20
            else:
                score += 5  # 部分点

        # 年収マッチング（30点）
        max_score += 30
        salary_min = preferences.get("salary_min")
        salary_max = preferences.get("salary_max")
        job_salary_min = job_data.get("salary_min")
        job_salary_max = job_data.get("salary_max")

        if salary_min and job_salary_max:
            if job_salary_max >= salary_min:
                # 希望年収範囲内
                overlap_score = min(30, (job_salary_max - salary_min) / 1000000 * 10)
                score += max(0, overlap_score)
            else:
                score += 5  # 低いが部分点

        # 雇用形態マッチング（15点）
        max_score += 15
        preferred_types = preferences.get("employment_types", [])
        job_type = job_data.get("employment_type")
        if preferred_types and job_type:
            if job_type in preferred_types:
                score += 15

        # リモートワークマッチング（15点）
        max_score += 15
        remote_preference = preferences.get("remote_work")
        job_remote = job_data.get("remote_work", False)
        if remote_preference is not None:
            if remote_preference == job_remote:
                score += 15
            elif remote_preference and not job_remote:
                score += 0  # リモート希望だが不可
            else:
                score += 10  # リモート不要だがリモート可

        # スキルマッチング（20点）
        max_score += 20
        preferred_skills = set(preferences.get("skills", []))
        job_tags = set(job_data.get("tags", []))
        if preferred_skills and job_tags:
            matching_skills = preferred_skills.intersection(job_tags)
            if matching_skills:
                skill_ratio = len(matching_skills) / len(preferred_skills)
                score += skill_ratio * 20

        # 正規化して0〜100に
        if max_score > 0:
            return (score / max_score) * 100
        return 50.0  # デフォルト

    @staticmethod
    def create_profile_embedding_text(profile: Dict[str, Any]) -> str:
        """
        プロフィールからエンベディング用テキストを作成

        Args:
            profile: ユーザープロフィール

        Returns:
            エンベディング用テキスト
        """
        parts = []

        if profile.get("skills"):
            parts.append(f"スキル: {', '.join(profile['skills'])}")

        if profile.get("experience"):
            parts.append(f"経験: {profile['experience']}")

        if profile.get("bio"):
            parts.append(f"自己紹介: {profile['bio']}")

        if profile.get("location"):
            parts.append(f"希望勤務地: {profile['location']}")

        if profile.get("desired_salary_min"):
            parts.append(f"希望年収: {profile['desired_salary_min']:,}円以上")

        return " | ".join(parts) if parts else "求職者"

    @staticmethod
    def create_job_embedding_text(job: Dict[str, Any]) -> str:
        """
        求人データからエンベディング用テキストを作成

        Args:
            job: 求人データ

        Returns:
            エンベディング用テキスト
        """
        parts = []

        if job.get("title"):
            parts.append(f"職種: {job['title']}")

        if job.get("description"):
            # 説明は最初の200文字まで
            desc = job['description'][:200]
            parts.append(f"仕事内容: {desc}")

        if job.get("tags"):
            parts.append(f"必要スキル: {', '.join(job['tags'])}")

        if job.get("location"):
            parts.append(f"勤務地: {job['location']}")

        if job.get("employment_type"):
            parts.append(f"雇用形態: {job['employment_type']}")

        return " | ".join(parts) if parts else "求人"
