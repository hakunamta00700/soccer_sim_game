"""Phase 전환 관리"""

from typing import Dict, List, Optional

from loguru import logger

from sim_soccer.models.match import MatchState
from sim_soccer.models.team import TeamState
from sim_soccer.systems.tactics import get_phase_transition_probability


class PhaseManager:
    """Phase 전환을 관리하는 클래스"""

    # Phase별 가능한 다음 Phase
    PHASE_TRANSITIONS: Dict[str, List[str]] = {
        "build_up": ["midfield", "transition"],
        "midfield": ["final_third", "transition"],
        "final_third": ["transition"],
        "transition": ["build_up", "midfield", "final_third", "defense"],
        "defense": ["transition", "build_up"],
    }

    def determine_next_phase(
        self,
        current_phase: str,
        action_result: bool,
        action_type: Optional[str] = None,
        match_state: Optional[MatchState] = None,
    ) -> str:
        """현재 Phase와 행동 결과를 기반으로 다음 Phase 결정
        
        Args:
            current_phase: 현재 Phase
            action_result: 행동 결과 (성공/실패)
            action_type: 행동 타입
            match_state: 현재 경기 상태
        
        Returns:
            다음 Phase
        """
        possible_phases = self.PHASE_TRANSITIONS.get(current_phase, [current_phase])
        
        # Phase별 전환 규칙 적용
        if current_phase == "build_up":
            if action_result and action_type == "pass":
                return "midfield"
            elif not action_result:
                return "transition"
        
        elif current_phase == "midfield":
            if action_result and action_type == "pass":
                return "final_third"
            elif action_result and action_type == "dribble":
                return "final_third"
            elif not action_result:
                return "transition"
        
        elif current_phase == "final_third":
            if action_result and action_type == "shoot":
                # 슈팅 성공 시 골 또는 전환
                return "transition"
            elif not action_result:
                return "transition"
        
        elif current_phase == "transition":
            # 전환 Phase에서는 행동 타입에 따라 결정
            if action_type == "quick_attack":
                return "final_third"
            elif action_type == "stable_build":
                return "build_up"
            elif action_type == "defense_setup":
                return "defense"
            else:
                return "midfield"
        
        elif current_phase == "defense":
            if action_result and action_type in ["tackle", "intercept"]:
                return "transition"
            elif not action_result:
                return "transition"
        
        # 기본값: 현재 Phase 유지 또는 첫 번째 가능한 Phase
        return possible_phases[0] if possible_phases else current_phase

    def calculate_transition_probability(
        self, current_phase: str, team: TeamState, match_state: MatchState
    ) -> float:
        """Phase 전환 확률 계산
        
        Args:
            current_phase: 현재 Phase
            team: 팀 상태
            match_state: 경기 상태
        
        Returns:
            전환 확률 (0.0-1.0)
        """
        # 관련 스탯 평균 계산
        if current_phase == "build_up":
            relevant_stat_avg = team.get_average_stat("PAS")
        elif current_phase == "midfield":
            relevant_stat_avg = (team.get_average_stat("PAS") + team.get_average_stat("DRI")) / 2
        elif current_phase == "final_third":
            relevant_stat_avg = team.get_average_stat("SHO")
        else:
            relevant_stat_avg = 5.0  # 기본값
        
        # 전술 기반 전환 확률 계산
        transition_prob = get_phase_transition_probability(
            team.tactics, current_phase, relevant_stat_avg
        )
        
        logger.debug(
            f"Phase transition probability: {current_phase} -> "
            f"{transition_prob:.2%} (team: {team.team_name})"
        )
        
        return transition_prob

    def should_transition_phase(
        self,
        current_phase: str,
        team: TeamState,
        match_state: MatchState,
        random_value: float,
    ) -> bool:
        """Phase 전환 여부 판정
        
        Args:
            current_phase: 현재 Phase
            team: 팀 상태
            match_state: 경기 상태
            random_value: 랜덤 값 (0.0-1.0)
        
        Returns:
            True if should transition, False otherwise
        """
        transition_prob = self.calculate_transition_probability(
            current_phase, team, match_state
        )
        return random_value < transition_prob
