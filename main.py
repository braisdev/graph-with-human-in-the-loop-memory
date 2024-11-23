from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class State(BaseModel):
    input: str
    user_feedback: str


# Define now our nodes
def step_1(state: State) -> None:
    print("--- Step 1 ---")


def human_feedback(state: State) -> None:
    print("--- Human Feedback ---")


def step_3(state: State) -> None:
    print("--- Step 3 ---")


# Let's create the Graph Builder
builder = StateGraph(State)

# Add nodes to the Graph
builder.add_node("step_1", step_1)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_3", step_3)

# Crate edges in the Graph
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")
builder.add_edge("human_feedback", "step_3")
builder.add_edge("step_3", END)

memory = MemorySaver()

graph = builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

graph.get_graph().draw_mermaid_png(output_file_path="graph.png")







