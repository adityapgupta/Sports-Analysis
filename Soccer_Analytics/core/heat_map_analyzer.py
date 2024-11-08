import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import yaml

class HeatMapAnalyzer:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize Heat Map Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        self.field_radius = config['field']['radius']
        self.grid_size = config['visualization']['heat_map']['grid_size']
        self.smoothing = config['visualization']['heat_map']['smoothing']
        
        # Initialize heat map grid
        self.grid = np.zeros(self.grid_size)
        
    def position_to_grid(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Convert field position to grid coordinates"""
        x_cell = int((position[0] / self.field_length) * self.grid_size[0])
        y_cell = int((position[1] / self.field_width) * self.grid_size[1])
        
        # Ensure within bounds
        x_cell = min(max(x_cell, 0), self.grid_size[0] - 1)
        y_cell = min(max(y_cell, 0), self.grid_size[1] - 1)
        
        return x_cell, y_cell
    
    def add_position(self, position: Tuple[float, float], duration: float = 1.0):
        """Add a position observation to the heat map"""
        x_cell, y_cell = self.position_to_grid(position)
        self.grid[x_cell, y_cell] += duration
    
    def add_positions(self, positions: List[Tuple[float, float]], durations: List[float] = None):
        """Add multiple position observations to the heat map"""
        if durations is None:
            durations = [1.0] * len(positions)
            
        for position, duration in zip(positions, durations):
            self.add_position(position, duration)
    
    def get_normalized_heat_map(self) -> np.ndarray:
        """Get normalized and smoothed heat map"""
        if np.max(self.grid) > 0:
            normalized = self.grid / np.max(self.grid)
        else:
            normalized = self.grid
            
        return gaussian_filter(normalized, sigma=self.smoothing)
    
    def visualize(self, title: str = "Heat Map", save_path: str = None):
        """Visualize the heat map"""
        plt.figure(figsize=(12, 8))
        
        # Plot heat map
        heat_map = self.get_normalized_heat_map()
        plt.imshow(heat_map.T, origin='lower', cmap='hot', 
                  extent=[0, self.field_length, 0, self.field_width])
        
        # Add field markings
        self._draw_field_markings()
        
        plt.colorbar(label='Normalized Presence')
        plt.title(title)
        plt.xlabel('Field Length (m)')
        plt.ylabel('Field Width (m)')
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        
        plt.close()
    
    def _draw_field_markings(self):
        """Draw basic football field markings"""
        # Field outline
        plt.plot([0, self.field_length], [0, 0], 'w-', alpha=0.5)
        plt.plot([0, self.field_length], [self.field_width, self.field_width], 'w-', alpha=0.5)
        plt.plot([0, 0], [0, self.field_width], 'w-', alpha=0.5)
        plt.plot([self.field_length, self.field_length], [0, self.field_width], 'w-', alpha=0.5)
        
        # Halfway line
        plt.plot([self.field_length/2, self.field_length/2], 
                [0, self.field_width], 'w-', alpha=0.5)
        
        # Center circle
        center_circle = plt.Circle((self.field_length/2, self.field_width/2), 
                                 self.field_radius, fill=False, color='w', alpha=0.5)
        plt.gca().add_artist(center_circle)
    
    def get_zone_statistics(self) -> Dict:
        """Calculate statistics for different zones of the field"""
        # Divide field into thirds
        thirds = np.array_split(self.grid, 3, axis=0)
        
        # Calculate time spent in each third
        defensive_third = np.sum(thirds[0])
        middle_third = np.sum(thirds[1])
        attacking_third = np.sum(thirds[2])
        total_time = defensive_third + middle_third + attacking_third
        
        return {
            'defensive_third_percentage': (defensive_third / total_time) * 100,
            'middle_third_percentage': (middle_third / total_time) * 100,
            'attacking_third_percentage': (attacking_third / total_time) * 100,
            'most_visited_zone': np.unravel_index(np.argmax(self.grid), self.grid.shape)
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = HeatMapAnalyzer()
    
    # Example tracking data (normally from your tracking system)
    example_positions = [
        (50.0, 30.0),
        (52.0, 32.0),
        (48.0, 35.0),
        # Add more positions...
    ]
    
    # Add positions to heat map
    analyzer.add_positions(example_positions)
    
    # Visualize heat map
    analyzer.visualize("Player Heat Map")
    
    # Get zone statistics
    stats = analyzer.get_zone_statistics()
    print("\nZone Statistics:")
    print(f"Defensive Third: {stats['defensive_third_percentage']:.1f}%")
    print(f"Middle Third: {stats['middle_third_percentage']:.1f}%")
    print(f"Attacking Third: {stats['attacking_third_percentage']:.1f}%")