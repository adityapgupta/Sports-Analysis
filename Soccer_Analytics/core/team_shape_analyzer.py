import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import yaml
from scipy.spatial.distance import pdist, squareform
import os


@dataclass
class TeamShape:
    timestamp: datetime
    positions: List[Tuple[float, float]]
    width: float
    depth: float
    area: float
    compactness: float
    centroid: Tuple[float, float]
    stretch_index: float
    player_distances: Dict[Tuple[int, int], float]

class TeamShapeAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """
        Initialize Team Shape Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.min_players = config['thresholds']['team_shape']['min_players']
        self.update_frequency = config['thresholds']['team_shape']['update_frequency']
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        
        self.shapes: List[TeamShape] = []
        self.last_update = None
    
    def calculate_team_shape(self, 
                           timestamp: datetime,
                           positions: List[Tuple[float, float]]) -> Dict:
        """
        Calculate team shape metrics for a given set of player positions
        
        Args:
            timestamp: Current timestamp
            positions: List of player positions (x, y)
        
        Returns:
            Dictionary containing team shape metrics
        """
        if len(positions) < self.min_players:
            return {}
            
        # Convert positions to numpy array for calculations
        pos_array = np.array(positions)
        
        # Calculate basic shape metrics
        x_coords, y_coords = pos_array[:, 0], pos_array[:, 1]
        
        # Width (lateral spread)
        width = np.max(x_coords) - np.min(x_coords)
        
        # Depth (longitudinal spread)
        depth = np.max(y_coords) - np.min(y_coords)
        
        # Calculate area using convex hull
        hull = ConvexHull(pos_array)
        area = hull.area
        
        # Calculate centroid
        centroid = (np.mean(x_coords), np.mean(y_coords))
        
        # Calculate compactness (average distance between players)
        distances = pdist(pos_array)
        compactness = np.mean(distances)
        
        # Calculate stretch index (ratio of actual area to minimal possible area)
        min_area = (width * depth) / 2
        stretch_index = area / min_area if min_area > 0 else 0
        
        # Calculate distance matrix between players
        distance_matrix = squareform(distances)
        player_distances = {
            (i, j): distance_matrix[i, j]
            for i in range(len(positions))
            for j in range(i + 1, len(positions))
        }
        
        # Create TeamShape object
        shape = TeamShape(
            timestamp=timestamp,
            positions=positions,
            width=width,
            depth=depth,
            area=area,
            compactness=compactness,
            centroid=centroid,
            stretch_index=stretch_index,
            player_distances=player_distances
        )
        
        self.shapes.append(shape)
        
        return {
            'width': width,
            'depth': depth,
            'area': area,
            'compactness': compactness,
            'centroid': centroid,
            'stretch_index': stretch_index
        }
    
    def get_shape_evolution(self, time_window: float = None) -> Dict:
        """
        Analyze how team shape evolves over time
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all shapes)
        """
        if not self.shapes:
            return {}
            
        # Filter shapes by time window if specified
        shapes = self.shapes
        if time_window is not None:
            latest_time = self.shapes[-1].timestamp
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            shapes = [s for s in shapes if s.timestamp >= cutoff_time]
        
        # Calculate evolution metrics
        widths = [s.width for s in shapes]
        depths = [s.depth for s in shapes]
        areas = [s.area for s in shapes]
        compactness = [s.compactness for s in shapes]
        
        return {
            'width': {
                'mean': np.mean(widths),
                'std': np.std(widths),
                'min': np.min(widths),
                'max': np.max(widths)
            },
            'depth': {
                'mean': np.mean(depths),
                'std': np.std(depths),
                'min': np.min(depths),
                'max': np.max(depths)
            },
            'area': {
                'mean': np.mean(areas),
                'std': np.std(areas),
                'min': np.min(areas),
                'max': np.max(areas)
            },
            'compactness': {
                'mean': np.mean(compactness),
                'std': np.std(compactness),
                'min': np.min(compactness),
                'max': np.max(compactness)
            }
        }
    
    def visualize_team_shape(self, shape_index: int = -1):
        """Visualize team shape for a specific moment"""
        if not self.shapes:
            return
            
        shape = self.shapes[shape_index]
        
        plt.figure(figsize=(12, 8))
        
        # Draw field
        plt.plot([0, self.field_length], [0, 0], 'k-')
        plt.plot([0, self.field_length], [self.field_width, self.field_width], 'k-')
        plt.plot([0, 0], [0, self.field_width], 'k-')
        plt.plot([self.field_length, self.field_length], [0, self.field_width], 'k-')
        plt.plot([self.field_length/2, self.field_length/2], [0, self.field_width], 'k--', alpha=0.3)
        
        # Plot player positions
        pos_array = np.array(shape.positions)
        plt.scatter(pos_array[:, 0], pos_array[:, 1], c='blue', s=100, label='Players')
        
        # Plot centroid
        plt.scatter([shape.centroid[0]], [shape.centroid[1]], c='red', s=200, 
                   marker='*', label='Team Centroid')
        
        # Draw convex hull
        hull = ConvexHull(pos_array)
        for simplex in hull.simplices:
            plt.plot(pos_array[simplex, 0], pos_array[simplex, 1], 'g-', alpha=0.5)
        
        # Add shape metrics as text
        plt.text(5, self.field_width - 5, 
                f'Width: {shape.width:.1f}m\n'
                f'Depth: {shape.depth:.1f}m\n'
                f'Area: {shape.area:.1f}m²\n'
                f'Compactness: {shape.compactness:.1f}m\n'
                f'Stretch Index: {shape.stretch_index:.2f}',
                bbox=dict(facecolor='white', alpha=0.7))
        
        plt.title(f'Team Shape Analysis at {shape.timestamp}')
        plt.xlabel('Field Length (m)')
        plt.ylabel('Field Width (m)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
    def plot_shape_evolution(self, metric: str = 'area'):
        """Plot the evolution of a shape metric over time"""
        if not self.shapes:
            return
            
        timestamps = [(s.timestamp - self.shapes[0].timestamp).total_seconds()
                     for s in self.shapes]
        
        if metric == 'area':
            values = [s.area for s in self.shapes]
            ylabel = 'Team Area (m²)'
        elif metric == 'width':
            values = [s.width for s in self.shapes]
            ylabel = 'Team Width (m)'
        elif metric == 'depth':
            values = [s.depth for s in self.shapes]
            ylabel = 'Team Depth (m)'
        elif metric == 'compactness':
            values = [s.compactness for s in self.shapes]
            ylabel = 'Team Compactness (m)'
        else:
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, 'b-')
        plt.title(f'Evolution of Team {metric.capitalize()} Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

    def analyze_tactical_balance(self) -> Dict:
        """Analyze the tactical balance and structure of the team"""
        if not self.shapes:
            return {}
        
        latest_shape = self.shapes[-1]
        positions = np.array(latest_shape.positions)
        
        # Calculate vertical balance (distribution across the pitch length)
        vertical_thirds = np.histogram(positions[:, 1], 
                                     bins=3, 
                                     range=(0, self.field_length))[0]
        vertical_balance = np.std(vertical_thirds) / np.mean(vertical_thirds)
        
        # Calculate horizontal balance (distribution across the pitch width)
        horizontal_thirds = np.histogram(positions[:, 0], 
                                       bins=3, 
                                       range=(0, self.field_width))[0]
        horizontal_balance = np.std(horizontal_thirds) / np.mean(horizontal_thirds)
        
        # Analyze team structure
        distances_to_centroid = np.linalg.norm(
            positions - np.array(latest_shape.centroid), 
            axis=1
        )
        
        return {
            'vertical_balance': vertical_balance,
            'horizontal_balance': horizontal_balance,
            'structure_symmetry': np.std(distances_to_centroid),
            'player_distribution': {
                'defensive_third': int(vertical_thirds[0]),
                'middle_third': int(vertical_thirds[1]),
                'attacking_third': int(vertical_thirds[2])
            }
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = TeamShapeAnalyzer()
    
    # Example tracking data
    example_positions = [
        (30.0, 20.0),
        (35.0, 25.0),
        (41.0, 30.0),
        (47.0, 35.0),
        (53.0, 40.0),
        (59.0, 45.0),
        (65.0, 50.0),
        (71.0, 55.0),
        (77.0, 60.0),
        (82.0, 65.0)
    ]
    
    # Calculate shape metrics
    metrics = analyzer.calculate_team_shape(datetime.now(), example_positions)
    print("\nTeam Shape Metrics:")
    print(f"Width: {metrics['width']:.1f}m")
    print(f"Depth: {metrics['depth']:.1f}m")
    print(f"Area: {metrics['area']:.1f}m²")
    print(f"Compactness: {metrics['compactness']:.1f}m")
    
    # Visualize current shape
    analyzer.visualize_team_shape()
    
    # Analyze tactical balance
    balance = analyzer.analyze_tactical_balance()
    print("\nTactical Balance:")
    print(f"Vertical Balance: {balance['vertical_balance']:.2f}")
    print(f"Horizontal Balance: {balance['horizontal_balance']:.2f}")
    print("\nPlayer Distribution:")
    for third, count in balance['player_distribution'].items():
        print(f"{third}: {count} players")