# Training

The base YOLO models have decent object detections for football videos,
but it can be improved using labelled data from Soccernet.

Two separate models have been finetuned, one for player detection and one for ball detection. Both of these are available in the `models` folder.

## Usage
1. Visit https://www.soccer-net.org/data to fill an NDA to access the data. This will give you a password to be used to download the data.
2. Run `data.py` with the password to download the data and split it into datasets for training. Run with `ball=True` to prepare the dataset for ball detection.
3. Run `finetune.py` to start the finetuning. Set various hyperparameters according to your needs. The outputs will be saved in the `models` folder (change the paths in the script if needed).
4. The `config` folder has the configuration files for the models. You can change the paths to the datasets and the model weights in these files.
