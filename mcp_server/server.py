# server.py
# server.py - Serveur MCP simple (outil de recherche de symptômes)
# Ce serveur expose des outils médicaux que les agents peuvent utiliser

from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

app = FastAPI(title="MCP Medical Server", version="1.0.0")

# Données médicales simples (dans un vrai projet, utilise une vraie BDD)
SYMPTOM_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "symptoms.json")


def load_symptoms():
    """Charge les données de symptômes depuis le fichier JSON."""
    if os.path.exists(SYMPTOM_DATA_FILE):
        with open(SYMPTOM_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


class SymptomRequest(BaseModel):
    symptom: str


@app.post("/tools/get_symptom_info")
def get_symptom_info(body: SymptomRequest):
    """
    Outil MCP : retourne des informations générales sur un symptôme.
    """
    symptoms_db = load_symptoms()
    symptom_lower = body.symptom.lower()

    # Chercher le symptôme dans la base
    for key, info in symptoms_db.items():
        if key in symptom_lower or symptom_lower in key:
            return {"symptom": body.symptom, "info": info}

    return {
        "symptom": body.symptom,
        "info": "Symptôme non trouvé dans la base. Consultez un médecin."
    }


@app.get("/tools")
def list_tools():
    """Liste tous les outils disponibles sur ce serveur MCP."""
    return {
        "tools": [
            {
                "name": "get_symptom_info",
                "description": "Retourne des informations générales sur un symptôme médical",
                "parameters": {"symptom": "string"}
            }
        ]
    }


@app.get("/")
def root():
    return {"message": "MCP Medical Server ✅"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
