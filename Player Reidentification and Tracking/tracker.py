import cv2
import numpy as np
from collections import defaultdict

class PlayerTracker:
    def __init__(self):
        self.track_history = defaultdict(lambda: {
            'jersey_numbers': [],
            'team_predictions': [],
            'frames_visible': 0,
            'last_seen': 0,
            'most_common_number': -1,
            'team': -1
        })
        
        # Colors for different teams and roles
        self.colors = {
            'team_a': (255, 50, 50),    # Red for team A
            'team_b': (50, 50, 255),    # Blue for team B
            'referee': (0, 255, 0),      # Green for referee
            'goalkeeper': (255, 255, 0),  # Yellow for goalkeeper
            'unknown': (128, 128, 128)   # Gray for unknown
        }
        
    def update_history(self, track_id: int, jersey_info: dict, frame_id: int):
        """Update tracking history for a player"""
        history = self.track_history[track_id]
        
        # Update frame information
        history['frames_visible'] += 1
        history['last_seen'] = frame_id
        
        # Update jersey number history
        if jersey_info['jersey_number'] != -1:
            history['jersey_numbers'].append(jersey_info['jersey_number'])
            
            # Update most common number if confidence is high
            if jersey_info['number_confidence'] > 0.7:
                numbers = history['jersey_numbers']
                if numbers:
                    from collections import Counter
                    counter = Counter(numbers)
                    history['most_common_number'] = counter.most_common(1)[0][0]
        
        # Update team prediction
        if jersey_info['team'] != -1 and jersey_info['team_confidence'] > 0.7:
            history['team_predictions'].append(jersey_info['team'])
            if history['team_predictions']:
                from collections import Counter
                counter = Counter(history['team_predictions'])
                history['team'] = counter.most_common(1)[0][0]
    
    def get_display_info(self, track_id: int) -> tuple:
        """Get display information for a track"""
        history = self.track_history[track_id]
        
        # Get jersey number
        number = history['most_common_number']
        number_str = f"#{number}" if number != -1 else ""
        
        # Get team color
        if history['team'] == 0:
            color = self.colors['team_a']
        elif history['team'] == 1:
            color = self.colors['team_b']
        else:
            color = self.colors['unknown']
            
        return number_str, color
    
    def draw_player_box(self, frame: np.ndarray, bbox: list, color: tuple, 
                       text: str = "", thickness: int = 2) -> np.ndarray:
        """Draw bounding box for a player"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Draw main bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw text if provided
        if text:
            # Calculate text size
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
            
            # Draw text background
            text_x = x1
            text_y = y1 - 5
            cv2.rectangle(frame, 
                         (text_x, text_y - text_size[1] - 5),
                         (text_x + text_size[0] + 5, text_y + 5),
                         color, -1)
            
            # Draw text
            cv2.putText(frame, text,
                       (text_x + 2, text_y),
                       font, font_scale, (255, 255, 255), 2)
        
        return frame
    
    def draw_player_ellipse(self, frame: np.ndarray, bbox: list, 
                           color: tuple, thickness: int = 2) -> np.ndarray:
        """Draw ellipse under player"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Calculate ellipse parameters
        center_x = (x1 + x2) // 2
        width = x2 - x1
        height = int(width * 0.3)  # Ellipse height as fraction of width
        
        # Draw ellipse
        cv2.ellipse(frame,
                   (center_x, y2),  # Center point
                   (width//2, height),  # Axes lengths
                   0,  # Angle
                   0, 360,  # Start and end angles
                   color,
                   thickness)
        
        return frame
    
    def draw_annotations(self, frame: np.ndarray, detection: dict) -> np.ndarray:
        """Draw all annotations for a player detection"""
        bbox = detection['bbox']
        track_id = detection['track_id']
        class_name = detection.get('class', 'unknown')
        
        # Get display information
        number_str, color = self.get_display_info(track_id)
        
        # Special colors for non-players
        if class_name == 'referee':
            color = self.colors['referee']
        elif class_name == 'goalkeeper':
            color = self.colors['goalkeeper']
        
        # Create display text
        if number_str:
            display_text = f"{track_id} {number_str}"
        else:
            display_text = str(track_id)
        
        # Draw annotations
        frame = self.draw_player_ellipse(frame, bbox, color)
        frame = self.draw_player_box(frame, bbox, color, display_text)
        
        return frame

class BallTracker:
    def __init__(self):
        self.color = (255, 255, 0)  # Yellow for ball
    
    def draw_annotations(self, frame: np.ndarray, bbox: list) -> np.ndarray:
        """Draw ball marker"""
        x1, y1, x2, y2 = map(int, bbox)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Draw circle
        radius = max(3, (x2 - x1) // 4)
        cv2.circle(frame, (center_x, center_y), radius, self.color, -1)
        
        return frame