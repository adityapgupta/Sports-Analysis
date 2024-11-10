import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yaml
import sys
if '/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils' not in sys.path:
    sys.path.append('/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils')

import os

from calculations import calculate_velocity, calculate_direction

@dataclass
class Sprint:
    start_time: datetime
    end_time: Optional[datetime]
    start_position: Tuple[float, float]
    end_position: Optional[Tuple[float, float]]
    distance: float = 0.0
    duration: float = 0.0
    avg_velocity: float = 0.0
    max_velocity: float = 0.0
    direction: str = ""
    recovery_time: float = 0.0

class SprintAnalyzer:
    """Analyzer for sprint detection and analysis"""
    
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """Initialize Sprint Analyzer with configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        sprint_config = config['thresholds']['sprint']
        self.sprint_threshold = sprint_config['min_velocity']
        self.min_sprint_duration = sprint_config['min_duration']
        self.recovery_threshold = sprint_config['recovery_threshold']
        self.update_frequency = sprint_config['update_frequency']
        self.smoothing_window = sprint_config['smoothing_window']
        
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        
        self.sprints: List[Sprint] = []
        self.current_sprint: Optional[Sprint] = None
        self.last_sprint_end: Optional[datetime] = None
        
        # Buffer for velocity smoothing
        self.velocity_buffer = []

    def process_position(self, 
                        timestamp: datetime,
                        position: Tuple[float, float],
                        last_position: Tuple[float, float],
                        last_timestamp: datetime) -> Dict:
        """Process new position data and detect sprints"""
        
        time_diff = (timestamp - last_timestamp).total_seconds()
        velocity = calculate_velocity(last_position, position, time_diff)
        
        # Update velocity buffer for smoothing
        self.velocity_buffer.append(velocity)
        if len(self.velocity_buffer) > self.smoothing_window:
            self.velocity_buffer.pop(0)
        
        # Use smoothed velocity for sprint detection
        smoothed_velocity = np.mean(self.velocity_buffer)
        
        sprint_data = {}
        
        if smoothed_velocity >= self.sprint_threshold:
            if self.current_sprint is None:
                # Start new sprint
                self.current_sprint = Sprint(
                    start_time=timestamp,
                    end_time=None,
                    start_position=last_position,
                    end_position=None
                )
                if self.last_sprint_end:
                    self.current_sprint.recovery_time = (
                        timestamp - self.last_sprint_end
                    ).total_seconds()
            
            # Update ongoing sprint
            self._update_sprint(position, timestamp, velocity)
            
            sprint_data = {
                'status': 'sprinting',
                'current_velocity': velocity,
                'sprint_duration': self.current_sprint.duration,
                'sprint_distance': self.current_sprint.distance
            }
        
        elif self.current_sprint is not None:
            # End sprint if minimum duration met
            if self.current_sprint.duration >= self.min_sprint_duration:
                self.sprints.append(self.current_sprint)
                self.last_sprint_end = timestamp
                sprint_data = {'status': 'sprint_ended'}
            else:
                sprint_data = {'status': 'sprint_discarded'}
            
            self.current_sprint = None
        
        else:
            sprint_data = {'status': 'no_sprint'}
        
        return sprint_data

    def _update_sprint(self, 
                      position: Tuple[float, float], 
                      timestamp: datetime,
                      current_velocity: float):
        """Update current sprint metrics"""
        self.current_sprint.end_time = timestamp
        if self.current_sprint.end_position is not None:    
            self.current_sprint.distance += np.sqrt(
                (position[0] - self.current_sprint.end_position[0])**2 +
                (position[1] - self.current_sprint.end_position[1])**2
            )
        else:
            self.current_sprint.distance += 0
        self.current_sprint.end_position = position

        self.current_sprint.duration = (
            timestamp - self.current_sprint.start_time
        ).total_seconds()
        
        self.current_sprint.avg_velocity = (
            self.current_sprint.distance / self.current_sprint.duration
        ) * 3.6 if self.current_sprint.duration != 0 else 0  # Convert to km/h
        self.current_sprint.max_velocity = max(
            current_velocity,
            self.current_sprint.max_velocity
        )
        self.current_sprint.direction = calculate_direction(
            self.current_sprint.start_position,
            position
        )

    def get_sprint_stats(self, time_window: float = None) -> Dict:
        """Get comprehensive sprint statistics"""
        if not self.sprints:
            return {}
            
        # Filter sprints by time window if specified
        sprints = self.sprints
        if time_window is not None:
            latest_time = self.sprints[-1].end_time
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            sprints = [s for s in sprints if s.end_time >= cutoff_time]
        
        # Calculate statistics
        distances = [s.distance for s in sprints]
        durations = [s.duration for s in sprints]
        velocities = [s.avg_velocity for s in sprints]
        max_velocities = [s.max_velocity for s in sprints]
        recovery_times = [s.recovery_time for s in sprints]
        
        # Direction distribution
        direction_dist = {}
        for sprint in sprints:
            direction_dist[sprint.direction] = direction_dist.get(sprint.direction, 0) + 1
        
        return {
            'total_sprints': len(sprints),
            'distances': {
                'mean': np.mean(distances),
                'max': np.max(distances),
                'total': np.sum(distances)
            },
            'durations': {
                'mean': np.mean(durations),
                'max': np.max(durations),
                'total': np.sum(durations)
            },
            'velocities': {
                'mean': np.mean(velocities),
                'max': np.max(max_velocities)
            },
            'recovery_times': {
                'mean': np.mean(recovery_times),
                'min': np.min(recovery_times),
                'max': np.max(recovery_times)
            },
            'direction_distribution': {
                dir: (count/len(sprints))*100 
                for dir, count in direction_dist.items()
            }
        }

    def visualize_sprints(self):
        """Visualize sprint patterns on the field"""
        if not self.sprints:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Draw field
        plt.plot([0, self.field_length], [0, 0], 'k-')
        plt.plot([0, self.field_length], [self.field_width, self.field_width], 'k-')
        plt.plot([0, 0], [0, self.field_width], 'k-')
        plt.plot([self.field_length, self.field_length], [0, self.field_width], 'k-')
        
        # Plot sprints
        for sprint in self.sprints:
            # Plot sprint path
            plt.plot([sprint.start_position[0], sprint.end_position[0]],
                    [sprint.start_position[1], sprint.end_position[1]],
                    'r-', alpha=0.6, linewidth=2)
            
            # Plot start and end points
            plt.plot(sprint.start_position[0], sprint.start_position[1], 
                    'go', label='Sprint Start' if sprint == self.sprints[0] else "")
            plt.plot(sprint.end_position[0], sprint.end_position[1], 
                    'ro', label='Sprint End' if sprint == self.sprints[0] else "")
        
        plt.title('Sprint Analysis')
        plt.xlabel('Field Length (m)')
        plt.ylabel('Field Width (m)')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.show()

    def plot_sprint_timeline(self):
        """Plot sprint occurrences and velocities over time"""
        if not self.sprints:
            return
        
        plt.figure(figsize=(12, 6))
        
        # Create timeline
        start_time = self.sprints[0].start_time
        for sprint in self.sprints:
            relative_start = (sprint.start_time - start_time).total_seconds()
            duration = sprint.duration
            plt.plot([relative_start, relative_start + duration],
                    [sprint.avg_velocity, sprint.avg_velocity],
                    'r-', linewidth=2)
        
        plt.axhline(y=self.sprint_threshold, color='g', linestyle='--',
                   label='Sprint Threshold')
        
        plt.title('Sprint Timeline')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (km/h)')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":

    # # Initialize analyzer
    # analyzer = SprintAnalyzer()

    # # Example tracking data
    # tracking_data = [
    #     (datetime.now(), (0.0, 0.0)),
    #     (datetime.now() + timedelta(seconds=1), (5.0, 5.0)),
    #     (datetime.now() + timedelta(seconds=2), (10.0, 8.0)),
    #     # Add more tracking data...
    # ]

    # # add few seconds for tracking data[1][0]

       

    # # Process positions
    # for i in range(1, len(tracking_data)):
    #     analyzer.process_position(
    #         tracking_data[i][0],
    #         tracking_data[i][1],
    #         tracking_data[i-1][1],
    #         tracking_data[i-1][0]
    #     )

    # # Get sprint statistics
    # sprint_stats = analyzer.get_sprint_stats()
    # print(sprint_stats)

    # # Visualize sprints
    # analyzer.visualize_sprints()

    # # Plot sprint timeline
    # analyzer.plot_sprint_timeline()

    analyzer = SprintAnalyzer()

    import pickle
    with open('Soccer_Analytics/core/detections.pkl', 'rb') as f:
        data = pickle.load(f)
    
    # Remove everything with label 0 or 3
    remove_indices = []
    for i in range(len(data)):
        for j in range(len(data[i])):

            if data[i][j][1] == 0 or data[i][j][1] == 3:
                remove_indices.append([i, j])

    # sort the indices in reverse order
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)

    for i, j in remove_indices:
        data[i].pop(j)
    
    # now find unique players
    players = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][0] not in players:
                players.append(data[i][j][0])

    # now track the players
    player_positions = {}
    for player in players:
        player_positions[player] = []

    for i in range(len(data)):
        for j in range(len(data[i])):
            player_positions[data[i][j][0]].append(data[i][j] + (i,))

    # now calculate tracking for each player
    player_tracking = {}
    player_sprint_stats = {}
    
    for player, positions in player_positions.items():
        analyzer = SprintAnalyzer()
        player_tracking[player] = []
        for i in range(1, len(positions)):
            player_tracking[player].append(
                analyzer.process_position(
                    datetime.now() + timedelta(seconds=positions[i][3]/25),
                    positions[i][2],
                    positions[i-1][2],
                    datetime.now() + timedelta(seconds=positions[i-1][3]/25)
                )
            )
        player_sprint_stats[player] = analyzer.get_sprint_stats()
        print(player_sprint_stats[player])
        analyzer.visualize_sprints()
        analyzer.plot_sprint_timeline()

    # # get the sprint stats for each player
    # player_sprint_stats = analyzer.get_sprint_stats()

    # print(player_sprint_stats)
    # # visualize the sprints for each player
    # analyzer.visualize_sprints()

    # # plot the sprint timeline for each player
    # analyzer.plot_sprint_timeline()

    
            