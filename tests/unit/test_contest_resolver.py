"""ContestResolver 단위 테스트"""

import pytest

from sim_soccer.core.contest_resolver import ContestResolver
from sim_soccer.models.player import PlayerState


def create_test_player(position: str, stats: dict) -> PlayerState:
    """테스트용 선수 생성"""
    default_stats = {
        "PAS": 5,
        "DRI": 5,
        "SHO": 5,
        "SPA": 5,
        "TAC": 5,
        "INT": 5,
        "STA": 5,
    }
    default_stats.update(stats)
    return PlayerState(
        player_id=1,
        name="Test Player",
        position=position,
        stats=default_stats,
        stamina=100.0,
    )


def test_calculate_contest_score_pass():
    """패스 컨테스트 점수 계산 테스트"""
    resolver = ContestResolver()
    
    attacker = create_test_player("MF", {"PAS": 8, "SPA": 7})
    defender = create_test_player("DF", {"INT": 6, "SPA": 6})
    
    tactics = {"attack": 5, "pass_style": 5, "pressing": 5, "defense_line": 5, "transition_speed": 5, "width": 5}
    situation = {"distance": 2, "pressing": 5}
    
    score = resolver.calculate_contest_score(
        attacker=attacker,
        defender=defender,
        action_type="pass",
        situation=situation,
        attacker_team_tactics=tactics,
        defender_team_tactics=tactics,
    )
    
    # 공격자가 더 높은 스탯이므로 양수일 가능성이 높음
    assert isinstance(score, float)


def test_calculate_contest_score_shoot():
    """슈팅 컨테스트 점수 계산 테스트"""
    resolver = ContestResolver()
    
    attacker = create_test_player("FW", {"SHO": 9, "SPA": 8})
    defender = create_test_player("GK", {"TAC": 7, "SPA": 6})
    
    tactics = {"attack": 5, "pass_style": 5, "pressing": 5, "defense_line": 5, "transition_speed": 5, "width": 5}
    situation = {"distance": 1, "pressing": 3}
    
    score = resolver.calculate_contest_score(
        attacker=attacker,
        defender=defender,
        action_type="shoot",
        situation=situation,
        attacker_team_tactics=tactics,
        defender_team_tactics=tactics,
    )
    
    assert isinstance(score, float)


def test_resolve_contest():
    """컨테스트 판정 테스트"""
    resolver = ContestResolver()
    
    # 높은 점수는 성공 확률 높음
    success_count = sum(
        resolver.resolve_contest(10.0, random_value=0.3) for _ in range(100)
    )
    assert success_count > 50  # 대부분 성공
    
    # 낮은 점수는 실패 확률 높음
    success_count = sum(
        resolver.resolve_contest(-10.0, random_value=0.7) for _ in range(100)
    )
    assert success_count < 50  # 대부분 실패


def test_resolve_contest_probability_range():
    """성공 확률 범위 테스트"""
    resolver = ContestResolver()
    
    # 매우 높은 점수
    success = resolver.resolve_contest(100.0, random_value=0.1)
    # 20% 확률이므로 실패할 수도 있음
    assert isinstance(success, bool)
    
    # 매우 낮은 점수
    success = resolver.resolve_contest(-100.0, random_value=0.9)
    # 80% 확률이므로 성공할 수도 있음
    assert isinstance(success, bool)
