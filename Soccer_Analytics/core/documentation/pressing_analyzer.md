# Pressing Analyzer Documentation

## Overview
The `PressingAnalyzer` class provides sophisticated analysis of team pressing behaviors in soccer matches. It tracks and analyzes how teams apply pressure to opponents with the ball, measuring aspects like pressing intensity, distances, and closing speeds.

## Key Classes

### PressingEvent
Represents a single instance of pressing behavior.

**Attributes:**
- `timestamp`: datetime - When the pressing event occurred
- `ball_position`: Tuple[float, float] - Ball location
- `pressing_players`: List[Tuple[float, float]] - Positions of pressing players
- `distances`: List[float] - Distances to ball
- `closing_speeds`: List[float] - Speeds of approaching players
- `reaction_time`: float - Time taken to initiate press

## Features

### Core Analysis
1. **Distance Analysis**
   - Calculates distances between defenders and ball
   - Tracks nearest defenders
   - Measures pressing coverage

2. **Speed Analysis**
   - Calculates closing velocities
   - Measures pressing intensity
   - Tracks acceleration patterns

3. **Intensity Metrics**
   - Composite pressing score
   - Pressure effectiveness
   - Team coordination

### Statistical Analysis
1. **Real-time Metrics**
   - Average distance to ball
   - Minimum pressing distance
   - Maximum closing speed
   - Pressing intensity score

2. **Historical Analysis**
   - Pressing patterns over time
   - Team pressing strategies
   - Effectiveness trends

## Main Methods

### Primary Functions

1. `analyze_frame()`
   ```python
   def analyze_frame(
       self,
       timestamp: datetime,
       ball_position: Tuple[float, float],
       defending_positions: List[Tuple[float, float]]
   ) -> Dict
   ```
   - Analyzes pressing in current frame
   - Returns comprehensive metrics

2. `get_pressing_statistics()`
   ```python
   def get_pressing_statistics(
       self,
       time_window: float = None
   ) -> Dict
   ```
   - Calculates statistical summaries
   - Optional time window analysis

3. `visualize_pressing()`
   ```python
   def visualize_pressing(
       self,
       event_index: int = -1
   )
   ```
   - Creates visual representation
   - Shows pressing patterns

## Configuration

### Required Settings
```yaml
field:
  length: float
  width: float

thresholds:
  pressing:
    max_distance: float
    reaction_time: float
    intensity_threshold: float
```

## Technical Implementation

### Pressing Detection
1. Distance Calculation
   - Uses scipy's cdist for efficient calculation
   - Tracks multiple defenders
   - Prioritizes closest players

2. Speed Calculation
   - Frame-to-frame velocity
   - Smoothed measurements
   - Vector-based calculations

3. Intensity Scoring
   - Weighted combination
   - Distance normalization
   - Speed integration

### Visualization Features
1. Field Representation
   - Full pitch drawing
   - Player positions
   - Pressure lines

2. Metric Display
   - Real-time stats
   - Historical trends
   - Event markers

## Performance Optimization

### Standard Version
- Simple position tracking
- Basic statistical analysis
- Straightforward visualization

### NumPy-Optimized Version
- Vectorized calculations
- Efficient matrix operations
- Optimized data structures

## Best Practices

### Data Quality
1. **Position Data**
   - Regular sampling rate
   - High accuracy tracking
   - Minimal noise

2. **Configuration**
   - Appropriate thresholds
   - Context-based settings
   - Team-specific adjustments

### Analysis Workflow
1. Initialize analyzer
2. Process frames sequentially
3. Calculate statistics
4. Generate visualizations

## Usage Examples

### Basic Usage
```python
# Initialize analyzer
analyzer = PressingAnalyzer(config_path='config/config.yaml')

# Analyze frame
metrics = analyzer.analyze_frame(
    timestamp=datetime.now(),
    ball_position=(60.0, 40.0),
    defending_positions=[(55.0, 35.0), (58.0, 38.0)]
)

# Print metrics
print(f"Average Distance: {metrics['average_distance']:.1f}m")
print(f"Pressing Intensity: {metrics['pressing_intensity']:.1f}/100")
```

### Advanced Analysis
```python
# Get stats over last 5 minutes
stats = analyzer.get_pressing_statistics(time_window=300)

# Visualize latest pressing event
analyzer.visualize_pressing()
```

## Integration Points

### Compatible Systems
1. Player tracking
2. Match analysis
3. Tactical analysis
4. Performance metrics

### Data Requirements
1. Ball tracking
2. Player positions
3. Temporal synchronization
4. Team identification

## Future Enhancements

### Potential Improvements
1. Machine learning integration
2. Advanced pattern recognition
3. Tactical context analysis
4. Multi-team coordination

### Development Areas
1. Real-time analysis
2. Additional metrics
3. Automated insights
4. Tactical recommendations