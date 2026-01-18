"""Zone 시스템"""

from typing import Tuple


# Zone 번호 체계 (설계 문서 참조)
# 후방:     [1] [2] [3]
# 후중앙:   [4] [5] [6]
# 중앙:     [7] [8] [9]
# 전중앙:   [10][11][12]
# 전방:     [13][14][15]
#
# [1]=좌측 후방, [2]=중앙 후방, [3]=우측 후방
# ...
# [13]=좌측 전방, [14]=중앙 전방, [15]=우측 전방

ZONE_ROWS = 5  # 세로 5등분
ZONE_COLS = 3  # 가로 3등분
TOTAL_ZONES = ZONE_ROWS * ZONE_COLS  # 15개


def zone_to_coords(zone: int) -> Tuple[int, int]:
    """Zone 번호를 좌표(row, col)로 변환
    
    Args:
        zone: Zone 번호 (1-15)
    
    Returns:
        (row, col) 튜플 (0-based)
    """
    if not (1 <= zone <= TOTAL_ZONES):
        raise ValueError(f"Zone must be between 1 and {TOTAL_ZONES}, got {zone}")
    
    zone_idx = zone - 1  # 0-based로 변환
    row = zone_idx // ZONE_COLS
    col = zone_idx % ZONE_COLS
    return (row, col)


def coords_to_zone(row: int, col: int) -> int:
    """좌표를 Zone 번호로 변환
    
    Args:
        row: 세로 위치 (0-4)
        col: 가로 위치 (0-2)
    
    Returns:
        Zone 번호 (1-15)
    """
    if not (0 <= row < ZONE_ROWS):
        raise ValueError(f"Row must be between 0 and {ZONE_ROWS-1}, got {row}")
    if not (0 <= col < ZONE_COLS):
        raise ValueError(f"Col must be between 0 and {ZONE_COLS-1}, got {col}")
    
    zone = row * ZONE_COLS + col + 1
    return zone


def calculate_distance(zone1: int, zone2: int) -> int:
    """두 Zone 간의 거리를 계산
    
    거리 = |Zone1의 세로 위치 - Zone2의 세로 위치| + |Zone1의 가로 위치 - Zone2의 가로 위치|
    
    Args:
        zone1: 첫 번째 Zone 번호
        zone2: 두 번째 Zone 번호
    
    Returns:
        거리 (정수)
    """
    row1, col1 = zone_to_coords(zone1)
    row2, col2 = zone_to_coords(zone2)
    
    distance = abs(row1 - row2) + abs(col1 - col2)
    return distance


def get_zone_row(zone: int) -> int:
    """Zone의 세로 위치(row)를 반환
    
    Returns:
        0 (후방) ~ 4 (전방)
    """
    row, _ = zone_to_coords(zone)
    return row


def get_zone_col(zone: int) -> int:
    """Zone의 가로 위치(col)를 반환
    
    Returns:
        0 (좌측) ~ 2 (우측)
    """
    _, col = zone_to_coords(zone)
    return col


def is_forward_zone(zone: int) -> bool:
    """전방 Zone인지 확인 (전방 = row 4)"""
    return get_zone_row(zone) == 4


def is_backward_zone(zone: int) -> bool:
    """후방 Zone인지 확인 (후방 = row 0)"""
    return get_zone_row(zone) == 0


def is_central_zone(zone: int) -> bool:
    """중앙 Zone인지 확인 (중앙 = col 1)"""
    return get_zone_col(zone) == 1


def get_zones_by_row(row: int) -> list[int]:
    """특정 row의 모든 Zone 번호를 반환"""
    if not (0 <= row < ZONE_ROWS):
        raise ValueError(f"Row must be between 0 and {ZONE_ROWS-1}, got {row}")
    
    zones = []
    for col in range(ZONE_COLS):
        zones.append(coords_to_zone(row, col))
    return zones


def get_zones_by_col(col: int) -> list[int]:
    """특정 col의 모든 Zone 번호를 반환"""
    if not (0 <= col < ZONE_COLS):
        raise ValueError(f"Col must be between 0 and {ZONE_COLS-1}, got {col}")
    
    zones = []
    for row in range(ZONE_ROWS):
        zones.append(coords_to_zone(row, col))
    return zones


# Phase별 기본 Zone 정의
BUILD_UP_ZONES = get_zones_by_row(0) + get_zones_by_row(1)  # 후방 + 후중앙
MIDFIELD_ZONES = get_zones_by_row(2)  # 중앙
FINAL_THIRD_ZONES = get_zones_by_row(3) + get_zones_by_row(4)  # 전중앙 + 전방
