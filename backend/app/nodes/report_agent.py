# report_agent.py
# report_agent.py - Génère le rapport final structuré

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from app.state import MedicalState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def report_agent_node(state: MedicalState) -> MedicalState:
    """
    Le ReportAgent prend toutes les informations collectées
    et génère un rapport final structuré.
    """
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")
    physician_treatment = state.get("physician_treatment", "")

    print("[ReportAgent] Génération du rapport final...")

    prompt = f"""
    Tu es un assistant médical académique. Génère un rapport clinique structuré.
    
    SYNTHÈSE CLINIQUE PRÉLIMINAIRE :
    {diagnostic_summary}
    
    RECOMMANDATION INTERMÉDIAIRE :
    {interim_care}
    
    TRAITEMENT PROPOSÉ PAR LE MÉDECIN :
    {physician_treatment}
    
    Génère un rapport final avec ces sections :
    1. Résumé du cas
    2. Synthèse clinique
    3. Recommandations
    4. Traitement prescrit
    5. Avertissement légal
    
    IMPORTANT : Termine TOUJOURS par : 
    "⚠️ Ce système ne remplace pas une consultation médicale."
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    final_report = response.content

    print(f"[ReportAgent] Rapport généré ({len(final_report)} caractères)")

    return {
        "final_report": final_report,
        "messages": [AIMessage(content=final_report)]
    }
