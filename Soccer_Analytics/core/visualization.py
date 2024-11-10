# imports
import numpy as np
from datetime import datetime, timedelta


# class imports
from ball_possession_analyzer import BallPossessionAnalyzer
from distance_analyzer import DistanceAnalyzer


# Visualization functions
def ball_possesion_visualization(data, times = None, last_n_events = 20, save_path = None, show = True):
  
    analyzer = BallPossessionAnalyzer()
    field_length = analyzer.field_length
    field_width = analyzer.field_width
    frame_rate = analyzer.frame_rate
    ball_pos = np.array([field_length/2, field_width/2])

    if type(times) == int:
        num_frames = times*frame_rate
        data = data[:num_frames]

    if type(times) == list:
        start_frame = int(times[0]*frame_rate)
        end_frame = int(times[1]*frame_rate)

        data = data[start_frame:end_frame]


    for j, frame in enumerate(data):

        home_positions = []
        away_positions = []

        num_objects = len(frame)

        for i in range(num_objects):

            if frame[i][1] ==0:
                ball_pos = frame[i][2]
            elif frame[i][1] ==1:
                home_positions.append((frame[i][0], frame[i][2]))
            elif frame[i][1] ==2:
                away_positions.append((frame[i][0], frame[i][2]))

        timestamp = datetime.fromtimestamp(j/frame_rate)

        analyzer.analyze_possession(timestamp, ball_pos, home_positions, away_positions)
    
    
    stats = analyzer.get_possession_stats()
    
    analyzer.visualize_possession(save_path = save_path, show = show)
    analyzer.plot_possession_flow(last_n_events = last_n_events,save_path = save_path)

    return stats

def speed_visualization(data, player_id, times = None, save_path = None, show = True):
    
    analyzer = DistanceAnalyzer()
    frame_rate = analyzer.frame_rate

    start_time = times[0] if type(times) == list else 0
    start_frame = int(start_time*frame_rate)

    if type(times) == int:
        num_frames = times*frame_rate
        data = data[:num_frames]

    if type(times) == list:
        start_frame = int(times[0]*frame_rate)
        end_frame = int(times[1]*frame_rate)

        data = data[start_frame:end_frame]

    # find frame id where player_id is present
    player_data = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][0] == player_id:
                player_data.append((datetime.fromtimestamp((i + start_frame)/ frame_rate), data[i][j][2]))
                
    
    for i in range(1, len(player_data)):
        analyzer.process_position(
            player_data[i][0],
            player_data[i][1],
            player_data[i-1][0],
            player_data[i-1][1]
        )
        print(player_data[i-1][1])
    print(len(player_data))

    stats = analyzer.get_distance_stats()
    analyzer.visualize_distance_breakdown(save_path = save_path, show = show)
    analyzer.plot_velocity_profile(save_path = save_path, show = show, smoothing_window = 10)

def voronoi_visualization(data, frame_id, save_path = None, show = True):
    pass











if __name__ == "__main__":
    
    import pickle
    with open('Soccer_Analytics/core/detections.pkl', 'rb') as f:
        data = pickle.load(f)

    player_id = 14

    speed_visualization(data, player_id, times = None, save_path = None, show = True)