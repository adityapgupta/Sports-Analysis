import shutil

from ultralytics import YOLO

# hyperparameters for fine-tuning
EPOCHS = 10
BATCH = 4
AMP = True  # set to False for GTX cards


# main function to fine-tune the YOLO model
if __name__ == '__main__':
    model = YOLO('../models/yolov10m.pt')  # loads YOLOv10 model from ultralytics

    model.train(
        data='config/config.yaml',
        epochs=EPOCHS,
        batch=BATCH,
        amp=AMP,
    )

    # save the best weights to the models folder
    shutil.copy(
        'runs/detect/train/weights/best.pt',
        '../models/players.pt',
    )
