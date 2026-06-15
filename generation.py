from typing import List
import anthropic
from models import Document

_client = anthropic.Anthropic()

_SYSTEM_PROMPT = (
    "You are a TA assistant for FIU CS students. Answer questions using only the "
    "provided student reviews. Do not use outside knowledge. If the reviews don't "
    "contain enough information to answer, say so.\n\n"
    "Each review below is prefixed with [Professor Name | rating: X]. "
    "The name in the prefix is the PROFESSOR being reviewed — not the student who wrote the review. "
    "The review text is always written BY a student ABOUT that professor.\n\n"
    "Given these reviews:\n{context}\n\n"
    "Answer the following question: {query}\n"
    "Cite ratings where relevant. At the end of your response, list the sources you "
    "drew from as:\n"
    "Sources: [professor_name, rating: X], [professor_name, rating: X], ..."
)


def _format_context(docs: List[Document]) -> str:
    lines = []
    for doc in docs:
        rating = doc["rating"]
        rating_str = "N/A" if rating == 0.0 else str(rating)
        prefix = f"[{doc['professor_name']} | rating: {rating_str}]"
        lines.append(f"{prefix} {doc['review_text']}")
    return "\n\n".join(lines)


def generate_response(query: str, context_docs: List[Document]) -> str:
    context = _format_context(context_docs)
    prompt = _SYSTEM_PROMPT.format(context=context, query=query)

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
