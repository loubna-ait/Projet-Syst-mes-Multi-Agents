# state.py - L'état partagé entre tous les agents

from typing import Annotated
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]   # Historique des messages
    next: Literal[                              # Prochain noeud à exécuter
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH"
    ]
    question_count: int         # Nombre de questions posées (max 5)
    patient_answers: list       # Liste des réponses du patient
    diagnostic_summary: str     # Synthèse clinique préliminaire
    interim_care: str           # Recommandation intermédiaire
    physician_treatment: str    # Traitement proposé par le médecin
    final_report: str           # Rapport final
