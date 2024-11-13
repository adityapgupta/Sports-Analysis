import numpy as np

from typing import Tuple, List
from scipy.spatial.distance import euclidean


def calculate_velocity(pos1: Tuple[float, float], 
                      pos2: Tuple[float, float], 
                      time_diff: float) -> float:
    """
    Calculate velocity between two positions
    
    Args:
        pos1: Starting position (x, y)
        pos2: Ending position (x, y)
        time_diff: Time difference in seconds
    
    Returns:
        Velocity in km/h
    """
    distance = euclidean(pos1, pos2)  # meters
    return (distance / time_diff) * 3.6  # Convert m/s to km/h


def calculate_direction(pos1: Tuple[float, float], 
                       pos2: Tuple[float, float]) -> str:
    """Calculate movement direction using 8 cardinal directions"""
    x_diff = pos2[0] - pos1[0]
    y_diff = pos2[1] - pos1[1]
    angle = np.degrees(np.arctan2(y_diff, x_diff))
    
    directions = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
    normalized_angle = (angle + 180) % 360
    direction_index = int(((normalized_angle + 22.5) % 360) / 45)
    return directions[direction_index]


def calculate_distance(positions: List[Tuple[float, float]]) -> float:
    """Calculate total distance covered through a series of positions"""
    total_distance = 0
    for i in range(1, len(positions)):
        total_distance += euclidean(positions[i-1], positions[i])
    return total_distance


def smooth_positions(positions: List[Tuple[float, float]], 
                    window_size: int = 5) -> List[Tuple[float, float]]:
    """Apply moving average smoothing to position data"""
    positions_array = np.array(positions)
    kernel = np.ones(window_size) / window_size
    smoothed_x = np.convolve(positions_array[:, 0], kernel, mode='valid')
    smoothed_y = np.convolve(positions_array[:, 1], kernel, mode='valid')
    return list(zip(smoothed_x, smoothed_y))


def calculate_team_centroid(positions: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the centroid of a group of positions"""
    positions_array = np.array(positions)
    return np.mean(positions_array[:, 0]), np.mean(positions_array[:, 1])


def calculate_convex_hull_area(positions: List[Tuple[float, float]]) -> float:
    """Calculate the area of the convex hull formed by a set of positions"""
    from scipy.spatial import ConvexHull
    if len(positions) < 3:
        return 0
    hull = ConvexHull(np.array(positions))
    return hull.area


def interpolate_position(pos1: Tuple[float, float],
                        pos2: Tuple[float, float],
                        ratio: float) -> Tuple[float, float]:
    """Linear interpolation between two positions"""
    return (pos1[0] + (pos2[0] - pos1[0]) * ratio,
            pos1[1] + (pos2[1] - pos1[1]) * ratio)
