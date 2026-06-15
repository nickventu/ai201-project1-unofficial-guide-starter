import gradio as gr
from retrieval import retrieve
from generation import generate_response


def chat(message: str, history: list) -> str:
    docs = retrieve(message, k=5)
    return generate_response(message, docs)


demo = gr.ChatInterface(
    fn=chat,
    title="FIU CS Professor Review Assistant",
    description=(
        "Ask questions about FIU CS professors based on student reviews. "
        "e.g. 'What do students say about Richard Whittaker's exams?'"
    ),
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
