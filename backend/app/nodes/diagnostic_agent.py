# diagnostic_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import interrupt
from app.state import MedicalState
from app.tools.care_tools import recommend_interim_care
from app.tools.patient_tools import ask_patient
from app.tools.mcp_client import get_medical_info

# Nous lions l'outil MCP au modèle pour la phase de synthèse
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([get_medical_info])
# LLM simple pour éviter l'appel d'outil si non nécessaire
llm_simple = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def diagnostic_agent_node(state: MedicalState) -> MedicalState:
    """
    Ce nœud gère deux phases :
    Phase 1 (< 5 réponses) : Pose la prochaine question médicale via le tool ask_patient
                             puis s'interrompt pour attendre la réponse du patient.
    Phase 2 (5 réponses)   : Génère la synthèse clinique préliminaire en utilisant MCP si besoin.
    """
    patient_answers = list(state.get("patient_answers", []))
    nb_answers = len(patient_answers)

    print(f"[DiagnosticAgent] {nb_answers}/5 réponses collectées")

    # ── Phase 2 : toutes les réponses collectées → synthèse ───────────────
    if nb_answers >= 5:
        # Si la synthèse est déjà générée, on ne fait rien (pour éviter de la refaire lors du retour de PhysicianReview)
        if state.get("diagnostic_summary"):
            return state

        print("[DiagnosticAgent] Génération de la synthèse...")

        qa_context = ""
        # On reconstitue le contexte des questions/réponses
        for i, a in enumerate(patient_answers):
            q = ask_patient.invoke({"question_index": i})
            qa_context += f"Q{i+1}: {q}\nRéponse: {a}\n\n"

        prompt = (
            "Tu es un assistant médical académique.\n"
            "Voici les réponses du patient :\n"
            f"{qa_context}\n"
            "Génère une synthèse clinique préliminaire COURTE (3-4 lignes).\n"
            "Tu peux utiliser l'outil get_medical_info si tu as besoin de vérifier un symptôme, "
            "sinon génère la synthèse directement.\n"
            "Rappelle que ceci n'est PAS un diagnostic médical définitif."
        )

        # On utilise le LLM (potentiellement avec outil)
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Si le LLM décide d'appeler l'outil (ToolCall)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                if tc["name"] == "get_medical_info":
                    mcp_result = get_medical_info.invoke(tc["args"])
                    prompt += f"\nInformation MCP obtenue : {mcp_result}\nMaintenant, génère la synthèse en tenant compte de cela."
            
            # Deuxième appel après l'outil
            response = llm_simple.invoke([HumanMessage(content=prompt)])

        summary = response.content
        interim = recommend_interim_care(summary)

        print("[DiagnosticAgent] Synthèse générée ✅")
        return {
            "diagnostic_summary": summary,
            "interim_care": interim,
            "messages": [AIMessage(content=f"✅ Synthèse clinique :\n{summary}")]
        }

    # ── Phase 1 : poser la prochaine question ────────────────────────────────
    next_index = nb_answers  # 0 → Q1, 1 → Q2, ..., 4 → Q5
    
    # Utilisation du tool LangChain pour récupérer la question
    current_question = ask_patient.invoke({"question_index": next_index})
    
    print(f"[DiagnosticAgent] Question {next_index + 1}/5 : {current_question}")

    # On demande au graphe de s'interrompre pour obtenir la réponse de l'utilisateur
    answer = interrupt({
        "message": current_question,
        "question_number": next_index + 1
    })

    # Quand le graphe reprend (via Command(resume=answer)), on traite la réponse
    if answer and isinstance(answer, str):
        patient_answers.append(answer)
        return {
            "question_count": next_index + 1,
            "patient_answers": patient_answers,
            "messages": [
                AIMessage(content=f"Question {next_index + 1}/5 : {current_question}"),
                HumanMessage(content=answer)
            ]
        }
    
    # Fallback si repris sans string (ex: via dict)
    if answer and isinstance(answer, dict) and "answer" in answer:
        patient_answers.append(answer["answer"])
        return {
            "question_count": next_index + 1,
            "patient_answers": patient_answers,
            "messages": [
                AIMessage(content=f"Question {next_index + 1}/5 : {current_question}"),
                HumanMessage(content=answer["answer"])
            ]
        }

    # Cas exceptionnel (reprise vide ou première exécution menant à l'interrupt)
    return {
        "messages": [AIMessage(content=f"Question {next_index + 1}/5 : {current_question}")]
    }