from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from PIL import Image
import io

# Create the FastAPI application instance
app = FastAPI(title="SQPM Defect Detection API")

# Load the model ONCE when the server starts (not on every request — that would be slow)
model = YOLO("models/best.pt")

@app.get("/")
def root():
    """Simple health check — confirms the server is alive."""
    return {"status": "SQPM API is running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, runs YOLOv8 inference,
    returns detected defects as JSON.
    """
    # Read the uploaded file's raw bytes and turn them into a PIL image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Run inference
    results = model(image)

    # Convert YOLO's result object into clean JSON
    detections = []
    for box in results[0].boxes:
        detections.append({
            "class": model.names[int(box.cls[0])],
            "confidence": round(float(box.conf[0]), 3),
            "bbox_xyxy": [round(float(v), 1) for v in box.xyxy[0].tolist()]
        })

    return {
        "filename": file.filename,
        "num_detections": len(detections),
        "detections": detections
    }
