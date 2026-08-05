from ultralytics import YOLO

# Load a small pretrained YOLOv8 model as our starting point (transfer learning)
model = YOLO("yolov8n.pt")  # "n" = nano, smallest/fastest variant — good for a first run

# Train on NEU-DET steel surface defect dataset
results = model.train(
    data="/home/melik/sqpm/data/neu_det/NEU-DET-object-detection-1/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,           # we'll adjust this once we know if you have GPU access
    project="runs",
    name="neu_det_v1"
)
