"""TeamState 단위 테스트"""

import pytest

from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def create_test_player(player_id: int, position: str) -> PlayerState:
    """테스트용 선수 생성"""
    return PlayerState(
        player_id=player_id,
        name=f"Player {player_id}",
        position=position,
        stats={"PAS": 5, "DRI": 5, "SHO": 5, "SPA": 5, "TAC": 5, "INT": 5, "STA": 5},
    )


def test_team_creation():
    """팀 생성 테스트"""
    players = [create_test_player(i, "MF") for i in range(1, 12)]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    assert team.team_id == "test_team"
    assert team.team_name == "Test Team"
    assert len(team.players) == 11
    assert team.score == 0
    assert team.momentum == 0


def test_get_player_by_id():
    """선수 ID로 찾기 테스트"""
    players = [create_test_player(i, "MF") for i in range(1, 12)]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    player = team.get_player_by_id(5)
    assert player is not None
    assert player.player_id == 5
    
    player = team.get_player_by_id(99)
    assert player is None


def test_get_players_by_position():
    """포지션으로 선수 찾기 테스트"""
    players = [
        create_test_player(1, "GK"),
        create_test_player(2, "DF"),
        create_test_player(3, "DF"),
        create_test_player(4, "MF"),
        create_test_player(5, "MF"),
        create_test_player(6, "FW"),
    ]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    df_players = team.get_players_by_position("DF")
    assert len(df_players) == 2
    assert all(p.position == "DF" for p in df_players)


def test_get_average_stat():
    """평균 스탯 계산 테스트"""
    players = [
        PlayerState(
            player_id=1,
            name="Player 1",
            position="MF",
            stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
        ),
        PlayerState(
            player_id=2,
            name="Player 2",
            position="MF",
            stats={"PAS": 6, "DRI": 5, "SHO": 4, "SPA": 5, "TAC": 3, "INT": 4, "STA": 6},
        ),
    ]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    avg_pas = team.get_average_stat("PAS")
    assert avg_pas == (8 + 6) / 2


def test_get_ball_holder():
    """공을 가진 선수 찾기 테스트"""
    players = [create_test_player(i, "MF") for i in range(1, 12)]
    players[0].has_ball = True
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    ball_holder = team.get_ball_holder()
    assert ball_holder is not None
    assert ball_holder.player_id == 1
    assert ball_holder.has_ball is True


def test_set_ball_holder():
    """공 소유자 설정 테스트"""
    players = [create_test_player(i, "MF") for i in range(1, 12)]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    team.set_ball_holder(5)
    assert team.get_ball_holder().player_id == 5
    
    team.set_ball_holder(None)
    assert team.get_ball_holder() is None


def test_default_tactics():
    """기본 전술 설정 테스트"""
    players = [create_test_player(i, "MF") for i in range(1, 12)]
    team = TeamState(
        team_id="test_team",
        team_name="Test Team",
        formation="1-4-4-2",
        players=players,
    )
    
    assert team.tactics["attack"] == 5
    assert team.tactics["pass_style"] == 5
    assert team.tactics["pressing"] == 5
