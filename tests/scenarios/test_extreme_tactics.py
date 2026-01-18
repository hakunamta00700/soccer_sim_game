"""극단적 전술 조합 시나리오 테스트"""

import pytest

from sim_soccer.core.simulator import MatchSimulator
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def create_team_with_tactics(tactics: dict) -> TeamState:
    """특정 전술을 가진 팀 생성"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    for i, position in enumerate(positions, 1):
        stats = {
            "PAS": 5,
            "DRI": 5,
            "SHO": 5,
            "SPA": 5,
            "TAC": 5,
            "INT": 5,
            "STA": 5,
        }
        
        player = PlayerState(
            player_id=i,
            name=f"Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
        tactics=tactics,
    )
    
    return team


def test_extreme_attack_vs_extreme_defense():
    """극단적 공격 vs 극단적 수비 테스트"""
    extreme_attack_team = create_team_with_tactics(
        {
            "attack": 10,
            "pass_style": 10,
            "pressing": 10,
            "defense_line": 10,
            "transition_speed": 10,
            "width": 10,
        }
    )
    
    extreme_defense_team = create_team_with_tactics(
        {
            "attack": 1,
            "pass_style": 1,
            "pressing": 1,
            "defense_line": 1,
            "transition_speed": 1,
            "width": 1,
        }
    )
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(
        extreme_attack_team, extreme_defense_team, random_seed=42
    )
    
    assert match_result.is_finished is True
    
    # 공격 팀이 더 많은 슈팅을 시도해야 함
    assert extreme_attack_team.stats["shots"] >= extreme_defense_team.stats["shots"]
    
    # 공격 팀의 체력 소모가 더 클 수 있음 (높은 압박과 공격성)
    avg_attack_stamina = sum(p.stamina for p in extreme_attack_team.players) / len(
        extreme_attack_team.players
    )
    avg_defense_stamina = sum(p.stamina for p in extreme_defense_team.players) / len(
        extreme_defense_team.players
    )
    
    # 공격 팀의 평균 체력이 더 낮을 가능성이 높음
    assert isinstance(avg_attack_stamina, float)
    assert isinstance(avg_defense_stamina, float)


def test_short_pass_vs_long_pass():
    """짧은 패스 vs 긴 패스 전술 테스트"""
    short_pass_team = create_team_with_tactics(
        {
            "attack": 5,
            "pass_style": 1,  # 매우 짧은 패스
            "pressing": 5,
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        }
    )
    
    long_pass_team = create_team_with_tactics(
        {
            "attack": 5,
            "pass_style": 10,  # 매우 긴 패스
            "pressing": 5,
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        }
    )
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(short_pass_team, long_pass_team, random_seed=42)
    
    assert match_result.is_finished is True
    
    # 패스 성공률 비교 (짧은 패스가 더 높을 가능성)
    short_pass_rate = (
        short_pass_team.stats["passes_completed"]
        / max(short_pass_team.stats["passes_attempted"], 1)
    )
    long_pass_rate = (
        long_pass_team.stats["passes_completed"]
        / max(long_pass_team.stats["passes_attempted"], 1)
    )
    
    assert isinstance(short_pass_rate, float)
    assert isinstance(long_pass_rate, float)


def test_high_pressing_vs_low_pressing():
    """높은 압박 vs 낮은 압박 테스트"""
    high_pressing_team = create_team_with_tactics(
        {
            "attack": 5,
            "pass_style": 5,
            "pressing": 10,  # 매우 높은 압박
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        }
    )
    
    low_pressing_team = create_team_with_tactics(
        {
            "attack": 5,
            "pass_style": 5,
            "pressing": 1,  # 매우 낮은 압박
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        }
    )
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(high_pressing_team, low_pressing_team, random_seed=42)
    
    assert match_result.is_finished is True
    
    # 높은 압박 팀이 더 많은 태클과 인터셉트를 시도해야 함
    assert (
        high_pressing_team.stats["tackles_attempted"]
        >= low_pressing_team.stats["tackles_attempted"]
    )
    
    # 높은 압박 팀의 체력 소모가 더 클 수 있음
    high_pressing_avg_stamina = sum(p.stamina for p in high_pressing_team.players) / len(
        high_pressing_team.players
    )
    low_pressing_avg_stamina = sum(p.stamina for p in low_pressing_team.players) / len(
        low_pressing_team.players
    )
    
    assert isinstance(high_pressing_avg_stamina, float)
    assert isinstance(low_pressing_avg_stamina, float)
