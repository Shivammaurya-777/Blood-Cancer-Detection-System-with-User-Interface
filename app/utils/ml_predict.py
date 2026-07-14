"""
Bridges prediction_routes.py to the real trained model in app/ml_model/.

Also classifies each predicted class as "positive" (abnormal/blast cell -
possible leukemia indicator) or "negative" (normal/mature cell), used for
the dashboard statistics (positive patients / negative patients).
"""

from typing import Tuple

from app.ml_model.load_model import predict_image as _predict_image
from app.ml_model.load_model import class_names, get_model_status

# Classes considered a "positive" / abnormal finding (immature / blast cells
# associated with leukemia). Everything else is treated as "negative".
#POSITIVE_CLASSES = {"MYB", "MYO", "PMO", "EBO"}

FULL_NAMES = {
    "BAS": "Basophil",
    "EBO": "Erythroblast",
    "EOS": "Eosinophil",
    "LYT": "Lymphocyte",
    "MON": "Monocyte",
    "MYB": "Myeloblast",
    "MYO": "Myelocyte",
    "NGB": "Neutrophil (Band form)",
    "NGS": "Neutrophil (Segmented)",
    "OTHER": "Other / Unclassified cell",
    "PMO": "Promyelocyte",
}

SYMPTOMS_MAP = {
    "BAS": "Basophil-related: allergic reactions, chronic inflammation, itching, fatigue, blood cell imbalance. Requires hematological monitoring.",
    "EBO": "Erythroblast abnormalities: anemia, pale skin, fatigue, dizziness, low oxygen circulation. Requires blood examination.",
    "EOS": "Eosinophil-related: allergic conditions, asthma symptoms, rashes, breathing difficulty. Requires medical investigation.",
    "LYT": "Lymphocyte abnormalities: fever, swollen lymph nodes, fatigue, frequent infections, weight loss. Requires hematological diagnosis.",
    "MON": "Monocyte-related: chronic infections, fever, fatigue, organ enlargement. Requires medical monitoring.",
    "MYB": "Myeloblast abnormalities: acute leukemia indicators, severe fatigue, bone pain, bruising, bleeding. Requires urgent medical care.",
    "MYO": "Myelocyte-related: bone marrow abnormalities, fatigue, infection susceptibility, leukemia-related indicators. Requires clinical evaluation.",
    "NGB": "Neutrophil band cell abnormalities: bacterial infections, fever, inflammation, bone marrow stress. Requires medical diagnosis.",
    "NGS": "Neutrophil segmented cell disorders: severe infections, fever, chills, weak immune response. Requires lab investigation.",
    "OTHER": "Rare/unclassified blood cell abnormalities: unusual patterns, bone marrow irregularities. Requires specialized testing.",
    "PMO": "Promyelocyte abnormalities: linked to acute promyelocytic leukemia, bleeding risk, fatigue, bone pain. Requires urgent care.",
}

MEDICINES_MAP = {
    "BAS": "General allergy/inflammation management as clinically indicated. Refer to hematologist for confirmatory workup.",
    "EBO": "Iron studies and anemia workup recommended before any treatment decision. Refer to hematologist.",
    "EOS": "Antihistamines/allergy management as clinically appropriate. Refer for eosinophilia workup if persistent.",
    "LYT": "Further lymphocyte subset analysis (flow cytometry) recommended. Refer to hematologist/oncologist.",
    "MON": "Infection workup recommended. Refer to hematologist if monocytosis persists.",
    "MYB": "Urgent referral to a hematologist/oncologist for bone marrow biopsy and acute leukemia workup.",
    "MYO": "Referral to hematologist for bone marrow evaluation recommended.",
    "NGB": "Investigate for underlying bacterial infection or bone marrow stress. Clinical correlation advised.",
    "NGS": "Investigate for underlying infection/inflammation. Clinical correlation advised.",
    "OTHER": "Specialized pathology review recommended for unclassified cell morphology.",
    "PMO": "Urgent referral to a hematologist/oncologist — promyelocyte abnormalities require prompt evaluation.",
}

DISCLAIMER = (
    "This is an AI-assisted academic project output and is NOT a certified medical "
    "diagnosis or treatment plan. All findings must be confirmed and acted upon only "
    "by a qualified hematologist/oncologist."
)


def predict(image_path: str) -> Tuple[str, float]:
    """Returns (cancer_type_code, confidence_percent). Raises on failure."""
    predicted_class, confidence = _predict_image(image_path)
    return predicted_class, confidence


def get_symptoms(cancer_type: str) -> str:
    base = SYMPTOMS_MAP.get(cancer_type, "Not available.")
    return f"{base} {DISCLAIMER}"


def get_medicines(cancer_type: str) -> str:
    base = MEDICINES_MAP.get(cancer_type, "Not available.")
    return f"{base} {DISCLAIMER}"


def get_full_name(cancer_type: str) -> str:
    return FULL_NAMES.get(cancer_type, cancer_type)


#def is_positive(cancer_type: str) -> bool:
 #  """True if this class is treated as an abnormal/positive finding."""
  # return cancer_type in POSITIVE_CLASSES
