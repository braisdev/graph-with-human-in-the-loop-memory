from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import dotenv

load_dotenv()


class State(BaseModel):
    input: str
    user_feedback: str = Field(default='')


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

# In memorySaver
memory = MemorySaver()

# sqlite memorySaver
conn = sqlite3.connect(database="checkpoints.sqlite", check_same_thread=False)
sqlite_memory = SqliteSaver(conn)

graph = builder.compile(checkpointer=sqlite_memory, interrupt_before=["human_feedback"])

graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

if __name__ == "__main__":
    # the thread_id is like a conversation_id or session_id
    # helps us to differentiate runs of our graph
    thread = {"configurable": {"thread_id": 2}}

    initial_input = {"input": "hello world"}

    for event in graph.stream(initial_input, thread, stream_mode="values"):
        print(event)

    print(graph.get_state(thread).next)

    user_input = input("Tell me how you want to update the state: ")

    graph.update_state(thread, values={"user_feedback": user_input}, as_node="human_feedback")

    print("--- State after update ---")
    print(graph.get_state(thread))

    for event in graph.stream(None, thread, stream_mode="values"):
        print(event)
