import streamlit as st
import torch
from PIL import Image
import cv2
from utils.detection import HilalDetector
from utils.hilal_calc import HilalCalculator
from utils.weather_api import get_weather

# Initialize detector
detector = HilalDetector()

st.title("Detektor Hilal/Bulan untuk Observasi")

     # Sidebar untuk input
st.sidebar.header("Input Lokasi")
lat = st.sidebar.number_input("Latitude", value=0.0)
lon = st.sidebar.number_input("Longitude", value=0.0)
date = st.sidebar.date_input("Tanggal Observasi")

     # Upload file
uploaded_file = st.file_uploader("Upload Gambar/Video Hilal", type=['jpg', 'png', 'mp4'])

if uploaded_file is not None:
    if uploaded_file.type.startswith('image/'):
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Asli")
        
        # Use the detector
        results = detector.detect(image)
        st.image(results.render()[0], caption="Deteksi Hilal")

             # Ekstrak metadata (GPS, timestamp)
        from PIL.ExifTags import TAGS
        exif = image._getexif()
        if exif:
            gps_info = {TAGS.get(tag): value for tag, value in exif.items() if TAGS.get(tag) == 'GPSInfo'}
            if gps_info:
                st.write(f"Metadata GPS: {gps_info}")  # Gunakan ini jika ada, fallback ke input manual

             # Klasifikasi kesulitan (contoh sederhana berdasarkan confidence dan ukuran)
        confidence = results.xyxy[0][0][4] if results.xyxy[0] else 0
        bbox_width = results.xyxy[0][0][2] - results.xyxy[0][0][0] if results.xyxy[0] else 0
        difficulty = classify_difficulty(confidence, bbox_width, lat, lon, date)  # Integrasi hilalpy & cuaca
        st.write(f"Kesulitan Observasi: {difficulty}")

    elif uploaded_file.type.startswith('video/'):
             # Handle video: Gunakan OpenCV untuk frame-by-frame deteksi
        video = cv2.VideoCapture(uploaded_file)
             # Loop deteksi per frame, tampilkan hasil
        st.video(video)

     # Fitur Cuaca
if lat and lon:
    weather = get_weather(lat, lon, api_key="YOUR_OPENWEATHER_API_KEY")
    st.subheader("Info Cuaca")
    st.write(f"Suhu: {weather['temp']}°C, Kelembaban: {weather['humidity']}%, Kondisi: {weather['description']}")

     # Data Historis Hilal
if st.button("Tampilkan Data Historis Hilal"):
    calculator = HilalCalculator(lat, lon, date)
    hilal_data = calculator.calculate_hilal()
    st.write(hilal_data)
