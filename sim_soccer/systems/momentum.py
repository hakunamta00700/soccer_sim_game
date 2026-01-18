"""모멘텀 시스템"""

from typing import Dict


# 이벤트별 모멘텀 변화 (설계 문서 참조)
MOMENTUM_CHANGES: Dict[str, int] = {
    "goal_scored": 3,
    "goal_conceded": -3,
    "major_chance_created": 1,
    "major_chance_missed": -1,
    "mistake": -1,  # 패스 실패 등
    "consecutive_success": 1,  # 연속 성공 (3회 이상)
}


def update_momentum(current_momentum: int, event_type: str) -> int:
    """모멘텀 업데이트
    
    Args:
        current_momentum: 현재 모멘텀 점수
        event_type: 이벤트 타입
    
    Returns:
        업데이트된 모멘텀 점수 (-10 ~ +10 범위)
    """
    change = MOMENTUM_CHANGES.get(event_type, 0)
    new_momentum = current_momentum + change
    
    # 범위 제한
    return max(-10, min(10, new_momentum))


def calculate_momentum_bonus(momentum: int, is_second_half: bool = False) -> float:
    """모멘텀에 따른 스탯 보정치 계산
    
    Args:
        momentum: 모멘텀 점수 (-10 ~ +10)
        is_second_half: 후반인지 여부
    
    Returns:
        보정치 (배율)
    """
    # 후반에는 모멘텀 효과 증가
    multiplier = 0.7 if is_second_half else 0.5
    
    bonus = momentum * multiplier * 0.01  # 최대 ±0.07 (후반) 또는 ±0.05 (전반)
    
    return 1.0 + bonus


def get_momentum_description(momentum: int) -> str:
    """모멘텀 점수에 대한 설명 반환"""
    if momentum >= 7:
        return "매우 높은 모멘텀"
    elif momentum >= 4:
        return "높은 모멘텀"
    elif momentum >= 1:
        return "약간 높은 모멘텀"
    elif momentum == 0:
        return "중립"
    elif momentum >= -3:
        return "약간 낮은 모멘텀"
    elif momentum >= -6:
        return "낮은 모멘텀"
    else:
        return "매우 낮은 모멘텀"
