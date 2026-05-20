from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def route_from_supervisor(state: MedicalState) -> str:
    return state.get("next", "FINISH")


def build_graph(with_checkpointer: bool = False):
    builder = StateGraph(MedicalState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        }
    )

    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    if with_checkpointer:
        memory = MemorySaver()
        return builder.compile(
            checkpointer=memory,
            interrupt_after=["diagnostic_agent"],
            interrupt_before=["physician_review"]
        )
    else:
        return builder.compile(
            interrupt_after=["diagnostic_agent"],
            interrupt_before=["physician_review"]
        )


# Studio utilise cette ligne - SANS checkpointer
medical_graph = build_graph(with_checkpointer=False)