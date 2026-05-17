## Blood Cancer Detection Model Loader"""

import tensorflow as tf
from PIL import Image
import numpy as np
import os

# Load model once with error handling
try:
    model_path = "saved_models/model_finetuned_v1.keras"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Class names for blood cell classification
class_names = [
    "BAS", "EBO", "EOS", "KSC", "LYA",
    "LYT", "MMZ", "MOB", "MON", "MYB",
    "MYO", "NGB", "NGS", "PMB", "PMO"
]

# Symptoms mapping for each class - Detailed medical descriptions
symptoms_map = {
    "BAS": """Basophil-related blood disorders may present with:
                  • Chronic fatigue and general weakness
                  • Recurrent fever episodes
                  • Skin rashes and allergic reactions
                  • Joint pain and inflammation
                  • Digestive issues including abdominal pain
                  • Headaches and dizziness
                  • Increased susceptibility to infections
                  • Abnormal bleeding or bruising tendencies
                  • Consult a hematologist for proper diagnosis and treatment""",

    "EBO": """Eosinophil-related conditions typically show:
                  • Severe allergic reactions and anaphylaxis
                  • Asthma attacks and breathing difficulties
                  • Chronic sinus infections and nasal congestion
                  • Skin conditions like eczema and dermatitis
                  • Gastrointestinal symptoms including nausea and diarrhea
                  • Joint swelling and arthritic pain
                  • Fever and night sweats
                  • Fatigue and general malaise
                  • Requires specialized allergy and hematology evaluation""",

    "EOS": """Eosinophil disorders may manifest as:
                  • Persistent allergic reactions
                  • Asthma and respiratory complications
                  • Chronic inflammatory conditions
                  • Skin eruptions and itching
                  • Gastrointestinal disturbances
                  • Joint inflammation and pain
                  • Systemic symptoms like fever
                  • Increased infection risk
                  • Needs comprehensive medical assessment""",

    "KSC": """KSC (likely referring to abnormal cell types) symptoms include:
                  • Unusual bleeding from gums or nose
                  • Easy bruising and hematoma formation
                  • Prolonged bleeding from minor cuts
                  • Petechiae (small red spots on skin)
                  • Fatigue and weakness
                  • Shortness of breath
                  • Pale skin and anemia signs
                  • Bone pain and tenderness
                  • Requires immediate hematological evaluation""",

    "LYA": """Lymphocyte abnormalities may present with:
                  • Frequent bacterial and viral infections
                  • Swollen lymph nodes in neck, armpits, and groin
                  • Persistent fever and night sweats
                  • Unexplained weight loss
                  • Fatigue and general weakness
                  • Skin rashes and itching
                  • Enlarged spleen or liver
                  • Joint pain and swelling
                  • Needs thorough immunological assessment""",

    "LYT": """Lymphocyte disorders typically show:
                  • Recurrent infections of various types
                  • Lymphadenopathy (swollen lymph nodes)
                  • Constitutional symptoms like fever and sweats
                  • Significant weight loss
                  • Chronic fatigue syndrome
                  • Autoimmune manifestations
                  • Organomegaly (enlarged organs)
                  • Arthralgia (joint pain)
                  • Requires specialized hematology consultation""",

    "MMZ": """Monocyte-related conditions may exhibit:
                  • Persistent low-grade fever
                  • Extreme fatigue and lethargy
                  • Unintended weight loss
                  • Night sweats
                  • Bone pain and tenderness
                  • Frequent infections
                  • Easy bruising
                  • Shortness of breath
                  • Needs comprehensive blood work evaluation""",

    "MOB": """Monocyte disorders can present with:
                  • Chronic fever patterns
                  • Severe fatigue and weakness
                  • Significant weight loss
                  • Profuse night sweats
                  • Bone marrow suppression symptoms
                  • Increased infection susceptibility
                  • Bleeding tendencies
                  • Respiratory symptoms
                  • Requires urgent hematological investigation""",

    "MON": """Monocyte abnormalities typically show:
                  • Systemic inflammatory symptoms
                  • Fever of unknown origin
                  • Profound fatigue
                  • Weight loss
                  • Night sweats
                  • Bone pain
                  • Infection vulnerability
                  • Bleeding disorders
                  • Needs immediate medical attention""",

    "MYB": """Myeloblast-related disorders present with:
                  • Severe anemia symptoms (pallor, weakness)
                  • Increased infection risk
                  • Bleeding tendencies
                  • Fatigue and shortness of breath
                  • Bone pain and tenderness
                  • Fever and night sweats
                  • Weight loss
                  • Easy bruising
                  • Requires emergency hematology care""",

    "MYO": """Myelocyte disorders may manifest as:
                  • Progressive anemia
                  • Recurrent infections
                  • Abnormal bleeding
                  • Chronic fatigue
                  • Dyspnea (difficulty breathing)
                  • Bone marrow failure symptoms
                  • Fever episodes
                  • Weight loss
                  • Needs specialized medical evaluation""",

    "NGB": """Neutrophil disorders typically show:
                  • Frequent bacterial infections
                  • Fever and sepsis
                  • Mouth ulcers and gum disease
                  • Skin infections and abscesses
                  • Respiratory tract infections
                  • Urinary tract infections
                  • Delayed wound healing
                  • Fatigue and malaise
                  • Requires immunological assessment""",

    "NGS": """Neutrophil abnormalities present with:
                  • Recurrent bacterial infections
                  • Severe sepsis episodes
                  • Oral infections and ulcers
                  • Skin abscesses and cellulitis
                  • Pneumonia and lung infections
                  • Kidney and bladder infections
                  • Poor wound healing
                  • Constitutional symptoms
                  • Needs comprehensive infection evaluation""",

    "PMB": """Promyeloblast conditions may exhibit:
                  • Severe anemia manifestations
                  • Bleeding disorders
                  • Infection susceptibility
                  • Fatigue and weakness
                  • Shortness of breath
                  • Bone pain
                  • Fever
                  • Weight loss
                  • Requires immediate oncology consultation""",

    "PMO": """Promonocyte disorders typically show:
                  • Fever and inflammatory symptoms
                  • Fatigue and weakness
                  • Weight loss
                  • Organomegaly (enlarged organs)
                  • Bone marrow dysfunction
                  • Infection risk
                  • Bleeding tendencies
                  • Respiratory symptoms
                  • Needs urgent hematological care"""
}

