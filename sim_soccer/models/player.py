"""PlayerState 모델"""

from dataclasses import dataclass, field
from typing import Dict


# 포지션별 스탯 가중치 (설계 문서 참조)
POSITION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "GK": {
        "PAS": 0.3,
        "DRI": 0.2,
        "SHO": 0.1,
        "SPA": 1.2,
        "TAC": 1.5,
        "INT": 1.3,
        "STA": 1.1,
    },
    "DF": {
        "PAS": 0.8,
        "DRI": 0.6,
        "SHO": 0.3,
        "SPA": 1.3,
        "TAC": 1.5,
        "INT": 1.4,
        "STA": 1.0,
    },
    "MF": {
        "PAS": 1.2,
        "DRI": 1.1,
        "SHO": 0.7,
        "SPA": 1.1,
        "TAC": 1.0,
        "INT": 1.1,
        "STA": 1.1,
    },
    "FW": {
        "PAS": 0.9,
        "DRI": 1.3,
        "SHO": 1.5,
        "SPA": 1.2,
        "TAC": 0.4,
        "INT": 0.6,
        "STA": 1.0,
    },
}


@dataclass
class PlayerState:
    """선수 상태를 나타내는 클래스"""

    player_id: int
    name: str
    position: str  # "GK", "DF", "MF", "FW"
    zone: int = 2  # 현재 Zone (1-15), 기본값은 중앙 후방
    stats: Dict[str, int] = field(default_factory=dict)
    stamina: float = 100.0  # 현재 체력 (0-100)
    has_ball: bool = False  # 공을 가지고 있는지

    def __post_init__(self):
        """초기화 후 포지션 가중치 계산"""
        if self.position not in POSITION_WEIGHTS:
            raise ValueError(f"Invalid position: {self.position}")
        self.position_weights = POSITION_WEIGHTS[self.position]

    def get_weighted_stat(self, stat_name: str) -> float:
        """포지션 가중치가 적용된 스탯 값을 반환"""
        base_stat = self.stats.get(stat_name, 0)
        weight = self.position_weights.get(stat_name, 1.0)
        return base_stat * weight

    def get_effective_stat(self, stat_name: str, stamina_penalty: int = 0) -> float:
        """체력 페널티가 적용된 유효 스탯 값을 반환"""
        weighted_stat = self.get_weighted_stat(stat_name)
        return max(0, weighted_stat - stamina_penalty)

    def calculate_stamina_penalty(self) -> int:
        """현재 체력 수준에 따른 스탯 페널티를 반환"""
        if self.stamina >= 70:
            return 0
        elif self.stamina >= 50:
            return 1
        elif self.stamina >= 30:
            return 2
        elif self.stamina >= 10:
            return 3
        else:
            return 4

    def get_total_points(self) -> int:
        """선수에게 할당된 총 포인트를 반환"""
        return sum(self.stats.values())
