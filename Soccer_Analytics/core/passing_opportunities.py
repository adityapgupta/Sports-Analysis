import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import yaml
from scipy.spatial.distance import cdist
import sys 
# if '/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils' not in sys.path:
#     sys.path.append('/home/shishirr/Desktop/Applied_Data_Science_and_Artificial_Intelligence/Project/Sports-Analysis/Soccer_Analytics/utils') 
import os

@dataclass
class PassingLane:
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    distance: float
    interceptors: List[Tuple[int, float]]  # (player_id, distance to passing lane)
    success_probability: float
    risk_score: float
    reward_score: float
    total_score: float

@dataclass
class PassingOpportunity:
    passer_id: int
    receiver_id: int
    lane: PassingLane
    defensive_pressure: float
    horizontal_progress: float
    space_gained: float
    # tactical_advantage: float
    timestamp: float

class PassingOpportunitiesAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """Initialize Passing Opportunities Analyzer"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Load field dimensions
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        
        # Load passing specific settings
        pass_config = config['thresholds']['passing_opportunities']
        self.min_pass_distance = pass_config['min_pass_distance']
        self.max_pass_distance = pass_config['max_pass_distance']
        self.passing_lane_width = pass_config['passing_lane_width']
        self.risk_zone_radius = pass_config['risk_zone_radius']
        self.success_probability_threshold = pass_config['success_probability_threshold']
        self.max_interceptor_distance = pass_config['max_interceptor_distance']
        self.defensive_pressure_radius = pass_config['defensive_pressure_radius']
        self.horizontal_progress_bonus = pass_config['horizontal_progress_bonus']
        
        # Load weight configurations
        self.risk_weights = pass_config['risk_weights']
        self.reward_weights = pass_config['reward_weights']
        
        self.current_opportunities: List[PassingOpportunity] = []

    def point_to_line_distance(self, point: Tuple[float, float], 
                             line_start: Tuple[float, float], 
                             line_end: Tuple[float, float]) -> float:
        """Calculate perpendicular distance from point to line segment"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
        denominator = np.sqrt((y2-y1)**2 + (x2-x1)**2)
        
        # Check if point projection falls outside line segment
        if denominator == 0:
            return np.sqrt((x0-x1)**2 + (y0-y1)**2)
            
        t = max(0, min(1, ((x0-x1)*(x2-x1) + (y0-y1)*(y2-y1)) / (denominator**2)))
        
        projection_x = x1 + t*(x2-x1)
        projection_y = y1 + t*(y2-y1)
        
        return np.sqrt((x0-projection_x)**2 + (y0-projection_y)**2)

    def find_interceptors(self, passing_lane: Tuple[Tuple[float, float], Tuple[float, float]], 
                         defender_positions: List[Tuple[int, Tuple[float, float]]]) -> List[Tuple[int, float]]:
        """Find defenders who could potentially intercept the pass"""
        interceptors = []
        start_pos, end_pos = passing_lane
        
        for defender_id, pos in defender_positions:
            distance = self.point_to_line_distance(pos, start_pos, end_pos)
            if distance <= self.max_interceptor_distance * cdist([start_pos], [end_pos])[0][0]:
                interceptors.append((defender_id, distance))
                
        return sorted(interceptors, key=lambda x: x[1])

    def calculate_defensive_pressure(self, position: Tuple[float, float], 
                                  defender_positions: List[Tuple[float, float]]) -> float:
        """Calculate defensive pressure at a given position"""
        if not defender_positions:
            return 0.0
            
        distances = cdist([position], defender_positions)[0]
        pressures = np.exp(-distances / self.defensive_pressure_radius)
        return np.sum(pressures)

    def calculate_pass_success_probability(self, passing_lane: PassingLane, 
                                        defensive_pressure: float) -> float:
        """Calculate probability of pass success based on various factors"""
        # Base probability decreases with distance
        base_prob = np.exp(-passing_lane.distance / self.max_pass_distance)
        distance = passing_lane.distance    
        # Adjust for interceptors
        interceptor_risk = sum(1.0 / (1.0 + 2*dist/distance) for _, dist in passing_lane.interceptors)
        interceptor_factor = np.exp(-interceptor_risk)
        
        # Adjust for defensive pressure
        pressure_factor = np.exp(-defensive_pressure / 2.0)
        
        return base_prob * interceptor_factor * pressure_factor

    def calculate_tactical_advantage(self, receiver_pos: Tuple[float, float],
                                  team_positions: List[Tuple[float, float]],
                                  opponent_positions: List[Tuple[float, float]]) -> float:
        """Calculate tactical advantage gained from potential pass"""
        # Calculate space control before and after pass
        current_control = self.calculate_space_control(team_positions, opponent_positions)
        new_positions = team_positions[:]
        new_positions.append(receiver_pos)
        new_control = self.calculate_space_control(new_positions, opponent_positions)
        
        return new_control - current_control

    def calculate_space_control(self, team_positions: List[Tuple[float, float]], 
                              opponent_positions: List[Tuple[float, float]]) -> float:
        """Calculate team's control of space using a simple model"""
        grid_points = self.generate_control_grid(5.0)  # 5m grid resolution
        team_control = 0
        
        for point in grid_points:
            team_distances = cdist([point], team_positions)
            opp_distances = cdist([point], opponent_positions)
            
            if np.min(team_distances) < np.min(opp_distances):
                team_control += 1
                
        return team_control / len(grid_points)

    def generate_control_grid(self, resolution: float) -> List[Tuple[float, float]]:
        """Generate grid points for space control calculation"""
        x_points = np.arange(0, self.field_length, resolution)
        y_points = np.arange(0, self.field_width, resolution)
        return [(x, y) for x in x_points for y in y_points]

    def analyze_passing_opportunities(self, 
                                   passer_id: int,
                                   passer_pos: Tuple[float, float],
                                   teammate_positions: List[Tuple[int, Tuple[float, float]]],
                                   opponent_positions: List[Tuple[int, Tuple[float, float]]],
                                   timestamp: float) -> List[PassingOpportunity]:
        """Analyze all possible passing opportunities for the ball carrier"""
        opportunities = []
        
        for receiver_id, receiver_pos in teammate_positions:
            if receiver_id == passer_id:
                continue
                
            # Calculate basic pass metrics
            pass_distance = np.sqrt(
                (receiver_pos[0] - passer_pos[0])**2 + 
                (receiver_pos[1] - passer_pos[1])**2
            )
            
            # Check if pass distance is within allowed range
            if not (self.min_pass_distance <= pass_distance <= self.max_pass_distance):
                continue
            
            # Analyze passing lane
            passing_lane = PassingLane(
                start_pos=passer_pos,
                end_pos=receiver_pos,
                distance=pass_distance,
                interceptors=self.find_interceptors(
                    (passer_pos, receiver_pos),
                    opponent_positions
                ),
                success_probability=0.0,  # Will be calculated
                risk_score=0.0,  # Will be calculated
                reward_score=0.0,  # Will be calculated
                total_score=0.0  # Will be calculated
            )
            
            # Calculate defensive pressure on receiver
            defensive_pressure = self.calculate_defensive_pressure(
                receiver_pos,
                [pos for _, pos in opponent_positions]
            )
            
            # Calculate horizontal progress
            horizontal_progress = (receiver_pos[0] - passer_pos[0]) / self.field_length
            
            # Calculate space gained
            space_gained = self.calculate_space_gained(
                passer_pos,
                receiver_pos,
                [pos for _, pos in opponent_positions]
            )
            
            # Calculate tactical advantage
            # tactical_advantage = self.calculate_tactical_advantage(
            #     receiver_pos,
            #     [pos for _, pos in teammate_positions],
            #     [pos for _, pos in opponent_positions]
            # )
            
            # Calculate success probability
            passing_lane.success_probability = self.calculate_pass_success_probability(
                passing_lane,
                defensive_pressure
            )
            
            # Calculate risk and reward scores
            passing_lane.risk_score = self.calculate_risk_score(
                passing_lane,
                defensive_pressure
            )
            
            passing_lane.reward_score = self.calculate_reward_score(
                horizontal_progress,
                space_gained,
                # tactical_advantage
            )
            
            # Calculate total score
            passing_lane.total_score = (
                passing_lane.reward_score * (1 - passing_lane.risk_score)
            )
            
            # Create passing opportunity if it meets threshold
            if passing_lane.success_probability >= self.success_probability_threshold:
                opportunity = PassingOpportunity(
                    passer_id=passer_id,
                    receiver_id=receiver_id,
                    lane=passing_lane,
                    defensive_pressure=defensive_pressure,
                    horizontal_progress=horizontal_progress,
                    space_gained=space_gained,
                    # tactical_advantage=tactical_advantage,
                    timestamp=timestamp
                )
                opportunities.append(opportunity)
        
        self.current_opportunities = opportunities
        return opportunities

    def calculate_risk_score(self, passing_lane: PassingLane, 
                           defensive_pressure: float) -> float:
        """Calculate overall risk score for a passing opportunity"""
        # Normalize components
        interceptor_risk = min(1.0, len(passing_lane.interceptors) / 3)
        pressure_risk = min(1.0, defensive_pressure / 3)
        distance_risk = passing_lane.distance / self.max_pass_distance
        
        # Weighted sum of risk components
        risk_score = (
            self.risk_weights['interceptor_probability'] * interceptor_risk +
            self.risk_weights['receiver_pressure'] * pressure_risk +
            self.risk_weights['pass_distance'] * distance_risk
        )
        
        return min(1.0, risk_score)

    def calculate_reward_score(self, horizontal_progress: float,
                             space_gained: float) -> float:
        """Calculate overall reward score for a passing opportunity"""
        # Normalize components
        horizontal_progress_norm = (horizontal_progress + 1) / 2  # Convert from [-1,1] to [0,1]
        space_gained_norm = min(1.0, space_gained / 20)  # Assume 20m is max space gain
        # tactical_advantage_norm = min(1.0, max(0.0, tactical_advantage))
        
        # Weighted sum of reward components
        reward_score = (
            self.reward_weights['horizontal_progress'] * horizontal_progress_norm +
            self.reward_weights['space_gained'] * space_gained_norm 
            # self.reward_weights['tactical_advantage'] * tactical_advantage_norm
        )
        
        return min(1.0, reward_score)

    def calculate_space_gained(self, start_pos: Tuple[float, float],
                             end_pos: Tuple[float, float],
                             opponent_positions: List[Tuple[float, float]]) -> float:
        """Calculate effective space gained by the pass"""
        if not opponent_positions:
            return 0.0
            
        # Calculate average distance to opponents before and after pass
        start_distances = cdist([start_pos], opponent_positions)[0]
        end_distances = cdist([end_pos], opponent_positions)[0]
        
        avg_start_distance = np.mean(start_distances)
        avg_end_distance = np.mean(end_distances)
        
        return max(0.0, avg_end_distance - avg_start_distance)

    def get_best_opportunity(self) -> Optional[PassingOpportunity]:
        """Get the highest-rated current passing opportunity"""
        if not self.current_opportunities:
            return None
            
        return max(self.current_opportunities, 
                  key=lambda x: x.lane.total_score)

    def get_opportunity_stats(self) -> Dict:
        """Get statistics about current passing opportunities"""
        if not self.current_opportunities:
            return {
                'num_opportunities': 0,
                'avg_success_prob': 0.0,
                'max_success_prob': 0.0,
                'avg_risk': 0.0,
                'avg_reward': 0.0
            }
            
        return {
            'num_opportunities': len(self.current_opportunities),
            'avg_success_prob': np.mean([op.lane.success_probability 
                                       for op in self.current_opportunities]),
            'max_success_prob': max(op.lane.success_probability 
                                  for op in self.current_opportunities),
            'avg_risk': np.mean([op.lane.risk_score 
                               for op in self.current_opportunities]),
            'avg_reward': np.mean([op.lane.reward_score 
                                 for op in self.current_opportunities])
        }
    


