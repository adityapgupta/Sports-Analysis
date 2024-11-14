# Sports Analysis

The aim of this project is to analyze a game of football using video feed from a camera. Finetuned versions of YOLOv10 are used to detect players and the ball. Using these detections, the game is analyzed to provide insights such as ball movement, team formation heatmaps, player statistics and passing opportunities.

## Usage
1. Install the required packages using `pip install -r requirements.txt`
2. Download the SV_FT_WC14_kp and SV_FT_WC14_lines files from https://github.com/mguti97/No-Bells-Just-Whistles and place them in the models folder.
3. If you want to finetune your own models, follow the instructions in the training folder. If not, you can use the weights provided in the models folder.
4. Run `main.py` to perform detection and analysis on the video feed.

Some videos with their detections have been provided in the results folder.