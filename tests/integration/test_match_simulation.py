"""경기 시뮬레이션 통합 테스트"""

import pytest

from sim_soccer.core.simulator import MatchSimulator
from sim_soccer.io.team_loader import load_team
from sim_soccer.models.match import MatchState
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def create_simple_team(team_name: str) -> TeamState:
    """간단한 테스트 팀 생성"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    # 총 100 포인트를 11명에게 분배
    # 각 선수 기본 9 포인트 (9 × 11 = 99), 마지막 선수만 10 포인트 = 총 100
    for i, position in enumerate(positions, 1):
        # 기본 스탯 (각 1) = 7 포인트
        stats = {
            "PAS": 1,
            "DRI": 1,
            "SHO": 1,
            "SPA": 1,
            "TAC": 1,
            "INT": 1,
            "STA": 1,
        }
        
        # 포지션별로 2 포인트 추가 (총 9 포인트)
        if position == "GK":
            stats["SPA"] = 2
            stats["TAC"] = 2  # 7 + 2 = 9
        elif position == "DF":
            stats["SPA"] = 2
            stats["TAC"] = 2  # 7 + 2 = 9
        elif position == "MF":
            stats["PAS"] = 2
            stats["DRI"] = 2  # 7 + 2 = 9
        else:  # FW
            stats["DRI"] = 2
            stats["SHO"] = 2  # 7 + 2 = 9
        
        # 마지막 선수만 추가 포인트 (총 10 포인트)
        if i == 11:
            if position == "FW":
                stats["SHO"] = 3  # +1 (총 10)
            else:
                stats["STA"] = 2  # +1 (총 10)
        
        player = PlayerState(
            player_id=i,
            name=f"{team_name} Player {i}",
            position=position,
            stats=stats,
        )
        players.append(player)
    
    team = TeamState(
        team_id=team_name.lower().replace(" ", "_"),
        team_name=team_name,
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


def test_match_simulation_basic():
    """기본 경기 시뮬레이션 테스트"""
    home_team = create_simple_team("Home Team")
    away_team = create_simple_team("Away Team")
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(home_team, away_team, random_seed=42)
    
    # 경기가 완료되었는지 확인
    assert match_result.is_finished is True
    assert match_result.winner in ["home", "away", "draw"]
    
    # 점수는 0 이상
    assert match_result.home_team.score >= 0
    assert match_result.away_team.score >= 0
    
    # 경기 시간 확인
    assert match_result.tick == MatchSimulator.TOTAL_TICKS - 1
    
    # 후반 확인
    assert match_result.half == 2


def test_match_simulation_reproducibility():
    """시뮬레이션 재현성 테스트"""
    simulator = MatchSimulator(random_seed=123)
    
    # 같은 시드로 두 번 실행 (매번 새로운 팀 객체 생성)
    home_team1 = create_simple_team("Home Team")
    away_team1 = create_simple_team("Away Team")
    result1 = simulator.simulate_match(home_team1, away_team1, random_seed=123)
    
    home_team2 = create_simple_team("Home Team")
    away_team2 = create_simple_team("Away Team")
    result2 = simulator.simulate_match(home_team2, away_team2, random_seed=123)
    
    # 결과가 동일해야 함
    assert result1.home_team.score == result2.home_team.score
    assert result1.away_team.score == result2.away_team.score
    assert result1.winner == result2.winner


def test_match_simulation_with_json_files():
    """JSON 파일을 사용한 경기 시뮬레이션 테스트"""
    try:
        home_team = load_team("examples/a.json")
        away_team = load_team("examples/b.json")
        
        simulator = MatchSimulator(random_seed=42)
        match_result = simulator.simulate_match(home_team, away_team, random_seed=42)
        
        assert match_result.is_finished is True
        assert isinstance(match_result.home_team.score, int)
        assert isinstance(match_result.away_team.score, int)
        
    except FileNotFoundError:
        pytest.skip("Example JSON files not found")


def test_match_simulation_events():
    """경기 이벤트 로그 테스트"""
    home_team = create_simple_team("Home Team")
    away_team = create_simple_team("Away Team")
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(home_team, away_team, random_seed=42)
    
    # 이벤트 로그가 있는지 확인
    assert len(match_result.event_log) > 0
    
    # 골 이벤트 확인
    goals = match_result.get_goals()
    assert len(goals) == match_result.home_team.score + match_result.away_team.score


def test_match_simulation_statistics():
    """경기 통계 테스트"""
    home_team = create_simple_team("Home Team")
    away_team = create_simple_team("Away Team")
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(home_team, away_team, random_seed=42)
    
    # 통계가 기록되었는지 확인
    assert match_result.home_team.stats["shots"] >= 0
    assert match_result.home_team.stats["passes_attempted"] >= 0
    
    # 슈팅 수는 유효 슈팅보다 크거나 같아야 함
    assert (
        match_result.home_team.stats["shots"]
        >= match_result.home_team.stats["shots_on_target"]
    )


def test_match_simulation_stamina():
    """체력 시스템 테스트"""
    home_team = create_simple_team("Home Team")
    away_team = create_simple_team("Away Team")
    
    simulator = MatchSimulator(random_seed=42)
    match_result = simulator.simulate_match(home_team, away_team, random_seed=42)
    
    # 경기 후 체력이 소모되었는지 확인
    for player in match_result.home_team.players:
        assert player.stamina <= 100.0
        # 후반 회복이 적용되었으므로 모든 선수의 체력이 0보다는 커야 함
        assert player.stamina >= 0.0
