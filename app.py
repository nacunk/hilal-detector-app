import streamlit as st
import torch
from PIL import Image
import io
import cv2
import numpy as np
from hilalpy import Hilal  # Untuk observabilitas (opsional)
import requests  # Untuk cuaca

# Load model YOLOv5 custom (path relatif untuk deployment)
@st.cache_resource
def load_model():
    model_path = './models/best.pt'  # Asumsi model di folder models/ di repo GitHub
    if not torch.cuda.is_available():
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, device='cpu')
    else:
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
    return model

# Fungsi deteksi dan draw bbox
def detect_hilal(image, model):
    results = model(image)
    detections = results.pandas().xyxy[0]
    hilal_detections = detections[detections['name'] == 'hilal']
    
    # Draw bbox dengan OpenCV
    img_array = np.array(image)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    for _, row in hilal_detections.iterrows():
        x1, y1, x2, y2, conf = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']), row['confidence']
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Bbox hijau
        cv2.putText(img_cv, f"Hilal: {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Konversi kembali ke PIL
    img_result = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    return img_result, hilal_detections

# Fungsi hilalpy dan cuaca
def get_observability_and_weather(image):
    # EXIF sederhana (timestamp, GPS default Jakarta)
    exif = image.getexif()
    timestamp = None
    lat, lon = -6.2088, 106.8456  # Default Jakarta
    if exif:
        for tag_id, value in exif.items():
            if tag_id == 306:  # DateTime tag
                timestamp = value
    
    # Hilalpy (try-except untuk hindari error)
    observability = "N/A"
    visibility_score = None
    try:
        if timestamp:
            hilal = Hilal(date=timestamp[:10])  # YYYY-MM-DD
            visibility_score = hilal.visibility()
            observability = "Visible" if visibility_score > 0.5 else "Marginal"
        else:
            observability = "Timestamp diperlukan (cek EXIF gambar)"
    except Exception as e:
        observability = f"Error hilalpy: {str(e)}"
    
    # Cuaca OpenWeather (ganti API_KEY)
    API_KEY = "YOUR_API_KEY_HERE"  # Daftar gratis di openweathermap.org
    weather = {"note": "Masukkan API key untuk cuaca real-time"}
    if API_KEY != "YOUR_API_KEY_HERE":
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                weather = {
                    "temp": data['main']['temp'],
                    "condition": data['weather'][0]['description'],
                    "visibility": "Good" if "clear" in data['weather'][0]['main'].lower() else "Poor"
                }
        except:
            weather = {"error": "Cuaca API gagal"}
    
    return observability, visibility_score, weather

# UI Streamlit
st.title("🌙 Deteksi Hilal Otomatis")
st.write("Upload gambar langit untuk deteksi hilal (YOLOv5 custom, mAP 0.89). Plus observabilitas & cuaca.")

# Load model
try:
    model = load_model()
    st.success("Model YOLOv5 loaded successfully!")
except Exception as e:
    st.error(f"Error load model: {e}. Pastikan file best.pt di folder models/.")
    st.stop()

# Upload file
uploaded_file = st.file_uploader("Pilih gambar (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gambar Asli", use_column_width=True)
    
    # Deteksi
    with st.spinner("Mendeteksi hilal..."):
        img_result, hilal_detections = detect_hilal(image, model)
        observability, visibility_score, weather = get_observability_and_weather(image)
    
    # Tampilkan hasil
    st.image(img_result, caption="Hasil Deteksi (BBox Hijau)", use_column_width=True)
    
    num_hilal = len(hilal_detections)
    if num_hilal > 0:
        st.success(f"✅ {num_hilal} hilal terdeteksi!")
        for _, row in hilal_detections.iterrows():
            st.write(f"- Confidence: {row['confidence']:.2f} | BBox: ({row['xmin']:.0f}, {row['ymin']:.0f}, {row['xmax']:.0f}, {row['ymax']:.0f})")
        st.write(f"**Observabilitas (hilalpy):** {observability} (Score: {visibility_score if visibility_score else 'N/A'})")
        st.write(f"**Cuaca (OpenWeather):** {weather}")
    else:
        st.warning("❌ Tidak ada hilal terdeteksi. Coba gambar dengan hilal lebih jelas.")
