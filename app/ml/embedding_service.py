# app/ml/embedding_service.py
"""
ベクトル埋め込み生成サービス
求人情報とユーザープロフィールをベクトル化
"""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """ベクトル埋め込み生成サービス"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Args:
            model_name: 使用するSentence Transformersモデル
                       多言語対応モデルを使用（日本語に対応）
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")

    def encode_text(self, text: str) -> np.ndarray:
        """
        テキストをベクトルに変換

        Args:
            text: 変換するテキスト

        Returns:
            ベクトル表現（numpy配列）
        """
        if not text or not text.strip():
            # 空のテキストの場合はゼロベクトルを返す
            return np.zeros(self.embedding_dim)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        複数のテキストを一括でベクトルに変換

        Args:
            texts: 変換するテキストのリスト

        Returns:
            ベクトル表現の配列（shape: [len(texts), embedding_dim]）
        """
        if not texts:
            return np.array([])

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def create_job_text(self, job_data: dict) -> str:
        """
        求人情報から埋め込み用のテキストを生成

        Args:
            job_data: 求人情報の辞書

        Returns:
            結合されたテキスト
        """
        components = []

        # タイトル（重要度高）
        if job_data.get("title"):
            components.append(f"職種: {job_data['title']}")

        # 説明文
        if job_data.get("description"):
            components.append(f"仕事内容: {job_data['description']}")

        # 勤務地
        if job_data.get("location"):
            components.append(f"勤務地: {job_data['location']}")

        # 雇用形態
        if job_data.get("employment_type"):
            employment_type_map = {
                "full_time": "正社員",
                "part_time": "パート・アルバイト",
                "contract": "契約社員",
                "intern": "インターン"
            }
            emp_type = employment_type_map.get(job_data["employment_type"], job_data["employment_type"])
            components.append(f"雇用形態: {emp_type}")

        # タグ/スキル
        if job_data.get("tags"):
            tags = ", ".join(job_data["tags"])
            components.append(f"必要スキル: {tags}")

        return " ".join(components)

    def create_seeker_text(self, seeker_data: dict) -> str:
        """
        求職者プロフィールから埋め込み用のテキストを生成

        Args:
            seeker_data: 求職者情報の辞書

        Returns:
            結合されたテキスト
        """
        components = []

        # スキル（重要度高）
        if seeker_data.get("skills"):
            skills = ", ".join(seeker_data["skills"])
            components.append(f"スキル: {skills}")

        # 経験
        if seeker_data.get("experience"):
            components.append(f"経験: {seeker_data['experience']}")

        # 学歴
        if seeker_data.get("education"):
            components.append(f"学歴: {seeker_data['education']}")

        # 希望勤務地
        if seeker_data.get("location"):
            components.append(f"希望勤務地: {seeker_data['location']}")

        return " ".join(components)


# グローバルインスタンス（シングルトンパターン）
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    埋め込みサービスのシングルトンインスタンスを取得

    Returns:
        EmbeddingServiceインスタンス
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
