import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
from ..utils.calculations import calculate_velocity, calculate_direction

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
    
    def __init__(self, config_path: str = '../../config/config.yaml'):
        """Initialize Sprint Analyzer with configuration"""
        try:
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
            
            # Initialize arrays for vectorized operations
            self.sprints: List[Sprint] = []
            self.current_sprint: Optional[Sprint] = None
            self.last_sprint_end: Optional[datetime] = None
            
            # Initialize velocity buffer as numpy array
            self.velocity_buffer = np.zeros(self.smoothing_window)
            self.buffer_index = 0
            self.buffer_full = False
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                "Make sure the path to config.yaml is correct."
            )
        except KeyError as e:
            raise KeyError(f"Missing required configuration key: {str(e)}")

    def process_position(self, 
                        timestamp: datetime,
                        position: Tuple[float, float],
                        last_position: Tuple[float, float],
                        last_timestamp: datetime) -> Dict:
        """Process new position data and detect sprints"""
        time_diff = (timestamp - last_timestamp).total_seconds()
        velocity = calculate_velocity(last_position, position, time_diff)
        
        # Update velocity buffer using circular indexing
        self.velocity_buffer[self.buffer_index] = velocity
        self.buffer_index = (self.buffer_index + 1) % self.smoothing_window
        if self.buffer_index == 0:
            self.buffer_full = True
        
        # Calculate smoothed velocity
        if self.buffer_full:
            smoothed_velocity = np.mean(self.velocity_buffer)
        else:
            smoothed_velocity = np.mean(self.velocity_buffer[:self.buffer_index])
        
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
        """Update current sprint metrics using vectorized operations"""
        self.current_sprint.end_time = timestamp
        self.current_sprint.end_position = position
        
        # Vectorized distance calculation
        pos_diff = np.array(position) - np.array(self.current_sprint.end_position)
        self.current_sprint.distance += np.linalg.norm(pos_diff)
        
        self.current_sprint.duration = (
            timestamp - self.current_sprint.start_time
        ).total_seconds()
        
        # Updated velocity calculations
        self.current_sprint.avg_velocity = (
            self.current_sprint.distance / self.current_sprint.duration
        ) * 3.6  # Convert to km/h
        self.current_sprint.max_velocity = max(
            current_velocity,
            self.current_sprint.max_velocity
        )
        self.current_sprint.direction = calculate_direction(
            self.current_sprint.start_position,
            position
        )

    def get_sprint_stats(self, time_window: float = None) -> Dict:
        """Get comprehensive sprint statistics using vectorized operations"""
        if not self.sprints:
            return {}
            
        # Filter sprints by time window if specified
        sprints = self.sprints
        if time_window is not None:
            latest_time = self.sprints[-1].end_time
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            sprints = [s for s in sprints if s.end_time >= cutoff_time]
        
        # Vectorized statistics calculations
        sprint_array = np.array([
            [s.distance, s.duration, s.avg_velocity, s.max_velocity, s.recovery_time]
            for s in sprints
        ])
        
        # Calculate direction distribution using Counter
        direction_dist = {}
        for sprint in sprints:
            direction_dist[sprint.direction] = direction_dist.get(sprint.direction, 0) + 1
        
        n_sprints = len(sprints)
        return {
            'total_sprints': n_sprints,
            'distances': {
                'mean': np.mean(sprint_array[:, 0]),
                'max': np.max(sprint_array[:, 0]),
                'total': np.sum(sprint_array[:, 0])
            },
            'durations': {
                'mean': np.mean(sprint_array[:, 1]),
                'max': np.max(sprint_array[:, 1]),
                'total': np.sum(sprint_array[:, 1])
            },
            'velocities': {
                'mean': np.mean(sprint_array[:, 2]),
                'max': np.max(sprint_array[:, 3])
            },
            'recovery_times': {
                'mean': np.mean(sprint_array[:, 4]),
                'min': np.min(sprint_array[:, 4]),
                'max': np.max(sprint_array[:, 4])
            },
            'direction_distribution': {
                dir: (count/n_sprints)*100 
                for dir, count in direction_dist.items()
            }
        }

    def visualize_sprints(self):
        """Visualize sprint patterns on the field"""
        if not self.sprints:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Draw field outline using single plot call
        field_outline = np.array([
            [0, 0], [self.field_length, 0],
            [self.field_length, self.field_width], [0, self.field_width], [0, 0]
        ])
        ax.plot(field_outline[:, 0], field_outline[:, 1], 'k-')

        # Halfway line
        ax.plot([self.field_length/2, self.field_length/2], 
                [0, self.field_width], 'k-', alpha=0.5)
        
        # Prepare sprint data for vectorized plotting
        for i, sprint in enumerate(self.sprints):
            start_pos = np.array(sprint.start_position)
            end_pos = np.array(sprint.end_position)
            
            # Plot sprint path
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]],
                   'r-', alpha=0.6, linewidth=2)
            
            # Plot start and end points
            ax.plot(start_pos[0], start_pos[1], 'go',
                   label='Sprint Start' if i == 0 else "")
            ax.plot(end_pos[0], end_pos[1], 'ro',
                   label='Sprint End' if i == 0 else "")
        
        ax.set_title('Sprint Analysis')
        ax.set_xlabel('Field Length (m)')
        ax.set_ylabel('Field Width (m)')
        ax.legend()
        ax.grid(True)
        ax.axis('equal')
        plt.show()

    def plot_sprint_timeline(self):
        """Plot sprint occurrences and velocities over time"""
        if not self.sprints:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create timeline using vectorized operations
        start_time = self.sprints[0].start_time
        
        for sprint in self.sprints:
            relative_start = (sprint.start_time - start_time).total_seconds()
            ax.plot([relative_start, relative_start + sprint.duration],
                   [sprint.avg_velocity, sprint.avg_velocity],
                   'r-', linewidth=2)
        
        ax.axhline(y=self.sprint_threshold, color='g', linestyle='--',
                  label='Sprint Threshold')
        
        ax.set_title('Sprint Timeline')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Velocity (km/h)')
        ax.legend()
        ax.grid(True)
        plt.show()