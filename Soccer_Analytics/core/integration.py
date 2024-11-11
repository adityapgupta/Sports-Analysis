import yaml
import os
import numpy as np
from datetime import datetime, timedelta
from ball_possession_analyzer import BallPossessionAnalyzer
from space_control_analyzer import SpaceControlAnalyzer
from passing_opportunities import PassingOpportunitiesAnalyzer
from heat_map_analyzer import HeatMapAnalyzer
import pprint as pp


def ball_possession_integrate(data, times = None):
  
    analyzer = BallPossessionAnalyzer()
    field_length = analyzer.field_length
    field_width = analyzer.field_width
    frame_rate = analyzer.frame_rate
    ball_pos = np.array([field_length/2, field_width/2])

    if times:
        num_frames = int(times*frame_rate)
        data = data[:num_frames]


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
    flow_data = analyzer.data_possession_flow()

    return stats, flow_data

def space_control_integrate(data):


    analyzer = SpaceControlAnalyzer()
    remove_indices = []
    num_frames = len(data)
    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            if data[i][j][1] == 0 or data[i][j][1] == 3:
                remove_indices.append([i, j])
    
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)

    for i, j in remove_indices:
        data[i].pop(j)
    
    control_history = []
    # now we need to find velocity of each player
    # Find unique players
    unique_players = []
    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            if data[i][j][0] not in unique_players:
                unique_players.append(data[i][j][0])

    # Now get the position of each player with respect to time
    player_positions = {}
    for player in unique_players:
        player_positions[player] = []

    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            player_id = data[i][j][0]
            player_position = data[i][j][2]
            player_positions[player_id].append(([i, player_position]))
    
    
    def frame_velocity(player_positions, frame_rate):
        player_velocity = {}
        for player in player_positions.keys():
            player_position = player_positions[player]
            player_velocity[player] = [(0, 0)]
            for i in range(1, len(player_position)):
                frame_diff = player_position[i][0] - player_position[i-1][0]
                time_diff = frame_diff/frame_rate
                position_diff = np.array(player_position[i][1]) - np.array(player_position[i-1][1])
                velocity = position_diff/time_diff
                velocity = tuple(velocity)
                player_velocity[player].append(velocity)
        return player_velocity
    
    player_velocity = frame_velocity(player_positions, analyzer.frame_rate)

    for i in range(1, num_frames):

        home_positions = []
        away_positions = []

        num_objects = len(data[i])
        for j in range(num_objects):

            player = data[i][j][0]
            lists = player_positions[player]
            length = len(lists)
            for k in range(length):
                if lists[k][0] == i:
                    position = k
                    break
            velocity = player_velocity[player][position]

            if data[i][j][1] == 1:
                home_positions.append((data[i][j][0], data[i][j][2], velocity))
            elif data[i][j][1] == 2:
                away_positions.append((data[i][j][0], data[i][j][2], velocity))

        results = analyzer.analyze_space_control(home_positions, away_positions)


        control_history.append(results)
    return control_history

def passing_oppurtunity_integrate(data, frame_id, player_id, timestamp = 10.0):

    analyzer = PassingOpportunitiesAnalyzer()
    frame = data[frame_id]
    # Find the player position
    player_position = None
    for i in range(len(frame)):
        if frame[i][0] == player_id:
            player_position = frame[i][2]
            player_team = frame[i][1]
            break
    if player_position is None:
        print("Player not found")
        return None
    
    # Find the positions of all the other players
    other_friendly_players = []
    other_opponent_players = []

    for i in range(len(frame)):
        if frame[i][0] != player_id:
            if frame[i][1] == player_team:
                other_friendly_players.append((frame[i][0], frame[i][2]))
            else:
                other_opponent_players.append((frame[i][0], frame[i][2]))
    

    opportunities = analyzer.analyze_passing_opportunities(player_id, player_position, other_friendly_players, other_opponent_players, timestamp)

    best_opportunities = analyzer.get_best_opportunity()


    return opportunities, best_opportunities

def heatmap_integrate(data):

    analyzer = HeatMapAnalyzer()

    remove_indices = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] == 3:
                remove_indices.append([i, j])
    
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)

    for i, j in remove_indices:
        data[i].pop(j)

    # make a dictionary with 3 keys, left-team, right-team, ball

    player_positions = {}

    # make the lists for the keys as 15x10 dimensions zeros

    player_positions['left-team'] = np.zeros((10, 15))
    player_positions['right-team'] = np.zeros((10, 15))
    player_positions['ball'] = np.zeros((10, 15))
    last_ball_position = [analyzer.field_length/2, analyzer.field_width/2]
    ball_position = None
    # now we need to find the positions of the players and the ball
    for i in range(len(data)):
        for j in range(len(data[i])):

            if data[i][j][1] == 0:
                ball_position = data[i][j][2]
                
            
            x_c, y_c = analyzer.position_to_grid(data[i][j][2])
            if data[i][j][1] == 1:
                player_positions['left-team'][y_c][x_c] += 1
            elif data[i][j][1] == 2:
                player_positions['right-team'][y_c][x_c] += 1
            elif data[i][j][1] == 0:
                player_positions['ball'][y_c][x_c] += 1
        if ball_position is not None:
            last_ball_position = ball_position
            ball_position = None
        else:
            x_c, y_c = analyzer.position_to_grid(last_ball_position)
            player_positions['ball'][x_c][y_c] += 1
    
    # convert the numpy arrays to list
    player_positions['left-team'] = player_positions['left-team'].tolist()
    player_positions['right-team'] = player_positions['right-team'].tolist()
    player_positions['ball'] = player_positions['ball'].tolist()
    # return this dictionary
    return player_positions

if __name__ == '__main__':
    
    import pickle
    with open('Soccer_Analytics/core/trimmed.pkl', 'rb') as f:
        _, data = pickle.load(f)
    
    
    data2 = []
    for i in range(len(data)):
        data2.append(data[i][0])
    from copy import deepcopy
    
    data = deepcopy(data2)
    for i in range(len(data)):
        for j in range(len(data[i])):
            # make data[i][j] to list
            data[i][j] = list(data[i][j])
            data[i][j][2] = (data[i][j][2][0]* 105, data[i][j][2][1]*68)
    
    
    # stats, flow_data = ball_possession_integrate(data)
    # print(space_control_integrate(data))
    # print(stats)
    # print(flow_data)

    frame_id = 100
    player_id = 8
    opportunities, best_opportunities = passing_oppurtunity_integrate(data, frame_id, player_id)


    for op in opportunities:
        print(f"Pass from {op.passer_id} to {int(op.receiver_id)}:")
        print(f"  Distance of Pass: {op.lane.distance:.2f}")
        print(f"  Defensive Pressure: {op.defensive_pressure:.2f}")
        print(f"  horizontal Progress: {op.horizontal_progress:.2f}")
        print(f"  Space Gained: {op.space_gained:.2f}")
        # print(f"  Tactical Advantage: {op.tactical_advantage:.2f}")
        print(f"  Total Score: {op.lane.total_score:.2f}")
        print()
        
    # pp.pprint(best_opportunities)

    print(f"Best pass is from {int(best_opportunities.passer_id)} to {int(best_opportunities.receiver_id)}")
    
    dataset_heat = heatmap_integrate(data)
    # print(dataset_heat)

    # combined = {}
    # combined['possession'] = stats
    # combined['time_possession'] = flow_data
    # combined['heatmap'] = dataset_heat
    
    #make it into a pickle file
    # with open('Soccer_Analytics/core/sharath.pkl', 'wb') as f:
    #     pickle.dump(combined, f)