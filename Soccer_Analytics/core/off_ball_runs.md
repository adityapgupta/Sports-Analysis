# Off-Ball Runs Analyzer Documentation

## Overview
The `OffBallRunsAnalyzer` class provides sophisticated analysis of player movements without the ball in soccer matches. It detects, tracks, and analyzes off-ball runs, providing insights into player movement patterns and tactical implications.

## Key Classes

### OffBallRun
Represents a single off-ball running movement.

**Attributes:**
- `player_id`: int - Player making the run
- `start_time`: float - Run start timestamp
- `end_time`: Optional[float] - Run end timestamp
- `start_position`: Tuple[float, float] - Starting coordinates
- `current_position`: Tuple[float, float] - Current coordinates
- `velocity`: Tuple[float, float] - Current velocity vector
- `run_distance`: float - Total distance covered
- `space_gained`: float - Effective space gained
- `threat_score`: float - Calculated threat level
- `run_type`: str - Classification of run type
- `is_active`: bool - Whether run is ongoing
- `creating_space_for`: Optional[int] - Beneficiary player ID
- `defensive_disruption`: float - Impact on defense

## Features

### Run Detection and Analysis

#### Detection Criteria
- Minimum velocity threshold
- Sustained movement duration
- Directional consistency
- Spatial relevance

#### Run Classifications
1. **Penetrating Runs**
   - Vertical movement behind defense
   - High threat potential
   - Goal-oriented direction

2. **Supporting Runs**
   - Movement to provide passing options
   - Creates space for teammates
   - Tactical repositioning

3. **Diversionary Runs**
   - Designed to draw defenders
   - Creates space for others
   - Tactical deception

### Metrics Calculation

#### Individual Run Metrics
- Run distance
- Space gained
- Threat score
- Defensive disruption
- Tactical advantage

#### Team-Level Metrics
- Run frequency
- Spatial distribution
- Tactical patterns
- Movement efficiency

## Main Methods

### Analysis Methods
1. `analyze_frame()`
   ```python
   def analyze_frame(
       self,
       timestamp: float,
       player_positions: List[Tuple[int, Tuple[float, float]]],
       ball_position: Tuple[float, float],
       ball_carrier_id: Optional[int],
       defender_positions: List[Tuple[float, float]]
   ) -> List[OffBallRun]
   ```
   - Analyzes a single frame of match data
   - Detects and updates runs
   - Returns active runs

2. `get_run_statistics()`
   ```python
   def get_run_statistics(self) -> Dict
   ```
   - Returns comprehensive run statistics
   - Includes averages and distributions
   - Provides tactical insights

3. `get_high_threat_runs()`
   ```python
   def get_high_threat_runs(threshold: float = 0.7) -> List[OffBallRun]
   ```
   - Returns runs above threat threshold
   - Filtered by significance
   - Sorted by threat level

## Configuration

### Required Settings
```yaml
field:
  length: float
  width: float

thresholds:
  min_run_velocity: float
  min_run_duration: float
  space_creation_radius: float
  min_distance_traveled: float
  max_run_duration: float
```

## Technical Details

### Run Detection Algorithm
1. Track player velocities
2. Apply smoothing window
3. Check threshold criteria
4. Classify run type
5. Calculate metrics
6. Update run status

### Metric Calculations

#### Space Gained
- Relative to defender positions
- Weighted by proximity
- Directional component

#### Threat Score
- Distance to goal
- Defensive pressure
- Run direction
- Spatial advantage

#### Defensive Disruption
- Defender displacement
- Coverage impact
- Structural effects

## Best Practices

### Data Quality
1. **Position Data**
   - Consistent sampling rate
   - Accurate coordinates
   - Complete tracking data

2. **Configuration**
   - Appropriate thresholds
   - Contextual parameters
   - Performance tuning

### Analysis Workflow
1. Initialize analyzer
2. Process frames sequentially
3. Monitor run developments
4. Calculate statistics
5. Identify patterns

## Usage Examples

### Basic Usage
```python
# Initialize analyzer
analyzer = OffBallRunsAnalyzer(config_path='config/config.yaml')

# Analyze frame
runs = analyzer.analyze_frame(
    timestamp=1234567890,
    player_positions=[(1, (10, 20)), (2, (15, 25))],
    ball_position=(12, 22),
    ball_carrier_id=1,
    defender_positions=[(50, 30), (55, 35)]
)

# Get statistics
stats = analyzer.get_run_statistics()
```

### Advanced Analysis
```python
# Get high-threat runs
threat_runs = analyzer.get_high_threat_runs(threshold=0.8)

# Clear history for new analysis
analyzer.clear_history()
```

## Performance Considerations

### Optimization Techniques
- Vectorized calculations
- Efficient data structures
- Memory management
- Computation caching

### Memory Management
- History window limits
- Data cleanup
- Resource efficiency
- Periodic resets

## Future Enhancements

### Potential Improvements
1. Machine learning classification
2. Advanced pattern recognition
3. Team-level analysis
4. Interactive visualization
5. Real-time processing

### Integration Points
1. Team tactics analysis
2. Player performance metrics
3. Match analysis systems
4. Training applications