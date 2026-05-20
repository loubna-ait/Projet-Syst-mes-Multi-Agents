#  Système Médical Multi-Agents - LangGraph
**Projet - Réalisé par Loubna Ait Hra**
**Projet - Pr. Mohamed YOUSSFI**

>  Ce système est un exercice académique. Il ne remplace pas une consultation médicale.

##  Objectif

Système multi-agents basé sur **LangGraph** qui simule un workflow d'orientation clinique :
1. Patient décrit son problème
2. DiagnosticAgent pose **5 questions** 
3. Synthèse clinique préliminaire + recommandation intermédiaire
4. **Médecin (Human-in-the-Loop)** valide et propose un traitement
5. ReportAgent génère le **rapport final**

## Architecture

```
project/
├── backend/
│   ├── app/
│   │   ├── graph.py          ← Graphe LangGraph principal
│   │   ├── state.py          ← État partagé (MedicalState)
│   │   ├── api.py            ← API FastAPI
│   │   ├── nodes/
│   │   │   ├── supervisor.py       ← Orchestre le workflow
│   │   │   ├── diagnostic_agent.py ← Pose les questions + synthèse
│   │   │   ├── physician_review.py ← Human-in-the-Loop
│   │   │   └── report_agent.py     ← Génère le rapport final
│   │   └── tools/
│   │       ├── care_tools.py   ← Recommandation intermédiaire
│   │       └── mcp_client.py   ← Client MCP
│   ├── langgraph.json   ← Configuration LangGraph Studio
│   └── requirements.txt
├── mcp_server/
│   ├── server.py        ← Serveur MCP (outils médicaux)
│   └── data/
│       └── symptoms.json
├── frontend/
│   └── app.py           ← Interface Streamlit
└── .env.example
```

##  Installation et Lancement

### 1. Prérequis
- Python 3.11+
- Clé API OpenAI

### 2. Installation
```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate       # Windows

# Installer les dépendances backend
pip install -r backend/requirements.txt

# Installer Streamlit pour le frontend
pip install streamlit
```

### 3. Configuration
```bash
# Copier le fichier .env
cp .env.example .env

# Éditer .env et mettre votre clé OpenAI
OPENAI_API_KEY=sk-proj-VOTRE_CLE_ICI
```

### 4. Lancer les serveurs

**Terminal 1 - Serveur MCP :**
```bash
cd mcp_server
python server.py
# → http://localhost:8001
```

**Terminal 2 - Backend FastAPI :**
```bash
cd backend
python main.py
# → http://localhost:8000
# → Docs : http://localhost:8000/docs
```

**Terminal 3 - Frontend Streamlit :**
```bash
cd frontend
streamlit run app.py
# → http://localhost:8501
```

**LangGraph Studio (optionnel) :**
```bash
cd backend
langgraph dev
```

##  Test rapide (API)

```bash
# Démarrer une consultation
curl -X POST http://localhost:8000/consultation/start \
  -H "Content-Type: application/json" \
  -d '{"patient_info": "J ai de la fièvre depuis 2 jours"}'
```

##  Workflow du graphe

```
START → Supervisor → DiagnosticAgent (x5 questions) 
      → Supervisor → PhysicianReview ← INTERRUPTION MÉDECIN
      → Supervisor → ReportAgent 
      → Supervisor → END
```
# 🏥 Système Médical Multi-Agents - LangGraph

**Projet académique - Pr. Mohamed YOUSSFI**

> ⚠️ Ce système est un exercice académique. Il ne remplace pas une consultation médicale.

## 🎯 Objectif

Système multi-agents basé sur **LangGraph** qui simule un workflow d'orientation clinique :
1. Patient décrit son problème
2. DiagnosticAgent pose **5 questions** 
3. Synthèse clinique préliminaire + recommandation intermédiaire
4. **Médecin (Human-in-the-Loop)** valide et propose un traitement
5. ReportAgent génère le **rapport final**

## 🏗️ Architecture

