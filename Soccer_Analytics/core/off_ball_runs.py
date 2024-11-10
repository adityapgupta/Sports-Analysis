import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import yaml
from scipy.spatial.distance import cdist
import sys 
from calculations import calculate_velocity, calculate_direction, smooth_positions
import os

@dataclass
class OffBallRun:
    player_id: int
    start_time: float
    end_time: Optional[float]
    start_position: Tuple[float, float]
    current_position: Tuple[float, float]
    velocity: Tuple[float, float]
    run_distance: float
    space_gained: float
    threat_score: float
    run_type: str  # 'penetrating', 'supporting', 'diversionary'
    is_active: bool
    creating_space_for: Optional[int]  # player_id benefiting from the run
    defensive_disruption: float

class OffBallRunsAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """Initialize Off-Ball Runs Analyzer"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Load field dimensions
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        
        # Configuration parameters
        self.min_run_velocity = 15.0  # km/h
        self.min_run_duration = 0.5   # seconds
        self.velocity_smoothing_window = 5  # frames
        self.space_creation_radius = 10.0  # meters
        self.min_distance_traveled = 5.0  # meters
        self.max_run_duration = 10.0  # seconds
        
        # Track active runs
        self.active_runs: Dict[int, OffBallRun] = {}
        self.completed_runs: List[OffBallRun] = []
        
        # Historical positions for velocity calculation
        self.position_history: Dict[int, List[Tuple[float, float]]] = {}
        self.time_history: Dict[int, List[float]] = {}
        
        self.history_window = 10  # frames to keep in history

    def update_position_history(self, player_id: int, 
                              position: Tuple[float, float], 
                              timestamp: float):
        """Update position history for a player"""
        if player_id not in self.position_history:
            self.position_history[player_id] = []
            self.time_history[player_id] = []
            
        self.position_history[player_id].append(position)
        self.time_history[player_id].append(timestamp)
        
        # Keep history within window
        if len(self.position_history[player_id]) > self.history_window:
            self.position_history[player_id].pop(0)
            self.time_history[player_id].pop(0)

    def calculate_smooth_velocity(self, player_id: int) -> Optional[Tuple[float, float]]:
        """Calculate smoothed velocity vector from position history"""
        positions = self.position_history.get(player_id, [])
        times = self.time_history.get(player_id, [])
        
        if len(positions) < 2:
            return None
            
        # Calculate velocities between consecutive positions
        velocities = []
        for i in range(1, len(positions)):
            dt = times[i] - times[i-1]
            if dt > 0:
                dx = positions[i][0] - positions[i-1][0]
                dy = positions[i][1] - positions[i-1][1]
                velocities.append((dx/dt, dy/dt))
        
        if not velocities:
            return None
            
        # Apply smoothing
        smoothed_velocities = smooth_positions(velocities, self.velocity_smoothing_window)
        return smoothed_velocities[-1] if smoothed_velocities else velocities[-1]

    def detect_run_start(self, player_id: int, 
                        velocity: Tuple[float, float], 
                        position: Tuple[float, float],
                        timestamp: float) -> bool:
        """Detect if a player has started a run based on velocity"""
        speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
        speed_kmh = speed * 3.6  # convert to km/h
        
        return (speed_kmh >= self.min_run_velocity and 
                player_id not in self.active_runs)

    def calculate_space_gained(self, start_pos: Tuple[float, float],
                             current_pos: Tuple[float, float],
                             defender_positions: List[Tuple[float, float]]) -> float:
        """Calculate effective space gained relative to defenders"""
        if not defender_positions:
            return 0.0
            
        # Calculate average distance to defenders before and after movement
        start_distances = cdist([start_pos], defender_positions)[0]
        current_distances = cdist([current_pos], defender_positions)[0]
        
        # Weight closer defenders more heavily
        weights = 1 / (start_distances + 1e-6)
        weights = weights / np.sum(weights)
        
        weighted_start = np.sum(start_distances * weights)
        weighted_current = np.sum(current_distances * weights)
        
        return max(0.0, weighted_current - weighted_start)

    def calculate_threat_score(self, position: Tuple[float, float],
                             velocity: Tuple[float, float],
                             ball_position: Tuple[float, float],
                             defender_positions: List[Tuple[float, float]]) -> float:
        """Calculate threat score of the run based on various factors"""
        # Distance to goal threat
        goal_pos = (self.field_length, self.field_width/2)
        distance_to_goal = np.sqrt(
            (position[0] - goal_pos[0])**2 + 
            (position[1] - goal_pos[1])**2
        )
        goal_threat = 1 - min(1.0, distance_to_goal / self.field_length)
        
        # Space threat
        if defender_positions:
            distances_to_defenders = cdist([position], defender_positions)[0]
            space_threat = min(1.0, np.min(distances_to_defenders) / 20.0)
        else:
            space_threat = 1.0
        
        # Running direction threat
        if velocity[0] != 0 or velocity[1] != 0:
            angle_to_goal = np.arctan2(goal_pos[1] - position[1], 
                                     goal_pos[0] - position[0])
            run_angle = np.arctan2(velocity[1], velocity[0])
            angle_diff = abs(angle_to_goal - run_angle)
            direction_threat = 1 - min(1.0, angle_diff / np.pi)
        else:
            direction_threat = 0.0
        
        # Combine threats with weights
        return 0.4 * goal_threat + 0.3 * space_threat + 0.3 * direction_threat

    def classify_run_type(self, run: OffBallRun, 
                         ball_position: Tuple[float, float],
                         teammate_positions: List[Tuple[float, float]]) -> str:
        """Classify the type of off-ball run"""
        # Calculate run direction relative to goal
        run_vector = (run.current_position[0] - run.start_position[0],
                     run.current_position[1] - run.start_position[1])
        
        # Check if run is mainly vertical (penetrating)
        vertical_component = abs(run_vector[1])
        horizontal_component = abs(run_vector[0])
        
        if vertical_component > horizontal_component and run.current_position[1] > run.start_position[1]:
            return 'penetrating'
        
        # Check if run is creating space for teammates
        for teammate_pos in teammate_positions:
            if teammate_pos != run.current_position:
                dist_to_teammate = np.sqrt(
                    (run.current_position[0] - teammate_pos[0])**2 +
                    (run.current_position[1] - teammate_pos[1])**2
                )
                if dist_to_teammate < self.space_creation_radius:
                    return 'supporting'
        
        return 'diversionary'

    def calculate_defensive_disruption(self, run: OffBallRun,
                                    defender_positions: List[Tuple[float, float]]) -> float:
        """Calculate how much the run disrupts the defensive organization"""
        if not defender_positions:
            return 0.0
            
        # Calculate defensive coverage before run
        initial_coverage = self._calculate_defensive_coverage(
            defender_positions, run.start_position)
        
        # Calculate defensive coverage after run
        current_coverage = self._calculate_defensive_coverage(
            defender_positions, run.current_position)
        
        return max(0.0, initial_coverage - current_coverage)

    def _calculate_defensive_coverage(self, 
                                   defender_positions: List[Tuple[float, float]],
                                   position: Tuple[float, float]) -> float:
        """Calculate defensive coverage at a position"""
        distances = cdist([position], defender_positions)[0]
        coverage = np.sum(1 / (1 + distances))  # Higher value = better coverage
        return coverage

    def analyze_frame(self, 
                     timestamp: float,
                     player_positions: List[Tuple[int, Tuple[float, float]]],
                     ball_position: Tuple[float, float],
                     ball_carrier_id: Optional[int],
                     defender_positions: List[Tuple[float, float]]) -> List[OffBallRun]:
        """Analyze a frame of tracking data for off-ball runs"""
        active_runs_update = {}
        
        # Update position history and analyze each player
        for player_id, position in player_positions:
            # Skip ball carrier
            if player_id == ball_carrier_id:
                continue
                
            # Update position history
            self.update_position_history(player_id, position, timestamp)
            
            # Calculate velocity
            velocity = self.calculate_smooth_velocity(player_id)
            if velocity is None:
                continue
                
            if player_id in self.active_runs:
                # Update existing run
                run = self.active_runs[player_id]
                run.current_position = position
                run.velocity = velocity
                
                # Update run metrics
                run.run_distance += np.sqrt(
                    (position[0] - run.current_position[0])**2 +
                    (position[1] - run.current_position[1])**2
                )
                
                run.space_gained = self.calculate_space_gained(
                    run.start_position, position, defender_positions)
                
                run.threat_score = self.calculate_threat_score(
                    position, velocity, ball_position, defender_positions)
                
                run.run_type = self.classify_run_type(
                    run, ball_position, 
                    [pos for pid, pos in player_positions if pid != player_id]
                )
                
                run.defensive_disruption = self.calculate_defensive_disruption(
                    run, defender_positions)
                
                # Check if run should be ended
                speed = np.sqrt(velocity[0]**2 + velocity[1]**2) * 3.6  # km/h
                run_duration = timestamp - run.start_time
                
                if (speed < self.min_run_velocity or 
                    run_duration > self.max_run_duration):
                    run.is_active = False
                    run.end_time = timestamp
                    self.completed_runs.append(run)
                else:
                    active_runs_update[player_id] = run
                    
            else:
                # Check for new run
                if self.detect_run_start(player_id, velocity, position, timestamp):
                    new_run = OffBallRun(
                        player_id=player_id,
                        start_time=timestamp,
                        end_time=None,
                        start_position=position,
                        current_position=position,
                        velocity=velocity,
                        run_distance=0.0,
                        space_gained=0.0,
                        threat_score=self.calculate_threat_score(
                            position, velocity, ball_position, defender_positions),
                        run_type='penetrating',  # Will be updated
                        is_active=True,
                        creating_space_for=None,  # Will be updated if applicable
                        defensive_disruption=0.0
                    )
                    active_runs_update[player_id] = new_run
        
        self.active_runs = active_runs_update
        return list(self.active_runs.values())

    def get_run_statistics(self) -> Dict:
        """Get statistics about completed runs"""
        if not self.completed_runs:
            return {
                'total_runs': 0,
                'avg_run_distance': 0.0,
                'avg_threat_score': 0.0,
                'run_types': {'penetrating': 0, 'supporting': 0, 'diversionary': 0}
            }
            
        return {
            'total_runs': len(self.completed_runs),
            'avg_run_distance': np.mean([run.run_distance for run in self.completed_runs]),
            'avg_threat_score': np.mean([run.threat_score for run in self.completed_runs]),
            'avg_space_gained': np.mean([run.space_gained for run in self.completed_runs]),
            'avg_defensive_disruption': np.mean([run.defensive_disruption 
                                               for run in self.completed_runs]),
            'run_types': {
                'penetrating': sum(1 for run in self.completed_runs 
                                 if run.run_type == 'penetrating'),
                'supporting': sum(1 for run in self.completed_runs 
                                if run.run_type == 'supporting'),
                'diversionary': sum(1 for run in self.completed_runs 
                                  if run.run_type == 'diversionary')
            },
            'avg_run_duration': np.mean([(run.end_time - run.start_time) 
                                       for run in self.completed_runs]),
            'most_active_player': max(
                set(run.player_id for run in self.completed_runs),
                key=lambda pid: sum(1 for run in self.completed_runs 
                                  if run.player_id == pid),
                default=None
            )
        }
        
    def get_high_threat_runs(self, threshold: float = 0.7) -> List[OffBallRun]:
        """Get list of completed runs with high threat scores"""
        return [run for run in self.completed_runs 
                if run.threat_score >= threshold]
                
    def clear_history(self):
        """Clear historical data"""
        self.completed_runs = []
        self.active_runs = {}
        self.position_history = {}
        self.time_history = {}