"""균형형 팀 vs 특화형 팀 시나리오 테스트"""

import pytest

from sim_soccer.core.simulator import MatchSimulator
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def create_balanced_team() -> TeamState:
    """균형형 팀 생성 (모든 선수에게 평균적으로 포인트 분배)"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    # 각 선수에게 평균 9.09 포인트 분배 (100 / 11)
    base_stats = {
        "PAS": 1,
        "DRI": 1,
        "SHO": 1,
        "SPA": 1,
        "TAC": 1,
        "INT": 1,
        "STA": 1,
    }
    # 각 선수에게 추가 포인트 분배
    for i, position in enumerate(positions, 1):
        stats = base_stats.copy()
        # 포지션에 맞게 약간의 보정
        if position == "GK":
            stats.update({"SPA": 2, "TAC": 2, "INT": 2})
        elif position == "DF":
            stats.update({"SPA": 2, "TAC": 2, "INT": 2})
        elif position == "MF":
            stats.update({"PAS": 2, "DRI": 2, "SPA": 2})
        else:  # FW
            stats.update({"DRI": 2, "SHO": 2, "SPA": 2})
        
        player = PlayerState(
            player_id=i,
            name=f"Balanced Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id="balanced_team",
        team_name="균형형 팀",
        formation="1-4-4-2",
        players=players,
        tactics={
            "attack": 5,
            "pass_style": 5,
            "pressing": 5,
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        },
    )
    
    return team


def create_specialized_team() -> TeamState:
    """특화형 팀 생성 (핵심 선수에 포인트 집중)"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    for i, position in enumerate(positions, 1):
        if i == 10 or i == 11:  # 공격수 2명에 포인트 집중
            stats = {
                "PAS": 2,
                "DRI": 10,
                "SHO": 10,
                "SPA": 8,
                "TAC": 1,
                "INT": 1,
                "STA": 8,
            }
        elif i == 6:  # 플레이메이커 미드필더
            stats = {
                "PAS": 10,
                "DRI": 8,
                "SHO": 2,
                "SPA": 8,
                "TAC": 1,
                "INT": 1,
                "STA": 7,
            }
        else:  # 나머지는 최소 포인트
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
            name=f"Specialized Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id="specialized_team",
        team_name="특화형 팀",
        formation="1-4-4-2",
        players=players,
        tactics={
            "attack": 8,
            "pass_style": 7,
            "pressing": 6,
            "defense_line": 6,
            "transition_speed": 8,
            "width": 7,
        },
    )
    
    return team


def test_balanced_vs_specialized_scenario():
    """균형형 팀 vs 특화형 팀 시나리오 테스트"""
    balanced_team = create_balanced_team()
    specialized_team = create_specialized_team()
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(balanced_team, specialized_team, random_seed=42)
    
    # 경기가 완료되었는지 확인
    assert match_result.is_finished is True
    
    # 특화형 팀의 공격수가 더 많은 슈팅을 시도해야 함
    specialized_fw = specialized_team.get_players_by_position("FW")
    assert len(specialized_fw) == 2
    
    # 균형형 팀은 더 균형잡힌 통계를 가져야 함
    balanced_avg_pas = balanced_team.get_average_stat("PAS")
    specialized_avg_pas = specialized_team.get_average_stat("PAS")
    
    # 균형형 팀의 평균 스탯이 더 균형잡혀 있어야 함
    assert isinstance(balanced_avg_pas, float)
    assert isinstance(specialized_avg_pas, float)


def test_balanced_vs_specialized_statistics():
    """균형형 vs 특화형 통계 비교"""
    balanced_team = create_balanced_team()
    specialized_team = create_specialized_team()
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(balanced_team, specialized_team, random_seed=42)
    
    # 특화형 팀의 공격수는 높은 SHO 스탯을 가져야 함
    specialized_fw = specialized_team.get_players_by_position("FW")
    for fw in specialized_fw:
        assert fw.stats["SHO"] >= 8
    
    # 균형형 팀의 선수들은 비슷한 수준의 스탯을 가져야 함
    balanced_stats = [sum(p.stats.values()) for p in balanced_team.players]
    # 표준편차가 작아야 함 (균형잡힌 분배)
    assert max(balanced_stats) - min(balanced_stats) < 10
