# Sports Analysis

Welcome to the Sports Analysis project! This innovative tool leverages advanced computer vision techniques to analyze football games using video feeds. By employing finetuned versions of YOLOv10, we accurately detect players and the ball, enabling comprehensive game analysis. Gain valuable insights such as ball movement patterns, team formation heatmaps, player statistics, and passing opportunities.

## Key Features
- **Accurate Player and Ball Detection**: Utilizing state-of-the-art YOLOv10 models.
- **In-depth Game Analysis**: Extract meaningful insights from video feeds.
- **Customizable Models**: Finetune your own models or use our pre-trained weights.
- **Visual Representations**: Heatmaps, minimaps, and more to visualize game dynamics.

## Getting Started
1. **Install Dependencies**: Run `pip install -r requirements.txt` to install the required packages.
2. **Download Models**: Obtain the `SV_FT_WC14_kp` and `SV_FT_WC14_lines` files from [this repository](https://github.com/mguti97/No-Bells-Just-Whistles) and place them in the `models` folder.
3. **Model Training**: If you wish to finetune your own models, follow the instructions in the `training` folder. Alternatively, use the provided weights in the `models` folder.
4. **Run Analysis**: Execute `main.py` to perform detection and analysis on the video feed.

## Results
Explore the results folder to see example videos with their detections.

## Pipeline Overview
![Pipeline](figures/arch.png)

## Demo

### Original Video
![Original](figures/original.jpg)

### Detection Markers
![Detection Markers](figures/marked.jpg)

### Minimap Visualization
![Minimap](figures/minimap.jpg)

Unlock the full potential of football game analysis with our cutting-edge Sports Analysis project. Dive into the data and transform the way you understand the game!
