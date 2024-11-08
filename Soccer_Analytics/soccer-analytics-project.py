soccer_analytics/
├── __init__.py
├── requirements.txt
├── config/
│   └── config.yaml
├── data/
│   └── __init__.py
├── core/
│   ├── __init__.py
│   ├── heat_map_analyzer.py
│   ├── formation_analyzer.py
│   ├── pressing_analyzer.py
│   ├── distance_analyzer.py
│   ├── sprint_analyzer.py
│   ├── team_shape_analyzer.py
│   ├── defensive_line_analyzer.py
│   ├── ball_possession_analyzer.py
│   ├── buildup_analyzer.py
│   ├── space_control_analyzer.py
│   ├── passing_opportunity_analyzer.py
│   └── off_ball_runs_analyzer.py
├── utils/
│   ├── __init__.py
│   ├── visualization.py
│   ├── calculations.py
│   └── data_processing.py
└── tests/
    ├── __init__.py
    └── test_analyzers/
        ├── __init__.py
        ├── test_heat_map.py
        ├── test_formation.py
        └── ...