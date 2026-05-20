# care_tools.py
# care_tools.py - Outils de recommandation intermédiaire

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def recommend_interim_care_tool(diagnostic_summary: str) -> str:
    """
    Génère une recommandation intermédiaire prudente basée sur la synthèse.
    Ceci N'EST PAS un diagnostic. C'est une recommandation générale.
    """
    prompt = f"""
    Basé sur cette synthèse clinique préliminaire :
    {diagnostic_summary}
    
    Donne une recommandation intermédiaire TRÈS PRUDENTE et GÉNÉRALE.
    Elle peut inclure : repos, hydratation, surveillance des symptômes,
    consultation rapide si aggravation.
    
    NE donne PAS de diagnostic définitif. 2-3 phrases maximum.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


# Version simple (sans @tool) pour appel direct dans le code
def recommend_interim_care(diagnostic_summary: str) -> str:
    """Version simple pour appel direct (pas via LangChain tool)."""
    prompt = f"""
    Basé sur cette synthèse clinique préliminaire :
    {diagnostic_summary}
    
    Donne une recommandation intermédiaire TRÈS PRUDENTE et GÉNÉRALE.
    Inclure : repos, hydratation, surveillance, consultation si aggravation.
    NE PAS donner de diagnostic définitif. 2-3 phrases max.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
