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
    pressing_players: List[Tuple[float, float]]
    distances: List[float]
    closing_speeds: List[float]
    reaction_time: float

class PressingAnalyzer:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize Pressing Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.max_distance = config['thresholds']['pressing']['max_distance']
        self.reaction_time = config['thresholds']['pressing']['reaction_time']
        self.intensity_threshold = config['thresholds']['pressing']['intensity_threshold']
        
        self.pressing_events: List[PressingEvent] = []
        self.previous_positions = None
        self.previous_timestamp = None

    def analyze_frame(self, 
                     timestamp: datetime,
                     ball_position: Tuple[float, float],
                     defending_positions: List[Tuple[float, float]]) -> Dict:
        """
        Analyze a single frame of defending team's pressing
        
        Args:
            timestamp: Current timestamp
            ball_position: (x, y) position of the ball
            defending_positions: List of (x, y) positions of defending players
        
        Returns:
            Dictionary containing pressing metrics for the current frame
        """
        # Calculate distances from each defender to the ball
        distances = cdist([ball_position], defending_positions)[0]
        
        # Sort distances and get nearest defenders
        sorted_indices = np.argsort(distances)
        nearest_three = sorted_indices[:3]
        
        # Calculate pressing metrics
        pressing_distances = distances[nearest_three]
        
        # Calculate closing speeds if we have previous positions
        closing_speeds = [0.0] * len(nearest_three)
        if self.previous_positions is not None and self.previous_timestamp is not None:
            time_diff = (timestamp - self.previous_timestamp).total_seconds()
            for i, idx in enumerate(nearest_three):
                if idx < len(self.previous_positions):
                    prev_dist = np.linalg.norm(
                        np.array(self.previous_positions[idx]) - 
                        np.array(self.previous_timestamp)
                    )
                    curr_dist = distances[idx]
                    closing_speeds[i] = (prev_dist - curr_dist) / time_diff
        
        # Store current frame as previous
        self.previous_positions = defending_positions
        self.previous_timestamp = timestamp
        
        # Create pressing event
        event = PressingEvent(
            timestamp=timestamp,
            ball_position=ball_position,
            pressing_players=[defending_positions[i] for i in nearest_three],
            distances=pressing_distances.tolist(),
            closing_speeds=closing_speeds,
            reaction_time=self.reaction_time
        )
        self.pressing_events.append(event)
        
        return {
            'average_distance': np.mean(pressing_distances),
            'min_distance': np.min(pressing_distances),
            'max_closing_speed': max(closing_speeds),
            'pressing_intensity': self._calculate_pressing_intensity(
                pressing_distances, closing_speeds
            )
        }
    
    def _calculate_pressing_intensity(self, 
                                   distances: List[float], 
                                   closing_speeds: List[float]) -> float:
        """Calculate pressing intensity score (0-100)"""
        # Normalize distances (closer is better)
        dist_scores = [max(0, 1 - (d / self.max_distance)) for d in distances]
        
        # Normalize closing speeds (faster closing is better)
        speed_scores = [max(0, min(1, s / self.intensity_threshold)) 
                       for s in closing_speeds]
        
        # Combine scores (70% distance, 30% closing speed)
        return 100 * (0.7 * np.mean(dist_scores) + 0.3 * np.mean(speed_scores))
    
    def get_pressing_statistics(self, 
                              time_window: float = None) -> Dict:
        """
        Calculate pressing statistics over a time window
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all events)
        """
        if not self.pressing_events:
            return {}
        
        # Filter events by time window if specified
        events = self.pressing_events
        if time_window is not None:
            latest_time = self.pressing_events[-1].timestamp
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            events = [e for e in events if e.timestamp >= cutoff_time]
        
        # Calculate statistics
        all_distances = [d for e in events for d in e.distances]
        all_speeds = [s for e in events for s in e.closing_speeds]
        
        return {
            'avg_distance_to_ball': np.mean(all_distances),
            'min_distance_to_ball': np.min(all_distances),
            'max_closing_speed': max(all_speeds),
            'avg_closing_speed': np.mean(all_speeds),
            'pressing_intensity': np.mean([
                self._calculate_pressing_intensity(e.distances, e.closing_speeds)
                for e in events
            ])
        }
    
    def visualize_pressing(self, 
                         event_index: int = -1,
                         field_length: float = 105,
                         field_width: float = 68):
        """Visualize a specific pressing event"""
        if not self.pressing_events:
            print("No pressing events to visualize")
            return
        
        event = self.pressing_events[event_index]
        
        plt.figure(figsize=(12, 8))
        
        # Draw field
        plt.plot([0, field_length], [0, 0], 'k-')
        plt.plot([0, field_length], [field_width, field_width], 'k-')
        plt.plot([0, 0], [0, field_width], 'k-')
        plt.plot([field_length, field_length], [0, field_width], 'k-')
        plt.plot([field_length/2, field_length/2], [0, field_width], 'k--', alpha=0.3)
        
        # Plot ball
        plt.plot(event.ball_position[0], event.ball_position[1], 'ro', 
                label='Ball', markersize=10)
        
        # Plot pressing players
        for i, pos in enumerate(event.pressing_players):
            plt.plot(pos[0], pos[1], 'bo', label=f'Pressing Player {i+1}')
            # Draw line to ball
            plt.plot([pos[0], event.ball_position[0]], 
                    [pos[1], event.ball_position[1]], 'b--', alpha=0.3)
        
        plt.title(f'Pressing Analysis at {event.timestamp}\n' +
                 f'Average Distance: {np.mean(event.distances):.1f}m\n' +
                 f'Max Closing Speed: {max(event.closing_speeds):.1f} m/s')
        plt.xlabel('Field Length (m)')
        plt.ylabel('Field Width (m)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()

# Example usage
if __name__ == "__main__":
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