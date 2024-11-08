import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
import os

@dataclass
class MovementSegment:
    start_time: datetime
    end_time: datetime
    start_pos: np.ndarray  # Changed to numpy array
    end_pos: np.ndarray    # Changed to numpy array
    distance: float
    velocity: float
    category: str  # 'sprint', 'high_intensity', 'jogging', 'walking'

class DistanceAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """
        Initialize Distance Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        try:
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
            
            # Precompute thresholds array for vectorized categorization
            self.threshold_values = np.array([
                self.jogging_threshold,
                self.high_intensity_threshold,
                self.sprint_threshold
            ])
            self.categories = ['walking', 'jogging', 'high_intensity', 'sprint']
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                "Make sure the path to config.yaml is correct."
            )
        except KeyError as e:
            raise KeyError(f"Missing required configuration key: {str(e)}")
    
    def categorize_movement(self, velocity: float) -> str:
        """Categorize movement based on velocity using vectorized operations"""
        return self.categories[np.searchsorted(self.threshold_values, velocity)]
    
    def process_position(self, 
                        timestamp: datetime,
                        position: Tuple[float, float],
                        last_timestamp: datetime = None,
                        last_position: Tuple[float, float] = None) -> Dict:
        """
        Process a new position reading using vectorized operations
        
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
        
        # Convert positions to numpy arrays
        pos_array = np.array(position)
        last_pos_array = np.array(last_position)
        
        # Calculate distance and velocity using numpy
        distance = np.linalg.norm(pos_array - last_pos_array)
        time_diff = (timestamp - last_timestamp).total_seconds()
        velocity = (distance / time_diff) * 3.6  # Convert to km/h
        
        # Categorize movement
        category = self.categorize_movement(velocity)
        
        # Create movement segment
        segment = MovementSegment(
            start_time=last_timestamp,
            end_time=timestamp,
            start_pos=last_pos_array,
            end_pos=pos_array,
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
        Get distance statistics using vectorized operations
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all segments)
        """
        if not self.segments:
            return {}
            
        # Filter segments by time window if specified
        segments = self.segments
        if time_window is not None:
            latest_time = segments[-1].end_time
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            segments = [s for s in segments if s.end_time >= cutoff_time]
        
        # Calculate statistics using numpy
        total_time = (segments[-1].end_time - segments[0].start_time).total_seconds()
        
        # Create arrays for vectorized operations
        velocities = np.array([s.velocity for s in segments])
        
        # Calculate distances by category using dictionary comprehension
        distances = {
            category: sum(s.distance for s in segments if s.category == category)
            for category in self.distances_by_category
        }
        
        total_distance = sum(distances.values())
        
        return {
            'total_distance': total_distance,
            'distances_by_category': distances,
            'percentages_by_category': {
                cat: (dist / total_distance) * 100 
                for cat, dist in distances.items()
            },
            'average_velocity': np.mean(velocities),
            'max_velocity': np.max(velocities),
            'distance_per_minute': total_distance / (total_time / 60)
        }
    
    def visualize_distance_breakdown(self):
        """Visualize distance breakdown by movement category using efficient plotting"""
        stats = self.get_distance_stats()
        
        # Prepare data for visualization
        categories = list(stats['distances_by_category'].keys())
        distances = np.array(list(stats['distances_by_category'].values()))
        percentages = np.array(list(stats['percentages_by_category'].values()))
        
        # Create color map
        colors = ['red', 'orange', 'yellow', 'green']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Pie chart
        ax1.pie(distances, 
                labels=[f"{cat}\n{dist:.1f}m" for cat, dist in zip(categories, distances)],
                colors=colors, autopct='%1.1f%%')
        ax1.set_title('Distance Breakdown by Movement Category')
        
        # Bar chart for average velocities
        velocities_by_cat = {
            cat: np.mean([s.velocity for s in self.segments if s.category == cat])
            for cat in categories
        }
        ax2.bar(categories, list(velocities_by_cat.values()), color=colors)
        ax2.set_title('Average Velocity by Category')
        ax2.set_ylabel('Velocity (km/h)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_velocity_profile(self, smoothing_window: int = 10):
        """Plot velocity profile over time using vectorized operations"""
        if not self.segments:
            return
            
        # Create arrays for vectorized operations
        timestamps = np.array([(s.end_time - self.segments[0].start_time).total_seconds()
                             for s in self.segments])
        velocities = np.array([s.velocity for s in self.segments])
        
        # Apply smoothing using numpy's convolve
        if smoothing_window > 1:
            kernel = np.ones(smoothing_window) / smoothing_window
            velocities = np.convolve(velocities, kernel, mode='valid')
            timestamps = timestamps[smoothing_window-1:]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot velocity profile
        ax.plot(timestamps, velocities, 'b-')
        
        # Add threshold lines
        thresholds = [
            (self.sprint_threshold, 'Sprint Threshold', 'red'),
            (self.high_intensity_threshold, 'High Intensity Threshold', 'orange'),
            (self.jogging_threshold, 'Jogging Threshold', 'green')
        ]
        
        for threshold, label, color in thresholds:
            ax.axhline(y=threshold, color=color, linestyle='--', label=label)
        
        ax.set_title('Velocity Profile')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Velocity (km/h)')
        ax.legend()
        ax.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize analyzer
        analyzer = DistanceAnalyzer()
        
        # Example tracking data using numpy arrays
        tracking_data = [
            (datetime.now(), np.array([0.0, 0.0])),
            (datetime.now(), np.array([5.0, 5.0])),
            (datetime.now(), np.array([10.0, 8.0])),
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
        
    except Exception as e:
        print(f"Error running example: {str(e)}")