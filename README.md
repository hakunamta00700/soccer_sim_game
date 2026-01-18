# sim_soccer

Football Manager 스타일 PvP 축구 시뮬레이션 게임

## 설치

```bash
uv sync
```

## 사용법

### CLI 사용

```bash
python -m sim_soccer.cli.main examples/a.json examples/b.json
```

### 라이브러리로 사용

```python
from sim_soccer.io.team_loader import load_team
from sim_soccer.core.simulator import MatchSimulator

# 팀 로드
home_team = load_team("examples/a.json")
away_team = load_team("examples/b.json")

# 시뮬레이션 실행
simulator = MatchSimulator()
match_result = simulator.simulate_match(home_team, away_team, random_seed=42)

# 결과 확인
print(f"최종 스코어: {match_result.home_team.score} - {match_result.away_team.score}")
```

## 프로젝트 구조

- `sim_soccer/models/`: 데이터 모델 (PlayerState, TeamState, MatchState 등)
- `sim_soccer/core/`: 핵심 시뮬레이션 엔진
- `sim_soccer/field/`: 필드/Zone 모델
- `sim_soccer/systems/`: 게임 시스템 (체력, 모멘텀, 전술)
- `sim_soccer/io/`: 입출력 처리 (팀 로더, 리포트 생성)
- `sim_soccer/cli/`: CLI 인터페이스

## 테스트

```bash
pytest
```

## 문서

자세한 게임 설계는 `docs/` 폴더를 참조하세요.
