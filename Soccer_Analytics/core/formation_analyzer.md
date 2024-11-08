# Formation Analyzer Documentation

## Overview
The `FormationAnalyzer` class provides advanced analysis of soccer team formations using player position data. It can detect and analyze team formations in real-time, track formation changes, and calculate various metrics related to team shape and structure.

## Key Classes

### FormationZone
Represents a specific zone in the team's formation.

**Attributes:**
- `center`: Tuple[float, float] - The central coordinates of the zone
- `players`: List[int] - List of player IDs in this zone
- `role`: str - Tactical role ('GK', 'DEF', 'MID', 'FWD')
- `average_width`: float - Average horizontal spread of players in the zone
- `average_depth`: float - Average vertical spread of players in the zone

### Formation
Represents the complete team formation at a given moment.

**Attributes:**
- `timestamp`: float - When the formation was detected
- `formation_string`: str - Formation notation (e.g., "4-3-3")
- `zones`: List[FormationZone] - List of formation zones
- `compactness`: float - How compact the team shape is
- `width`: float - Team's horizontal spread
- `depth`: float - Team's vertical spread
- `balance_score`: float - How well-balanced the formation is

## Main Features

### Formation Detection
- Automatically detects team formations from player positions
- Supports common formations (4-4-2, 4-3-3, 3-5-2, etc.)
- Handles dynamic formation changes
- Accounts for player movements and positional fluidity

### Metrics Calculation
- Team compactness
- Formation width and depth
- Tactical balance
- Formation stability over time
- Dynamic role assignment

### Analysis Methods
1. `analyze_frame(home_positions, away_positions, timestamp)`:
   - Analyzes formations for both teams in a single frame
   - Returns Formation objects for each team

2. `get_formation_stability(team)`:
   - Calculates formation stability metrics
   - Tracks formation changes over time

3. `get_formation_summary()`:
   - Provides comprehensive formation analysis
   - Includes statistical summaries and key metrics

## Configuration

The analyzer requires a YAML configuration file with the following key sections:
```yaml
field:
  length: float
  width: float

thresholds:
  formation:
    window_size: int
    cluster_tolerance: float
```

## Usage Example

```python
analyzer = FormationAnalyzer(config_path='config/config.yaml')

# Analyze a frame
formations = analyzer.analyze_frame(
    home_positions=[(1, (10, 20)), (2, (15, 25))],
    away_positions=[(1, (60, 20)), (2, (65, 25))],
    timestamp=1234567890
)

# Get formation summary
summary = analyzer.get_formation_summary()

# Check formation stability
stability = analyzer.get_formation_stability('home')
```

## Technical Details

### Position Clustering
- Uses K-means clustering to group players into tactical units
- Employs sliding window approach for temporal smoothing
- Handles missing player data gracefully

### Formation Detection Algorithm
1. Clusters player positions vertically
2. Identifies tactical lines (defense, midfield, attack)
3. Assigns roles based on spatial relationships
4. Matches against known formation templates
5. Calculates formation metrics

### Performance Considerations
- Optimized for real-time analysis
- Efficient clustering algorithms
- Configurable parameters for performance tuning

## Best Practices

1. **Configuration Tuning**
   - Adjust cluster_tolerance based on tracking data precision
   - Set appropriate window_size for formation stability

2. **Data Quality**
   - Ensure consistent player tracking data
   - Handle missing players appropriately
   - Pre-process position data if needed

3. **Analysis Workflow**
   - Initialize analyzer with proper configuration
   - Process frames sequentially
   - Monitor formation stability over time
   - Use summary statistics for overall analysis