# Path: soccer_analytics/core/formation_analyzer.py

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import yaml
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import logging
from datetime import datetime
import os

@dataclass
class FormationZone:
    """Represents a zone in the formation"""
    center: Tuple[float, float]
    players: List[int]  # player IDs in this zone
    role: str  # 'GK', 'DEF', 'MID', 'FWD'
    average_width: float
    average_depth: float

@dataclass
class Formation:
    """Represents a team's formation"""
    timestamp: float
    formation_string: str  # e.g., "4-3-3"
    zones: List[FormationZone]
    compactness: float
    width: float
    depth: float
    balance_score: float

class FormationAnalyzer:
    def __init__(self, config_path: str = f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.yaml'):
        """Initialize Formation Analyzer"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self.logger = logging.getLogger(__name__)
        
        # Load field dimensions
        self.field_length = config['field']['length']
        self.field_width = config['field']['width']
        
        # Load formation specific settings
        formation_config = config['thresholds']['formation']
        self.window_size = formation_config['window_size']
        self.cluster_tolerance = formation_config['cluster_tolerance']
        
        # Formation detection parameters
        self.min_players = 7  # Minimum players needed for formation detection
        self.position_history: Dict[str, List[List[Tuple[float, float]]]] = {
            'home': [], 'away': []
        }
        self.formation_history: Dict[str, List[Formation]] = {'home': [], 'away': []}
        
        # Common formation templates for matching
        self.formation_templates = {
            '4-4-2': {'DEF': 4, 'MID': 4, 'FWD': 2},
            '4-3-3': {'DEF': 4, 'MID': 3, 'FWD': 3},
            '3-5-2': {'DEF': 3, 'MID': 5, 'FWD': 2},
            '4-2-3-1': {'DEF': 4, 'MID': 5, 'FWD': 1},
            '4-1-4-1': {'DEF': 4, 'MID': 5, 'FWD': 1},
            '3-4-3': {'DEF': 3, 'MID': 4, 'FWD': 3},
            '5-3-2': {'DEF': 5, 'MID': 3, 'FWD': 2},
            '4-5-1': {'DEF': 4, 'MID': 5, 'FWD': 1}
        }

    def _cluster_positions(self, positions: List[Tuple[float, float]], 
                         n_clusters: int) -> Tuple[List[Tuple[float, float]], List[int]]:
        """Cluster player positions into tactical units"""
        if len(positions) < n_clusters:
            return [], []
            
        # Convert positions to numpy array
        pos_array = np.array(positions)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        labels = kmeans.fit_predict(pos_array)
        centers = kmeans.cluster_centers_
        
        # Convert centers back to tuples
        centers_tuple = [(float(c[0]), float(c[1])) for c in centers]
        
        return centers_tuple, labels.tolist()

    def _assign_roles(self, centers: List[Tuple[float, float]], 
                     n_defenders: int, n_midfielders: int, n_forwards: int) -> List[str]:
        """Assign tactical roles to position clusters"""
        # Sort centers by y-coordinate (vertical position)
        sorted_centers = sorted(centers, key=lambda x: x[1])
        
        roles = []
        current_idx = 0
        
        # Assign defenders
        for _ in range(n_defenders):
            if current_idx < len(sorted_centers):
                roles.append('DEF')
                current_idx += 1
        
        # Assign midfielders
        for _ in range(n_midfielders):
            if current_idx < len(sorted_centers):
                roles.append('MID')
                current_idx += 1
        
        # Assign forwards
        for _ in range(n_forwards):
            if current_idx < len(sorted_centers):
                roles.append('FWD')
                current_idx += 1
        
        return roles

    def _calculate_formation_metrics(self, positions: List[Tuple[float, float]], 
                                  zones: List[FormationZone]) -> Dict[str, float]:
        """Calculate formation metrics like compactness, width, depth"""
        if not positions or not zones:
            return {
                'compactness': 0.0,
                'width': 0.0,
                'depth': 0.0,
                'balance_score': 0.0
            }
        
        # Calculate compactness (average distance between players)
        distances = cdist(np.array(positions), np.array(positions))
        compactness = np.mean(distances[distances > 0])
        
        # Calculate width (max distance between players horizontally)
        x_coords = [pos[0] for pos in positions]
        width = max(x_coords) - min(x_coords)
        
        # Calculate depth (max distance between players vertically)
        y_coords = [pos[1] for pos in positions]
        depth = max(y_coords) - min(y_coords)
        
        # Calculate balance score (symmetry of formation)
        center_x = self.field_width / 2
        x_deviations = [abs(pos[0] - center_x) for pos in positions]
        balance_score = 1 - (np.mean(x_deviations) / (self.field_width / 2))
        
        return {
            'compactness': float(compactness),
            'width': float(width),
            'depth': float(depth),
            'balance_score': float(balance_score)
        }

    def _detect_formation_pattern(self, zones: List[FormationZone]) -> str:
        """Detect the formation pattern based on player positions"""
        # Count players in each role
        role_counts = {'DEF': 0, 'MID': 0, 'FWD': 0}
        for zone in zones:
            role_counts[zone.role] += len(zone.players)
        
        # Match against templates
        best_match = None
        best_diff = float('inf')
        
        for formation, template in self.formation_templates.items():
            diff = sum(abs(role_counts[role] - template.get(role, 0)) 
                      for role in role_counts)
            if diff < best_diff:
                best_diff = diff
                best_match = formation
        
        return best_match or f"{role_counts['DEF']}-{role_counts['MID']}-{role_counts['FWD']}"

    def analyze_frame(self, home_positions: List[Tuple[int, Tuple[float, float]]],
                     away_positions: List[Tuple[int, Tuple[float, float]]],
                     timestamp: float = None) -> Dict[str, Formation]:
        """Analyze formation for both teams in current frame"""
        formations = {}
        
        for team, positions in [('home', home_positions), ('away', away_positions)]:
            if len(positions) < self.min_players:
                continue
            
            # Split player IDs and positions
            player_ids, pos = zip(*positions)
            
            # Update position history
            self.position_history[team].append(list(pos))
            if len(self.position_history[team]) > self.window_size:
                self.position_history[team].pop(0)
            
            # Calculate average positions over window
            avg_positions = np.mean(self.position_history[team], axis=0)
            avg_positions = [(float(p[0]), float(p[1])) for p in avg_positions]
            
            # Detect number of lines based on vertical clustering
            y_coords = [p[1] for p in avg_positions]
            y_clusters = KMeans(n_clusters=min(4, len(y_coords)), n_init=10).fit_predict(
                np.array(y_coords).reshape(-1, 1))
            n_lines = len(set(y_clusters))
            
            # Cluster positions for each tactical unit
            defender_centers, defender_labels = self._cluster_positions(
                [pos for i, pos in enumerate(avg_positions) 
                 if y_clusters[i] == 0], 
                4)  # Assuming maximum 4 defenders
                
            midfielder_centers, midfielder_labels = self._cluster_positions(
                [pos for i, pos in enumerate(avg_positions) 
                 if y_clusters[i] == 1], 
                5)  # Assuming maximum 5 midfielders
                
            forward_centers, forward_labels = self._cluster_positions(
                [pos for i, pos in enumerate(avg_positions) 
                 if y_clusters[i] == 2], 
                3)  # Assuming maximum 3 forwards
            
            # Create formation zones
            zones = []
            for center, role in zip(defender_centers + midfielder_centers + forward_centers,
                                  ['DEF']*len(defender_centers) + 
                                  ['MID']*len(midfielder_centers) + 
                                  ['FWD']*len(forward_centers)):
                # Find players in this zone
                zone_players = [pid for pid, pos in positions 
                              if np.sqrt((pos[0]-center[0])**2 + 
                                       (pos[1]-center[1])**2) < self.cluster_tolerance]
                
                # Calculate zone metrics
                zone_positions = [pos for pid, pos in positions if pid in zone_players]
                if zone_positions:
                    zone_width = max(p[0] for p in zone_positions) - min(p[0] for p in zone_positions)
                    zone_depth = max(p[1] for p in zone_positions) - min(p[1] for p in zone_positions)
                else:
                    zone_width = zone_depth = 0.0
                
                zones.append(FormationZone(
                    center=center,
                    players=zone_players,
                    role=role,
                    average_width=zone_width,
                    average_depth=zone_depth
                ))
            
            # Calculate formation metrics
            metrics = self._calculate_formation_metrics(avg_positions, zones)
            
            # Create Formation object
            formation = Formation(
                timestamp=timestamp or datetime.now().timestamp(),
                formation_string=self._detect_formation_pattern(zones),
                zones=zones,
                compactness=metrics['compactness'],
                width=metrics['width'],
                depth=metrics['depth'],
                balance_score=metrics['balance_score']
            )
            
            formations[team] = formation
            self.formation_history[team].append(formation)
            
            # Keep formation history within window
            if len(self.formation_history[team]) > self.window_size:
                self.formation_history[team].pop(0)
        
        return formations

    def get_formation_stability(self, team: str) -> Dict[str, float]:
        """Calculate formation stability metrics"""
        if not self.formation_history[team]:
            return {
                'formation_changes': 0,
                'compactness_variance': 0.0,
                'width_variance': 0.0,
                'depth_variance': 0.0
            }
        
        # Count formation changes
        formations = [f.formation_string for f in self.formation_history[team]]
        formation_changes = sum(1 for i in range(1, len(formations))
                              if formations[i] != formations[i-1])
        
        # Calculate metric variances
        compactness_var = np.var([f.compactness for f in self.formation_history[team]])
        width_var = np.var([f.width for f in self.formation_history[team]])
        depth_var = np.var([f.depth for f in self.formation_history[team]])
        
        return {
            'formation_changes': formation_changes,
            'compactness_variance': float(compactness_var),
            'width_variance': float(width_var),
            'depth_variance': float(depth_var)
        }

    def get_formation_summary(self) -> Dict[str, Dict]:
        """Get summary of formation analysis for both teams"""
        summary = {}
        
        for team in ['home', 'away']:
            if not self.formation_history[team]:
                continue
                
            # Get most common formation
            formations = [f.formation_string for f in self.formation_history[team]]
            most_common = max(set(formations), key=formations.count)
            
            # Calculate average metrics
            avg_compactness = np.mean([f.compactness for f in self.formation_history[team]])
            avg_width = np.mean([f.width for f in self.formation_history[team]])
            avg_depth = np.mean([f.depth for f in self.formation_history[team]])
            avg_balance = np.mean([f.balance_score for f in self.formation_history[team]])
            
            # Get stability metrics
            stability = self.get_formation_stability(team)
            
            summary[team] = {
                'primary_formation': most_common,
                'formation_changes': stability['formation_changes'],
                'average_metrics': {
                    'compactness': float(avg_compactness),
                    'width': float(avg_width),
                    'depth': float(avg_depth),
                    'balance': float(avg_balance)
                },
                'stability_metrics': stability
            }
        
        return summary

    def reset(self):
        """Reset analyzer state"""
        self.position_history = {'home': [], 'away': []}
        self.formation_history = {'home': [], 'away': []}