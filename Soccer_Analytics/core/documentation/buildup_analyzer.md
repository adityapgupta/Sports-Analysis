# Buildup Play Analyzer Documentation

## Overview
The `BuildupAnalyzer` class analyzes team buildup play phases, tracking progression from defensive third to attacking positions.

## Class: BuildupAnalyzer

### Purpose
Analyzes and tracks buildup play phases, measuring progression, success rates, and involved players.

### Dependencies
```python
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.distance import cdist
```

### Data Structures

#### BuildupPhase
```python
@dataclass
class BuildupPhase:
    start_time: datetime
    end_time: Optional[datetime]
    start_position: Tuple[float, float]
    current_position: Tuple[float, float]
    involved_players: List[int]
    progression_speed: float = 0.0
    vertical_progress: float = 0.0
    num_passes: int = 0
    success: bool = False
    duration: float = 0.0
    reached_final_third: bool = False
    transition_type: str = "organized"  # 'organized' or 'counter'
```

### Configuration
- Loads from YAML configuration file (`../../config/config.yaml`)
- Key parameters:
  - Minimum buildup duration
  - Counter-attack threshold
  - Field dimensions
  - Final third line position

### Main Methods

#### `analyze_buildup(self, timestamp, ball_position, possessing_team, possessing_player, player_positions, last_timestamp) -> Dict`
Analyzes buildup play for the current frame.
- **Parameters:**
  - `timestamp`: Current time
  - `ball_position`: Ball's position
  - `possessing_team`: Team in possession
  - `possessing_player`: Player in possession
  - `player_positions`: All player positions
  - `last_timestamp`: Previous timestamp
- **Returns:** Dictionary with buildup metrics

#### `get_buildup_stats(self, time_window: float = None) -> Dict`
Calculates comprehensive buildup statistics.
- **Parameters:**
  - `time_window`: Optional time window for analysis
- **Returns:** Dictionary containing:
  - Success rates
  - Average duration
  - Player involvement
  - Progression metrics

### Visualization Methods

#### `visualize_buildup_patterns(self)`
Visualizes buildup patterns on the field showing:
- Successful and unsuccessful buildups
- Field thirds
- Progression paths

#### `plot_buildup_success_timeline(self)`
Plots buildup success rate over time.

#### `plot_progression_heatmap(self)`
Creates heatmap of successful buildup progression.

### Helper Methods

#### `start_buildup(self, timestamp, position, player_id)`
Starts tracking a new buildup phase.

#### `end_buildup(self, timestamp, reached_final_third)`
Ends current buildup phase with success/failure status.

### Usage Example
```python
# Initialize analyzer
analyzer = BuildupAnalyzer()

# Analyze buildup for a frame
result = analyzer.analyze_buildup(
    timestamp=current_time,
    ball_position=(50.0, 20.0),
    possessing_team='home',
    possessing_player=1,
    player_positions={1: (50.0, 20.0), 2: (40.0, 25.0)}
)

# Get buildup statistics
stats = analyzer.get_buildup_stats()

# Visualize patterns
analyzer.visualize_buildup_patterns()
analyzer.plot_buildup_success_timeline()
```

### Analysis Features
- Buildup phase detection
- Success rate tracking
- Progression speed analysis
- Player involvement tracking
- Transition type classification
- Vertical progression measurement

### Visualization Features
- Buildup pattern mapping
- Success rate timeline
- Progression heatmaps
- Field zone visualization

### Key Metrics
1. Buildup Success Rate
2. Average Duration
3. Progression Speed
4. Player Involvement
5. Vertical Progress
6. Transition Type Distribution

### Notes
- Requires proper configuration file setup
- Tracks both organized and counter-attack buildups
- Provides comprehensive statistical analysis
- Includes multiple visualization options
- Focuses on progression from defensive third