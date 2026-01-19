"""실시간 이벤트 출력 모듈"""

from typing import Optional

from sim_soccer.models.match import MatchState
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


class EventPrinter:
    """실시간 이벤트를 게임 같은 형식으로 출력하는 클래스"""

    def __init__(self, enabled: bool = True):
        """이벤트 프린터 초기화
        
        Args:
            enabled: 출력 활성화 여부
        """
        self.enabled = enabled

    def format_time(self, tick: int) -> str:
        """Tick을 시간 형식으로 변환
        
        Args:
            tick: 현재 Tick
        
        Returns:
            "[분:초]" 형식의 문자열
        """
        minutes = tick // 60
        seconds = tick % 60
        return f"[{minutes}분 {seconds}초]"

    def format_player_info(self, player: Optional[PlayerState], team: TeamState) -> str:
        """선수 정보 포맷팅
        
        Args:
            player: 선수 객체
            team: 팀 객체
        
        Returns:
            "팀명 번호번 선수(이름)" 형식의 문자열
        """
        if not player:
            return f"{team.team_name} 선수"
        return f"{team.team_name} {player.player_id}번 선수({player.name})"

    def print_dribble(
        self,
        tick: int,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        match_state: MatchState,
    ):
        """드리블 이벤트 출력"""
        if not self.enabled:
            return
        
        time_str = self.format_time(tick)
        player_info = self.format_player_info(player, team)
        
        if success:
            print(f"{time_str} {player_info}가 드리블을 시도하고 있습니다...")
            print(f"{time_str} 드리블 성공! 상대 수비수를 제쳤습니다.")
        else:
            print(f"{time_str} {player_info}가 드리블을 시도했습니다...")
            print(f"{time_str} 드리블 실패. 공을 잃었습니다.")

    def print_shoot(
        self,
        tick: int,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        is_goal: bool,
        match_state: MatchState,
    ):
        """슈팅 이벤트 출력"""
        if not self.enabled:
            return
        
        time_str = self.format_time(tick)
        player_info = self.format_player_info(player, team)
        
        print(f"{time_str} {player_info}가 슛을 시도했습니다!")
        
        if is_goal:
            home_score = match_state.home_team.score
            away_score = match_state.away_team.score
            home_name = match_state.home_team.team_name
            away_name = match_state.away_team.team_name
            print(f"{time_str} 골!!! {home_name} {home_score} - {away_score} {away_name}")
        elif success:
            print(f"{time_str} 골키퍼가 막았습니다.")
        else:
            print(f"{time_str} 슛이 골대를 벗어났습니다.")

    def print_pass(
        self,
        tick: int,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        match_state: MatchState,
    ):
        """패스 이벤트 출력 (주요 패스만)"""
        if not self.enabled:
            return
        
        # 일반 패스는 너무 많으므로 출력하지 않음
        # 중요한 패스만 출력 (예: 파이널 서드로의 패스)
        if match_state.current_phase == "final_third":
            time_str = self.format_time(tick)
            player_info = self.format_player_info(player, team)
            
            if success:
                print(f"{time_str} {player_info}가 위험한 패스를 성공했습니다!")
            else:
                print(f"{time_str} {player_info}의 패스가 실패했습니다...")

    def print_tackle(
        self,
        tick: int,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        match_state: MatchState,
    ):
        """태클 이벤트 출력"""
        if not self.enabled:
            return
        
        time_str = self.format_time(tick)
        player_info = self.format_player_info(player, team)
        
        if success:
            print(f"{time_str} {player_info}가 태클을 시도했습니다!")
            print(f"{time_str} 태클 성공! 공을 빼앗았습니다.")
        else:
            print(f"{time_str} {player_info}가 태클을 시도했습니다...")
            print(f"{time_str} 태클 실패. 상대가 공을 유지했습니다.")

    def print_intercept(
        self,
        tick: int,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        match_state: MatchState,
    ):
        """인터셉트 이벤트 출력"""
        if not self.enabled:
            return
        
        time_str = self.format_time(tick)
        player_info = self.format_player_info(player, team)
        
        if success:
            print(f"{time_str} {player_info}가 패스를 차단했습니다!")
            print(f"{time_str} 인터셉트 성공! 공을 획득했습니다.")
        else:
            print(f"{time_str} {player_info}가 인터셉트를 시도했습니다...")
            print(f"{time_str} 인터셉트 실패.")

    def print_phase_transition(
        self,
        tick: int,
        old_phase: str,
        new_phase: str,
        match_state: MatchState,
    ):
        """Phase 전환 출력 (선택적)"""
        if not self.enabled:
            return
        
        # Phase 전환은 너무 상세하므로 출력하지 않음
        pass

    def print_action(
        self,
        tick: int,
        action_type: str,
        player: Optional[PlayerState],
        team: TeamState,
        success: bool,
        match_state: MatchState,
        is_goal: bool = False,
    ):
        """행동 이벤트 출력 (통합 메서드)"""
        if action_type == "dribble":
            self.print_dribble(tick, player, team, success, match_state)
        elif action_type == "shoot":
            self.print_shoot(tick, player, team, success, is_goal, match_state)
        elif action_type in ["pass", "pass_long", "pass_to_midfield", "pass_to_forward"]:
            self.print_pass(tick, player, team, success, match_state)
        elif action_type == "tackle":
            self.print_tackle(tick, player, team, success, match_state)
        elif action_type == "intercept":
            self.print_intercept(tick, player, team, success, match_state)

    def print_match_start(self, match_state: MatchState):
        """경기 시작 출력"""
        if not self.enabled:
            return
        
        print("=" * 60)
        print(f"경기 시작: {match_state.home_team.team_name} vs {match_state.away_team.team_name}")
        print("=" * 60)
        print()

    def print_half_time(self, match_state: MatchState):
        """전반 종료 출력"""
        if not self.enabled:
            return
        
        home_score = match_state.home_team.score
        away_score = match_state.away_team.score
        home_name = match_state.home_team.team_name
        away_name = match_state.away_team.team_name
        
        print()
        print("=" * 60)
        print(f"전반 종료: {home_name} {home_score} - {away_score} {away_name}")
        print("=" * 60)
        print()
