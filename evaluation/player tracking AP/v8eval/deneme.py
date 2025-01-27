import cv2
from ultralytics import YOLO

model_path = "yolov8_footballplayer_detection/best.pt"
cap = cv2.VideoCapture("futbol.mp4")

# Video dosyasının doğru bir şekilde açıldığını kontrol edin
if not cap.isOpened():
    print("Video dosyası açılamadı.")
    exit()

# Modeli yükleyin
model = YOLO(model_path)  # Özel bir modeli yükleyin

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

    # 'q' tuşuna basıldığında döngüyü kırın
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
