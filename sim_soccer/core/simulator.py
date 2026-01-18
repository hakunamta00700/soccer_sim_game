"""경기 시뮬레이션 메인 클래스"""

import random
from typing import Optional
from uuid import uuid4

from loguru import logger

from sim_soccer.core.action_selector import ActionSelector
from sim_soccer.core.contest_resolver import ContestResolver
from sim_soccer.core.phase_manager import PhaseManager
from sim_soccer.field.positioning import initialize_player_positions
from sim_soccer.models.events import EventLog
from sim_soccer.models.match import MatchState
from sim_soccer.models.team import TeamState
from sim_soccer.systems.momentum import update_momentum
from sim_soccer.systems.stamina import (
    apply_half_time_rest,
    calculate_stamina_cost,
)


class MatchSimulator:
    """경기 시뮬레이션을 실행하는 메인 클래스"""

    TOTAL_TICKS = 5400  # 90분 = 5400초
    HALF_TIME_TICK = 2700  # 전반 종료 시점

    def __init__(self, random_seed: Optional[int] = None):
        """시뮬레이터 초기화
        
        Args:
            random_seed: 랜덤 시드 (재현 가능성을 위해)
        """
        self.resolver = ContestResolver()
        self.phase_manager = PhaseManager()
        self.action_selector = ActionSelector()
        self.random_seed = random_seed
        
        if random_seed is not None:
            random.seed(random_seed)
            logger.info(f"Random seed set to {random_seed}")

    def simulate_match(
        self,
        home_team: TeamState,
        away_team: TeamState,
        random_seed: Optional[int] = None,
    ) -> MatchState:
        """경기 시뮬레이션 실행
        
        Args:
            home_team: 홈 팀 상태
            away_team: 원정 팀 상태
            random_seed: 랜덤 시드 (재현 가능성을 위해)
        
        Returns:
            시뮬레이션 완료된 MatchState
        """
        if random_seed is not None:
            random.seed(random_seed)
            self.random_seed = random_seed
        
        # 초기 상태 설정
        match_state = MatchState(
            match_id=str(uuid4()),
            tick=0,
            half=1,
            home_team=home_team,
            away_team=away_team,
            current_phase="build_up",
            attacking_team="home",
            ball_zone=2,  # 중앙 후방
            ball_holder=None,
        )
        
        # 초기 선수 위치 설정
        initialize_player_positions(
            home_team, match_state.current_phase, True
        )
        initialize_player_positions(
            away_team, "defense", False
        )
        
        # 초기 볼 소유자 설정 (홈 팀 골키퍼)
        home_gk = home_team.get_players_by_position("GK")[0]
        home_gk.has_ball = True
        match_state.ball_holder = home_gk.player_id
        match_state.ball_zone = home_gk.zone
        
        logger.info(
            f"Match simulation started: {home_team.team_name} vs {away_team.team_name}"
        )
        
        # Tick 단위 시뮬레이션
        for tick in range(self.TOTAL_TICKS):
            match_state.tick = tick
            
            # 전반/후반 구분
            if tick == self.HALF_TIME_TICK:
                match_state.half = 2
                self._apply_half_time_rest(match_state)
                logger.info("Half time - Second half started")
            
            # Phase 처리 및 전환
            self._process_phase(match_state)
            
            # 행동 선택 및 실행
            self._process_action(match_state)
            
            # 상태 업데이트
            self._update_state(match_state)
            
            # 경기 종료 조건 확인 (조기 종료는 없음, 항상 90분 진행)
        
        # 경기 종료 처리
        match_state.finish_match()
        
        logger.info(
            f"Match finished: {home_team.team_name} {home_team.score} - "
            f"{away_team.score} {away_team.team_name}"
        )
        
        return match_state

    def _process_phase(self, match_state: MatchState):
        """Phase 처리 및 전환 판정"""
        current_phase = match_state.current_phase
        attacking_team = match_state.get_attacking_team()
        
        # Phase 전환 확률 계산
        transition_prob = self.phase_manager.calculate_transition_probability(
            current_phase, attacking_team, match_state
        )
        
        # 전환 판정
        if random.random() < transition_prob:
            # 전환 시 다음 Phase 결정 (임시로 성공으로 가정)
            next_phase = self.phase_manager.determine_next_phase(
                current_phase, True, None, match_state
            )
            
            if next_phase != current_phase:
                logger.debug(
                    f"Phase transition: {current_phase} -> {next_phase} "
                    f"(tick: {match_state.tick})"
                )
                match_state.current_phase = next_phase

    def _process_action(self, match_state: MatchState):
        """행동 선택 및 실행"""
        attacking_team = match_state.get_attacking_team()
        defending_team = match_state.get_defending_team()
        
        # 행동 선택
        action_type, situation = self.action_selector.select_action(
            match_state.current_phase, attacking_team, match_state
        )
        
        # 행동의 주체와 대상 선정
        attacker, defender = self.action_selector.select_players(
            action_type, attacking_team, match_state
        )
        
        if not attacker:
            logger.warning("No attacker found, skipping action")
            return
        
        # 컨테스트 계산
        contest_score = self.resolver.calculate_contest_score(
            attacker=attacker,
            defender=defender,
            action_type=action_type,
            situation=situation,
            attacker_team_tactics=attacking_team.tactics,
            defender_team_tactics=defending_team.tactics,
            attacker_momentum=attacking_team.momentum,
            defender_momentum=defending_team.momentum,
            is_second_half=match_state.half == 2,
        )
        
        # 성공/실패 판정
        success = self.resolver.resolve_contest(contest_score)
        
        # 결과 적용
        self._apply_action_result(
            action_type, success, attacker, defender, attacking_team, defending_team, match_state
        )
        
        # 이벤트 로그 기록 (중요 이벤트만)
        if self._is_important_event(action_type, success):
            self._log_event(
                action_type, success, attacker, defender, attacking_team, match_state
            )

    def _apply_action_result(
        self,
        action_type: str,
        success: bool,
        attacker: Optional,
        defender: Optional,
        attacking_team: TeamState,
        defending_team: TeamState,
        match_state: MatchState,
    ):
        """행동 결과 적용"""
        from sim_soccer.field.zone import FINAL_THIRD_ZONES
        
        # 체력 소모
        if attacker:
            stamina_cost = calculate_stamina_cost(
                action_type, attacking_team.tactics, attacker.stats.get("STA", 5)
            )
            attacker.stamina = max(0, attacker.stamina - stamina_cost)
        
        if defender:
            stamina_cost = calculate_stamina_cost(
                action_type, defending_team.tactics, defender.stats.get("STA", 5)
            )
            defender.stamina = max(0, defender.stamina - stamina_cost)
        
        # 통계 업데이트
        if action_type == "shoot":
            attacking_team.stats["shots"] += 1
            if success:
                attacking_team.stats["shots_on_target"] += 1
        elif action_type == "pass":
            attacking_team.stats["passes_attempted"] += 1
            if success:
                attacking_team.stats["passes_completed"] += 1
        elif action_type == "dribble":
            attacking_team.stats["dribbles_attempted"] += 1
            if success:
                attacking_team.stats["dribbles_successful"] += 1
        elif action_type == "tackle":
            defending_team.stats["tackles_attempted"] += 1
            if success:
                defending_team.stats["tackles_successful"] += 1
        
        # 성공 시 상태 업데이트
        if success:
            if action_type == "shoot":
                # 슈팅 성공 시 골 확률 계산
                if self._calculate_goal_probability(attacker, defender, attacking_team):
                    attacking_team.score += 1
                    attacking_team.momentum = update_momentum(
                        attacking_team.momentum, "goal_scored"
                    )
                    defending_team.momentum = update_momentum(
                        defending_team.momentum, "goal_conceded"
                    )
                    logger.info(
                        f"GOAL! {attacking_team.team_name} scores! "
                        f"(tick: {match_state.tick}, player: {attacker.name if attacker else 'Unknown'})"
                    )
                    # 골 후 킥오프 (수비 팀이 공격 시작)
                    match_state.switch_attacking_team()
                    match_state.current_phase = "build_up"
                    # 볼 위치를 수비 팀 후방으로 이동
                    defending_gk = defending_team.get_players_by_position("GK")[0]
                    match_state.ball_zone = defending_gk.zone
                    match_state.ball_holder = defending_gk.player_id
                    defending_gk.has_ball = True
                    attacking_team.set_ball_holder(None)
            
            elif action_type in ["pass", "pass_long", "pass_to_midfield", "pass_to_forward"]:
                # 패스 성공 시 볼 이동
                if attacker:
                    # 임시로 Phase에 따라 볼 위치 결정
                    if match_state.current_phase == "final_third":
                        target_zone = 14  # 중앙 전방
                    elif match_state.current_phase == "midfield":
                        target_zone = 8  # 중앙 중앙
                    else:
                        target_zone = 5  # 중앙 후중앙
                    
                    match_state.ball_zone = target_zone
                    # 해당 Zone의 선수에게 볼 전달
                    from sim_soccer.field.positioning import get_players_in_zone
                    target_players = get_players_in_zone(attacking_team, target_zone)
                    if target_players:
                        target_player = target_players[0]
                        target_player.has_ball = True
                        match_state.ball_holder = target_player.player_id
                        attacker.has_ball = False
            
            elif action_type == "dribble":
                # 드리블 성공 시 전방으로 이동 가능
                if attacker and match_state.current_phase != "final_third":
                    # 전방 Zone으로 이동
                    from sim_soccer.field.zone import get_zone_row
                    current_row = get_zone_row(attacker.zone)
                    if current_row < 4:
                        attacker.zone += 3  # 한 행 앞으로
                        match_state.ball_zone = attacker.zone
            
            elif action_type in ["tackle", "intercept"]:
                # 태클/인터셉트 성공 시 공수 전환
                if defender:
                    match_state.switch_attacking_team()
                    match_state.current_phase = "transition"
                    defender.has_ball = True
                    match_state.ball_holder = defender.player_id
                    match_state.ball_zone = defender.zone
                    attacking_team.set_ball_holder(None)
        
        else:
            # 실패 시
            if action_type in ["pass", "dribble"]:
                # 패스/드리블 실패 시 공수 전환 가능성
                if random.random() < 0.3:  # 30% 확률로 전환
                    match_state.switch_attacking_team()
                    match_state.current_phase = "transition"
                    attacking_team.momentum = update_momentum(
                        attacking_team.momentum, "mistake"
                    )
            
            elif action_type == "shoot":
                # 슈팅 실패 시 골킥
                match_state.switch_attacking_team()
                match_state.current_phase = "build_up"
                defending_gk = defending_team.get_players_by_position("GK")[0]
                match_state.ball_zone = defending_gk.zone
                match_state.ball_holder = defending_gk.player_id
                defending_gk.has_ball = True
                attacking_team.set_ball_holder(None)

    def _calculate_goal_probability(
        self,
        attacker: Optional,
        defender: Optional,
        attacking_team: TeamState,
    ) -> bool:
        """골 확률 계산 및 판정"""
        if not attacker:
            return False
        
        # 슈팅 정확도 기반 골 확률
        sho_stat = attacker.get_weighted_stat("SHO")
        base_goal_prob = 0.3 + (sho_stat - 5) * 0.05  # 기본 30% + 스탯 보정
        
        # 골키퍼 방어 고려
        if defender and defender.position == "GK":
            gk_tac = defender.get_weighted_stat("TAC")
            gk_defense = gk_tac * 1.5  # 골키퍼 가중치
            goal_prob = base_goal_prob - (gk_defense - 5) * 0.03
        else:
            goal_prob = base_goal_prob
        
        # 범위 제한 (10%-60%)
        goal_prob = max(0.1, min(0.6, goal_prob))
        
        return random.random() < goal_prob

    def _is_important_event(self, action_type: str, success: bool) -> bool:
        """중요한 이벤트인지 판정"""
        important_actions = ["goal", "shoot", "tackle", "intercept"]
        return action_type in important_actions or (action_type == "shoot" and success)

    def _log_event(
        self,
        action_type: str,
        success: bool,
        attacker: Optional,
        defender: Optional,
        team: TeamState,
        match_state: MatchState,
    ):
        """이벤트 로그 기록"""
        event_type = "goal" if action_type == "shoot" and success else action_type
        
        event = EventLog(
            tick=match_state.tick,
            phase=match_state.current_phase,
            event_type=event_type,
            team="home" if team == match_state.home_team else "away",
            player_id=attacker.player_id if attacker else None,
            action=action_type,
            result="success" if success else "failure",
            description=f"{action_type} {'success' if success else 'failure'}",
        )
        
        match_state.add_event(event)

    def _apply_half_time_rest(self, match_state: MatchState):
        """후반 시작 시 체력 회복"""
        from sim_soccer.systems.stamina import apply_half_time_rest
        
        for player in match_state.home_team.players:
            player.stamina = apply_half_time_rest(player.stamina)
        
        for player in match_state.away_team.players:
            player.stamina = apply_half_time_rest(player.stamina)
        
        logger.info("Half time rest applied - stamina restored")

    def _update_state(self, match_state: MatchState):
        """경기 상태 업데이트 (점유율 등)"""
        # 점유율은 간단히 공격 팀이 공을 가지고 있는 시간으로 계산
        # 실제로는 더 복잡한 계산이 필요하지만, 여기서는 생략
