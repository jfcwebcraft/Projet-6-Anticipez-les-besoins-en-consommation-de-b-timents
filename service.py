# API de serving BentoML pour la prédiction de consommation d'énergie

import bentoml
import numpy as np
import pandas as pd
import json
import joblib
from pathlib import Path

from validation import BuildingInput, validate_input


MODEL_PATH = Path(__file__).parent / "model" / "best_model.joblib"
FEATURES_PATH = Path(__file__).parent / "model" / "feature_names.json"


def load_model_and_features():
    model = joblib.load(MODEL_PATH)
    with open(FEATURES_PATH, "r", encoding="utf-8") as f:
        feature_names = json.load(f)
    return model, feature_names


model_pipeline, feature_names = load_model_and_features()

# Correspondance pour le regroupement thématique des usages principaux
PROPERTY_CATEGORY_MAPPING = {
    "Small- and Mid-Sized Office": "Office",
    "Large Office": "Office",
    "Medical Office": "Office",
    "Office": "Office",
    "K-12 School": "Education",
    "University": "Education",
    "Retail Store": "Retail & Food",
    "Supermarket / Grocery Store": "Retail & Food",
    "Restaurant": "Retail & Food",
    "Warehouse": "Industrial & Storage",
    "Distribution Center": "Industrial & Storage",
    "Refrigerated Warehouse": "Industrial & Storage",
    "Self-Storage Facility": "Industrial & Storage",
    "Laboratory": "Industrial & Storage",
    "Hotel": "Hospitality",
    "Hospital": "Healthcare",
    "Worship Facility": "Public / Institutional",
    "Mixed Use Property": "Mixed Use",
    "Other": "Other",
}

# Liste des catégories d'usage pour l'encodage One-Hot (Education sert de référence)
ALL_CATEGORIES = [
    "Healthcare", "Hospitality", "Industrial & Storage",
    "Mixed Use", "Office", "Other",
    "Public / Institutional", "Retail & Food",
]


def prepare_features(data: BuildingInput) -> pd.DataFrame:
    """Reproduit le feature engineering du notebook."""
    building_age = 2016 - data.year_built
    surface_par_etage = (
        data.property_gfa_total / data.number_of_floors
        if data.number_of_floors and data.number_of_floors > 0
        else 0.0
    )
    ratio_largest_use = (
        data.largest_property_use_type_gfa / data.property_gfa_total
        if data.property_gfa_total > 0
        else 0.0
    )

    category = PROPERTY_CATEGORY_MAPPING.get(data.primary_property_type, "Other")

    row = {
        "BuildingAge": building_age,
        "SurfaceParEtage": surface_par_etage,
        "RatioLargestUse": ratio_largest_use,
        "NumberofBuildings": data.number_of_buildings,
        "NumberofFloors": data.number_of_floors,
        "PropertyGFATotal": data.property_gfa_total,
        "PropertyGFAParking": data.property_gfa_parking,
        "PropertyGFABuilding(s)": data.property_gfa_building,
        "LargestPropertyUseTypeGFA": data.largest_property_use_type_gfa,
        "SecondLargestPropertyUseTypeGFA": data.second_largest_property_use_type_gfa,
    }

    # Encodage One-Hot
    for cat in ALL_CATEGORIES:
        col_name = f"PropertyCategory_{cat}"
        row[col_name] = 1 if category == cat else 0

    df = pd.DataFrame([row])
    df = df[feature_names]
    return df


@bentoml.service(
    name="energy_prediction_service",
    traffic={"timeout": 60},
)
class EnergyPredictionService:

    @bentoml.api()
    def predict(self, input_data: BuildingInput) -> dict:
        """Inférence de la consommation énergétique."""
        validate_input(input_data)
        X = prepare_features(input_data)

        log_pred = model_pipeline.predict(X)[0]
        pred_kbtu = float(np.expm1(log_pred))

        return {
            "predicted_energy_kbtu": round(pred_kbtu, 2),
            "predicted_log1p_energy": round(float(log_pred), 4),
            "unit": "kBtu",
            "input_summary": {
                "property_type": input_data.primary_property_type,
                "year_built": input_data.year_built,
                "total_area_sqft": input_data.property_gfa_total,
            },
        }

    @bentoml.api()
    def healthcheck(self) -> dict:
        return {"status": "ok", "model_features": len(feature_names)}


