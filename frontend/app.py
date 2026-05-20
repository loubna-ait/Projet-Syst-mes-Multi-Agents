# app.py - Frontend Streamlit simple et propre
# Pour lancer : streamlit run frontend/app.py

import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Diagnostic Médical - Multi-Agents",
    page_icon="⚕️",
    layout="centered"
)

st.title("⚕️ Système de Diagnostic Multi-Agents")
st.markdown("*Projet loubna ait-hra*")
st.divider()

# --- Initialisation de la session Streamlit ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "status" not in st.session_state:
    st.session_state.status = "start"  # start | asking | physician | done
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "question_number" not in st.session_state:
    st.session_state.question_number = 1
if "diagnostic_summary" not in st.session_state:
    st.session_state.diagnostic_summary = ""
if "interim_care" not in st.session_state:
    st.session_state.interim_care = ""
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ===== ÉCRAN 1 : Démarrage =====
if st.session_state.status == "start":
    st.subheader("📋 Décrire votre cas")
    patient_info = st.text_area(
        "Décrivez brièvement votre problème de santé :",
        placeholder="Ex: J'ai de la fièvre depuis 2 jours et une toux sèche...",
        height=100
    )

    if st.button("🚀 Démarrer la consultation", type="primary"):
        if not patient_info.strip():
            st.error("Veuillez décrire votre problème.")
        else:
            with st.spinner("Connexion au système..."):
                try:
                    r = httpx.post(
                        f"{API_URL}/consultation/start",
                        json={"patient_info": patient_info},
                        timeout=120
                    )
                    data = r.json()

                    st.session_state.thread_id = data["thread_id"]
                    st.session_state.current_question = data["question"]
                    st.session_state.question_number = data["question_number"]
                    st.session_state.status = "asking"
                    st.session_state.chat_history.append(
                        ("patient", patient_info)
                    )
                    st.session_state.chat_history.append(
                        ("agent", data["question"])
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur de connexion à l'API : {e}")


# ===== ÉCRAN 2 : Questions/Réponses =====
elif st.session_state.status == "asking":
    st.subheader(f"💬 Question {st.session_state.question_number}/5")

    # Afficher l'historique du chat
    for role, msg in st.session_state.chat_history:
        if role == "patient":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    # Question actuelle
    st.info(f"🤖 **Agent :** {st.session_state.current_question}")

    # Réponse du patient
    answer = st.text_input(
        "Votre réponse :",
        key=f"q_{st.session_state.question_number}"
    )

    if st.button("Envoyer ➡️", type="primary"):
        if not answer.strip():
            st.error("Veuillez entrer une réponse.")
        else:
            with st.spinner("Traitement..."):
                try:
                    r = httpx.post(
                        f"{API_URL}/consultation/resume",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "user_message": answer,
                            "is_physician": False
                        },
                        timeout=120
                    )
                    data = r.json()

                    st.session_state.chat_history.append(("patient", answer))

                    if data["status"] == "asking_questions":
                        st.session_state.current_question = data["question"]
                        st.session_state.question_number = data["question_number"]
                        st.session_state.chat_history.append(
                            ("agent", data["question"])
                        )

                    elif data["status"] == "waiting_physician":
                        st.session_state.diagnostic_summary = data.get("diagnostic_summary", "")
                        st.session_state.interim_care = data.get("interim_care", "")
                        st.session_state.status = "physician"

                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")


# ===== ÉCRAN 3 : Revue du médecin =====
elif st.session_state.status == "physician":
    st.subheader("👨‍⚕️ Revue du Médecin Traitant")
    st.success("✅ Les questions patient sont terminées. En attente du médecin.")

    st.markdown("### 📊 Synthèse Clinique Préliminaire")
    st.info(st.session_state.diagnostic_summary)

    st.markdown("### 💊 Recommandation Intermédiaire")
    st.warning(st.session_state.interim_care)

    st.divider()
    st.markdown("### ✍️ Traitement / Conduite à tenir (Médecin)")
    treatment = st.text_area(
        "Le médecin propose :",
        placeholder="Ex: Repos 3 jours, paracétamol 1g toutes les 8h, hydratation importante...",
        height=120
    )

    if st.button("✅ Valider et Générer le Rapport Final", type="primary"):
        if not treatment.strip():
            st.error("Veuillez entrer un traitement.")
        else:
            with st.spinner("Génération du rapport final..."):
                try:
                    r = httpx.post(
                        f"{API_URL}/consultation/resume",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "user_message": treatment,
                            "is_physician": True
                        },
                        timeout=60
                    )
                    data = r.json()
                    st.session_state.final_report = data.get("final_report", "")
                    st.session_state.status = "done"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")


# ===== ÉCRAN 4 : Rapport Final =====
elif st.session_state.status == "done":
    st.subheader("📄 Rapport Final de Consultation")
    st.success("✅ Consultation terminée !")

    st.markdown("---")
    st.markdown(st.session_state.final_report)
    st.markdown("---")

    st.warning("⚠️ Ce système ne remplace pas une consultation médicale.")

    if st.button("🔄 Nouvelle Consultation"):
        # Reset de la session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
