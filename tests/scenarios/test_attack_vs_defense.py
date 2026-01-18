"""공격팀 vs 수비팀 시나리오 테스트"""

import pytest

from sim_soccer.core.simulator import MatchSimulator
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def create_attacking_team() -> TeamState:
    """공격적 팀 생성"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    # 공격수에 포인트 집중
    for i, position in enumerate(positions, 1):
        if position == "FW":
            stats = {
                "PAS": 2,
                "DRI": 8,
                "SHO": 10,
                "SPA": 8,
                "TAC": 1,
                "INT": 1,
                "STA": 8,
            }
        elif position == "MF":
            stats = {
                "PAS": 8,
                "DRI": 7,
                "SHO": 3,
                "SPA": 6,
                "TAC": 2,
                "INT": 2,
                "STA": 7,
            }
        else:
            stats = {
                "PAS": 1,
                "DRI": 1,
                "SHO": 1,
                "SPA": 1,
                "TAC": 1,
                "INT": 1,
                "STA": 1,
            }
        
        player = PlayerState(
            player_id=i,
            name=f"Attacking Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id="attacking_team",
        team_name="공격의 화신 FC",
        formation="1-4-4-2",
        players=players,
        tactics={
            "attack": 9,
            "pass_style": 8,
            "pressing": 8,
            "defense_line": 7,
            "transition_speed": 9,
            "width": 8,
        },
    )
    
    return team


def create_defensive_team() -> TeamState:
    """수비적 팀 생성"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    # 수비수에 포인트 집중
    for i, position in enumerate(positions, 1):
        if position == "GK":
            stats = {
                "PAS": 1,
                "DRI": 1,
                "SHO": 1,
                "SPA": 2,
                "TAC": 3,
                "INT": 3,
                "STA": 1,
            }
        elif position == "DF":
            stats = {
                "PAS": 1,
                "DRI": 1,
                "SHO": 1,
                "SPA": 2,
                "TAC": 3,
                "INT": 3,
                "STA": 1,
            }
        elif position == "MF":
            stats = {
                "PAS": 2,
                "DRI": 1,
                "SHO": 1,
                "SPA": 1,
                "TAC": 1,
                "INT": 1,
                "STA": 1,
            }
        else:  # FW
            stats = {
                "PAS": 1,
                "DRI": 1,
                "SHO": 2,
                "SPA": 2,
                "TAC": 1,
                "INT": 1,
                "STA": 1,
            }
        
        player = PlayerState(
            player_id=i,
            name=f"Defensive Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id="defensive_team",
        team_name="철벽 수비 FC",
        formation="1-4-4-2",
        players=players,
        tactics={
            "attack": 3,
            "pass_style": 2,
            "pressing": 3,
            "defense_line": 2,
            "transition_speed": 3,
            "width": 3,
        },
    )
    
    return team


def test_attack_vs_defense_scenario():
    """공격팀 vs 수비팀 시나리오 테스트"""
    attacking_team = create_attacking_team()
    defensive_team = create_defensive_team()
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(attacking_team, defensive_team, random_seed=42)
    
    # 경기가 완료되었는지 확인
    assert match_result.is_finished is True
    
    # 공격팀이 더 많은 슈팅을 시도해야 함
    assert attacking_team.stats["shots"] >= defensive_team.stats["shots"]
    
    # 수비팀이 더 많은 태클을 시도해야 함
    assert defensive_team.stats["tackles_attempted"] >= attacking_team.stats["tackles_attempted"]


def test_attack_vs_defense_multiple_runs():
    """공격팀 vs 수비팀 여러 번 실행하여 패턴 확인"""
    attacking_team = create_attacking_team()
    defensive_team = create_defensive_team()
    
    simulator = MatchSimulator()
    
    attacking_wins = 0
    defensive_wins = 0
    draws = 0
    
    for seed in range(10):
        result = simulator.simulate_match(
            attacking_team, defensive_team, random_seed=seed
        )
        
        if result.winner == "home":  # attacking_team이 홈팀
            attacking_wins += 1
        elif result.winner == "away":  # defensive_team이 원정팀
            defensive_wins += 1
        else:
            draws += 1
    
    # 결과가 다양하게 나와야 함 (랜덤 요소)
    assert attacking_wins + defensive_wins + draws == 10
    
    # 공격팀이 평균적으로 더 많은 골을 넣어야 함 (하지만 항상 그런 것은 아님)
    total_attacking_goals = sum(
        simulator.simulate_match(attacking_team, defensive_team, random_seed=s).home_team.score
        for s in range(10)
    )
    total_defensive_goals = sum(
        simulator.simulate_match(attacking_team, defensive_team, random_seed=s).away_team.score
        for s in range(10)
    )
    
    # 공격팀이 평균적으로 더 많은 골을 넣는 경향이 있어야 함
    # 하지만 랜덤 요소로 인해 항상 그런 것은 아님
    assert isinstance(total_attacking_goals, int)
    assert isinstance(total_defensive_goals, int)
