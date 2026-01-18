"""컨테스트 계산 및 판정"""

import random
from typing import Dict, Optional

from loguru import logger

from sim_soccer.field.zone import calculate_distance
from sim_soccer.models.player import PlayerState
from sim_soccer.systems.momentum import calculate_momentum_bonus
from sim_soccer.systems.stamina import apply_stamina_penalty
from sim_soccer.systems.tactics import calculate_tactics_bonus


class ContestResolver:
    """컨테스트(행동 판정)를 계산하는 클래스"""

    def calculate_contest_score(
        self,
        attacker: PlayerState,
        defender: Optional[PlayerState],
        action_type: str,
        situation: Dict,
        attacker_team_tactics: Dict[str, int],
        defender_team_tactics: Optional[Dict[str, int]] = None,
        attacker_momentum: int = 0,
        defender_momentum: int = 0,
        is_second_half: bool = False,
    ) -> float:
        """컨테스트 점수 계산
        
        Args:
            attacker: 공격자 (행동을 시도하는 선수)
            defender: 수비자 (방어하는 선수, None 가능)
            action_type: 행동 타입 ("pass", "dribble", "shoot", "tackle", "intercept")
            situation: 상황 변수 (압박, 거리, 공간 등)
            attacker_team_tactics: 공격 팀 전술
            defender_team_tactics: 수비 팀 전술
            attacker_momentum: 공격 팀 모멘텀
            defender_momentum: 수비 팀 모멘텀
            is_second_half: 후반인지 여부
        
        Returns:
            컨테스트 점수 (공격자 점수 - 수비자 점수)
        """
        # 공격자 점수 계산
        attacker_score = self._calculate_attacker_score(
            attacker,
            action_type,
            situation,
            attacker_team_tactics,
            attacker_momentum,
            is_second_half,
        )
        
        # 수비자 점수 계산 (있는 경우)
        defender_score = 0.0
        if defender:
            defender_score = self._calculate_defender_score(
                defender,
                action_type,
                situation,
                defender_team_tactics or {},
                defender_momentum,
                is_second_half,
            )
        
        contest_score = attacker_score - defender_score
        
        logger.debug(
            f"Contest: {action_type}, Attacker: {attacker_score:.2f}, "
            f"Defender: {defender_score:.2f}, Score: {contest_score:.2f}"
        )
        
        return contest_score

    def _calculate_attacker_score(
        self,
        player: PlayerState,
        action_type: str,
        situation: Dict,
        tactics: Dict[str, int],
        momentum: int,
        is_second_half: bool,
    ) -> float:
        """공격자 점수 계산"""
        # 행동 타입에 따른 관련 스탯 선택
        relevant_stats = self._get_relevant_stats(action_type)
        
        # 스탯 값 계산 (포지션 가중치 적용)
        stat_value = 0.0
        for stat_name in relevant_stats:
            base_stat = player.stats.get(stat_name, 0)
            weight = player.position_weights.get(stat_name, 1.0)
            stat_value += base_stat * weight
        
        # 체력 페널티 적용
        stamina_penalty = apply_stamina_penalty(player.stamina)
        stat_value -= stamina_penalty * len(relevant_stats) * 0.5
        
        # 전술 보정 적용
        tactics_bonus = calculate_tactics_bonus(tactics, action_type, situation)
        stat_value *= tactics_bonus
        
        # 모멘텀 보정 적용
        momentum_bonus = calculate_momentum_bonus(momentum, is_second_half)
        stat_value *= momentum_bonus
        
        # 상황 변수 보정
        situation_penalty = self._calculate_situation_penalty(action_type, situation)
        stat_value -= situation_penalty
        
        return max(0, stat_value)

    def _calculate_defender_score(
        self,
        player: PlayerState,
        action_type: str,
        situation: Dict,
        tactics: Dict[str, int],
        momentum: int,
        is_second_half: bool,
    ) -> float:
        """수비자 점수 계산"""
        # 행동 타입에 따른 관련 스탯 선택
        relevant_stats = self._get_relevant_stats_for_defense(action_type)
        
        # 스탯 값 계산
        stat_value = 0.0
        for stat_name in relevant_stats:
            base_stat = player.stats.get(stat_name, 0)
            weight = player.position_weights.get(stat_name, 1.0)
            stat_value += base_stat * weight
        
        # 체력 페널티 적용
        stamina_penalty = apply_stamina_penalty(player.stamina)
        stat_value -= stamina_penalty * len(relevant_stats) * 0.5
        
        # 전술 보정 적용
        tactics_bonus = calculate_tactics_bonus(tactics, action_type, situation)
        stat_value *= tactics_bonus
        
        # 모멘텀 보정 적용
        momentum_bonus = calculate_momentum_bonus(momentum, is_second_half)
        stat_value *= momentum_bonus
        
        # 상황 변수 보너스 (수비자는 포지셔닝 보너스)
        situation_bonus = self._calculate_situation_bonus(action_type, situation)
        stat_value += situation_bonus
        
        return max(0, stat_value)

    def _get_relevant_stats(self, action_type: str) -> list[str]:
        """행동 타입에 따른 관련 스탯 목록 반환"""
        stats_map = {
            "pass": ["PAS", "SPA"],
            "dribble": ["DRI", "SPA"],
            "shoot": ["SHO", "SPA"],
            "tackle": ["TAC", "SPA"],
            "intercept": ["INT", "SPA"],
            "transition": ["PAS", "SPA"],
        }
        return stats_map.get(action_type, ["SPA"])

    def _get_relevant_stats_for_defense(self, action_type: str) -> list[str]:
        """수비 행동에 따른 관련 스탯 목록 반환"""
        stats_map = {
            "pass": ["INT", "SPA"],  # 패스를 차단
            "dribble": ["TAC", "SPA"],  # 드리블을 막음
            "shoot": ["TAC", "SPA"],  # 슈팅을 막음 (GK)
            "tackle": ["DRI", "SPA"],  # 태클을 회피
            "intercept": ["PAS", "SPA"],  # 인터셉트를 회피
        }
        return stats_map.get(action_type, ["SPA", "TAC"])

    def _calculate_situation_penalty(self, action_type: str, situation: Dict) -> float:
        """상황 변수에 따른 페널티 계산"""
        penalty = 0.0
        
        # 거리 페널티
        distance = situation.get("distance", 0)
        if action_type == "pass":
            penalty += distance * 2.0
        elif action_type == "shoot":
            penalty += distance * 5.0
        
        # 압박 페널티
        pressing = situation.get("pressing", 0)
        if action_type == "pass":
            penalty += pressing * 3.0
        elif action_type == "shoot":
            penalty += pressing * 4.0
        elif action_type == "dribble":
            penalty += pressing * 2.0
        
        return penalty

    def _calculate_situation_bonus(self, action_type: str, situation: Dict) -> float:
        """상황 변수에 따른 보너스 계산 (수비자용)"""
        bonus = 0.0
        
        # 포지셔닝 보너스
        positioning = situation.get("positioning", 0)
        bonus += positioning * 2.0
        
        return bonus

    def resolve_contest(
        self, contest_score: float, random_value: Optional[float] = None
    ) -> bool:
        """컨테스트 점수를 기반으로 성공/실패 판정
        
        Args:
            contest_score: 컨테스트 점수
            random_value: 랜덤 값 (0.0-1.0), None이면 자동 생성
        
        Returns:
            True if success, False if failure
        """
        if random_value is None:
            random_value = random.random()
        
        # 기본 성공 확률
        base_success_rate = 0.5
        
        # 점수 차이에 따른 보정 (±30% 최대)
        score_bonus = min(max(contest_score * 0.03, -0.3), 0.3)
        
        # 최종 성공 확률 (20%-80% 범위)
        success_rate = base_success_rate + score_bonus
        success_rate = min(max(success_rate, 0.2), 0.8)
        
        success = random_value < success_rate
        
        logger.debug(
            f"Contest resolution: score={contest_score:.2f}, "
            f"success_rate={success_rate:.2%}, result={'SUCCESS' if success else 'FAILURE'}"
        )
        
        return success
