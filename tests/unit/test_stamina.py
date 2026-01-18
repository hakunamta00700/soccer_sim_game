"""체력 시스템 단위 테스트"""

import pytest

from sim_soccer.systems.stamina import (
    ACTION_STAMINA_COST,
    apply_half_time_rest,
    apply_stamina_penalty,
    calculate_stamina_cost,
    get_stamina_multiplier_for_action_frequency,
)


def test_calculate_stamina_cost():
    """체력 소모량 계산 테스트"""
    tactics = {"attack": 5, "pressing": 5, "transition_speed": 5}
    
    # 기본 패스 소모량
    cost = calculate_stamina_cost("pass", tactics, 5)
    assert cost > 0
    assert cost == pytest.approx(ACTION_STAMINA_COST["pass"] * 1.0 * 1.0, abs=0.1)
    
    # 드리블은 더 많이 소모
    dribble_cost = calculate_stamina_cost("dribble", tactics, 5)
    pass_cost = calculate_stamina_cost("pass", tactics, 5)
    assert dribble_cost > pass_cost
    
    # 태클은 가장 많이 소모
    tackle_cost = calculate_stamina_cost("tackle", tactics, 5)
    assert tackle_cost > dribble_cost


def test_stamina_cost_with_tactics():
    """전술에 따른 체력 소모량 테스트"""
    base_tactics = {"attack": 5, "pressing": 5, "transition_speed": 5}
    high_pressing_tactics = {"attack": 5, "pressing": 10, "transition_speed": 5}
    
    base_cost = calculate_stamina_cost("tackle", base_tactics, 5)
    high_pressing_cost = calculate_stamina_cost("tackle", high_pressing_tactics, 5)
    
    # 높은 압박은 더 많은 체력 소모
    assert high_pressing_cost > base_cost


def test_stamina_cost_with_stat():
    """STA 스탯에 따른 체력 소모량 테스트"""
    tactics = {"attack": 5, "pressing": 5, "transition_speed": 5}
    
    low_sta_cost = calculate_stamina_cost("pass", tactics, 1)
    high_sta_cost = calculate_stamina_cost("pass", tactics, 10)
    
    # 높은 STA 스탯은 적은 체력 소모
    assert high_sta_cost < low_sta_cost


def test_apply_stamina_penalty():
    """체력 페널티 적용 테스트"""
    assert apply_stamina_penalty(100.0) == 0
    assert apply_stamina_penalty(70.0) == 0
    assert apply_stamina_penalty(50.0) == 1
    assert apply_stamina_penalty(30.0) == 2
    assert apply_stamina_penalty(10.0) == 3
    assert apply_stamina_penalty(5.0) == 4


def test_apply_half_time_rest():
    """후반 시작 시 체력 회복 테스트"""
    # 체력이 낮은 경우
    restored = apply_half_time_rest(30.0)
    assert restored == 50.0
    
    # 체력이 높은 경우
    restored = apply_half_time_rest(90.0)
    assert restored == 100.0  # 최대 100
    
    # 체력이 매우 낮은 경우
    restored = apply_half_time_rest(5.0)
    assert restored == 25.0


def test_get_stamina_multiplier():
    """체력에 따른 행동 빈도 배율 테스트"""
    assert get_stamina_multiplier_for_action_frequency(100.0) == 1.0
    assert get_stamina_multiplier_for_action_frequency(50.0) == 1.0
    assert get_stamina_multiplier_for_action_frequency(30.0) == 0.8
    assert get_stamina_multiplier_for_action_frequency(10.0) == 0.5
