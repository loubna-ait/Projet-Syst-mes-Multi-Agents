# physician_review.py - Human-in-the-Loop : le médecin valide la synthèse

from langchain_core.messages import AIMessage
from langgraph.types import interrupt
from app.state import MedicalState


def physician_review_node(state: MedicalState) -> MedicalState:
    """
    Ce noeud est une interruption Human-in-the-Loop.
    LangGraph va s'arrêter ici et attendre l'input du médecin.
    Le médecin reçoit la synthèse et propose un traitement.
    """
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")

    print("[PhysicianReview] En attente de la validation du médecin...")
    
    # Message destiné au studio
    message_content = f"""
    ⚕️ REVUE MÉDECIN REQUISE
    
    Synthèse clinique préliminaire :
    {diagnostic_summary}
    
    Recommandation intermédiaire :
    {interim_care}
    
    → Le médecin doit proposer un traitement ou une conduite à tenir.
    """
    
    # Si le traitement a déjà été injecté via API, on passe à la suite
    # Mais dans LangGraph Studio, on va utiliser l'interruption
    if state.get("physician_treatment"):
        print("[PhysicianReview] Traitement reçu, passage au noeud suivant.")
        return state

    # Utilisation du nouveau mécanisme d'interruption de LangGraph
    response = interrupt({
        "message": "Revue médecin requise",
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care
    })
    
    # Quand on reprend (resume) après l'interruption, la réponse contient le traitement
    if response and isinstance(response, str):
        return {
            "physician_treatment": response,
            "messages": [AIMessage(content=f"Médecin : {response}")]
        }
    elif response and isinstance(response, dict) and "physician_treatment" in response:
        return {
            "physician_treatment": response["physician_treatment"],
            "messages": [AIMessage(content=f"Médecin : {response['physician_treatment']}")]
        }
        
    # Fallback pour un retour vide
    return {
        "messages": [AIMessage(content=message_content)]
    }
