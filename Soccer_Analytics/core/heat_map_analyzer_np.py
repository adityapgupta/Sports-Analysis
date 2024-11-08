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
        self.grid_size = np.array(config['visualization']['heat_map']['grid_size'])
        self.smoothing = config['visualization']['heat_map']['smoothing']
        
        # Initialize heat map grid
        self.grid = np.zeros(self.grid_size)
        
        # Pre-compute scaling factors for position conversion
        self.scale_factors = np.array([
            self.grid_size[0] / self.field_length,
            self.grid_size[1] / self.field_width
        ])
        
    def positions_to_grid(self, positions: np.ndarray) -> np.ndarray:
        """
        Vectorized conversion of field positions to grid coordinates
        
        Args:
            positions: Nx2 array of positions
        Returns:
            Nx2 array of grid coordinates
        """
        # Scale positions to grid coordinates
        grid_coords = positions * self.scale_factors
        
        # Clip to ensure within bounds
        return np.clip(
            grid_coords.astype(np.int32),
            0,
            np.array([self.grid_size[0] - 1, self.grid_size[1] - 1])
        )
    
    def add_positions(self, positions: List[Tuple[float, float]], durations: List[float] = None):
        """
        Add multiple position observations to the heat map using vectorized operations
        """
        # Convert positions to numpy array
        pos_array = np.array(positions)
        
        # Get grid coordinates for all positions at once
        grid_coords = self.positions_to_grid(pos_array)
        
        # Handle durations
        if durations is None:
            durations = np.ones(len(positions))
        else:
            durations = np.array(durations)
        
        # Use numpy's add.at for atomic operations
        np.add.at(self.grid, (grid_coords[:, 0], grid_coords[:, 1]), durations)
    
    def add_position(self, position: Tuple[float, float], duration: float = 1.0):
        """Add a single position observation to the heat map"""
        self.add_positions([position], [duration])
    
    def get_normalized_heat_map(self) -> np.ndarray:
        """Get normalized and smoothed heat map"""
        grid_max = np.max(self.grid)
        if grid_max > 0:
            normalized = self.grid / grid_max
        else:
            normalized = self.grid
            
        return gaussian_filter(normalized, sigma=self.smoothing)
    
    def visualize(self, title: str = "Heat Map", save_path: str = None):
        """Visualize the heat map"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot heat map
        heat_map = self.get_normalized_heat_map()
        im = ax.imshow(heat_map.T, origin='lower', cmap='hot', 
                      extent=[0, self.field_length, 0, self.field_width])
        
        # Add field markings
        self._draw_field_markings(ax)
        
        plt.colorbar(im, label='Normalized Presence')
        ax.set_title(title)
        ax.set_xlabel('Field Length (m)')
        ax.set_ylabel('Field Width (m)')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        else:
            plt.show()
        
        plt.close()
    
    def _draw_field_markings(self, ax):
        """Draw basic football field markings"""
        # Field outline - using numpy arrays for vectorized plotting
        field_outline = np.array([
            [[0, self.field_length], [0, 0]],  # bottom line
            [[0, self.field_length], [self.field_width, self.field_width]],  # top line
            [[0, 0], [0, self.field_width]],  # left line
            [[self.field_length, self.field_length], [0, self.field_width]]  # right line
        ])
        
        for line in field_outline:
            ax.plot(line[0], line[1], 'w-', alpha=0.5)
        
        # Halfway line
        ax.plot([self.field_length/2, self.field_length/2], 
                [0, self.field_width], 'w-', alpha=0.5)
        
        # Center circle
        center_circle = plt.Circle((self.field_length/2, self.field_width/2), 
                                 self.field_radius, fill=False, color='w', alpha=0.5)
        ax.add_artist(center_circle)
    
    def get_zone_statistics(self) -> Dict:
        """Calculate statistics for different zones of the field using vectorized operations"""
        # Calculate thirds using vectorized operations
        third_size = self.grid_size[0] // 3
        thirds_sum = np.array([
            np.sum(self.grid[:third_size]),
            np.sum(self.grid[third_size:2*third_size]),
            np.sum(self.grid[2*third_size:])
        ])
        
        total_time = np.sum(thirds_sum)
        
        # Avoid division by zero
        if total_time > 0:
            percentages = (thirds_sum / total_time) * 100
        else:
            percentages = np.zeros(3)
        
        # Get most visited zone using numpy's argmax
        most_visited_idx = np.unravel_index(np.argmax(self.grid), self.grid.shape)
        
        return {
            'defensive_third_percentage': percentages[0],
            'middle_third_percentage': percentages[1],
            'attacking_third_percentage': percentages[2],
            'most_visited_zone': most_visited_idx
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = HeatMapAnalyzer()
    
    # Example tracking data as numpy array
    example_positions = np.array([
        [50.0, 30.0],
        [52.0, 32.0],
        [48.0, 35.0],
        # Add more positions...
    ])
    
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