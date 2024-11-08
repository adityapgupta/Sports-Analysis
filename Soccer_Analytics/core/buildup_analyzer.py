# soccer_analytics/core/buildup_analyzer.py

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.distance import cdist
import sys
# if '/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils' not in sys.path:
#     sys.path.append('/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils')

from calculations import calculate_velocity
import os

@dataclass
class BuildupPhase:
    start_time: datetime
    end_time: Optional[datetime]
    start_position: Tuple[float, float]
    current_position: Tuple[float, float]
    involved_players: List[int]
    progression_speed: float = 0.0
    vertical_progress: float = 0.0
    num_passes: int = 0
    success: bool = False
    duration: float = 0.0
    reached_final_third: bool = False
    transition_type: str = "organized"  # 'organized' or 'counter'

class BuildupAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """Initialize Build-up Analyzer"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        self.final_third_line = self.field_length * 2/3
        self.defensive_third_line = self.field_length * 1/3
        self.buildup_config = config['thresholds']['buildup']
        
        self.buildup_phases: List[BuildupPhase] = []
        self.current_buildup: Optional[BuildupPhase] = None
        
    def start_buildup(self, 
                     timestamp: datetime,
                     position: Tuple[float, float],
                     player_id: int) -> None:
        """Start a new build-up phase"""
        self.current_buildup = BuildupPhase(
            start_time=timestamp,
            end_time=None,
            start_position=position,
            current_position=position,
            involved_players=[player_id]
        )
        
    def end_buildup(self, 
                   timestamp: datetime,
                   reached_final_third: bool = False) -> None:
        """End current build-up phase"""
        if self.current_buildup:
            self.current_buildup.end_time = timestamp
            self.current_buildup.duration = (
                timestamp - self.current_buildup.start_time
            ).total_seconds()
            self.current_buildup.success = reached_final_third
            self.current_buildup.reached_final_third = reached_final_third
            
            if self.current_buildup.duration >= self.buildup_config['min_duration']:
                self.buildup_phases.append(self.current_buildup)
            
            self.current_buildup = None
            
    def analyze_buildup(self,
                       timestamp: datetime,
                       ball_position: Tuple[float, float],
                       possessing_team: str,
                       possessing_player: int,
                       player_positions: Dict[int, Tuple[float, float]],
                       last_timestamp: Optional[datetime] = None) -> Dict:
        """
        Analyze build-up play
        
        Args:
            timestamp: Current timestamp
            ball_position: Current ball position (x, y)
            possessing_team: Team in possession ('home' or 'away')
            possessing_player: ID of player in possession
            player_positions: Dictionary of player positions {id: (x, y)}
            last_timestamp: Previous timestamp for velocity calculation
        """
        result = {}
        
        # Check if in defensive third
        in_defensive_third = ball_position[1] < self.defensive_third_line
        in_final_third = ball_position[1] > self.final_third_line
        
        # Start new build-up if in defensive third
        if in_defensive_third and not self.current_buildup:
            self.start_buildup(timestamp, ball_position, possessing_player)
            result['event'] = 'buildup_started'
        
        # Update current build-up
        elif self.current_buildup:
            # Calculate progression
            vertical_progress = ball_position[1] - self.current_buildup.current_position[1]
            
            # Update current buildup
            if last_timestamp:
                time_diff = (timestamp - last_timestamp).total_seconds()
                self.current_buildup.progression_speed = (
                    vertical_progress / time_diff if time_diff > 0 else 0
                )
            
            self.current_buildup.vertical_progress += max(0, vertical_progress)
            self.current_buildup.current_position = ball_position
            
            # Add player if new
            if possessing_player not in self.current_buildup.involved_players:
                self.current_buildup.involved_players.append(possessing_player)
            
            # Check if buildup should end
            if in_final_third:
                self.end_buildup(timestamp, reached_final_third=True)
                result['event'] = 'buildup_successful'
            elif ball_position[1] < self.current_buildup.start_position[1]:
                self.end_buildup(timestamp, reached_final_third=False)
                result['event'] = 'buildup_backwards'
        
        result.update(self._get_current_buildup_stats())
        return result
    
    def _get_current_buildup_stats(self) -> Dict:
        """Get statistics for current build-up phase"""
        if not self.current_buildup:
            return {}
            
        return {
            'duration': (datetime.now() - self.current_buildup.start_time).total_seconds(),
            'vertical_progress': self.current_buildup.vertical_progress,
            'num_players_involved': len(self.current_buildup.involved_players),
            'progression_speed': self.current_buildup.progression_speed
        }
    
    def get_buildup_stats(self, time_window: float = None) -> Dict:
        """Get comprehensive build-up statistics"""
        if not self.buildup_phases:
            return {}
            
        # Filter phases by time window if specified
        phases = self.buildup_phases
        if time_window is not None:
            latest_time = self.buildup_phases[-1].end_time
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            phases = [p for p in phases if p.end_time >= cutoff_time]
        
        successful_phases = [p for p in phases if p.success]
        
        return {
            'total_buildups': len(phases),
            'successful_buildups': len(successful_phases),
            'success_rate': len(successful_phases) / len(phases) if phases else 0,
            'avg_duration': np.mean([p.duration for p in phases]),
            'avg_players_involved': np.mean([len(p.involved_players) for p in phases]),
            'avg_vertical_progress': np.mean([p.vertical_progress for p in phases]),
            'avg_progression_speed': np.mean([p.progression_speed for p in phases]),
            'most_involved_players': self._get_most_involved_players(phases)
        }
    
    def _get_most_involved_players(self, phases: List[BuildupPhase]) -> Dict[int, int]:
        """Get count of player involvements in build-up phases"""
        player_counts = {}
        for phase in phases:
            for player in phase.involved_players:
                player_counts[player] = player_counts.get(player, 0) + 1
        return dict(sorted(player_counts.items(), key=lambda x: x[1], reverse=True))
    
    def visualize_buildup_patterns(self):
        """Visualize build-up patterns on the field"""
        if not self.buildup_phases:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Draw field
        plt.plot([0, self.field_length], [0, 0], 'k-')
        plt.plot([0, self.field_length], [self.field_width, self.field_width], 'k-')
        plt.plot([0, 0], [0, self.field_width], 'k-')
        plt.plot([self.field_length, self.field_length], [0, self.field_width], 'k-')
        
        # Draw thirds
        plt.axhline(y=self.buildup_config['defensive_third_line'], 
                   color='g', linestyle='--', alpha=0.3)
        plt.axhline(y=self.buildup_config['final_third_line'], 
                   color='r', linestyle='--', alpha=0.3)
        
        # Plot successful and unsuccessful build-ups
        for phase in self.buildup_phases:
            color = 'g' if phase.success else 'r'
            alpha = 0.6 if phase.success else 0.3
            
            plt.plot([phase.start_position[0], phase.current_position[0]],
                    [phase.start_position[1], phase.current_position[1]],
                    color=color, alpha=alpha, linewidth=2)
        
        plt.title('Build-up Patterns Analysis')
        plt.xlabel('Field Width (m)')
        plt.ylabel('Field Length (m)')
        
        # Add legend
        plt.plot([], [], 'g-', label='Successful Build-up')
        plt.plot([], [], 'r-', label='Unsuccessful Build-up')
        plt.legend()
        
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
    def plot_buildup_success_timeline(self):
        """Plot build-up success rate over time"""
        if not self.buildup_phases:
            return
        
        plt.figure(figsize=(12, 6))
        
        # Calculate rolling success rate
        window_size = 5
        success_values = [1 if p.success else 0 for p in self.buildup_phases]
        rolling_success = np.convolve(success_values, 
                                    np.ones(window_size)/window_size, 
                                    mode='valid')
        
        # Plot success rate
        timestamps = [(p.end_time - self.buildup_phases[0].start_time).total_seconds() 
                     for p in self.buildup_phases[window_size-1:]]
        
        plt.plot(timestamps, rolling_success, 'b-')
        
        plt.title(f'Build-up Success Rate (Rolling Average: {window_size} attempts)')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Success Rate')
        plt.grid(True)
        plt.show()
    
    def plot_progression_heatmap(self):
        """Create heatmap of successful build-up progression"""
        if not self.buildup_phases:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Create grid for heatmap
        grid_size = 10
        x_grid = np.linspace(0, self.field_width, grid_size)
        y_grid = np.linspace(0, self.field_length, grid_size)
        heatmap = np.zeros((grid_size-1, grid_size-1))
        
        # Populate heatmap
        for phase in self.buildup_phases:
            if phase.success:
                x_idx = int(phase.current_position[0] / self.field_width * (grid_size-1))
                y_idx = int(phase.current_position[1] / self.field_length * (grid_size-1))
                x_idx = min(max(x_idx, 0), grid_size-2)
                y_idx = min(max(y_idx, 0), grid_size-2)
                heatmap[x_idx, y_idx] += 1
        
        plt.imshow(heatmap.T, origin='lower', cmap='hot', 
                  extent=[0, self.field_width, 0, self.field_length])
        
        plt.title('Build-up Progression Heatmap')
        plt.xlabel('Field Width (m)')
        plt.ylabel('Field Length (m)')
        plt.colorbar(label='Number of Successful Build-ups')
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = BuildupAnalyzer()
    
    # Example tracking data
    timestamp = datetime.now()
    ball_pos = (50.0, 20.0)  # In defensive third
    possessing_team = 'home'
    possessing_player = 1
    player_positions = {
        1: (50.0, 20.0),
        2: (40.0, 25.0),
        3: (60.0, 25.0),
        # Add more player positions...
    }
    
    # Analyze buildup
    result = analyzer.analyze_buildup(
        timestamp,
        ball_pos,
        possessing_team,
        possessing_player,
        player_positions
    )
    
    print("\nBuild-up Analysis:")
    for key, value in result.items():
        print(f"{key}: {value}")