"""MatchState 모델"""

from dataclasses import dataclass, field
from typing import List, Optional

from sim_soccer.models.events import EventLog
from sim_soccer.models.team import TeamState


@dataclass
class MatchState:
    """경기 상태를 나타내는 클래스"""

    match_id: str
    tick: int = 0  # 현재 Tick (0-5400)
    half: int = 1  # 전반(1) 또는 후반(2)
    home_team: TeamState = None
    away_team: TeamState = None
    current_phase: str = "build_up"  # 현재 Phase
    attacking_team: str = "home"  # 현재 공격 팀 ("home" 또는 "away")
    ball_zone: int = 2  # 볼이 있는 Zone (1-15)
    ball_holder: Optional[int] = None  # 공을 가진 선수 ID
    event_log: List[EventLog] = field(default_factory=list)
    is_finished: bool = False
    winner: Optional[str] = None  # "home", "away", "draw"

    def __post_init__(self):
        """초기화 후 기본 설정"""
        if self.home_team is None or self.away_team is None:
            raise ValueError("home_team and away_team must be provided")

    def get_attacking_team(self) -> TeamState:
        """현재 공격 팀을 반환"""
        return self.home_team if self.attacking_team == "home" else self.away_team

    def get_defending_team(self) -> TeamState:
        """현재 수비 팀을 반환"""
        return self.away_team if self.attacking_team == "home" else self.home_team

    def switch_attacking_team(self):
        """공격 팀 전환"""
        self.attacking_team = "away" if self.attacking_team == "home" else "home"

    def add_event(self, event: EventLog):
        """이벤트 로그 추가"""
        self.event_log.append(event)

    def get_events_by_type(self, event_type: str) -> List[EventLog]:
        """특정 타입의 이벤트만 필터링하여 반환"""
        return [e for e in self.event_log if e.event_type == event_type]

    def get_goals(self) -> List[EventLog]:
        """골 이벤트만 반환"""
        return self.get_events_by_type("goal")

    def determine_winner(self) -> str:
        """경기 승자 결정"""
        if self.home_team.score > self.away_team.score:
            return "home"
        elif self.away_team.score > self.home_team.score:
            return "away"
        else:
            return "draw"

    def finish_match(self):
        """경기 종료 처리"""
        self.is_finished = True
        self.winner = self.determine_winner()
