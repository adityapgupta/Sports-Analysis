# Defensive Line Analyzer Documentation

## Overview
The `DefensiveLineAnalyzer` class analyzes the characteristics and behavior of the defensive line in soccer, including line height, angle, and coordination.

## Class: DefensiveLineAnalyzer

### Purpose
Analyzes defensive line formations, measuring key metrics such as line height, straightness, spacing, and coordination between defenders.

### Dependencies
```python
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
from scipy import stats
import yaml
```

### Data Structures

#### DefensiveLine
```python
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
```

### Configuration
- Loads from YAML configuration file (`../../config/config.yaml`)
- Key parameters:
  - Field dimensions
  - Analysis thresholds

### Main Methods

#### `analyze_defensive_line(self, timestamp: datetime, positions: List[Tuple[float, float]]) -> Dict`
Analyzes defensive line characteristics for a given frame.
- **Parameters:**
  - `timestamp`: Current time
  - `positions`: List of defender positions
- **Returns:** Dictionary containing defensive line metrics
  - Line height
  - Line angle
  - Straightness
  - Spacing
  - Coordination
  - Offside line position

#### `get_defensive_trends(self, time_window: float = None) -> Dict`
Analyzes trends in defensive line behavior.
- **Parameters:**
  - `time_window`: Optional time window for analysis
- **Returns:** Dictionary containing trends in:
  - Height
  - Angle
  - Straightness
  - Spacing
  - Coordination

### Statistical Methods

#### `fit_defensive_line(self, positions: List[Tuple[float, float]]) -> Tuple[float, float, float]`
Fits a line to defensive positions using linear regression.
- Returns slope, intercept, and R² value

#### `calculate_line_spacing(self, positions: List[Tuple[float, float]]) -> float`
Calculates average spacing between defenders.

#### `calculate_coordination(self, current_positions, previous_positions, time_diff) -> float`
Calculates coordination based on movement consistency.

### Visualization Methods

#### `visualize_defensive_line(self, line_index: int = -1)`
Visualizes defensive line for a specific moment including:
- Defender positions
- Fitted line
- Offside line
- Key metrics

#### `plot_metric_evolution(self, metric: str = 'line_height')`
Plots the evolution of a defensive line metric over time.

### Usage Example
```python
# Initialize analyzer
analyzer = DefensiveLineAnalyzer()

# Example defensive line positions
positions = [
    (10.0, 30.0),  # Left back
    (25.0, 32.0),  # Left center back
    (35.0, 31.0),  # Right center back
    (50.0, 33.0)   # Right back
]

# Analyze defensive line
metrics = analyzer.analyze_defensive_line(datetime.now(), positions)

# Visualize
analyzer.visualize_defensive_line()
analyzer.plot_metric_evolution('line_height')
```

### Analysis Features
- Line height tracking
- Line angle calculation
- Straightness measurement
- Defender spacing analysis
- Movement coordination
- Offside line tracking
- Trend analysis

### Visualization Features
- Defensive line mapping
- Metric evolution plots
- Field visualization
- Real-time analysis display

### Key Metrics
1. Line Height
2. Line Angle
3. Line Straightness (R²)
4. Defender Spacing
5. Movement Coordination
6. Offside Line Position

### Notes
- Requires minimum of 3 defenders for analysis
- Uses linear regression for line fitting
- Provides trend analysis over time
- Includes coordination metrics
- Supports real-time analysis