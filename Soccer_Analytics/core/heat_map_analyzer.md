# Heat Map Analyzer Documentation

## Overview
The `HeatMapAnalyzer` class provides functionality for creating and analyzing heat maps of player movements and positions on a soccer field. It includes both a standard implementation and a NumPy-optimized version for improved performance.

## Features

### Core Functionality
- Creates heat maps from player position data
- Supports temporal weighting of positions
- Provides zone-based statistical analysis
- Includes visualization capabilities
- Optimized implementation for large datasets

### Heat Map Generation
- Configurable grid resolution
- Gaussian smoothing for visual appeal
- Normalized intensity scaling
- Support for duration-weighted positions

## Classes

### HeatMapAnalyzer (Standard Version)

#### Initialization
```python
analyzer = HeatMapAnalyzer(config_path='config/config.yaml')
```

#### Key Methods
1. `add_position(position: Tuple[float, float], duration: float = 1.0)`
   - Adds single position to heat map
   - Optional duration weighting

2. `add_positions(positions: List[Tuple[float, float]], durations: List[float] = None)`
   - Adds multiple positions
   - Batch processing for efficiency

3. `get_normalized_heat_map() -> np.ndarray`
   - Returns normalized heat map data
   - Applies Gaussian smoothing

4. `visualize(title: str = "Heat Map", save_path: str = None)`
   - Creates visual representation
   - Optional save to file

5. `get_zone_statistics() -> Dict`
   - Calculates zonal statistics
   - Returns percentage distributions

### HeatMapAnalyzer (NumPy-Optimized Version)

#### Key Improvements
- Vectorized operations for better performance
- Optimized memory usage
- Enhanced handling of large datasets
- Pre-computed scaling factors

## Configuration

Required YAML configuration structure:
```yaml
field:
  length: float
  width: float
  radius: float

visualization:
  heat_map:
    grid_size: [int, int]
    smoothing: float
```

## Zone Analysis

### Zones Defined
1. Defensive Third
2. Middle Third
3. Attacking Third

### Statistics Calculated
- Percentage time in each third
- Most visited zones
- Zone transitions
- Activity distribution

## Visualization Features

### Field Markings
- Full field outline
- Halfway line
- Center circle
- Optional additional markings

### Heat Map Properties
- Configurable color scheme
- Normalized intensity
- Smooth gradients
- Optional overlays

## Performance Optimization

### Standard Version
- Suitable for small to medium datasets
- Simple implementation
- Memory efficient
- Easy to modify

### NumPy-Optimized Version
- Vectorized operations
- Batch processing
- Pre-computed conversions
- Optimized memory usage

## Usage Examples

### Basic Usage
```python
# Initialize analyzer
analyzer = HeatMapAnalyzer()

# Add positions
positions = [(50.0, 30.0), (52.0, 32.0)]
analyzer.add_positions(positions)

# Generate visualization
analyzer.visualize("Player Heat Map")

# Get statistics
stats = analyzer.get_zone_statistics()
```

### Advanced Usage
```python
# With duration weighting
positions = [(50.0, 30.0), (52.0, 32.0)]
durations = [2.0, 1.5]
analyzer.add_positions(positions, durations)

# Custom visualization
analyzer.visualize(
    title="Custom Heat Map",
    save_path="heatmap.png"
)

# Detailed statistics
stats = analyzer.get_zone_statistics()
print(f"Defensive Third: {stats['defensive_third_percentage']:.1f}%")
```

## Best Practices

### Data Preparation
1. Clean position data
2. Handle outliers
3. Consider temporal aspects
4. Normalize coordinates

### Analysis Workflow
1. Initialize with appropriate configuration
2. Add positions systematically
3. Apply appropriate smoothing
4. Generate visualizations
5. Calculate statistics

### Performance Considerations
1. Choose appropriate implementation
2. Batch process when possible
3. Optimize grid size
4. Consider memory constraints

## Technical Notes

### Grid Resolution
- Balance between detail and performance
- Adjust based on data density
- Consider visualization needs

### Smoothing Parameters
- Affects visual appearance
- Impacts data interpretation
- Configurable via settings

### Coordinate System
- Origin at field corner
- Length along x-axis
- Width along y-axis
- Units in meters