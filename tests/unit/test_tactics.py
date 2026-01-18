"""전술 시스템 단위 테스트"""

import pytest

from sim_soccer.systems.tactics import (
    calculate_attack_bonus,
    calculate_defense_line_bonus,
    calculate_pass_style_bonus,
    calculate_pressing_bonus,
    calculate_tactics_bonus,
    calculate_transition_speed_bonus,
    calculate_width_bonus,
    get_phase_transition_probability,
)


def test_calculate_attack_bonus():
    """공격성 보정치 테스트"""
    # 기본값 (5)
    bonus = calculate_attack_bonus(5, "pass")
    assert bonus == pytest.approx(1.0, abs=0.01)
    
    # 높은 공격성 (10)
    bonus = calculate_attack_bonus(10, "dribble")
    assert bonus > 1.0
    
    # 낮은 공격성 (1)
    bonus = calculate_attack_bonus(1, "dribble")
    assert bonus < 1.0


def test_calculate_pass_style_bonus():
    """패스 스타일 보정치 테스트"""
    # 짧은 패스 (1)
    bonus = calculate_pass_style_bonus(1, 0)
    assert bonus > 1.0
    
    # 긴 패스 (10)
    bonus = calculate_pass_style_bonus(10, 0)
    assert bonus < 1.0
    
    # 거리가 멀수록 짧은 패스는 페널티
    short_pass_close = calculate_pass_style_bonus(1, 0)
    short_pass_far = calculate_pass_style_bonus(1, 5)
    assert short_pass_far < short_pass_close


def test_calculate_pressing_bonus():
    """압박 강도 보정치 테스트"""
    # 인터셉트에 큰 영향
    bonus = calculate_pressing_bonus(10, "intercept")
    assert bonus > 1.0
    
    # 태클에도 큰 영향
    bonus = calculate_pressing_bonus(10, "tackle")
    assert bonus > 1.0
    
    # 낮은 압박
    bonus = calculate_pressing_bonus(1, "intercept")
    assert bonus < 1.0


def test_calculate_defense_line_bonus():
    """수비 라인 보정치 테스트"""
    # 공격 시 상향 라인은 보너스
    bonus_attacking = calculate_defense_line_bonus(10, True)
    assert bonus_attacking > 1.0
    
    # 수비 시 하향 라인은 보너스
    bonus_defending = calculate_defense_line_bonus(1, False)
    assert bonus_defending > 1.0


def test_calculate_transition_speed_bonus():
    """전환 속도 보정치 테스트"""
    bonus = calculate_transition_speed_bonus(10)
    assert bonus > 1.0
    
    bonus = calculate_transition_speed_bonus(1)
    assert bonus < 1.0


def test_calculate_width_bonus():
    """폭 보정치 테스트"""
    # 사이드 플레이에 큰 영향
    bonus = calculate_width_bonus(10, "side_play")
    assert bonus > 1.0
    
    # 공간 감각에도 영향
    bonus = calculate_width_bonus(10, "space_sense")
    assert bonus > 1.0


def test_calculate_tactics_bonus():
    """전술 보정치 종합 계산 테스트"""
    tactics = {
        "attack": 8,
        "pass_style": 3,
        "pressing": 7,
        "defense_line": 6,
        "transition_speed": 8,
        "width": 7,
    }
    
    # 공격 행동
    bonus = calculate_tactics_bonus(tactics, "dribble")
    assert bonus > 1.0
    
    # 패스 행동
    bonus = calculate_tactics_bonus(tactics, "pass", {"distance": 2})
    assert bonus != 1.0


def test_get_phase_transition_probability():
    """Phase 전환 확률 테스트"""
    tactics = {
        "attack": 5,
        "pass_style": 5,
        "pressing": 5,
        "defense_line": 5,
        "transition_speed": 5,
        "width": 5,
    }
    
    # 기본 확률 범위 확인
    prob = get_phase_transition_probability(tactics, "build_up", 5.0)
    assert 0.15 <= prob <= 0.5
    
    # 높은 스탯은 전환 확률 증가
    prob_high = get_phase_transition_probability(tactics, "build_up", 8.0)
    prob_low = get_phase_transition_probability(tactics, "build_up", 2.0)
    assert prob_high > prob_low
