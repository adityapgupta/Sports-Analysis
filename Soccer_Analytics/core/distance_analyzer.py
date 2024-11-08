import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.distance import euclidean

@dataclass
class MovementSegment:
    start_time: datetime
    end_time: datetime
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    distance: float
    velocity: float
    category: str  # 'sprint', 'high_intensity', 'jogging', 'walking'

class DistanceAnalyzer:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize Distance Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self.sprint_threshold = config['thresholds']['distance']['sprint_threshold']
        self.high_intensity_threshold = config['thresholds']['distance']['high_intensity_threshold']
        self.jogging_threshold = config['thresholds']['distance']['jogging_threshold']
        
        self.segments: List[MovementSegment] = []
        self.total_distance = 0.0
        self.distances_by_category = {
            'sprint': 0.0,
            'high_intensity': 0.0,
            'jogging': 0.0,
            'walking': 0.0
        }
    
    def categorize_movement(self, velocity: float) -> str:
        """Categorize movement based on velocity"""
        if velocity >= self.sprint_threshold:
            return 'sprint'
        elif velocity >= self.high_intensity_threshold:
            return 'high_intensity'
        elif velocity >= self.jogging_threshold:
            return 'jogging'
        return 'walking'
    
    def process_position(self, 
                        timestamp: datetime,
                        position: Tuple[float, float],
                        last_timestamp: datetime = None,
                        last_position: Tuple[float, float] = None) -> Dict:
        """
        Process a new position reading
        
        Args:
            timestamp: Current timestamp
            position: Current position (x, y)
            last_timestamp: Previous timestamp (optional)
            last_position: Previous position (optional)
        
        Returns:
            Dictionary containing movement metrics
        """
        if last_timestamp is None or last_position is None:
            return {}
        
        # Calculate distance and velocity
        distance = euclidean(last_position, position)
        time_diff = (timestamp - last_timestamp).total_seconds()
        velocity = (distance / time_diff) * 3.6  # Convert to km/h
        
        # Categorize movement
        category = self.categorize_movement(velocity)
        
        # Create movement segment
        segment = MovementSegment(
            start_time=last_timestamp,
            end_time=timestamp,
            start_pos=last_position,
            end_pos=position,
            distance=distance,
            velocity=velocity,
            category=category
        )
        self.segments.append(segment)
        
        # Update totals
        self.total_distance += distance
        self.distances_by_category[category] += distance
        
        return {
            'distance': distance,
            'velocity': velocity,
            'category': category
        }
    
    def get_distance_stats(self, time_window: float = None) -> Dict:
        """
        Get distance statistics
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all segments)
        """
        if not self.segments:
            return {}
            
        # Filter segments by time window if specified
        segments = self.segments
        if time_window is not None:
            latest_time = self.segments[-1].end_time
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            segments = [s for s in segments if s.end_time >= cutoff_time]
        
        # Calculate statistics
        total_time = (segments[-1].end_time - segments[0].start_time).total_seconds()
        
        distances = {category: sum(s.distance for s in segments if s.category == category)
                    for category in self.distances_by_category.keys()}
        
        velocities = [s.velocity for s in segments]
        
        return {
            'total_distance': sum(distances.values()),
            'distances_by_category': distances,
            'percentages_by_category': {
                cat: (dist / sum(distances.values())) * 100 
                for cat, dist in distances.items()
            },
            'average_velocity': np.mean(velocities),
            'max_velocity': max(velocities),
            'distance_per_minute': sum(distances.values()) / (total_time / 60)
        }
    
    def visualize_distance_breakdown(self):
        """Visualize distance breakdown by movement category"""
        stats = self.get_distance_stats()
        
        # Prepare data for pie chart
        categories = list(stats['distances_by_category'].keys())
        distances = list(stats['distances_by_category'].values())
        percentages = list(stats['percentages_by_category'].values())
        
        # Create color map
        colors = ['red', 'orange', 'yellow', 'green']
        
        plt.figure(figsize=(12, 6))
        
        # Pie chart
        plt.subplot(1, 2, 1)
        plt.pie(distances, labels=[f"{cat}\n{dist:.1f}m" 
                                 for cat, dist in zip(categories, distances)],
                colors=colors, autopct='%1.1f%%')
        plt.title('Distance Breakdown by Movement Category')
        
        # Bar chart for average velocities
        plt.subplot(1, 2, 2)
        velocities_by_cat = {
            cat: np.mean([s.velocity for s in self.segments if s.category == cat])
            for cat in categories
        }
        plt.bar(categories, velocities_by_cat.values(), color=colors)
        plt.title('Average Velocity by Category')
        plt.ylabel('Velocity (km/h)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_velocity_profile(self, smoothing_window: int = 10):
        """Plot velocity profile over time"""
        if not self.segments:
            return
            
        timestamps = [(s.end_time - self.segments[0].start_time).total_seconds()
                     for s in self.segments]
        velocities = [s.velocity for s in self.segments]
        
        # Apply smoothing
        if smoothing_window > 1:
            velocities = np.convolve(velocities, 
                                   np.ones(smoothing_window)/smoothing_window,
                                   mode='valid')
            timestamps = timestamps[smoothing_window-1:]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, velocities, 'b-')
        
        # Add threshold lines
        plt.axhline(y=self.sprint_threshold, color='r', linestyle='--',
                   label='Sprint Threshold')
        plt.axhline(y=self.high_intensity_threshold, color='orange', 
                   linestyle='--', label='High Intensity Threshold')
        plt.axhline(y=self.jogging_threshold, color='g', linestyle='--',
                   label='Jogging Threshold')
        
        plt.title('Velocity Profile')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (km/h)')
        plt.legend()
        plt.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = DistanceAnalyzer()
    
    # Example tracking data
    tracking_data = [
        (datetime.now(), (0.0, 0.0)),
        (datetime.now(), (5.0, 5.0)),
        (datetime.now(), (10.0, 8.0)),
        # Add more tracking data...
    ]
    
    # Process positions
    for i in range(1, len(tracking_data)):
        analyzer.process_position(
            tracking_data[i][0],
            tracking_data[i][1],
            tracking_data[i-1][0],
            tracking_data[i-1][1]
        )
    
    # Get and print statistics
    stats = analyzer.get_distance_stats()
    print("\nDistance Statistics:")
    print(f"Total Distance: {stats['total_distance']:.1f}m")
    print("\nBreakdown by Category:")
    for cat, dist in stats['distances_by_category'].items():
        print(f"{cat}: {dist:.1f}m ({stats['percentages_by_category'][cat]:.1f}%)")
    
    # Visualize
    analyzer.visualize_distance_breakdown()
    analyzer.plot_velocity_profile()