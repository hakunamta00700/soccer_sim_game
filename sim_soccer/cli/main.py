"""CLI 메인 실행 스크립트"""

import argparse
import sys
from pathlib import Path

from loguru import logger

from sim_soccer.core.simulator import MatchSimulator
from sim_soccer.io.reporter import print_match_report
from sim_soccer.io.team_loader import (
    PointSumError,
    PositionError,
    StatRangeError,
    TacticRangeError,
    ValidationError,
    load_team,
)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Football Manager 스타일 PvP 축구 시뮬레이션 게임"
    )
    parser.add_argument(
        "home_team_file",
        type=str,
        help="홈 팀 JSON 파일 경로",
    )
    parser.add_argument(
        "away_team_file",
        type=str,
        help="원정 팀 JSON 파일 경로",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="랜덤 시드 (재현 가능성을 위해)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="상세 로그 출력",
    )
    parser.add_argument(
        "--live",
        "-l",
        action="store_true",
        help="실시간 이벤트 출력 (게임 같은 형식)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="로깅 출력 비활성화",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=60.0,
        help="경기 진행 시간 (초 단위, 기본값: 60초)",
    )
    
    args = parser.parse_args()
    
    # 로깅 설정
    if args.quiet:
        logger.remove()  # 모든 로거 제거
    elif args.verbose:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")
    
    try:
        # 팀 로드
        logger.info(f"Loading home team from {args.home_team_file}")
        home_team = load_team(args.home_team_file)
        
        logger.info(f"Loading away team from {args.away_team_file}")
        away_team = load_team(args.away_team_file)
        
        # 시뮬레이션 실행
        logger.info("Starting match simulation...")
        simulator = MatchSimulator(random_seed=args.seed, live_output=args.live)
        match_result = simulator.simulate_match(
            home_team, away_team, args.seed, live_output=args.live, duration=args.duration
        )
        
        # 리포트 출력
        print_match_report(match_result)
        
        # 종료 코드 (승자에 따라)
        if match_result.winner == "home":
            sys.exit(0)
        elif match_result.winner == "away":
            sys.exit(0)
        else:
            sys.exit(0)  # 무승부도 정상 종료
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    
    except PointSumError as e:
        logger.error(f"Point sum error: {e}")
        sys.exit(1)
    
    except PositionError as e:
        logger.error(f"Position error: {e}")
        sys.exit(1)
    
    except StatRangeError as e:
        logger.error(f"Stat range error: {e}")
        sys.exit(1)
    
    except TacticRangeError as e:
        logger.error(f"Tactic range error: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
