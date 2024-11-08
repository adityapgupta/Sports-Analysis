import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import yaml
from datetime import datetime

@dataclass
class PressingEvent:
    timestamp: datetime
    ball_position: Tuple[float, float]
    pressing_players: np.ndarray  # Changed to numpy array for better performance
    distances: np.ndarray        # Changed to numpy array
    closing_speeds: np.ndarray   # Changed to numpy array
    reaction_time: float

class PressingAnalyzer:
    def __init__(self, config_path: str = '../../config/config.yaml'):
        """
        Initialize Pressing Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.field_length = config['field']['length']
            self.field_width = config['field']['width']
            self.max_distance = config['thresholds']['pressing']['max_distance']
            self.reaction_time = config['thresholds']['pressing']['reaction_time']
            self.intensity_threshold = config['thresholds']['pressing']['intensity_threshold']
            
            self.pressing_events: List[PressingEvent] = []
            self.previous_positions = None
            self.previous_timestamp = None
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                "Make sure the path to config.yaml is correct."
            )
        except KeyError as e:
            raise KeyError(f"Missing required configuration key: {str(e)}")

    def analyze_frame(self, 
                     timestamp: datetime,
                     ball_position: Tuple[float, float],
                     defending_positions: List[Tuple[float, float]]) -> Dict:
        """
        Analyze a single frame of defending team's pressing using vectorized operations
        
        Args:
            timestamp: Current timestamp
            ball_position: (x, y) position of the ball
            defending_positions: List of (x, y) positions of defending players
        
        Returns:
            Dictionary containing pressing metrics for the current frame
        """
        # Convert inputs to numpy arrays for vectorized operations
        ball_pos_array = np.array([ball_position])
        def_pos_array = np.array(defending_positions)
        
        # Calculate distances using vectorized operations
        distances = cdist(ball_pos_array, def_pos_array)[0]
        
        # Get nearest defenders using vectorized operations
        nearest_three = np.argpartition(distances, 3)[:3]
        pressing_distances = distances[nearest_three]
        
        # Calculate closing speeds if we have previous positions
        closing_speeds = np.zeros(len(nearest_three))
        if self.previous_positions is not None and self.previous_timestamp is not None:
            time_diff = (timestamp - self.previous_timestamp).total_seconds()
            prev_pos_array = np.array(self.previous_positions)
            
            # Vectorized closing speed calculation
            if len(prev_pos_array) > 0:
                prev_distances = np.linalg.norm(
                    prev_pos_array[nearest_three] - ball_pos_array, 
                    axis=1
                )
                closing_speeds = (prev_distances - pressing_distances) / time_diff
        
        # Store current frame as previous
        self.previous_positions = defending_positions
        self.previous_timestamp = timestamp
        
        # Create pressing event with numpy arrays
        event = PressingEvent(
            timestamp=timestamp,
            ball_position=ball_position,
            pressing_players=def_pos_array[nearest_three],
            distances=pressing_distances,
            closing_speeds=closing_speeds,
            reaction_time=self.reaction_time
        )
        self.pressing_events.append(event)
        
        # Calculate metrics using numpy operations
        return {
            'average_distance': np.mean(pressing_distances),
            'min_distance': np.min(pressing_distances),
            'max_closing_speed': np.max(closing_speeds),
            'pressing_intensity': self._calculate_pressing_intensity(
                pressing_distances, closing_speeds
            )
        }
    
    def _calculate_pressing_intensity(self, 
                                   distances: np.ndarray, 
                                   closing_speeds: np.ndarray) -> float:
        """Calculate pressing intensity score (0-100) using vectorized operations"""
        # Vectorized distance normalization
        dist_scores = np.clip(1 - (distances / self.max_distance), 0, 1)
        
        # Vectorized speed normalization
        speed_scores = np.clip(closing_speeds / self.intensity_threshold, 0, 1)
        
        # Weighted combination
        return 100 * (0.7 * np.mean(dist_scores) + 0.3 * np.mean(speed_scores))
    
    def get_pressing_statistics(self, 
                              time_window: float = None) -> Dict:
        """
        Calculate pressing statistics over a time window using vectorized operations
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all events)
        """
        if not self.pressing_events:
            return {}
        
        # Filter events by time window if specified
        events = self.pressing_events
        if time_window is not None:
            latest_time = events[-1].timestamp
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            events = [e for e in events if e.timestamp >= cutoff_time]
        
        # Vectorized statistics calculation
        all_distances = np.concatenate([e.distances for e in events])
        all_speeds = np.concatenate([e.closing_speeds for e in events])
        
        # Calculate intensity scores using vectorized operations
        intensities = np.array([
            self._calculate_pressing_intensity(e.distances, e.closing_speeds)
            for e in events
        ])
        
        return {
            'avg_distance_to_ball': np.mean(all_distances),
            'min_distance_to_ball': np.min(all_distances),
            'max_closing_speed': np.max(all_speeds),
            'avg_closing_speed': np.mean(all_speeds),
            'pressing_intensity': np.mean(intensities)
        }
    
    def visualize_pressing(self, 
                         event_index: int = -1):
        """Visualize a specific pressing event using efficient plotting"""
        if not self.pressing_events:
            print("No pressing events to visualize")
            return
        
        event = self.pressing_events[event_index]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Draw field outline using single plot call with numpy array
        field_outline = np.array([
            [0, 0], [self.field_length, 0],
            [self.field_length, self.field_width], [0, self.field_width],
            [0, 0]
        ])
        ax.plot(field_outline[:, 0], field_outline[:, 1], 'k-')
        
        # Draw halfway line
        ax.plot([self.field_length/2, self.field_length/2], [0, self.field_width], 
                'k--', alpha=0.3)
        
        # Plot ball
        ball_x, ball_y = event.ball_position
        ax.plot(ball_x, ball_y, 'ro', label='Ball', markersize=10)
        
        # Vectorized plotting of pressing players and lines to ball
        for i, (px, py) in enumerate(event.pressing_players):
            ax.plot(px, py, 'bo', label=f'Pressing Player {i+1}')
            ax.plot([px, ball_x], [py, ball_y], 'b--', alpha=0.3)
        
        # Set title with metrics
        ax.set_title(
            f'Pressing Analysis at {event.timestamp}\n'
            f'Average Distance: {np.mean(event.distances):.1f}m\n'
            f'Max Closing Speed: {np.max(event.closing_speeds):.1f} m/s'
        )
        
        ax.set_xlabel('Field Length (m)')
        ax.set_ylabel('Field Width (m)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        plt.show()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize analyzer
        analyzer = PressingAnalyzer()
        
        # Example data for one frame
        timestamp = datetime.now()
        ball_pos = (60.0, 40.0)
        defending_positions = [
            (55.0, 35.0),
            (58.0, 38.0),
            (57.0, 42.0),
            (62.0, 45.0),
            # Add more positions...
        ]
        
        # Analyze frame
        frame_metrics = analyzer.analyze_frame(timestamp, ball_pos, defending_positions)
        print("\nFrame Metrics:")
        print(f"Average Distance: {frame_metrics['average_distance']:.1f}m")
        print(f"Pressing Intensity: {frame_metrics['pressing_intensity']:.1f}/100")
        
        # Visualize
        analyzer.visualize_pressing()
        
    except Exception as e:
        print(f"Error running example: {str(e)}")