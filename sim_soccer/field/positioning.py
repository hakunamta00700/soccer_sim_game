"""선수 위치 관리"""

from typing import List, Optional

from sim_soccer.field.zone import (
    BUILD_UP_ZONES,
    FINAL_THIRD_ZONES,
    MIDFIELD_ZONES,
    get_zones_by_row,
)
from sim_soccer.models.player import PlayerState
from sim_soccer.models.team import TeamState


def get_default_zone_for_position(position: str, phase: str, is_attacking: bool) -> int:
    """포지션과 Phase에 따른 기본 Zone 반환
    
    Args:
        position: 선수 포지션 ("GK", "DF", "MF", "FW")
        phase: 현재 Phase
        is_attacking: 공격 중인지 여부
    
    Returns:
        기본 Zone 번호
    """
    if phase == "build_up":
        if position == "GK":
            return 2  # 중앙 후방
        elif position == "DF":
            # 후방과 후중앙에 분산
            return 2  # 기본값은 중앙 후방
        elif position == "MF":
            return 5  # 중앙 후중앙
        else:  # FW
            return 8  # 중앙 중앙
    
    elif phase == "midfield":
        if position == "GK":
            return 2  # 중앙 후방
        elif position == "DF":
            return 5  # 중앙 후중앙
        elif position == "MF":
            return 8  # 중앙 중앙
        else:  # FW
            return 11  # 중앙 전중앙
    
    elif phase == "final_third":
        if position == "GK":
            return 2  # 중앙 후방
        elif position == "DF":
            return 5  # 중앙 후중앙
        elif position == "MF":
            return 8  # 중앙 중앙
        else:  # FW
            return 14  # 중앙 전방
    
    elif phase == "defense":
        if position == "GK":
            return 2  # 중앙 후방
        elif position == "DF":
            return 2  # 중앙 후방
        elif position == "MF":
            return 5  # 중앙 후중앙
        else:  # FW
            return 8  # 중앙 중앙
    
    else:  # transition
        # 전환 Phase에서는 현재 위치 유지 또는 기본 위치
        return get_default_zone_for_position(position, "midfield", is_attacking)


def initialize_player_positions(team: TeamState, phase: str, is_attacking: bool):
    """팀의 선수들을 Phase에 맞게 초기 위치 설정"""
    for player in team.players:
        player.zone = get_default_zone_for_position(
            player.position, phase, is_attacking
        )


def get_players_in_zone(team: TeamState, zone: int) -> List[PlayerState]:
    """특정 Zone에 있는 선수들을 반환"""
    return [p for p in team.players if p.zone == zone]


def get_players_in_zones(team: TeamState, zones: List[int]) -> List[PlayerState]:
    """여러 Zone에 있는 선수들을 반환"""
    return [p for p in team.players if p.zone in zones]


def get_players_by_phase(team: TeamState, phase: str) -> List[PlayerState]:
    """Phase에 해당하는 Zone에 있는 선수들을 반환"""
    if phase == "build_up":
        zones = BUILD_UP_ZONES
    elif phase == "midfield":
        zones = MIDFIELD_ZONES
    elif phase == "final_third":
        zones = FINAL_THIRD_ZONES
    else:
        zones = list(range(1, 16))  # 모든 Zone
    
    return get_players_in_zones(team, zones)


def find_nearest_player(
    team: TeamState, target_zone: int, exclude_player_id: Optional[int] = None
) -> Optional[PlayerState]:
    """특정 Zone에 가장 가까운 선수를 찾아 반환"""
    from sim_soccer.field.zone import calculate_distance
    
    nearest_player = None
    min_distance = float("inf")
    
    for player in team.players:
        if exclude_player_id and player.player_id == exclude_player_id:
            continue
        
        distance = calculate_distance(player.zone, target_zone)
        if distance < min_distance:
            min_distance = distance
            nearest_player = player
    
    return nearest_player
