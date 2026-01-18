"""Zone 시스템 단위 테스트"""

import pytest

from sim_soccer.field.zone import (
    BUILD_UP_ZONES,
    FINAL_THIRD_ZONES,
    MIDFIELD_ZONES,
    calculate_distance,
    coords_to_zone,
    get_zone_col,
    get_zone_row,
    is_backward_zone,
    is_central_zone,
    is_forward_zone,
    zone_to_coords,
)


def test_zone_to_coords():
    """Zone 번호를 좌표로 변환 테스트"""
    row, col = zone_to_coords(1)
    assert row == 0
    assert col == 0
    
    row, col = zone_to_coords(8)
    assert row == 2
    assert col == 1
    
    row, col = zone_to_coords(15)
    assert row == 4
    assert col == 2


def test_coords_to_zone():
    """좌표를 Zone 번호로 변환 테스트"""
    assert coords_to_zone(0, 0) == 1
    assert coords_to_zone(2, 1) == 8
    assert coords_to_zone(4, 2) == 15


def test_zone_invalid():
    """잘못된 Zone 번호 테스트"""
    with pytest.raises(ValueError):
        zone_to_coords(0)
    
    with pytest.raises(ValueError):
        zone_to_coords(16)
    
    with pytest.raises(ValueError):
        coords_to_zone(5, 0)
    
    with pytest.raises(ValueError):
        coords_to_zone(0, 3)


def test_calculate_distance():
    """Zone 간 거리 계산 테스트"""
    # 같은 Zone
    assert calculate_distance(1, 1) == 0
    
    # 같은 행
    assert calculate_distance(1, 2) == 1  # 좌측 후방 -> 중앙 후방
    assert calculate_distance(1, 3) == 2  # 좌측 후방 -> 우측 후방
    
    # 같은 열
    assert calculate_distance(2, 8) == 2  # 중앙 후방 -> 중앙 중앙
    
    # 대각선
    assert calculate_distance(1, 15) == 6  # 좌측 후방 -> 우측 전방


def test_get_zone_row():
    """Zone의 세로 위치 테스트"""
    assert get_zone_row(1) == 0  # 후방
    assert get_zone_row(8) == 2  # 중앙
    assert get_zone_row(15) == 4  # 전방


def test_get_zone_col():
    """Zone의 가로 위치 테스트"""
    assert get_zone_col(1) == 0  # 좌측
    assert get_zone_col(8) == 1  # 중앙
    assert get_zone_col(15) == 2  # 우측


def test_is_forward_zone():
    """전방 Zone 확인 테스트"""
    assert is_forward_zone(13) is True
    assert is_forward_zone(14) is True
    assert is_forward_zone(15) is True
    assert is_forward_zone(8) is False


def test_is_backward_zone():
    """후방 Zone 확인 테스트"""
    assert is_backward_zone(1) is True
    assert is_backward_zone(2) is True
    assert is_backward_zone(3) is True
    assert is_backward_zone(8) is False


def test_is_central_zone():
    """중앙 Zone 확인 테스트"""
    assert is_central_zone(2) is True
    assert is_central_zone(5) is True
    assert is_central_zone(8) is True
    assert is_central_zone(1) is False


def test_phase_zones():
    """Phase별 Zone 테스트"""
    # 빌드업 Zone은 후방 + 후중앙
    assert 1 in BUILD_UP_ZONES
    assert 5 in BUILD_UP_ZONES
    assert 8 not in BUILD_UP_ZONES
    
    # 중원 Zone은 중앙만
    assert 8 in MIDFIELD_ZONES
    assert 1 not in MIDFIELD_ZONES
    
    # 파이널 서드 Zone은 전중앙 + 전방
    assert 11 in FINAL_THIRD_ZONES
    assert 14 in FINAL_THIRD_ZONES
    assert 8 not in FINAL_THIRD_ZONES
