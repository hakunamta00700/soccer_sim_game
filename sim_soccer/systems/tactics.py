"""전술 효과 계산"""

from typing import Dict


def calculate_attack_bonus(attack: int, action_type: str) -> float:
    """공격성 전술의 보정치 계산
    
    Args:
        attack: 공격성 값 (1-10)
        action_type: 행동 타입
    
    Returns:
        보정치 (배율)
    """
    base_bonus = (attack - 5) * 0.1  # 기본 보정
    
    if action_type == "dribble":
        return 1.0 + base_bonus * 2.0  # 드리블에 더 큰 영향
    elif action_type == "shoot":
        return 1.0 + base_bonus * 1.5  # 슈팅 기회 증가
    elif action_type == "pass":
        return 1.0 + base_bonus * 0.5  # 패스에 작은 영향
    else:
        return 1.0 + base_bonus


def calculate_pass_style_bonus(pass_style: int, distance: int) -> float:
    """패스 스타일 전술의 보정치 계산
    
    Args:
        pass_style: 패스 스타일 값 (1=짧은 패스, 10=긴 패스)
        distance: 패스 거리
    
    Returns:
        보정치 (배율)
    """
    if pass_style <= 3:  # 짧은 패스
        bonus = (4 - pass_style) * 0.05  # 최대 0.15
        distance_penalty = distance * 0.02  # 거리가 멀수록 페널티
        return 1.0 + bonus - distance_penalty
    elif pass_style >= 7:  # 긴 패스
        penalty = (pass_style - 6) * 0.03  # 최대 0.12
        distance_bonus = distance * 0.01  # 거리가 멀수록 작은 보너스
        return 1.0 - penalty + distance_bonus
    else:  # 중간
        return 1.0


def calculate_pressing_bonus(pressing: int, action_type: str) -> float:
    """압박 강도 전술의 보정치 계산
    
    Args:
        pressing: 압박 강도 값 (1-10)
        action_type: 행동 타입
    
    Returns:
        보정치 (배율)
    """
    base_bonus = (pressing - 5) * 0.04  # 기본 보정
    
    if action_type == "intercept":
        return 1.0 + base_bonus * 3.0  # 인터셉트에 큰 영향
    elif action_type == "tackle":
        return 1.0 + base_bonus * 2.0  # 태클에 큰 영향
    elif action_type == "pass":  # 상대 패스 방해
        return 1.0 - base_bonus * 0.5  # 상대 패스 성공률 감소
    else:
        return 1.0 + base_bonus


def calculate_defense_line_bonus(defense_line: int, is_attacking: bool) -> float:
    """수비 라인 전술의 보정치 계산
    
    Args:
        defense_line: 수비 라인 값 (1=하향, 10=상향)
        is_attacking: 공격 중인지 여부
    
    Returns:
        보정치 (배율)
    """
    if is_attacking:
        # 공격 시: 상향 라인은 공격 공간 증가
        return 1.0 + (defense_line - 5) * 0.05
    else:
        # 수비 시: 하향 라인은 수비 안정성 증가
        return 1.0 - (defense_line - 5) * 0.03


def calculate_transition_speed_bonus(transition_speed: int) -> float:
    """전환 속도 전술의 보정치 계산
    
    Args:
        transition_speed: 전환 속도 값 (1-10)
    
    Returns:
        보정치 (배율)
    """
    return 1.0 + (transition_speed - 5) * 0.02


def calculate_width_bonus(width: int, action_type: str) -> float:
    """폭 전술의 보정치 계산
    
    Args:
        width: 폭 값 (1=좁음, 10=넓음)
        action_type: 행동 타입
    
    Returns:
        보정치 (배율)
    """
    base_bonus = (width - 5) * 0.03
    
    if action_type == "space_sense":  # 공간 감각
        return 1.0 + base_bonus
    elif action_type == "side_play":  # 사이드 플레이
        return 1.0 + base_bonus * 2.0
    else:
        return 1.0


def calculate_tactics_bonus(
    tactics: Dict[str, int], action_type: str, situation: Dict = None
) -> float:
    """전술 보정치 종합 계산
    
    Args:
        tactics: 전술 딕셔너리
        action_type: 행동 타입
        situation: 상황 변수 (거리, 압박 등)
    
    Returns:
        종합 보정치 (배율)
    """
    if situation is None:
        situation = {}
    
    bonus = 1.0
    
    # 공격성 보정
    attack = tactics.get("attack", 5)
    bonus *= calculate_attack_bonus(attack, action_type)
    
    # 패스 스타일 보정 (패스 관련 행동에만)
    if action_type == "pass":
        pass_style = tactics.get("pass_style", 5)
        distance = situation.get("distance", 0)
        bonus *= calculate_pass_style_bonus(pass_style, distance)
    
    # 압박 보정 (수비 행동에만)
    if action_type in ["intercept", "tackle"]:
        pressing = tactics.get("pressing", 5)
        bonus *= calculate_pressing_bonus(pressing, action_type)
    
    # 전환 속도 보정 (전환 관련 행동에만)
    if action_type == "transition":
        transition_speed = tactics.get("transition_speed", 5)
        bonus *= calculate_transition_speed_bonus(transition_speed)
    
    # 폭 보정 (공간 활용 관련)
    if action_type in ["space_sense", "side_play"]:
        width = tactics.get("width", 5)
        bonus *= calculate_width_bonus(width, action_type)
    
    return bonus


def get_phase_transition_probability(
    tactics: Dict[str, int], phase: str, relevant_stat_avg: float
) -> float:
    """Phase 전환 확률 계산
    
    Args:
        tactics: 전술 딕셔너리
        phase: 현재 Phase
        relevant_stat_avg: 관련 스탯 평균
    
    Returns:
        전환 확률 (0.0-1.0)
    """
    # Phase별 기본 전환 확률
    base_probabilities = {
        "build_up": 0.3,
        "midfield": 0.35,
        "final_third": 0.4,
        "transition": 0.5,
        "defense": 0.3,
    }
    
    base_prob = base_probabilities.get(phase, 0.3)
    
    # 전술 보정
    attack = tactics.get("attack", 5)
    pass_style = tactics.get("pass_style", 5)
    
    if phase == "build_up":
        # 짧은 패스는 전환 확률 감소, 긴 패스는 증가
        if pass_style <= 3:
            tactics_bonus = -(4 - pass_style) * 0.02  # 최대 -0.06
        elif pass_style >= 7:
            tactics_bonus = (pass_style - 6) * 0.02  # 최대 +0.08
        else:
            tactics_bonus = 0.0
    elif phase == "midfield":
        # 공격성이 높으면 전환 확률 증가
        tactics_bonus = (attack - 5) * 0.02
    elif phase == "final_third":
        # 공격성이 높으면 전환 확률 증가
        tactics_bonus = (attack - 5) * 0.03
    else:
        tactics_bonus = 0.0
    
    # 스탯 보정 (±10% 최대)
    stat_bonus = min(max((relevant_stat_avg - 5) * 0.02, -0.1), 0.1)
    
    # 최종 확률 계산
    final_prob = base_prob + tactics_bonus + stat_bonus
    
    # 범위 제한 (15%-50%)
    return min(max(final_prob, 0.15), 0.5)
