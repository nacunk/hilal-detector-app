import yolov5
import torch

class HilalDetector:
    def __init__(self, model_path='yolov5s.pt'):
        self.model = yolov5.load(model_path)
        
    def detect(self, image):
        results = self.model(image)
        return results