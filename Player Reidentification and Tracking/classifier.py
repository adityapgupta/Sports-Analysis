import torch
import torch.nn as nn
import torchvision.models as models
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
from pathlib import Path
import cv2
import json

class JerseyNumberNet(nn.Module):
    def __init__(self, num_classes, pretrained=True):
        super(JerseyNumberNet, self).__init__()

        # Use EfficientNet as base model (matching your training)
        self.backbone = models.efficientnet_b0(pretrained=pretrained)
        
        # Replace classification head with same architecture used in training
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)

class JerseyNumberRecognizer:
    def __init__(self, model_path=None, json_path=None, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """
        Initialize Jersey Number Recognizer
        Args:
            model_path: Path to trained model weights
            json_path: Path to training annotations json to build class mapping
            device: Device to run inference on
        """
        # Load class mapping from json
        self.number_to_idx = {}
        self.idx_to_number = {}
        if json_path:
            self._build_class_mapping(json_path)
        else:
            print("Warning: No json_path provided. Class mapping will be empty.")
            
        self.device = device
        self.model = JerseyNumberNet(
            num_classes=len(self.number_to_idx) if self.number_to_idx else 45
        ).to(device)
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=device))
        self.model.eval()

        # Use same transforms as training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),  # EfficientNet preferred size
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
    def _build_class_mapping(self, json_path):
        """Build class mapping from training annotations"""
        try:
            with open(json_path, 'r') as f:
                annotations = json.load(f)
                
            # Get unique numbers and sort them
            unique_numbers = sorted(list(set(annotations.values())))
            
            # Create mapping
            self.number_to_idx = {num: idx for idx, num in enumerate(unique_numbers)}
            self.idx_to_number = {idx: num for num, idx in self.number_to_idx.items()}
            
            print(f"Built class mapping with {len(self.number_to_idx)} classes")
            print(f"Class mapping: {self.number_to_idx}")
            
        except Exception as e:
            print(f"Error building class mapping: {e}")
            raise
        
    def extract_jersey_region(self, frame: np.ndarray, bbox: list) -> np.ndarray:
        """Extract jersey region from player detection"""
        x1, y1, x2, y2 = map(int, bbox)
        h = y2 - y1
        w = x2 - x1
        
        # Extract upper body region (same as training)
        jersey_y1 = max(0, y1 + int(h * 0.15))  # Start below neck
        jersey_y2 = min(frame.shape[0], y1 + int(h * 0.5))  # End at waist
        jersey_x1 = max(0, x1)
        jersey_x2 = min(frame.shape[1], x2)
        
        jersey_crop = frame[jersey_y1:jersey_y2, jersey_x1:jersey_x2]
        
        return jersey_crop if jersey_crop.size > 0 else None

    def predict(self, frame: np.ndarray, bbox: list) -> tuple:
        """
        Predict jersey number from player detection
        Args:
            frame: Full frame
            bbox: [x1, y1, x2, y2] player bounding box
        Returns:
            tuple: (jersey_number, confidence)
            jersey_number: int (-1 if not visible)
            confidence: float (0-1)
        """
        if not self.number_to_idx:
            print("Warning: No class mapping available. Predictions may be incorrect.")
            return -1, 0.0
            
        self.model.eval()
        
        # Extract jersey region
        jersey_crop = self.extract_jersey_region(frame, bbox)
        if jersey_crop is None:
            return -1, 0.0
            
        # Preprocess
        try:
            image = Image.fromarray(cv2.cvtColor(jersey_crop, cv2.COLOR_BGR2RGB))
            image = self.transform(image).unsqueeze(0).to(self.device)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return -1, 0.0

        # Inference
        with torch.no_grad():
            try:
                outputs = self.model(image)
                probabilities = torch.softmax(outputs, dim=1)
                prediction_idx = torch.argmax(probabilities).item()
                confidence = probabilities[0, prediction_idx].item()
                
                # Convert index to actual number
                jersey_number = self.idx_to_number[prediction_idx]
                
                return jersey_number, confidence
                
            except Exception as e:
                print(f"Error during inference: {e}")
                return -1, 0.0

# # Example usage:
# if __name__ == "__main__":
#     # Initialize with json for class mapping
#     recognizer = JerseyNumberRecognizer(
#         model_path="path/to/model.pth",
#         json_path="path/to/train_gt.json"
#     )
    
#     # Test prediction
#     frame = cv2.imread("test_image.jpg")
#     bbox = [100, 100, 200, 300]  # Example bbox
#     number, conf = recognizer.predict(frame, bbox)
#     print(f"Predicted number: {number}, confidence: {conf:.2f}")