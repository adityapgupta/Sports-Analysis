import os
from tracking.detect2 import *
from tqdm import tqdm

data_path = "../SoccerNet/tracking-2023/test"

for file in tqdm(os.listdir(data_path)):
    # make_video(f"{data_path}/{file}/img1", f"{data_path}/{file}/out.mp4")

    detections(
        clip_path= f"{data_path}/{file}/out.mp4",
        model_path="yolov8m-football.pt",
        pkl_path=f"{data_path}/{file}/det8_2.pkl")

    
