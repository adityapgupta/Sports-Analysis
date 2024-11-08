import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
from scipy import stats
import yaml

@dataclass
class DefensiveLine:
    timestamp: datetime
    positions: List[Tuple[float, float]]
    line_height: float  # Distance from goal line
    line_angle: float  # Angle of defensive line
    straightness: float  # How straight the line is (R² value)
    spacing: float  # Average distance between defenders
    coordination: float  # Standard deviation of movement
    offside_line: float  # Y-coordinate of the offside line

class DefensiveLineAnalyzer:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize Defensive Line Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        self.defensive_lines: List[DefensiveLine] = []
        self.previous_positions: Optional[List[Tuple[float, float]]] = None
        self.previous_timestamp: Optional[datetime] = None
    
    def fit_defensive_line(self, positions: List[Tuple[float, float]]) -> Tuple[float, float, float]:
        """
        Fit a line to defensive positions using linear regression
        
        Returns:
            Tuple of (slope, intercept, R² value)
        """
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        if len(set(x_coords)) < 2:  # Vertical line case
            return float('inf'), np.mean(x_coords), 1.0
            
        slope, intercept, r_value, _, _ = stats.linregress(x_coords, y_coords)
        return slope, intercept, r_value ** 2
    
    def calculate_line_spacing(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate average spacing between defenders"""
        if len(positions) < 2:
            return 0.0
            
        # Sort positions from left to right
        sorted_positions = sorted(positions, key=lambda x: x[0])
        
        # Calculate distances between adjacent defenders
        spacings = []
        for i in range(len(sorted_positions) - 1):
            dist = np.sqrt((sorted_positions[i+1][0] - sorted_positions[i][0])**2 +
                         (sorted_positions[i+1][1] - sorted_positions[i][1])**2)
            spacings.append(dist)
            
        return np.mean(spacings)
    
    def calculate_coordination(self, 
                             current_positions: List[Tuple[float, float]],
                             previous_positions: List[Tuple[float, float]],
                             time_diff: float) -> float:
        """Calculate coordination based on movement consistency"""
        if len(current_positions) != len(previous_positions):
            return 0.0
            
        # Calculate individual movements
        movements = []
        for curr, prev in zip(current_positions, previous_positions):
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            movement = np.sqrt(dx**2 + dy**2)
            movements.append(movement)
            
        # Lower standard deviation indicates better coordination
        return np.std(movements)
    
    def analyze_defensive_line(self, 
                             timestamp: datetime,
                             positions: List[Tuple[float, float]]) -> Dict:
        """
        Analyze defensive line characteristics
        
        Args:
            timestamp: Current timestamp
            positions: List of defender positions (x, y)
        
        Returns:
            Dictionary containing defensive line metrics
        """
        # Need at least 3 defenders to analyze line
        if len(positions) < 3:
            return {}
            
        # Fit line to positions
        slope, intercept, r_squared = self.fit_defensive_line(positions)
        
        # Calculate line height (average distance from goal line)
        line_height = np.mean([p[1] for p in positions])
        
        # Calculate line angle
        line_angle = np.degrees(np.arctan(slope)) if slope != float('inf') else 90
        
        # Calculate spacing
        spacing = self.calculate_line_spacing(positions)
        
        # Calculate coordination if we have previous positions
        coordination = 0.0
        if self.previous_positions is not None and self.previous_timestamp is not None:
            time_diff = (timestamp - self.previous_timestamp).total_seconds()
            coordination = self.calculate_coordination(
                positions, 
                self.previous_positions,
                time_diff
            )
        
        # Calculate offside line (most advanced defender)
        offside_line = max(p[1] for p in positions)
        
        # Create DefensiveLine object
        defensive_line = DefensiveLine(
            timestamp=timestamp,
            positions=positions,
            line_height=line_height,
            line_angle=line_angle,
            straightness=r_squared,
            spacing=spacing,
            coordination=coordination,
            offside_line=offside_line
        )
        
        self.defensive_lines.append(defensive_line)
        
        # Update previous state
        self.previous_positions = positions
        self.previous_timestamp = timestamp
        
        return {
            'line_height': line_height,
            'line_angle': line_angle,
            'straightness': r_squared,
            'spacing': spacing,
            'coordination': coordination,
            'offside_line': offside_line
        }
    
    def get_defensive_trends(self, time_window: float = None) -> Dict:
        """
        Analyze trends in defensive line behavior
        
        Args:
            time_window: Optional time window in seconds to analyze
                        (None for all data)
        """
        if not self.defensive_lines:
            return {}
            
        # Filter by time window if specified
        lines = self.defensive_lines
        if time_window is not None:
            latest_time = self.defensive_lines[-1].timestamp
            cutoff_time = latest_time - datetime.timedelta(seconds=time_window)
            lines = [l for l in lines if l.timestamp >= cutoff_time]
        
        # Calculate trends
        heights = [l.line_height for l in lines]
        angles = [l.line_angle for l in lines]
        straightness = [l.straightness for l in lines]
        spacings = [l.spacing for l in lines]
        coordination = [l.coordination for l in lines]
        
        return {
            'height': {
                'mean': np.mean(heights),
                'std': np.std(heights),
                'trend': np.polyfit(range(len(heights)), heights, 1)[0]
            },
            'angle': {
                'mean': np.mean(angles),
                'std': np.std(angles),
                'trend': np.polyfit(range(len(angles)), angles, 1)[0]
            },
            'straightness': {
                'mean': np.mean(straightness),
                'std': np.std(straightness),
                'trend': np.polyfit(range(len(straightness)), straightness, 1)[0]
            },
            'spacing': {
                'mean': np.mean(spacings),
                'std': np.std(spacings),
                'trend': np.polyfit(range(len(spacings)), spacings, 1)[0]
            },
            'coordination': {
                'mean': np.mean(coordination),
                'std': np.std(coordination),
                'trend': np.polyfit(range(len(coordination)), coordination, 1)[0]
            }
        }
    
    def visualize_defensive_line(self, line_index: int = -1):
        """Visualize defensive line for a specific moment"""
        if not self.defensive_lines:
            return
            
        line = self.defensive_lines[line_index]
        
        plt.figure(figsize=(12, 8))
        
        # Draw field
        plt.plot([0, self.field_length], [0, 0], 'k-')
        plt.plot([0, self.field_length], [self.field_width, self.field_width], 'k-')
        plt.plot([0, 0], [0, self.field_width], 'k-')
        plt.plot([self.field_length, self.field_length], [0, self.field_width], 'k-')
        plt.plot([self.field_length/2, self.field_length/2], [0, self.field_width], 'k--', alpha=0.3)
        
        # Plot defender positions
        positions = np.array(line.positions)
        plt.scatter(positions[:, 0], positions[:, 1], c='blue', s=100, label='Defenders')
        
        # Draw defensive line
        if abs(line.line_angle) != 90:
            x_coords = np.array([0, self.field_width])
            slope = np.tan(np.radians(line.line_angle))
            y_coords = slope * x_coords + line.line_height
            plt.plot(x_coords, y_coords, 'r--', label='Defensive Line')
        else:
            plt.axvline(x=line.line_height, color='r', linestyle='--', label='Defensive Line')
        
        # Draw offside line
        plt.axhline(y=line.offside_line, color='g', linestyle='--', label='Offside Line')
        
        # Add metrics as text
        plt.text(5, self.field_width - 5,
                f'Line Height: {line.line_height:.1f}m\n'
                f'Line Angle: {line.line_angle:.1f}°\n'
                f'Straightness: {line.straightness:.2f}\n'
                f'Spacing: {line.spacing:.1f}m\n'
                f'Coordination: {line.coordination:.2f}',
                bbox=dict(facecolor='white', alpha=0.7))
        
        plt.title(f'Defensive Line Analysis at {line.timestamp}')
        plt.xlabel('Field Width (m)')
        plt.ylabel('Field Length (m)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
    def plot_metric_evolution(self, metric: str = 'line_height'):
        """Plot the evolution of a defensive line metric over time"""
        if not self.defensive_lines:
            return
            
        timestamps = [(l.timestamp - self.defensive_lines[0].timestamp).total_seconds()
                     for l in self.defensive_lines]
        
        metric_map = {
            'line_height': ('line_height', 'Line Height (m)'),
            'line_angle': ('line_angle', 'Line Angle (degrees)'),
            'straightness': ('straightness', 'Line Straightness (R²)'),
            'spacing': ('spacing', 'Defender Spacing (m)'),
            'coordination': ('coordination', 'Movement Coordination')
        }
        
        if metric not in metric_map:
            return
            
        attr_name, ylabel = metric_map[metric]
        values = [getattr(l, attr_name) for l in self.defensive_lines]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, 'b-')
        plt.title(f'Evolution of {ylabel}')
        plt.xlabel('Time (seconds)')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = DefensiveLineAnalyzer()
    
    # Example defensive line positions
    example_positions = [
        (10.0, 30.0),  # Left back
        (25.0, 32.0),  # Left center back
        (35.0, 31.0),  # Right center back
        (50.0, 33.0)   # Right back
    ]
    
    # Analyze defensive line
    metrics = analyzer.analyze_defensive_line(datetime.now(), example_positions)
    
    print("\nDefensive Line Metrics:")
    print(f"Line Height: {metrics['line_height']:.1f}m")
    print(f"Line Angle: {metrics['line_angle']:.1f}°")
    print(f"Straightness: {metrics['straightness']:.2f}")
    print(f"Spacing: {metrics['spacing']:.1f}m")
    
    # Visualize
    analyzer.visualize_defensive_line()
    
    # Plot metric evolution
    analyzer.plot_metric_evolution('line_height')