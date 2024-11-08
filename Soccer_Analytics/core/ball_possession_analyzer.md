# Ball Possession Analyzer Documentation

## Overview
The `BallPossessionAnalyzer` class analyzes ball possession during a soccer match, tracking possession events, durations, and zones.

## Class: BallPossessionAnalyzer

### Purpose
Analyzes and tracks ball possession statistics, including team possession percentages, zone analysis, and possession events.

### Dependencies
```python
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import yaml
```

### Configuration
- Loads from YAML configuration file (`../../config/config.yaml`)
- Key parameters:
  - Field dimensions
  - Control radius
  - Minimum possession duration

### Data Structures

#### PossessionEvent
```python
@dataclass
class PossessionEvent:
    timestamp: datetime
    ball_position: Tuple[float, float]
    possessing_team: str  # 'home' or 'away'
    player_id: int
    zone: str  # 'defensive', 'middle', 'attacking'
    duration: float
    distance_covered: float
```

### Main Methods

#### `analyze_possession(self, timestamp, ball_position, home_positions, away_positions) -> Dict`
Analyzes ball possession for the current frame.
- **Parameters:**
  - `timestamp`: Current time
  - `ball_position`: Ball's position
  - `home_positions`: Home team player positions
  - `away_positions`: Away team player positions
- **Returns:** Dictionary with possession metrics

#### `get_possession_stats(self, time_window: float = None) -> Dict`
Calculates comprehensive possession statistics.
- **Parameters:**
  - `time_window`: Optional time window for analysis
- **Returns:** Dictionary containing:
  - Team possession percentages
  - Zone possession statistics
  - Player possession times

### Visualization Methods

#### `visualize_possession(self, time_window: float = None)`
Creates visualization of possession statistics including:
- Team possession pie chart
- Zone possession bar chart
- Possession map on field

#### `plot_possession_flow(self, last_n_events: int = 20)`
Plots possession flow over time showing possession changes between teams.

### Helper Methods

#### `determine_zone(self, position: Tuple[float, float], team: str) -> str`
Determines which zone the ball is in based on position.

#### `find_possessing_player(self, ball_position, home_positions, away_positions) -> Tuple[str, int]`
Determines which player has possession of the ball.

### Usage Example
```python
# Initialize analyzer
analyzer = BallPossessionAnalyzer()

# Analyze possession for a frame
metrics = analyzer.analyze_possession(
    timestamp=current_time,
    ball_position=(50.0, 40.0),
    home_positions=[(1, (48.0, 38.0)), (2, (52.0, 42.0))],
    away_positions=[(1, (53.0, 41.0)), (2, (47.0, 39.0))]
)

# Get possession statistics
stats = analyzer.get_possession_stats()

# Visualize
analyzer.visualize_possession()
analyzer.plot_possession_flow()
```

### Possession Analysis Features
- Team possession tracking
- Zone-based analysis
- Player-specific possession times
- Possession event tracking
- Distance covered during possession
- Possession duration analysis

### Visualization Features
- Team possession distribution
- Zone-based possession breakdown
- Spatial possession mapping
- Temporal possession flow

### Notes
- Requires proper configuration file setup
- Uses scipy for distance calculations
- Implements comprehensive possession event tracking
- Provides multiple visualization options