from sports.annotators.soccer import draw_pitch, draw_pitch_voronoi_diagram
from sports.configs.soccer import SoccerPitchConfiguration
import pickle
import numpy as np
import pprint as pp
import supervision as sv

CONFIG = SoccerPitchConfiguration()


# Load the data
with open('Soccer_Analytics/core/detections.pkl', 'rb') as f:
    data = pickle.load(f)

pp.pprint(data)

# Sample 10 distinct frames using random sampling
frame_ids = np.random.choice(len(data), 10, replace=False)

for frame_id in frame_ids:
    frame_data = data[frame_id]

    home_positions = []
    away_positions = []

    for i in range(len(frame_data)):
        if frame_data[i][1] == 1:
            home_positions.append(np.array(frame_data[i][2]))
        elif frame_data[i][1] == 2:
            away_positions.append(np.array(frame_data[i][2]))
    print(home_positions)
    print(away_positions)
    home_positions = np.array(home_positions)
    away_positions = np.array(away_positions)

    # Draw the pitch
    pitch = draw_pitch_voronoi_diagram(
        config=CONFIG,
        team_1_xy=home_positions,
        team_2_xy=away_positions,
        team_1_color=sv.Color.from_hex('#00BFFF'),
        team_2_color=sv.Color.from_hex('FF1493'),
    )

    sv.plot_image(pitch)

