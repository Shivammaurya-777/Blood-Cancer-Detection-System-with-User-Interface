"""
Loads the trained blood cell classification model (ResNet50 backbone with a
custom classification head) and exposes predict_image() for inference.

Architecture and class order must exactly match how best_model.pth was
trained, otherwise predictions will be meaningless.
"""

import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Exact class order the model was trained with
class_names = [
    'BAS', 'EBO', 'EOS', 'LYT',
    'MON', 'MYB', 'MYO', 'NGB',
    'NGS', 'OTHER', 'PMO'
]

# Recreate the exact ResNet50 architecture used during training
model = models.resnet50(pretrained=False)
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, len(class_names))
)

_model_load_error = None

try:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model = model.to(device)
    model.eval()
    print("[load_model] PyTorch model loaded successfully")

except Exception as e:
    _model_load_error = str(e)
    print(f"[load_model] ERROR loading model: {e}")
    model = None


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def predict_image(image_path_str: str):
    """
    Returns (predicted_class: str, confidence_percent: float)
    Raises an Exception if the model isn't loaded or the image can't be read.
    """
    if model is None:
        raise RuntimeError(f"Model not loaded: {_model_load_error}")

    if not os.path.exists(image_path_str):
        raise FileNotFoundError(f"Image file not found: {image_path_str}")

    img = Image.open(image_path_str).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    predicted_class = class_names[predicted.item()]
    confidence_percent = round(confidence.item() * 100, 2)

    return predicted_class, confidence_percent


def get_model_status():
    return {
        "model_loaded": model is not None,
        "error": _model_load_error,
        "classes": class_names,
    }