# Preprocess image with error handling
def preprocess_image(image_path_str):
    try:
        if not os.path.exists(image_path_str):
            raise FileNotFoundError(f"Image file not found: {image_path_str}")

        img = Image.open(image_path_str).convert("RGB")
        img = img.resize((224, 224))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    except Exception as e:
        raise Exception(f"Error preprocessing image: {e}")

# Prediction function with comprehensive error handling
def predict_image(image_path_str):
    try:
        if model is None:
            raise Exception("Model not loaded properly")

        # Preprocess the image
        img = preprocess_image(image_path_str)

        # Make prediction
        preds = model.predict(img, verbose=0)
        class_index = np.argmax(preds)
        confidence = float(np.max(preds))

        # Get predicted class and symptoms
        predicted_class = class_names[class_index]
        symptoms = symptoms_map.get(predicted_class, "Symptoms information not available for this classification")

        return predicted_class, confidence, symptoms

    except Exception as e:
        error_msg = f"Prediction failed: {str(e)}"
        print(error_msg)
        return "ERROR", 0.0, f"Unable to analyze image. {error_msg}"

# Utility function to get all available classes
def get_available_classes():
    """Return list of all blood cell classes the model can predict"""
    return class_names.copy()

# Utility function to get symptoms for a specific class
def get_symptoms_for_class(class_name):
    """Get detailed symptoms for a specific blood cell class"""
    return symptoms_map.get(class_name.upper(), "Class not found or symptoms not available")

# Utility function to validate image file
def is_valid_image(image_path_str):
    """Check if the image file exists and is a valid image format"""
    if not os.path.exists(image_path_str):
        return False, "File does not exist"

    try:
        with Image.open(image_path_str) as img:
            img.verify()
        return True, "Valid image"
    except Exception as e:
        return False, f"Invalid image file: {e}"

# Model information
def get_model_info():
    """Get information about the loaded model"""
    info = {
        "model_loaded": model is not None,
        "num_classes": len(class_names),
        "classes": class_names,
        "input_shape": "(224, 224, 3)" if model else "Unknown"
    }
    return info