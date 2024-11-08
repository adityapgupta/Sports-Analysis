# Path: soccer_analytics/core/analytics_integrator.py

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import yaml
from datetime import datetime
import logging

# Import analyzers from core package
from formation_analyzer import FormationAnalyzer
from .heat_map_analyzer import HeatMapAnalyzer
from .pressing_analyzer import PressingAnalyzer
from .distance_analyzer import DistanceAnalyzer
from .sprint_analyzer import SprintAnalyzer
from .team_shape_analyzer import TeamShapeAnalyzer
from .defensive_line_analyzer import DefensiveLineAnalyzer
from .ball_possession_analyzer import BallPossessionAnalyzer
from .buildup_analyzer import BuildupAnalyzer
from .space_control_analyzer import SpaceControlAnalyzer
from .passing_opportunities import PassingOpportunitiesAnalyzer
from .off_ball_runs import OffBallRunsAnalyzer

# Import utilities
from ..utils.calculations import calculate_velocity, calculate_direction
# from ..utils.visualization import VisualizationHelper



@dataclass
class PlayerState:
    position: Tuple[float, float]
    team: str  # 'home' or 'away'
    role: str  # e.g., 'goalkeeper', 'defender', 'midfielder', 'forward'
    jersey_number: int

class SoccerAnalyticsIntegrator:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize Soccer Analytics Integrator"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize analyzers
        self.heat_map_analyzer = HeatMapAnalyzer(config_path)
        self.formation_analyzer = FormationAnalyzer(config_path)
        self.pressing_analyzer = PressingAnalyzer(config_path)
        self.distance_analyzer = DistanceAnalyzer(config_path)
        self.sprint_analyzer = SprintAnalyzer(config_path)
        self.team_shape_analyzer = TeamShapeAnalyzer(config_path)
        self.ball_possession_analyzer = BallPossessionAnalyzer(config_path)
        self.buildup_analyzer = BuildupAnalyzer(config_path)
        self.space_control_analyzer = SpaceControlAnalyzer(config_path)
        self.passing_opportunities_analyzer = PassingOpportunitiesAnalyzer(config_path)
        self.off_ball_runs_analyzer = OffBallRunsAnalyzer(config_path)
        
        # Cache for player states
        self.player_state_cache: Dict[int, Dict[int, PlayerState]] = {}
        self.current_frame_id: Optional[int] = None
        
        # Cache control
        self.cache_size = 1000  # number of frames to keep in cache
        self.cache_cleanup_interval = 100  # frames between cleanup
        
        # Analysis state
        self.ball_carrier_id: Optional[int] = None
        self.possession_team: Optional[str] = None
        
        # Track active player IDs
        self.home_player_ids: List[int] = []
        self.away_player_ids: List[int] = []

    def extract_position(self, frame_id: int, player_id: int) -> Optional[PlayerState]:
        """
        Black box function to extract player position and state
        This would be implemented by the tracking system
        """
        # This is a placeholder - implement actual position extraction
        raise NotImplementedError("Position extraction must be implemented!")

    def _get_player_state(self, frame_id: int, player_id: int,
                         use_cache: bool = True) -> Optional[PlayerState]:
        """Get player state with caching"""
        # Check cache first
        if use_cache and frame_id in self.player_state_cache:
            if player_id in self.player_state_cache[frame_id]:
                return self.player_state_cache[frame_id][player_id]
        
        # Extract position if not in cache
        try:
            state = self.extract_position(frame_id, player_id)
            
            # Update cache
            if frame_id not in self.player_state_cache:
                self.player_state_cache[frame_id] = {}
            self.player_state_cache[frame_id][player_id] = state
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error extracting position for player {player_id} at frame {frame_id}: {e}")
            return None

    def _cleanup_cache(self):
        """Remove old frames from cache"""
        if self.current_frame_id is None:
            return
            
        frames_to_remove = []
        for frame_id in self.player_state_cache:
            if self.current_frame_id - frame_id > self.cache_size:
                frames_to_remove.append(frame_id)
                
        for frame_id in frames_to_remove:
            del self.player_state_cache[frame_id]

    def _get_team_positions(self, frame_id: int, team: str) -> List[Tuple[int, Tuple[float, float]]]:
        """Get positions for all players of a team"""
        player_ids = self.home_player_ids if team == 'home' else self.away_player_ids
        positions = []
        
        for player_id in player_ids:
            state = self._get_player_state(frame_id, player_id)
            if state and state.team == team:
                positions.append((player_id, state.position))
                
        return positions

    def analyze_frame(self, frame_id: int, timestamp: float) -> Dict[str, Any]:
        """Analyze a single frame of the game"""
        self.current_frame_id = frame_id
        
        # Perform cache cleanup if needed
        if frame_id % self.cache_cleanup_interval == 0:
            self._cleanup_cache()
        
        # Get all player positions
        home_positions = self._get_team_positions(frame_id, 'home')
        away_positions = self._get_team_positions(frame_id, 'away')
        
        # Get ball position and carrier
        ball_state = self._get_player_state(frame_id, -1)  # Assuming -1 is ball ID
        ball_position = ball_state.position if ball_state else None
        
        # Initialize results dictionary
        results = {
            'frame_id': frame_id,
            'timestamp': timestamp,
            'analysis': {}
        }
        
        try:
            # Update heat maps
            self.heat_map_analyzer.add_positions([pos for _, pos in home_positions], team='home')
            self.heat_map_analyzer.add_positions([pos for _, pos in away_positions], team='away')
            results['analysis']['heat_maps'] = {
                'home': self.heat_map_analyzer.get_zone_statistics(),
                'away': self.heat_map_analyzer.get_zone_statistics()
            }
            
            # Analyze team formations
            results['analysis']['formations'] = self.formation_analyzer.analyze_frame(
                home_positions, away_positions)
            
            # Analyze pressing
            if ball_position and self.ball_carrier_id:
                results['analysis']['pressing'] = self.pressing_analyzer.analyze_frame(
                    ball_position, self.ball_carrier_id,
                    home_positions if self.possession_team == 'away' else away_positions)
            
            # Update distance and sprint analysis
            results['analysis']['distance'] = self.distance_analyzer.update_frame(
                frame_id, home_positions, away_positions)
            results['analysis']['sprints'] = self.sprint_analyzer.analyze_frame(
                frame_id, home_positions, away_positions)
            
            # Analyze team shape
            results['analysis']['team_shape'] = self.team_shape_analyzer.analyze_frame(
                home_positions, away_positions)
            
            # Analyze ball possession
            if ball_position:
                possession_result = self.ball_possession_analyzer.analyze_frame(
                    frame_id, ball_position, home_positions, away_positions)
                results['analysis']['possession'] = possession_result
                self.possession_team = possession_result.get('possession_team')
            
            # Analyze build-up play
            if self.possession_team:
                results['analysis']['buildup'] = self.buildup_analyzer.analyze_frame(
                    frame_id,
                    home_positions if self.possession_team == 'home' else away_positions,
                    away_positions if self.possession_team == 'home' else home_positions)
            
            # Analyze space control
            results['analysis']['space_control'] = self.space_control_analyzer.analyze_space_control(
                home_positions, away_positions)
            
            # Analyze passing opportunities
            if self.ball_carrier_id:
                carrier_team = self._get_player_state(frame_id, self.ball_carrier_id).team
                teammate_positions = (home_positions if carrier_team == 'home' 
                                   else away_positions)
                opponent_positions = (away_positions if carrier_team == 'home' 
                                   else home_positions)
                
                results['analysis']['passing_opportunities'] = (
                    self.passing_opportunities_analyzer.analyze_passing_opportunities(
                        self.ball_carrier_id,
                        self._get_player_state(frame_id, self.ball_carrier_id).position,
                        teammate_positions,
                        opponent_positions,
                        timestamp
                    )
                )
            
            # Analyze off-ball runs
            results['analysis']['off_ball_runs'] = self.off_ball_runs_analyzer.analyze_frame(
                timestamp,
                home_positions if self.possession_team == 'home' else away_positions,
                ball_position,
                self.ball_carrier_id,
                [pos for _, pos in (away_positions if self.possession_team == 'home' 
                                  else home_positions)]
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing frame {frame_id}: {e}")
            results['error'] = str(e)
        
        return results

    def analyze_sequence(self, start_frame: int, end_frame: int) -> List[Dict[str, Any]]:
        """Analyze a sequence of frames"""
        sequence_results = []
        
        for frame_id in range(start_frame, end_frame + 1):
            timestamp = frame_id / self.config['sampling']['position_frequency']
            result = self.analyze_frame(frame_id, timestamp)
            sequence_results.append(result)
        
        return sequence_results

    def get_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from a sequence of frame analyses"""
        summary = {
            'duration': len(results) / self.config['sampling']['position_frequency'],
            'frames_analyzed': len(results),
            'heat_maps': self.heat_map_analyzer.get_zone_statistics(),
            'formations': self.formation_analyzer.get_formation_summary(),
            'pressing_stats': self.pressing_analyzer.get_pressing_stats(),
            'distance_stats': self.distance_analyzer.get_distance_summary(),
            'sprint_stats': self.sprint_analyzer.get_sprint_statistics(),
            'possession_stats': self.ball_possession_analyzer.get_possession_stats(),
            'buildup_stats': self.buildup_analyzer.get_buildup_statistics(),
            'space_control_summary': self.space_control_analyzer.get_zone_statistics(),
            'passing_opportunities': self.passing_opportunities_analyzer.get_opportunity_stats(),
            'off_ball_runs': self.off_ball_runs_analyzer.get_run_statistics()
        }
        
        return summary

    def reset_analysis(self):
        """Reset all analyzers and clear cache"""
        self.player_state_cache = {}
        self.current_frame_id = None
        self.ball_carrier_id = None
        self.possession_team = None
        
        # Reset all analyzers
        self.heat_map_analyzer = HeatMapAnalyzer(self.config)
        self.formation_analyzer = FormationAnalyzer(self.config)
        self.pressing_analyzer = PressingAnalyzer(self.config)
        self.distance_analyzer = DistanceAnalyzer(self.config)
        self.sprint_analyzer = SprintAnalyzer(self.config)
        self.team_shape_analyzer = TeamShapeAnalyzer(self.config)
        self.ball_possession_analyzer = BallPossessionAnalyzer(self.config)
        self.buildup_analyzer = BuildupAnalyzer(self.config)
        self.space_control_analyzer = SpaceControlAnalyzer(self.config)
        self.passing_opportunities_analyzer = PassingOpportunitiesAnalyzer(self.config)
        self.off_ball_runs_analyzer = OffBallRunsAnalyzer(self.config)