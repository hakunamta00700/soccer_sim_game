"""TeamState 모델"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sim_soccer.models.player import PlayerState


@dataclass
class TeamState:
    """팀 상태를 나타내는 클래스"""

    team_id: str
    team_name: str
    formation: str
    players: List[PlayerState] = field(default_factory=list)
    tactics: Dict[str, int] = field(default_factory=dict)
    score: int = 0
    momentum: int = 0  # -10 ~ +10
    possession: float = 0.0  # 점유율 (0.0-1.0)

    # 통계
    stats: Dict[str, int] = field(
        default_factory=lambda: {
            "shots": 0,
            "shots_on_target": 0,
            "passes_attempted": 0,
            "passes_completed": 0,
            "tackles_attempted": 0,
            "tackles_successful": 0,
            "dribbles_attempted": 0,
            "dribbles_successful": 0,
        }
    )

    def __post_init__(self):
        """초기화 후 기본 전술 설정"""
        if not self.tactics:
            self.tactics = {
                "attack": 5,
                "pass_style": 5,
                "pressing": 5,
                "defense_line": 5,
                "transition_speed": 5,
                "width": 5,
            }

    def get_player_by_id(self, player_id: int) -> Optional[PlayerState]:
        """선수 ID로 선수를 찾아 반환"""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_players_by_position(self, position: str) -> List[PlayerState]:
        """포지션으로 선수들을 찾아 반환"""
        return [p for p in self.players if p.position == position]

    def get_average_stat(self, stat_name: str) -> float:
        """팀의 평균 스탯을 반환"""
        if not self.players:
            return 0.0
        total = sum(p.stats.get(stat_name, 0) for p in self.players)
        return total / len(self.players)

    def get_ball_holder(self) -> Optional[PlayerState]:
        """공을 가진 선수를 반환"""
        for player in self.players:
            if player.has_ball:
                return player
        return None

    def set_ball_holder(self, player_id: Optional[int]):
        """공을 가진 선수를 설정"""
        for player in self.players:
            player.has_ball = player.player_id == player_id

    def update_possession(self, total_ticks: int, team_ticks: int):
        """점유율 업데이트"""
        if total_ticks > 0:
            self.possession = team_ticks / total_ticks
