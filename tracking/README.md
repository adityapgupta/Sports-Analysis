# Tracking

This directory contains the code for tracking the players and the ball,
and for using the detections to annotate the videos and create minimaps.

## Detections
`detect.py` contains functions to detect the players and the ball in a frame.
The outputs are written to a pkl file to be used later.

The team classification is done using a SigLIP model https://huggingface.co/docs/transformers/en/model_doc/siglip

The code for this has been taken from https://github.com/roboflow/sports

The projections are calculated using a homography matrix. The code for this has been taken from https://github.com/mguti97/No-Bells-Just-Whistles. The relevant files are placed in the `utils` folder.

## Interpolate
`interpolate.py` contains functions to smooth out the detections since they contain a lot of jitter. This has been done to get smoother outputs for further analytics.

Interpolation for players has been performed by averaging the detections over a sliding window of 5 frames. Interpolation for the ball is done using linear interpolation between the frames.

## Draw
`draw.py` contains functions to draw the detections on the frames and create minimaps.