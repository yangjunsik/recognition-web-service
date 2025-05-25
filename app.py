from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os, time, base64
import numpy as np
import cv2
from ultralytics import YOLO

app = Flask(__name__, template_folder='./www', static_folder='./www', static_url_path='/')
CORS(app)

model = YOLO('yolov8n.pt')

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect', methods=['POST'])
def detect_objects():
    if 'image' not in request.json:
        return jsonify({'error': 'No image data provided'}), 400

    try:
        img_data = request.json['image']
        if ',' in img_data:
            img_data = img_data.split(',')[1]

        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        timestamp = int(time.time())
        img_path = f"{UPLOAD_FOLDER}/image_{timestamp}.jpg"
        cv2.imwrite(img_path, image)

        results = model(image)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                name = model.names[cls]

                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class': cls,
                    'name': name
                })

        return jsonify({'success': True, 'detections': detections})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
