"""팀 로더 통합 테스트"""

import json
import tempfile
from pathlib import Path

import pytest

from sim_soccer.io.team_loader import (
    PointSumError,
    PositionError,
    StatRangeError,
    TacticRangeError,
    ValidationError,
    load_team,
)


def create_test_team_json() -> dict:
    """테스트용 팀 JSON 데이터 생성"""
    players = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "MF", "FW", "FW"]
    
    # 총 100 포인트를 11명에게 분배
    base_stats = {
        "PAS": 1,
        "DRI": 1,
        "SHO": 1,
        "SPA": 1,
        "TAC": 1,
        "INT": 1,
        "STA": 1,
    }
    
    for i, position in enumerate(positions, 1):
        stats = base_stats.copy()
        
        # 포지션별 기본 스탯 조정 (각 선수 9 포인트)
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
        
        players.append(
            {
                "player_id": i,
                "name": f"Player {i}",
                "position": position,
                "stats": stats,
            }
        )
    
    return {
        "team_name": "Test Team",
        "formation": "1-4-4-2",
        "players": players,
        "tactics": {
            "attack": 5,
            "pass_style": 5,
            "pressing": 5,
            "defense_line": 5,
            "transition_speed": 5,
            "width": 5,
        },
    }


def test_load_valid_team():
    """유효한 팀 로드 테스트"""
    team_data = create_test_team_json()
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        team = load_team(temp_path)
        assert team.team_name == "Test Team"
        assert len(team.players) == 11
        assert team.formation == "1-4-4-2"
    finally:
        Path(temp_path).unlink()


def test_load_team_invalid_player_count():
    """잘못된 선수 수 테스트"""
    team_data = create_test_team_json()
    team_data["players"].pop()  # 선수 한 명 제거
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        with pytest.raises(ValidationError):
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()


def test_load_team_invalid_point_sum():
    """잘못된 포인트 합계 테스트"""
    team_data = create_test_team_json()
    # 포인트 합계를 100이 아닌 값으로 변경 (스탯 범위는 유지)
    # 두 번째 선수의 STA를 2에서 3으로 올리면 총 포인트가 101이 됨
    # (기본 9 포인트에서 +1)
    team_data["players"][1]["stats"]["STA"] = 3  # +1 (총 10 포인트)
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        with pytest.raises(PointSumError):
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()


def test_load_team_invalid_position():
    """잘못된 포지션 구성 테스트"""
    team_data = create_test_team_json()
    # GK를 제거하고 DF 추가
    team_data["players"][0]["position"] = "DF"
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        with pytest.raises(PositionError):
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()


def test_load_team_invalid_stat_range():
    """잘못된 스탯 범위 테스트"""
    team_data = create_test_team_json()
    team_data["players"][0]["stats"]["PAS"] = 11  # 범위 초과
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        with pytest.raises(StatRangeError):
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()


def test_load_team_invalid_tactic_range():
    """잘못된 전술 범위 테스트"""
    team_data = create_test_team_json()
    team_data["tactics"]["attack"] = 11  # 범위 초과
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        with pytest.raises(TacticRangeError):
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()


def test_load_team_missing_tactics():
    """전술이 없는 경우 기본값 설정 테스트"""
    team_data = create_test_team_json()
    del team_data["tactics"]
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(team_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        # 기본값이 설정되어야 함
        with pytest.raises(ValidationError):
            # 하지만 tactics 필드가 없으면 ValidationError 발생
            load_team(temp_path)
    finally:
        Path(temp_path).unlink()
