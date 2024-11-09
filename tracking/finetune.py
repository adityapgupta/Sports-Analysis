import shutil

from ultralytics import YOLO


EPOCHS = 10
BATCH = 4
AMP = True  # set to False for GTX cards


if __name__ == '__main__':
    model = YOLO('../models/yolov10m.pt')

    model.train(
        data='yml/config.yaml',
        epochs=EPOCHS,
        batch=BATCH,
        amp=AMP,
    )

    shutil.copy(
        'runs/detect/train/weights/best.pt',
        '../models/players.pt',
    )
