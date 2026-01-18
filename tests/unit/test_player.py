"""PlayerState 단위 테스트"""

import pytest

from sim_soccer.models.player import PlayerState, POSITION_WEIGHTS


def test_player_creation():
    """선수 생성 테스트"""
    player = PlayerState(
        player_id=1,
        name="Test Player",
        position="MF",
        stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
    )
    
    assert player.player_id == 1
    assert player.name == "Test Player"
    assert player.position == "MF"
    assert player.stats["PAS"] == 8
    assert player.position_weights == POSITION_WEIGHTS["MF"]


def test_player_invalid_position():
    """잘못된 포지션 테스트"""
    with pytest.raises(ValueError):
        PlayerState(
            player_id=1,
            name="Test Player",
            position="INVALID",
            stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
        )


def test_get_weighted_stat():
    """가중치 적용된 스탯 테스트"""
    player = PlayerState(
        player_id=1,
        name="Test Player",
        position="MF",
        stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
    )
    
    # MF의 PAS 가중치는 1.2
    weighted_pas = player.get_weighted_stat("PAS")
    assert weighted_pas == 8 * 1.2
    
    # MF의 SHO 가중치는 0.7
    weighted_sho = player.get_weighted_stat("SHO")
    assert weighted_sho == 6 * 0.7


def test_get_effective_stat():
    """체력 페널티가 적용된 유효 스탯 테스트"""
    player = PlayerState(
        player_id=1,
        name="Test Player",
        position="MF",
        stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
        stamina=40.0,  # 체력 낮음
    )
    
    # 체력 페널티는 2 (40 >= 30)
    effective_stat = player.get_effective_stat("PAS", stamina_penalty=2)
    weighted_stat = player.get_weighted_stat("PAS")
    assert effective_stat == weighted_stat - 2


def test_calculate_stamina_penalty():
    """체력 페널티 계산 테스트"""
    player = PlayerState(
        player_id=1,
        name="Test Player",
        position="MF",
        stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
    )
    
    player.stamina = 100.0
    assert player.calculate_stamina_penalty() == 0
    
    player.stamina = 50.0
    assert player.calculate_stamina_penalty() == 1
    
    player.stamina = 30.0
    assert player.calculate_stamina_penalty() == 2
    
    player.stamina = 10.0
    assert player.calculate_stamina_penalty() == 3
    
    player.stamina = 5.0
    assert player.calculate_stamina_penalty() == 4


def test_get_total_points():
    """총 포인트 계산 테스트"""
    player = PlayerState(
        player_id=1,
        name="Test Player",
        position="MF",
        stats={"PAS": 8, "DRI": 7, "SHO": 6, "SPA": 7, "TAC": 5, "INT": 6, "STA": 8},
    )
    
    total_points = player.get_total_points()
    assert total_points == 8 + 7 + 6 + 7 + 5 + 6 + 8


def test_position_weights():
    """포지션별 가중치 테스트"""
    # GK는 TAC, INT가 높음
    gk = PlayerState(
        player_id=1,
        name="GK",
        position="GK",
        stats={"PAS": 1, "DRI": 1, "SHO": 1, "SPA": 2, "TAC": 2, "INT": 2, "STA": 1},
    )
    assert gk.position_weights["TAC"] == 1.5
    assert gk.position_weights["PAS"] == 0.3
    
    # FW는 SHO, DRI가 높음
    fw = PlayerState(
        player_id=2,
        name="FW",
        position="FW",
        stats={"PAS": 1, "DRI": 2, "SHO": 2, "SPA": 1, "TAC": 1, "INT": 1, "STA": 1},
    )
    assert fw.position_weights["SHO"] == 1.5
    assert fw.position_weights["DRI"] == 1.3
    assert fw.position_weights["TAC"] == 0.4
