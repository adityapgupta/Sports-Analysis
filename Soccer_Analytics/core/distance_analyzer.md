# Distance Analyzer Documentation

## Overview
The `DistanceAnalyzer` class analyzes player movement patterns, distances covered, and movement intensities during a soccer match.

## Class: DistanceAnalyzer

### Purpose
Tracks and analyzes player movements, categorizing them by intensity and calculating comprehensive distance statistics.

### Dependencies
```python
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.distance import euclidean
```

### Data Structures

#### MovementSegment
```python
@dataclass
class MovementSegment:
    start_time: datetime
    end_time: datetime
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    distance: float
    velocity: float
    category: str  # 'sprint', 'high_intensity', 'jogging', 'walking'
```

### Configuration
- Loads from YAML configuration file (`../../config/config.yaml`)
- Key thresholds:
  - Sprint threshold
  - High-intensity threshold
  - Jogging threshold

### Main Methods

#### `process_position(self, timestamp, position, last_timestamp, last_position) -> Dict`
Processes a new position reading and categorizes movement.
- **Parameters:**
  - `timestamp`: Current time
  - `position`: Current position
  - `last_timestamp`: Previous timestamp
  - `last_position`: Previous position
- **Returns:** Dictionary containing:
  - Distance covered
  - Velocity
  - Movement category

#### `get_distance_stats(self, time_window: float = None) -> Dict`
Calculates comprehensive distance statistics.
- **Parameters:**
  - `time_window`: Optional time window for analysis
- **Returns:** Dictionary containing:
  - Total distance
  - Distances by category
  - Percentages by category
  - Average velocity
  - Distance per minute

### Movement Categorization

#### `categorize_movement(self, velocity: float) -> str`
Categorizes movement based on velocity thresholds:
- Sprint
- High-intensity
- Jogging
- Walking

### Visualization Methods

#### `visualize_distance_breakdown(self)`
Creates visualization of distance statistics:
- Pie chart of distance breakdown
- Bar chart of average velocities by category

#### `plot_velocity_profile(self, smoothing_window: int = 10)`
Plots velocity profile over time with threshold indicators.

### Usage Example
```python
# Initialize analyzer
analyzer = DistanceAnalyzer()

# Process positions
analyzer.process_position(
    timestamp=current_time,
    position=(10.0, 8.0),
    last_timestamp=previous_time,
    last_position=(5.0, 5.0)
)

# Get statistics
stats = analyzer.get_distance_stats()

# Visualize
analyzer.visualize_distance_breakdown()
analyzer.plot_velocity_profile()
```

### Analysis Features
- Distance tracking
- Velocity calculation
- Movement categorization
- Time-windowed analysis
- Category-based statistics
- Performance metrics

### Visualization Features
- Distance breakdown charts
- Category distribution
- Velocity profiling
- Threshold visualization

### Key Metrics
1. Total Distance
2. Category-wise Distances
   - Sprint distance
   - High-intensity distance
   - Jogging distance
   - Walking distance
3. Average Velocity
4. Distance per Minute
5. Category Percentages

### Statistics Calculated
- Total distances
- Category breakdown
- Movement percentages
- Velocity statistics
- Time-based metrics

### Notes
- Supports real-time analysis
- Includes smoothing for velocity profiles
- Provides category-based breakdowns
- Uses euclidean distance calculations
- Supports time-windowed analysis

### Performance Considerations
- Efficient distance calculations
- Optimized data structures
- Configurable smoothing windows
- Category threshold customization