```
project/
├── backend/
│   ├── app/
│   │   ├── graph.py          ← Graphe LangGraph principal
│   │   ├── state.py          ← État partagé (MedicalState)
│   │   ├── api.py            ← API FastAPI
│   │   ├── nodes/
│   │   │   ├── supervisor.py       ← Orchestre le workflow
│   │   │   ├── diagnostic_agent.py ← Pose les questions + synthèse
│   │   │   ├── physician_review.py ← Human-in-the-Loop
│   │   │   └── report_agent.py     ← Génère le rapport final
│   │   └── tools/
│   │       ├── care_tools.py   ← Recommandation intermédiaire
│   │       └── mcp_client.py   ← Client MCP
│   ├── langgraph.json   ← Configuration LangGraph Studio
│   └── requirements.txt
├── mcp_server/
│   ├── server.py        ← Serveur MCP (outils médicaux)
│   └── data/
│       └── symptoms.json
├── frontend/
│   └── app.py           ← Interface Streamlit
└── .env.example
```

## 🚀 Installation et Lancement

### 1. Prérequis
- Python 3.11+
- Clé API OpenAI

### 2. Installation
```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate       # Windows

# Installer les dépendances backend
pip install -r backend/requirements.txt

# Installer Streamlit pour le frontend
pip install streamlit
```

### 3. Configuration
```bash
# Copier le fichier .env
cp .env.example .env

# Éditer .env et mettre votre clé OpenAI
OPENAI_API_KEY=sk-proj-VOTRE_CLE_ICI
```

### 4. Lancer les serveurs

**Terminal 1 - Serveur MCP :**
```bash
cd mcp_server
python server.py
# → http://localhost:8001
```

**Terminal 2 - Backend FastAPI :**
```bash
cd backend
python main.py
# → http://localhost:8000
# → Docs : http://localhost:8000/docs
```

**Terminal 3 - Frontend Streamlit :**
```bash
cd frontend
streamlit run app.py
# → http://localhost:8501
```

**LangGraph Studio (optionnel) :**
```bash
cd backend
langgraph dev
```

## 🧪 Test rapide (API)

```bash
# Démarrer une consultation
curl -X POST http://localhost:8000/consultation/start \
  -H "Content-Type: application/json" \
  -d '{"patient_info": "J ai de la fièvre depuis 2 jours"}'
```

## 📊 Workflow du graphe

```
START → Supervisor → DiagnosticAgent (x5 questions) 
      → Supervisor → PhysicianReview ← INTERRUPTION MÉDECIN
      → Supervisor → ReportAgent 
      → Supervisor → END
```

## 🎓 Technologies utilisées
- **LangGraph** : orchestration multi-agents
- **LangChain + OpenAI** : LLM
- **FastAPI** : API REST
- **MCP** : serveur d'outils
- **Streamlit** : frontend

## 📸 Démonstration (LangGraph Studio)

Voici un aperçu de l'exécution du workflow dans **LangGraph Studio** :

### 1. Collecte des symptômes (Diagnostic Agent)
![Collecte des symptômes](images/langgraph_1.png)
*L'agent diagnostique interagit avec le patient pour recueillir les informations nécessaires (symptômes, durée, antécédents, traitements en cours).*

### 2. Synthèse et recommandation intermédiaire
![Synthèse Diagnostique](images/langgraph_2.png)
*Une fois les informations collectées, l'agent génère un résumé diagnostique et propose des recommandations de soins intermédiaires (interim_care).*

### 3. Validation Médicale (Human-in-the-Loop)
![Validation Médecin](images/langgraph_3.png)
*Le workflow s'interrompt (physician_review) pour permettre à un médecin d'examiner le dossier et de saisir sa décision de traitement (ex: "Repos trois jours").*

### 4. Rapport Final (Report Agent)
![Rapport Final](images/langgraph_4.png)
*Le Report Agent compile toutes les données (synthèse de l'agent diagnostique et avis du médecin humain) pour générer le Rapport Clinique Final structuré.*

## Technologies utilisées
- **LangGraph** : orchestration multi-agents
- **LangChain + OpenAI** : LLM
- **FastAPI** : API REST
- **MCP** : serveur d'outils
- **Streamlit** : frontend
