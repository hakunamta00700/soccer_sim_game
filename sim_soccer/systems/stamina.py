"""체력 시스템"""

from typing import Dict


# 행동별 기본 체력 소모량 (설계 문서 참조)
ACTION_STAMINA_COST: Dict[str, float] = {
    "pass": 0.5,
    "dribble": 1.5,
    "shoot": 1.0,
    "tackle": 2.0,
    "intercept": 1.5,
    "transition_dash": 2.5,
    "default": 1.0,
}


def calculate_stamina_cost(
    action_type: str, tactics: Dict[str, int], player_sta: int
) -> float:
    """체력 소모량 계산
    
    Args:
        action_type: 행동 타입
        tactics: 전술 딕셔너리
        player_sta: 선수의 STA 스탯
    
    Returns:
        체력 소모량
    """
    # 기본 소모량
    base_cost = ACTION_STAMINA_COST.get(action_type, ACTION_STAMINA_COST["default"])
    
    # 전술 보정
    pressing = tactics.get("pressing", 5)
    attack = tactics.get("attack", 5)
    transition_speed = tactics.get("transition_speed", 5)
    
    tactics_multiplier = 1.0
    
    # 압박 강도에 따른 소모량 증가
    if action_type in ["tackle", "intercept", "dribble"]:
        tactics_multiplier *= 1.0 + (pressing - 5) * 0.15
    
    # 공격성에 따른 공격 행동 소모량 증가
    if action_type in ["dribble", "shoot", "transition_dash"]:
        tactics_multiplier *= 1.0 + (attack - 5) * 0.1
    
    # 전환 속도에 따른 전환 행동 소모량 증가
    if action_type == "transition_dash":
        tactics_multiplier *= 1.0 + (transition_speed - 5) * 0.1
    
    # STA 스탯에 따른 소모량 감소
    sta_multiplier = 1.0 - (player_sta - 5) * 0.05
    sta_multiplier = max(sta_multiplier, 0.7)  # 최소 0.7배
    
    # 최종 소모량
    final_cost = base_cost * tactics_multiplier * sta_multiplier
    
    return max(final_cost, 0.1)  # 최소 0.1


def apply_stamina_penalty(stamina: float) -> int:
    """체력 수준에 따른 스탯 페널티 반환
    
    Args:
        stamina: 현재 체력 (0-100)
    
    Returns:
        스탯 페널티 (0-4)
    """
    if stamina >= 70:
        return 0
    elif stamina >= 50:
        return 1
    elif stamina >= 30:
        return 2
    elif stamina >= 10:
        return 3
    else:
        return 4


def apply_half_time_rest(stamina: float) -> float:
    """후반 시작 시 체력 회복
    
    Args:
        stamina: 현재 체력
    
    Returns:
        회복된 체력 (최대 100)
    """
    return min(stamina + 20, 100.0)


def get_stamina_multiplier_for_action_frequency(stamina: float) -> float:
    """체력에 따른 행동 빈도 배율 반환
    
    체력이 낮을수록 고강도 행동 빈도 감소
    
    Args:
        stamina: 현재 체력
    
    Returns:
        행동 빈도 배율 (0.5-1.0)
    """
    if stamina >= 50:
        return 1.0
    elif stamina >= 30:
        return 0.8
    else:
        return 0.5
