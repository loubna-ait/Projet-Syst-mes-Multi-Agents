# mcp_client.py
# mcp_client.py - Client MCP simple pour appeler les outils du mcp_server

import httpx
from langchain_core.tools import tool

MCP_SERVER_URL = "http://localhost:8001"  # L'adresse du serveur MCP


def call_mcp_tool(tool_name: str, params: dict) -> dict:
    """
    Appelle un outil sur le serveur MCP.
    Simple requête HTTP POST.
    """
    try:
        response = httpx.post(
            f"{MCP_SERVER_URL}/tools/{tool_name}",
            json=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[MCP Client] Erreur : {e}")
        return {"error": str(e)}


@tool
def get_medical_info(symptom: str) -> str:
    """
    Utilise le serveur MCP pour chercher des infos sur un symptôme médical spécifique.
    À utiliser lors de l'analyse d'un cas patient pour obtenir des informations générales.
    """
    result = call_mcp_tool("get_symptom_info", {"symptom": symptom})
    return result.get("info", "Aucune information disponible.")
