from dotenv import load_dotenv
load_dotenv()

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph

memory = MemorySaver()

#medical_graph = build_graph().compile(checkpointer=memory)
medical_graph = build_graph()



app = FastAPI(title="Système Médical Multi-Agents", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class StartConsultation(BaseModel):
    patient_info: str

class ResumeConsultation(BaseModel):
    thread_id: str
    user_message: str
    is_physician: bool = False


@app.post("/sessions/start")
def start_session():
    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id, "message": "Session créée."}


@app.post("/consultation/start")
def start_consultation(body: StartConsultation):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content=body.patient_info)],
        "question_count": 0,
        "patient_answers": []
    }

    # Lance le graphe, qui va probablement s'interrompre dans le DiagnosticAgent (Phase 1)
    medical_graph.invoke(initial_state, config=config)

    state = medical_graph.get_state(config)
    
    # Pour récupérer la question posée, on peut lire les interrupts en cours ou le message d'état
    # DiagnosticAgent met à jour le state "messages" AVANT l'interrupt ou pendant le retour
    # En fait, notre implémentation met le payload de l'interruption
    question = "Pas de question"
    question_number = 1
    
    if state.tasks and state.tasks[0].interrupts:
        interrupt_val = state.tasks[0].interrupts[0].value
        if isinstance(interrupt_val, dict) and "message" in interrupt_val:
            question = interrupt_val["message"]
            question_number = interrupt_val.get("question_number", 1)

    return {
        "thread_id": thread_id,
        "question": question,
        "question_number": question_number,
        "status": "asking_questions"
    }


@app.post("/consultation/resume")
def resume_consultation(body: ResumeConsultation):
    config = {"configurable": {"thread_id": body.thread_id}}

    current_state = medical_graph.get_state(config)
    if not current_state:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    if body.is_physician:
        # Le médecin valide la synthèse et propose un traitement
        # Utilisation de Command(resume=...) pour relancer le graphe depuis l'interruption
        medical_graph.invoke(Command(resume={"physician_treatment": body.user_message}), config=config)

        saved = medical_graph.get_state(config)
        return {
            "status": "report_generated",
            "final_report": saved.values.get("final_report", ""),
            "thread_id": body.thread_id
        }

    else:
        # Le patient répond à une question
        # On relance le graphe en passant la réponse dans le resume payload
        medical_graph.invoke(Command(resume={"answer": body.user_message}), config=config)

        # Lire l'état APRÈS l'invocation (qui a probablement atteint une nouvelle interruption)
        saved = medical_graph.get_state(config)
        saved_values = saved.values
        new_count = saved_values.get("question_count", 0)

        # Vérifier si on est en attente du médecin (interruption dans physician_review)
        if saved.tasks and saved.tasks[0].name == "physician_review":
            return {
                "status": "waiting_physician",
                "diagnostic_summary": saved_values.get("diagnostic_summary", ""),
                "interim_care": saved_values.get("interim_care", ""),
                "thread_id": body.thread_id,
                "message": "Le médecin doit valider la synthèse"
            }

        # Sinon on est toujours en train de poser des questions
        question = ""
        question_number = new_count + 1
        if saved.tasks and saved.tasks[0].interrupts:
            interrupt_val = saved.tasks[0].interrupts[0].value
            if isinstance(interrupt_val, dict) and "message" in interrupt_val:
                question = interrupt_val["message"]
                question_number = interrupt_val.get("question_number", question_number)

        return {
            "status": "asking_questions",
            "question": question,
            "question_number": question_number,
            "thread_id": body.thread_id
        }


@app.get("/consultation/{thread_id}")
def get_consultation(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = medical_graph.get_state(config)
    if not state:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    return {"thread_id": thread_id, "state": state.values}


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = medical_graph.get_state(config)
    if not state:
        raise HTTPException(status_code=404, detail="Consultation non trouvée")
    final_report = state.values.get("final_report", "")
    if not final_report:
        raise HTTPException(status_code=400, detail="Rapport pas encore généré")
    return {"thread_id": thread_id, "final_report": final_report}


@app.get("/")
def root():
    return {"message": "API Médicale Multi-Agents - LangGraph ✅"}