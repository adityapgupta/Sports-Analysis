import os
import yaml
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass
from typing import List, Tuple, Dict

cdir = os.path.dirname(os.path.abspath(__file__))


@dataclass
class ControlZone:
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    controlled_area: float
    dominance_score: float
    reachable_space: List[Tuple[float, float]]
    team: str
    player_id: int


class SpaceControlAnalyzer:
    def __init__(self, config_path: str = f'{cdir}/../config/config.yaml'):
        """Initialize Space Control Analyzer"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        self.frame_rate = config['frame_rate']

        # Load space control specific settings
        space_config = config.get('thresholds', {}).get('space_control', {
            'grid_resolution': 1.0,  # meters between grid points
            'max_reach_time': 4.0,   # seconds
            'acceleration': 3.0,     # m/s²
            'max_speed': 8.0,        # m/s
            'control_decay': 0.7     # spatial influence decay factor
        })

        self.grid_resolution = space_config['grid_resolution']
        self.max_reach_time = space_config['max_reach_time']
        self.acceleration = space_config['acceleration']
        self.max_speed = space_config['max_speed']
        self.control_decay = space_config['control_decay']

        # Create field grid
        self.x_grid = np.arange(0, self.field_length, self.grid_resolution)
        self.y_grid = np.arange(0, self.field_width, self.grid_resolution)
        self.grid_points = np.array(
            [(x, y) for x in self.x_grid for y in self.y_grid])

        self.control_zones: List[ControlZone] = []
        self.dominant_regions = None
        self.control_surface = None

    def calculate_arrival_time(self,
                               start_pos: Tuple[float, float],
                               velocity: Tuple[float, float],
                               target_pos: Tuple[float, float]) -> float:
        """
        Calculate time to reach target position considering acceleration and max speed

        Args:
            start_pos: Starting position (x, y)
            velocity: Current velocity vector (vx, vy)
            target_pos: Target position (x, y)

        Returns:
            Time in seconds to reach target
        """
        # Calculate distance
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Simple physics model with acceleration and max speed
        current_speed = np.sqrt(velocity[0]**2 + velocity[1]**2)

        # Time to reach max speed
        time_to_max = (self.max_speed - current_speed) / self.acceleration
        distance_to_max = current_speed * time_to_max + \
            0.5 * self.acceleration * time_to_max**2

        if distance_to_max >= distance:
            # Target reached during acceleration phase
            return (-current_speed + np.sqrt(current_speed**2 + 2*self.acceleration*distance)) / self.acceleration
        else:
            # Need to consider max speed phase
            remaining_distance = distance - distance_to_max
            time_at_max = remaining_distance / self.max_speed
            return time_to_max + time_at_max

    def calculate_control_score(self,
                                point: Tuple[float, float],
                                player_pos: Tuple[float, float],
                                player_vel: Tuple[float, float]) -> float:
        """Calculate control score for a point based on arrival time"""
        arrival_time = self.calculate_arrival_time(
            player_pos, player_vel, point)
        if arrival_time > self.max_reach_time:
            return 0

        # Exponential decay based on arrival time
        return np.exp(-self.control_decay * arrival_time)

    def analyze_space_control(self,
                              home_positions: List[Tuple[int, Tuple[float, float], Tuple[float, float]]],
                              away_positions: List[Tuple[int, Tuple[float, float], Tuple[float, float]]]) -> Dict:
        """
        Analyze space control for current frame

        Args:
            home_positions: List of (player_id, position, velocity) for home team
            away_positions: List of (player_id, position, velocity) for away team

        Returns:
            Dictionary containing space control metrics
        """
        all_positions = [(pid, pos, vel, 'home')
                         for pid, pos, vel in home_positions]
        all_positions.extend([(pid, pos, vel, 'away')
                             for pid, pos, vel in away_positions])

        # Calculate control scores for each grid point
        control_matrix = np.zeros((len(self.grid_points), len(all_positions)))

        for i, point in enumerate(self.grid_points):
            for j, (_, pos, vel, _) in enumerate(all_positions):
                control_matrix[i, j] = self.calculate_control_score(
                    point, pos, vel)

        # Determine dominant team for each point
        home_control = control_matrix[:, :len(home_positions)].sum(axis=1)
        away_control = control_matrix[:, len(home_positions):].sum(axis=1)

        dominant_team = np.where(home_control > away_control, 'home', 'away')
        dominance_strength = np.maximum(home_control, away_control)

        # Calculate overall metrics
        total_points = len(self.grid_points)
        home_points = np.sum(dominant_team == 'home')
        away_points = np.sum(dominant_team == 'away')

        # Store results for visualization
        self.dominant_regions = dominant_team.reshape(
            len(self.x_grid), len(self.y_grid))
        self.control_surface = dominance_strength.reshape(
            len(self.x_grid), len(self.y_grid))

        # Create control zones for each player
        self.control_zones = []
        for pid, pos, vel, team in all_positions:
            # Calculate individual control area
            player_control = control_matrix[:, all_positions.index(
                (pid, pos, vel, team))]
            controlled_points = self.grid_points[player_control >
                                                 0.5 * np.max(player_control)]

            zone = ControlZone(
                position=pos,
                velocity=vel,
                controlled_area=len(controlled_points) *
                self.grid_resolution**2,
                dominance_score=np.mean(player_control),
                reachable_space=controlled_points.tolist(),
                team=team,
                player_id=pid
            )
            self.control_zones.append(zone)

        return {
            'space_control': {
                'home': home_points / total_points * 100,
                'away': away_points / total_points * 100
            },
            'control_zones': {
                'home': [z for z in self.control_zones if z.team == 'home'],
                'away': [z for z in self.control_zones if z.team == 'away']
            },
            'pitch_control': {
                'defensive_third': self._calculate_zone_control(0, self.field_length/3),
                'middle_third': self._calculate_zone_control(self.field_length/3, 2*self.field_length/3),
                'attacking_third': self._calculate_zone_control(2*self.field_length/3, self.field_length)
            }
        }

    def _calculate_zone_control(self, start_y: float, end_y: float) -> Dict:
        """Calculate control percentages for a specific zone of the pitch"""
        zone_mask = (self.grid_points[:, 1] >= start_y) & (
            self.grid_points[:, 1] < end_y)
        zone_teams = self.dominant_regions.flatten()[zone_mask]

        total_points = np.sum(zone_mask)
        home_points = np.sum(zone_teams == 'home')

        return {
            'home': home_points / total_points * 100,
            'away': (total_points - home_points) / total_points * 100
        }

    def visualize_space_control(self):
        """Visualize space control analysis"""
        if self.dominant_regions is None or self.control_surface is None:
            return

        plt.figure(figsize=(15, 8))

        # Plot control surface
        plt.subplot(121)
        plt.imshow(self.control_surface.T, origin='lower',
                   extent=[0, self.field_length, 0, self.field_width],
                   cmap='RdYlBu', aspect='equal')

        # Add player positions
        for zone in self.control_zones:
            color = 'blue' if zone.team == 'home' else 'red'
            plt.plot(zone.position[0], zone.position[1],
                     'o', color=color, markersize=8)

            # Plot velocity vectors
            plt.arrow(zone.position[0], zone.position[1],
                      zone.velocity[0], zone.velocity[1],
                      color=color, width=0.1, head_width=0.5)

        plt.title('Space Control Intensity')
        plt.colorbar(label='Control Strength')

        # Plot dominant regions
        plt.subplot(122)
        plt.imshow(np.where(self.dominant_regions.T == 'home', 1, 0),
                   origin='lower', extent=[0, self.field_length, 0, self.field_width],
                   cmap='RdBu', aspect='equal')

        # Add pitch markings
        self._draw_pitch_markings()

        plt.title('Dominant Team Regions (Blue: Home, Red: Away)')

        plt.tight_layout()
        plt.show()

    def _draw_pitch_markings(self):
        """Draw basic pitch markings on the current plot"""
        plt.plot([0, self.field_length], [0, 0], 'k-')
        plt.plot([0, self.field_length], [
                 self.field_width, self.field_width], 'k-')
        plt.plot([0, 0], [0, self.field_width], 'k-')
        plt.plot([self.field_length, self.field_length],
                 [0, self.field_width], 'k-')

        # Draw thirds
        plt.axvline(x=self.field_length/3, color='k',
                    linestyle='--', alpha=0.3)
        plt.axvline(x=2*self.field_length/3, color='k',
                    linestyle='--', alpha=0.3)

    def visualize_player_influence(self, player_id: int, team: str, show: bool = True):
        """Visualize individual player's spatial influence"""
        zone = next((z for z in self.control_zones
                    if z.player_id == player_id and z.team == team), None)

        if not zone:
            return

        # Plot reachable space
        reachable_space = np.array(zone.reachable_space)
        plt.scatter(reachable_space[:, 0], reachable_space[:, 1],
                    c='blue' if team == 'home' else 'red',
                    alpha=0.3)

        if show:
            self._draw_pitch_markings()

            plt.title(f'Player {player_id} ({team}) Spatial Influence\n' +
                      f'Controlled Area: {zone.controlled_area:.1f}m²')
            plt.axis('equal')
            plt.grid(True)
            plt.show()

    def visualize_players_influence(self, player_data: List[Tuple[int, str]]):
        plt.figure(figsize=(15, 8))

        for player_id, team in player_data:
            self.visualize_player_influence(player_id, team, show=False)

        self._draw_pitch_markings()
        plt.title('Players Spatial Influence')
        plt.axis('equal')
        plt.grid(True)
        plt.show()

    def plot_control_evolution(self, control_history: List[Dict]):
        """Plot evolution of space control over time"""
        if not control_history:
            return

        times = range(len(control_history))
        home_control = [frame['space_control']['home']
                        for frame in control_history]
        away_control = [frame['space_control']['away']
                        for frame in control_history]

        plt.figure(figsize=(12, 6))
        plt.plot(times, home_control, 'b-', label='Home Team')
        plt.plot(times, away_control, 'r-', label='Away Team')

        plt.title('Space Control Evolution')
        plt.xlabel('Time (frames)')
        plt.ylabel('Controlled Space (%)')
        plt.legend()
        plt.grid(True)
        plt.show()
