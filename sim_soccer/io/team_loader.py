"""팀 데이터 로드 및 검증"""

import json
from pathlib import Path
from typing import Dict, List

from loguru import logger

from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


class ValidationError(Exception):
    """검증 오류"""

    pass


class PlayerCountError(ValidationError):
    """선수 수 오류"""

    pass


class PointSumError(ValidationError):
    """포인트 합계 오류"""

    pass


class PositionError(ValidationError):
    """포지션 구성 오류"""

    pass


class StatRangeError(ValidationError):
    """스탯 범위 오류"""

    pass


class TacticRangeError(ValidationError):
    """전술 범위 오류"""

    pass


def load_team(file_path: str) -> TeamState:
    """JSON 파일에서 팀 데이터를 로드하고 검증하여 TeamState 객체 생성
    
    Args:
        file_path: JSON 파일 경로
    
    Returns:
        TeamState 객체
    
    Raises:
        ValidationError: 검증 실패 시
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Team file not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 검증
    validate_team_data(data)
    
    # TeamState 객체 생성
    team = create_team_from_data(data)
    
    logger.info(f"Team loaded: {team.team_name} ({team.formation})")
    
    return team


def validate_team_data(data: Dict):
    """팀 데이터 검증
    
    Args:
        data: 팀 데이터 딕셔너리
    
    Raises:
        ValidationError: 검증 실패 시
    """
    # 필수 필드 확인
    required_fields = ["team_name", "formation", "players", "tactics"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # 선수 수 검증
    players = data["players"]
    if len(players) != 11:
        raise PlayerCountError(f"Team must have exactly 11 players, got {len(players)}")
    
    # 선수 검증
    player_ids = set()
    gk_count = 0
    
    for player_data in players:
        # 필수 필드 확인
        if "player_id" not in player_data:
            raise ValidationError("Player missing player_id")
        if "name" not in player_data:
            raise ValidationError("Player missing name")
        if "position" not in player_data:
            raise ValidationError("Player missing position")
        if "stats" not in player_data:
            raise ValidationError("Player missing stats")
        
        # player_id 고유성 확인
        player_id = player_data["player_id"]
        if player_id in player_ids:
            raise ValidationError(f"Duplicate player_id: {player_id}")
        if not (1 <= player_id <= 11):
            raise ValidationError(f"player_id must be between 1 and 11, got {player_id}")
        player_ids.add(player_id)
        
        # 포지션 확인
        position = player_data["position"]
        if position not in ["GK", "DF", "MF", "FW"]:
            raise ValidationError(f"Invalid position: {position}")
        if position == "GK":
            gk_count += 1
        
        # 스탯 검증
        stats = player_data["stats"]
        required_stats = ["PAS", "DRI", "SHO", "SPA", "TAC", "INT", "STA"]
        for stat_name in required_stats:
            if stat_name not in stats:
                raise ValidationError(f"Player {player_id} missing stat: {stat_name}")
            stat_value = stats[stat_name]
            if not isinstance(stat_value, int) or not (1 <= stat_value <= 10):
                raise StatRangeError(
                    f"Player {player_id} stat {stat_name} must be between 1 and 10, got {stat_value}"
                )
    
    # GK 수 확인
    if gk_count != 1:
        raise PositionError(f"Team must have exactly 1 GK, got {gk_count}")
    
    # 포인트 합계 검증
    total_points = sum(sum(p["stats"].values()) for p in players)
    if total_points != 100:
        raise PointSumError(
            f"Total points must be exactly 100, got {total_points}"
        )
    
    # 전술 검증
    tactics = data["tactics"]
    required_tactics = [
        "attack",
        "pass_style",
        "pressing",
        "defense_line",
        "transition_speed",
        "width",
    ]
    for tactic_name in required_tactics:
        if tactic_name not in tactics:
            # 기본값 설정
            tactics[tactic_name] = 5
            continue
        tactic_value = tactics[tactic_name]
        if not isinstance(tactic_value, int) or not (1 <= tactic_value <= 10):
            raise TacticRangeError(
                f"Tactic {tactic_name} must be between 1 and 10, got {tactic_value}"
            )


def create_team_from_data(data: Dict) -> TeamState:
    """검증된 데이터로부터 TeamState 객체 생성"""
    players = []
    
    for player_data in data["players"]:
        player = PlayerState(
            player_id=player_data["player_id"],
            name=player_data["name"],
            position=player_data["position"],
            stats=player_data["stats"],
            zone=2,  # 기본 위치
        )
        players.append(player)
    
    team = TeamState(
        team_id=data.get("team_id", data["team_name"]),
        team_name=data["team_name"],
        formation=data["formation"],
        players=players,
        tactics=data["tactics"],
    )
    
    return team
