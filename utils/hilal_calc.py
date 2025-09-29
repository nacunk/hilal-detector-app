from datetime import datetime
from hilalpy import Hilal

class HilalCalculator:
    def __init__(self, lat, lon, date):
        self.hilal = Hilal(lat, lon, date)
    
    def calculate_hilal(self):
        try:
            data = self.hilal.get_data()
            return {
                "elongation": data.get("elongation", 0),
                "age": data.get("moon_age", 0),
                "altitude": data.get("altitude", 0),
                "azimuth": data.get("azimuth", 0)
            }
        except Exception as e:
            print(f"Error calculating hilal data: {e}")
            return None

def classify_difficulty(conf, bbox_w, lat, lon, date):
    hilal = calculate_hilal(lat, lon, date)
    if hilal['elongasi'] > 10 and conf > 0.8 and bbox_w > 50:  # Threshold contoh
        return "Mudah Diamati"
    elif hilal['elongasi'] > 5 and conf > 0.5:
        return "Sulit Diamati"
    else:
        return "Sangat Sulit/Mustahil Diamati"