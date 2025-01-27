# YOLO Football Player Detection - README

## Overview
This Python script utilizes the YOLO (You Only Look Once) v8 model to detect football players in a video file. It leverages the `cv2` module from OpenCV for video processing and the `ultralytics` package to load and run the YOLO model. The script reads frames from a video, applies the YOLO model to detect objects, and then visualizes the detections by drawing bounding boxes and class labels on the frames.

## Prerequisites
Before running the script, ensure you have the following dependencies installed:
- Python 3.x
- OpenCV (`cv2`)
- Ultralytics YOLO

You can install the required libraries using the following commands:
```bash
pip install opencv-python
pip install ultralytics
```

## Usage
1. **Model Path**: Update the `model_path` variable with the path to your trained YOLO model (e.g., `"yolov8_footballplayer_detection/best.pt"`).

2. **Video File**: Update the `cv2.VideoCapture` argument with the path to your video file (e.g., `"futbol.mp4"`).

3. **Threshold**: Adjust the `threshold` variable to set the confidence level for detections.

### Running the Script
Execute the script using Python:
```bash
python detect_football_players.py
```

### Script Breakdown
1. **Import Libraries**:
    ```python
    import cv2
    from ultralytics import YOLO
    ```

2. **Initialize Model and Video Capture**:
    ```python
    model_path = "yolov8_footballplayer_detection/best.pt"
    cap = cv2.VideoCapture("futbol.mp4")
    ```

3. **Check if Video is Opened Correctly**:
    ```python
    if not cap.isOpened():
        print("Video dosyası açılamadı.")
        exit()
    ```

4. **Load YOLO Model**:
    ```python
    model = YOLO(model_path)
    ```

5. **Processing Video Frames**:
    - Read each frame from the video.
    - Apply the YOLO model to detect objects.
    - Draw bounding boxes and labels for detections with a confidence score above the threshold.

    ```python
    threshold = 0.5

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Videodan kare alınamadı veya video sonuna ulaşıldı.")
            break

        results = model(frame)[0]

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            color = (class_id*10, class_id*100, class_id*10)

            if score > threshold:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 4)
                cv2.putText(frame, model.names[int(class_id)].upper(), (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3, cv2.LINE_AA)

        cv2.imshow("frame", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    ```

### Exiting the Script
Press the 'q' key to stop the video processing loop and close all OpenCV windows.

## Notes
- Make sure your video file is accessible and the path is correct.
- The color scheme for bounding boxes is generated based on the `class_id`, which can be customized as needed.
- The `threshold` value can be adjusted to increase or decrease the sensitivity of the detections.

## Troubleshooting
- If the video file cannot be opened, ensure the file path is correct and the file is not corrupted.
- If the model fails to load, verify the model path and ensure the YOLO model file exists and is properly formatted.
- Ensure all dependencies are installed and compatible with your Python version.
