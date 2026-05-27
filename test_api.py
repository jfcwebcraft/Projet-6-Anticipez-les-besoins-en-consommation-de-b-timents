# Script de tests unitaires locaux pour l'API de prédiction de consommation
# Lancer le service avant : bentoml serve service:EnergyPredictionService

import requests
import json

BASE_URL = "http://localhost:3000"


def test_predict_valid():
    payload = {
        "primary_property_type": "Large Office",
        "year_built": 1990,
        "number_of_buildings": 1,
        "number_of_floors": 15,
        "property_gfa_total": 200000,
        "property_gfa_parking": 30000,
        "property_gfa_building": 170000,
        "largest_property_use_type_gfa": 170000,
        "second_largest_property_use_type_gfa": 0,
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    print(f"[VALID] Status: {resp.status_code}")
    print(f"  Response: {json.dumps(resp.json(), indent=2)}")
    assert resp.status_code == 200
    return resp.json()


def test_predict_hotel():
    payload = {
        "primary_property_type": "Hotel",
        "year_built": 2005,
        "number_of_buildings": 1,
        "number_of_floors": 8,
        "property_gfa_total": 80000,
        "property_gfa_parking": 10000,
        "property_gfa_building": 70000,
        "largest_property_use_type_gfa": 65000,
        "second_largest_property_use_type_gfa": 5000,
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    print(f"[HOTEL] Status: {resp.status_code}")
    print(f"  Response: {json.dumps(resp.json(), indent=2)}")
    return resp.json()


def test_invalid_surface():
    # Validation de la cohérence physique (surface bâtiment > surface totale)
    payload = {
        "primary_property_type": "Warehouse",
        "year_built": 2000,
        "number_of_buildings": 1,
        "number_of_floors": 2,
        "property_gfa_total": 10000,
        "property_gfa_parking": 0,
        "property_gfa_building": 50000,  # > total => erreur attendue
        "largest_property_use_type_gfa": 10000,
        "second_largest_property_use_type_gfa": 0,
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    print(f"[INVALID SURFACE] Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")
    assert resp.status_code in (400, 422), f"Erreur attendue (4xx), reçu {resp.status_code}"


def test_invalid_type():
    # Validation de la cohérence de l'usage (usage résidentiel exclu)
    payload = {
        "primary_property_type": "Maison individuelle",
        "year_built": 2000,
        "number_of_buildings": 1,
        "number_of_floors": 2,
        "property_gfa_total": 10000,
        "property_gfa_parking": 0,
        "property_gfa_building": 10000,
        "largest_property_use_type_gfa": 10000,
        "second_largest_property_use_type_gfa": 0,
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    print(f"[INVALID TYPE] Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")
    assert resp.status_code in (400, 422), f"Erreur attendue (4xx), reçu {resp.status_code}"



def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck", timeout=10)
    print(f"[HEALTHCHECK] Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")


if __name__ == "__main__":
    print("--- Tests API ---\n")
    try:
        test_healthcheck()
        print()
        test_predict_valid()
        print()
        test_predict_hotel()
        print()
        test_invalid_surface()
        print()
        test_invalid_type()
    except requests.exceptions.ConnectionError:
        print("ERREUR : Le service n'est pas démarré.")
        print("Lancez d'abord : bentoml serve service:EnergyPredictionService")
