# Soccer Analytics Integrator Documentation

## Overview
The `SoccerAnalyticsIntegrator` class serves as the main orchestrator for soccer analytics, integrating various specialized analyzers to provide comprehensive game analysis.

## Class: SoccerAnalyticsIntegrator

### Purpose
Coordinates multiple specialized analyzers to process player tracking data and generate comprehensive game analytics.

### Dependencies
```python
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import yaml
from datetime import datetime
import logging
```

### Configuration
- Loads from a YAML configuration file (`../../config/config.yaml`)
- Initializes multiple specialized analyzers for different aspects of the game

### Key Components

#### Integrated Analyzers
- Heat Map Analysis
- Formation Analysis
- Pressing Analysis
- Distance Analysis
- Sprint Analysis
- Team Shape Analysis
- Ball Possession Analysis
- Buildup Play Analysis
- Space Control Analysis
- Passing Opportunities Analysis
- Off-ball Runs Analysis

### Main Methods

#### `__init__(self, config_path: str = '../../config/config.yaml')`
Initializes the integrator with all required analyzers and caching mechanisms.

#### `analyze_frame(self, frame_id: int, timestamp: float) -> Dict[str, Any]`
Analyzes a single frame of the game, coordinating all specialized analyzers.
- **Parameters:**
  - `frame_id`: Unique identifier for the frame
  - `timestamp`: Time of the frame
- **Returns:** Dictionary containing analysis results from all analyzers

#### `analyze_sequence(self, start_frame: int, end_frame: int) -> List[Dict[str, Any]]`
Analyzes a sequence of frames.
- **Parameters:**
  - `start_frame`: First frame to analyze
  - `end_frame`: Last frame to analyze
- **Returns:** List of frame analysis results

#### `get_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]`
Generates summary statistics from a sequence of frame analyses.

### Cache Management

#### `_cleanup_cache(self)`
Removes old frames from cache to manage memory usage.

#### `_get_player_state(self, frame_id: int, player_id: int, use_cache: bool = True)`
Retrieves player state with caching mechanism.

### Usage Example
```python
# Initialize integrator
integrator = SoccerAnalyticsIntegrator()

# Analyze a single frame
frame_results = integrator.analyze_frame(frame_id=1000, timestamp=1234.5)

# Analyze a sequence
sequence_results = integrator.analyze_sequence(start_frame=1000, end_frame=1100)

# Get summary
summary = integrator.get_analysis_summary(sequence_results)
```

### Error Handling
- Uses logging for error tracking
- Includes comprehensive error handling for missing data and configuration issues

### Performance Considerations
- Implements caching for player positions
- Configurable cache size and cleanup intervals
- Efficient data structures for analysis results

### Notes
- The integrator assumes a specific project structure with configuration files
- Requires proper initialization of all analyzer components
- Cache management is crucial for long-running analyses