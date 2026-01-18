"""이벤트 로그 모델"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EventLog:
    """경기 이벤트 로그"""

    tick: int  # 발생 시간 (Tick)
    phase: str  # 발생 Phase
    event_type: str  # 이벤트 타입 (골, 기회, 전환 등)
    team: str  # 관련 팀 ("home" 또는 "away")
    player_id: Optional[int] = None  # 관련 선수 ID
    action: Optional[str] = None  # 행동 (슈팅, 패스 등)
    result: Optional[str] = None  # 결과 (성공/실패)
    stats_used: Optional[Dict[str, float]] = None  # 사용된 스탯
    tactics_impact: Optional[Dict[str, float]] = None  # 전술 영향
    description: Optional[str] = None  # 이벤트 설명

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "tick": self.tick,
            "phase": self.phase,
            "event_type": self.event_type,
            "team": self.team,
            "player_id": self.player_id,
            "action": self.action,
            "result": self.result,
            "stats_used": self.stats_used,
            "tactics_impact": self.tactics_impact,
            "description": self.description,
        }
