# app/services/scout_service.py
"""
スカウトサービス
"""
from typing import Optional, List, Dict, Any
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.scout import Scout, ScoutStatus
from app.models.user import User
from app.repositories.scout_repository import ScoutRepository
from app.repositories.user_repository import UserRepository


class ScoutService:
    """スカウトサービス"""

    def __init__(self, db: Session):
        self.db = db
        self.scout_repo = ScoutRepository(db)
        self.user_repo = UserRepository(db)

    def get_seeker_scouts(
        self,
        seeker_id: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """求職者のスカウト一覧を取得"""
        scouts = self.scout_repo.get_by_seeker(seeker_id, status=status)
        total = self.scout_repo.count_by_seeker(seeker_id)

        return {
            "scouts": scouts,
            "total": total,
        }

    def get_employer_scouts(
        self,
        employer_id: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """企業のスカウト一覧を取得"""
        scouts = self.scout_repo.get_by_employer(employer_id, status=status)
        total = self.scout_repo.count_by_employer(employer_id)

        return {
            "scouts": scouts,
            "total": total,
        }

    def get_scout_detail(self, scout_id: str) -> Optional[Scout]:
        """スカウト詳細を取得"""
        return self.scout_repo.get_by_id(scout_id)

    def create_scout(
        self,
        employer: User,
        seeker_id: str,
        title: str,
        message: str,
        job_id: Optional[str] = None,
        match_score: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Scout:
        """スカウトを作成"""
        # 求職者の存在確認
        seeker = self.user_repo.get_by_id(seeker_id)
        if not seeker or seeker.role.value != "seeker":
            raise ValueError("候補者が見つかりません")

        scout = Scout(
            id=str(uuid.uuid4()),
            employer_id=employer.id,
            seeker_id=seeker_id,
            job_id=job_id,
            title=title,
            message=message,
            match_score=match_score,
            status=ScoutStatus.NEW,
            tags=json.dumps(tags) if tags else None,
        )

        return self.scout_repo.create(scout)

    def update_scout(
        self,
        scout: Scout,
        status: Optional[str] = None,
    ) -> Scout:
        """スカウトを更新"""
        if status is not None:
            scout.status = ScoutStatus(status)
            if status == "read" and not scout.read_at:
                scout.read_at = datetime.utcnow()
            elif status == "replied" and not scout.replied_at:
                scout.replied_at = datetime.utcnow()

        return self.scout_repo.update(scout)

    def scout_to_item(self, scout: Scout, employer: Optional[User] = None, seeker: Optional[User] = None) -> Dict[str, Any]:
        """スカウトをリストアイテム形式に変換"""
        tags = []
        if scout.tags:
            try:
                tags = json.loads(scout.tags)
            except:
                pass

        return {
            "id": scout.id,
            "title": scout.title,
            "company": employer.company_name if employer else None,
            "candidateName": seeker.name if seeker else None,
            "message": scout.message[:100] + "..." if len(scout.message) > 100 else scout.message,
            "matchScore": scout.match_score,
            "status": scout.status.value,
            "createdAt": scout.created_at.isoformat() if scout.created_at else None,
            "readAt": scout.read_at.isoformat() if scout.read_at else None,
            "repliedAt": scout.replied_at.isoformat() if scout.replied_at else None,
            "tags": tags,
            "jobId": scout.job_id,
        }

    def scout_to_detail(self, scout: Scout, employer: Optional[User] = None, seeker: Optional[User] = None) -> Dict[str, Any]:
        """スカウトを詳細形式に変換"""
        item = self.scout_to_item(scout, employer, seeker)
        item["message"] = scout.message  # 全文を返す
        return item

    def get_seeker_stats(self, seeker_id: str) -> Dict[str, int]:
        """求職者のスカウト統計を取得"""
        return {
            "total": self.scout_repo.count_by_seeker(seeker_id),
            "new": self.scout_repo.count_new_by_seeker(seeker_id),
        }
