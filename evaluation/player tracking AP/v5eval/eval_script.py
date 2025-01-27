"""
Download best.pt from:
https://drive.google.com/file/d/1RJ3_c4iU1TQLLE2iBnUC6qiuaMuEgc6Y/view?usp=sharing
"""

import os
from tracking.detect2 import *
from tqdm import tqdm

data_path = "../SoccerNet/tracking-2023/test"

for file in tqdm(os.listdir(data_path)):
    # make_video(f"{data_path}/{file}/img1", f"{data_path}/{file}/out.mp4")

    detections(
        clip_path= f"{data_path}/{file}/out.mp4",
        model_path="best.pt",
        pkl_path=f"{data_path}/{file}/det5.pkl")

    
