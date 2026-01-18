"""행동 선택 로직"""

import random
from typing import Dict, List, Optional, Tuple

from loguru import logger

from sim_soccer.field.positioning import get_players_by_phase, get_players_in_zone
from sim_soccer.models.match import MatchState
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


class ActionSelector:
    """행동 선택을 담당하는 클래스"""

    # Phase별 가능한 행동 및 기본 확률
    PHASE_ACTIONS: Dict[str, List[Tuple[str, float]]] = {
        "build_up": [
            ("pass", 0.5),
            ("pass_long", 0.2),
            ("dribble", 0.1),
            ("pass_to_midfield", 0.2),
        ],
        "midfield": [
            ("pass", 0.4),
            ("dribble", 0.3),
            ("pass_to_forward", 0.2),
            ("shoot_long", 0.1),
        ],
        "final_third": [
            ("pass", 0.3),
            ("dribble", 0.2),
            ("shoot", 0.3),
            ("cross", 0.2),
        ],
        "transition": [
            ("quick_attack", 0.4),
            ("stable_build", 0.3),
            ("defense_setup", 0.3),
        ],
        "defense": [
            ("tackle", 0.4),
            ("intercept", 0.4),
            ("positioning", 0.2),
        ],
    }

    def select_action(
        self, phase: str, team: TeamState, match_state: MatchState
    ) -> Tuple[str, Dict]:
        """Phase와 팀 상태를 기반으로 행동 선택
        
        Args:
            phase: 현재 Phase
            team: 팀 상태
            match_state: 경기 상태
        
        Returns:
            (action_type, situation) 튜플
        """
        # Phase별 가능한 행동 가져오기
        possible_actions = self.PHASE_ACTIONS.get(phase, [("pass", 1.0)])
        
        # 전술에 따른 확률 조정
        adjusted_actions = self._adjust_action_probabilities(
            possible_actions, team.tactics, phase
        )
        
        # 행동 선택
        action_type = self._select_by_probability(adjusted_actions)
        
        # 상황 변수 생성
        situation = self._create_situation(action_type, team, match_state)
        
        logger.debug(
            f"Action selected: {action_type} (phase: {phase}, team: {team.team_name})"
        )
        
        return action_type, situation

    def _adjust_action_probabilities(
        self,
        actions: List[Tuple[str, float]],
        tactics: Dict[str, int],
        phase: str,
    ) -> List[Tuple[str, float]]:
        """전술에 따른 행동 확률 조정"""
        attack = tactics.get("attack", 5)
        pass_style = tactics.get("pass_style", 5)
        
        adjusted = []
        total_prob = 0.0
        
        for action_type, base_prob in actions:
            prob = base_prob
            
            # 공격성에 따른 조정
            if action_type in ["dribble", "shoot", "quick_attack"]:
                prob *= 1.0 + (attack - 5) * 0.1
            elif action_type in ["pass", "stable_build"]:
                prob *= 1.0 - (attack - 5) * 0.05
            
            # 패스 스타일에 따른 조정
            if action_type == "pass_long":
                prob *= 1.0 + (pass_style - 5) * 0.1
            elif action_type == "pass":
                prob *= 1.0 - (pass_style - 5) * 0.05
            
            adjusted.append((action_type, prob))
            total_prob += prob
        
        # 확률 정규화
        if total_prob > 0:
            adjusted = [(a, p / total_prob) for a, p in adjusted]
        
        return adjusted

    def _select_by_probability(
        self, actions: List[Tuple[str, float]]
    ) -> str:
        """확률에 따라 행동 선택"""
        r = random.random()
        cumulative = 0.0
        
        for action_type, prob in actions:
            cumulative += prob
            if r < cumulative:
                return action_type
        
        # 기본값: 마지막 행동
        return actions[-1][0]

    def _create_situation(
        self, action_type: str, team: TeamState, match_state: MatchState
    ) -> Dict:
        """행동에 대한 상황 변수 생성"""
        from sim_soccer.field.zone import calculate_distance
        
        situation = {}
        
        # 거리 계산 (볼 위치와 대상 Zone 간)
        ball_zone = match_state.ball_zone
        if action_type in ["pass", "pass_long", "pass_to_midfield", "pass_to_forward"]:
            # 패스의 경우 대상 Zone 추정 (임시로 중앙 중앙으로 설정)
            target_zone = 8
            situation["distance"] = calculate_distance(ball_zone, target_zone)
        
        # 압박 강도
        defending_team = match_state.get_defending_team()
        situation["pressing"] = defending_team.tactics.get("pressing", 5)
        
        # 포지셔닝 (수비자용)
        situation["positioning"] = 5  # 기본값
        
        return situation

    def select_players(
        self,
        action_type: str,
        team: TeamState,
        match_state: MatchState,
    ) -> Tuple[Optional[PlayerState], Optional[PlayerState]]:
        """행동의 주체와 대상 선수 선정
        
        Args:
            action_type: 행동 타입
            team: 팀 상태
            match_state: 경기 상태
        
        Returns:
            (attacker, defender) 튜플
        """
        # 공을 가진 선수 찾기
        attacker = team.get_ball_holder()
        if not attacker:
            # 공을 가진 선수가 없으면 볼 위치의 선수 선택
            players_in_zone = get_players_in_zone(team, match_state.ball_zone)
            if players_in_zone:
                attacker = players_in_zone[0]
            else:
                # 볼 위치에 선수가 없으면 Phase에 맞는 선수 선택
                phase_players = get_players_by_phase(team, match_state.current_phase)
                if phase_players:
                    attacker = phase_players[0]
        
        # 수비자 선택 (필요한 경우)
        defender = None
        if action_type in ["pass", "dribble", "shoot"]:
            defending_team = match_state.get_defending_team()
            # 볼 위치 근처의 수비자 선택
            defenders_in_zone = get_players_in_zone(
                defending_team, match_state.ball_zone
            )
            if defenders_in_zone:
                defender = defenders_in_zone[0]
            else:
                # 가장 가까운 수비자 선택
                from sim_soccer.field.positioning import find_nearest_player
                defender = find_nearest_player(
                    defending_team, match_state.ball_zone
                )
        
        return attacker, defender
