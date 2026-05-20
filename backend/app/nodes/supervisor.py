# supervisor.py
from app.state import MedicalState

def supervisor_node(state: MedicalState) -> MedicalState:
    question_count = state.get("question_count", 0)
    patient_answers = state.get("patient_answers", [])
    diagnostic_summary = state.get("diagnostic_summary", "")
    physician_treatment = state.get("physician_treatment", "")
    final_report = state.get("final_report", "")

    print(f"[Supervisor] q_count={question_count}, answers={len(patient_answers)}, summary={bool(diagnostic_summary)}, treatment={bool(physician_treatment)}, report={bool(final_report)}")

    if final_report:
        # Étape 4 : Rapport généré → Fin
        next_step = "FINISH"
    elif physician_treatment and diagnostic_summary:
        # Étape 3 : Médecin a validé → Générer rapport
        next_step = "report_agent"
    elif diagnostic_summary:
        # Étape 2 : Synthèse prête → Revue médecin
        next_step = "physician_review"
    else:
        # Étape 1 : On délègue toujours au diagnostic_agent pour collecter les réponses ou générer la synthèse.
        # Le graphe se mettra en pause (interrupt) de lui-même dans le noeud diagnostic_agent s'il a besoin d'une réponse.
        next_step = "diagnostic_agent"

    print(f"[Supervisor] Décision : → {next_step}")
    return {"next": next_step}