"""경기 리포트 생성"""

from typing import List

from loguru import logger

from sim_soccer.models.events import EventLog
from sim_soccer.models.match import MatchState


def generate_match_report(match_state: MatchState) -> str:
    """경기 리포트 생성
    
    Args:
        match_state: 경기 상태
    
    Returns:
        리포트 문자열
    """
    report_lines = []
    
    # 경기 요약
    report_lines.append("=" * 60)
    report_lines.append("경기 리포트")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    report_lines.append(
        f"{match_state.home_team.team_name} vs {match_state.away_team.team_name}"
    )
    report_lines.append(
        f"최종 스코어: {match_state.home_team.score} - {match_state.away_team.score}"
    )
    
    if match_state.winner == "home":
        report_lines.append(f"승자: {match_state.home_team.team_name}")
    elif match_state.winner == "away":
        report_lines.append(f"승자: {match_state.away_team.team_name}")
    else:
        report_lines.append("무승부")
    
    report_lines.append("")
    
    # 득점자
    goals = match_state.get_goals()
    if goals:
        report_lines.append("득점:")
        for goal in goals:
            team_name = (
                match_state.home_team.team_name
                if goal.team == "home"
                else match_state.away_team.team_name
            )
            player = None
            if goal.team == "home":
                player = match_state.home_team.get_player_by_id(goal.player_id or 0)
            else:
                player = match_state.away_team.get_player_by_id(goal.player_id or 0)
            
            player_name = player.name if player else "Unknown"
            minute = goal.tick // 60
            report_lines.append(f"  {minute}분 - {team_name}: {player_name}")
        report_lines.append("")
    
    # 통계
    report_lines.append("통계:")
    report_lines.append(f"  {match_state.home_team.team_name}:")
    report_lines.append(
        f"    슈팅: {match_state.home_team.stats['shots']} "
        f"(유효: {match_state.home_team.stats['shots_on_target']})"
    )
    report_lines.append(
        f"    패스: {match_state.home_team.stats['passes_completed']}/"
        f"{match_state.home_team.stats['passes_attempted']} "
        f"({match_state.home_team.stats['passes_completed'] / max(match_state.home_team.stats['passes_attempted'], 1) * 100:.1f}%)"
    )
    report_lines.append(
        f"    드리블: {match_state.home_team.stats['dribbles_successful']}/"
        f"{match_state.home_team.stats['dribbles_attempted']}"
    )
    report_lines.append("")
    
    report_lines.append(f"  {match_state.away_team.team_name}:")
    report_lines.append(
        f"    슈팅: {match_state.away_team.stats['shots']} "
        f"(유효: {match_state.away_team.stats['shots_on_target']})"
    )
    report_lines.append(
        f"    패스: {match_state.away_team.stats['passes_completed']}/"
        f"{match_state.away_team.stats['passes_attempted']} "
        f"({match_state.away_team.stats['passes_completed'] / max(match_state.away_team.stats['passes_attempted'], 1) * 100:.1f}%)"
    )
    report_lines.append(
        f"    드리블: {match_state.away_team.stats['dribbles_successful']}/"
        f"{match_state.away_team.stats['dribbles_attempted']}"
    )
    report_lines.append("")
    
    # 주요 이벤트
    important_events = [
        e
        for e in match_state.event_log
        if e.event_type in ["goal", "shoot", "tackle", "intercept"]
    ]
    
    if important_events:
        report_lines.append("주요 이벤트:")
        for event in important_events[:20]:  # 최대 20개만 표시
            minute = event.tick // 60
            team_name = (
                match_state.home_team.team_name
                if event.team == "home"
                else match_state.away_team.team_name
            )
            report_lines.append(
                f"  {minute}분 - {team_name}: {event.event_type} "
                f"({event.result})"
            )
        report_lines.append("")
    
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def print_match_report(match_state: MatchState):
    """경기 리포트 출력"""
    report = generate_match_report(match_state)
    print(report)
    logger.info("Match report generated")
