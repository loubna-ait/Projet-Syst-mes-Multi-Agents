# patient_tools.py - Outils pour les questions patient (via tool LangChain)

from langchain_core.tools import tool

QUESTIONS = [
    "Quels sont vos symptômes principaux ?",
    "Depuis combien de temps avez-vous ces symptômes ?",
    "Avez-vous de la fièvre ? Si oui, quelle température ?",
    "Avez-vous des maladies chroniques ou des allergies connues ?",
    "Prenez-vous des médicaments actuellement ?"
]


@tool
def ask_patient(question_index: int) -> str:
    """
    Retourne la question médicale correspondant à l'index donné (0 à 4).
    Utilisé par le DiagnosticAgent pour poser les 5 questions au patient.
    """
    if 0 <= question_index < len(QUESTIONS):
        return QUESTIONS[question_index]
    return "Toutes les questions ont été posées."
