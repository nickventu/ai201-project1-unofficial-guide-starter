# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

The domain is informal student reviews of FIU CS professors. While RateMyProfessors is a publicly accessible resource, this type of knowledge is still valuable because it captures student-to-student discourse that official channels do not produce. FIU's official faculty evaluations are private, aggregated, and never shared publicly. The informal, unfiltered language students use to describe teaching quality, course difficulty, and grading style represents a form of collective knowledge that exists outside institutional channels.

---

## Document Sources

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate My Professor page (Kianoosh Boroojeni)        |68 ratings, 4.3 |https://www.ratemyprofessors.com/professor/2295919 |
| 2 |Rate My Professor page (Richard Whittaker)         |354 ratings, 4.8 |https://www.ratemyprofessors.com/professor/1935348 |
| 3 |Rate My Professor page (Caryl Rahn)                |179 ratings, 2.1 |https://www.ratemyprofessors.com/professor/2044920 |
| 4 |Rate My Professor page (Patricia McDermott Wells)  |149 ratings, 3.9 |https://www.ratemyprofessors.com/professor/241078 |
| 5 |Rate My Professor page (Jill Weiss)                |354 ratings, 4.6 |https://www.ratemyprofessors.com/professor/300089 |
| 6 |r/FIU Reddit Thread (How is Computer Science?)     |2 years old, incoming student asking about current CS students' experiences in FIU|https://www.reddit.com/r/FIU/comments/1f5j4vt/how_is_computer_science/ |
| 7 |r/FIU Reddit Thread (Discrete Structures)          |5 years old, asking about professors for course Discrete Structures |https://www.reddit.com/r/FIU/comments/17rr3kg/discrete_structures/ |
| 8 |Rate My Professor page (Ahmad Waqas)               |115 ratings, 4.2 |https://www.ratemyprofessors.com/professor/2736433 |
| 9 |Rate My Professor page (Michael Robinson)          |312 ratings, 3.4 |https://www.ratemyprofessors.com/professor/1591088 |
| 10|r/FIU Reddit Thread (Help picking CS professors)   |6 years old, original post deleted |https://www.reddit.com/r/FIU/comments/jry3og/help_picking_cs_professors/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 
1 chunk per review/comment

**Overlap:** 
0

**Why these choices fit your documents:**
RateMyProfessors reviews are typically 50–200 words, and Reddit comments vary similarly, splitting at review/comment boundaries preserves meaning well. Overlap is unnecessary because reviews are independent of eachother.
In rare cases where a Reddit comment is unusually long, it may exceed typical chunk size guidelines, but this is uncommon enough in this domain that review-level chunking remains the best fit.

**Final chunk count:**
1550

---

## Embedding Model

nomic-embed-text

**Top-k:**
5-10

**Production tradeoff reflection:**
My other consideration was all-MiniLM-L6-v2 which is comparatively less heavy but for the purposes of this project that is not a problem. For this specific domain nomic-embed-text is a better choice for the following reasons:
The native prefix support is a direct match for my prefix prompting approach.
Short opinion text benefits from the higher-dimensional representation capturing subtle sentiment differences
It's built with both similarity and retrieval in mind.

---

## Grounded Generation

**System prompt grounding instruction:**
The system prompt contains two explicit constraints: "Answer questions using only the provided student reviews. Do not use outside knowledge. If the reviews don't contain enough information to answer, say so." The prompt also clarifies the data structure to prevent misattribution: "The name in the prefix is the PROFESSOR being reviewed — not the student who wrote the review. The review text is always written BY a student ABOUT that professor." This was added after early tests showed the model misidentifying professors as students when chunk text lacked clear subject identification.

**How source attribution is surfaced in the response:**
The system prompt instructs the model to append a sources list at the end of every response in the format Sources: [professor_name, rating: X], [professor_name, rating: X], .... The professor name and rating in each source entry come directly from the chunk prefix injected by _format_context(), which formats each retrieved document as [Professor Name | rating: X] review_text before passing it to the model. This means attribution is structurally tied to the retrieved chunks rather than generated from the model's own knowledge.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |What complaints do students most commonly have about FIU CS professors? |The most common complaints are perceived communication barriers, lack of responsiveness, and tough workloads. |Disorganization & Poor Communication, Unclear or Surprise Assignments, No Flexibility (No Makeups/Extra Credit), Difficult or Poorly Designed Coursework |Relevant |Accurate |
| 2 |What do students say about Caryl Rahn's grading style? |Students say Caryl Rahn's grading style is unfair and unnecessarily stressful. |Students don't comment much on Caryl Rahn's grading directly — reviews focus on workload over grading criteria, describing the class as tedious but manageable. The main warning is that the final presentation and essay are syllabus-only, with no verbal notice. |Relevant |Partially accurate |
| 3 |Is Kianoosh Boroojeni known for steep curving? |Yes, Kianoosh gives tough exams but he is known for generous curving so your grade won't suffer much. |Students confirm he curves generously — partial credit on exams, 60% passing threshold for a C, and a reputation for giving students "that extra push to pass." Reviews frame it as broad grading leniency rather than a steep curve specifically, with beginners still able to earn a B+/A-. |Relevant |Accurate |
| 4 |How do students describe the workload in COT3100(Discrete Structures) at FIU? |It can depend on professor but generally students describe COT3100 as heavy on proofs and problem sets, with weekly homework and difficult exams. |COT3100 workload: No information in the corpus — none of the retrieved reviews mention Discrete Structures or COT3100 by name. System correctly declined to answer |Off-target |Inaccurate |
| 5 |Do students find Richard Whittaker's exams fair? |Exams are fair and one to one with prior exam reviews, however they usually make up 90% of the grade and exam dates are unnegotiable |Students find Whittaker's exams fair and predictable — 20 multiple choice questions that closely mirror both the reviews and homework assignments. Both reviewers rated him a 5 and considered the class an easy A as a result. |Relevant |Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"How do students describe the workload in COT3100 (Discrete Structures) at FIU?"

**What the system returned:**
No information found — the system correctly declined to answer rather than hallucinate, but it failed to surface the 4 Reddit chunks from the Discrete Structures thread that were explicitly ingested for this purpose.

**Root cause (tied to a specific pipeline stage):**
At ingestion, Reddit chunks were stored with the thread title as professor_name and no course code field in metadata. At retrieval, similarity_search competes across all 1,550 documents and the 4 Discrete Structures chunks were semantically similar enough to other workload-related reviews that they ranked outside the top 50 fetched. There is no course_id metadata field to filter on, so there was no way to directly target course-specific chunks regardless of query phrasing.

**What you would change to fix it:**
Add a course_id field (e.g. "COT3100") to the Document schema in models.py and populate it during Reddit chunking when the thread title or post body contains a recognizable course code. This would allow retrieve() to apply a where={"course_id": "COT3100"} filter in Chroma, bypassing semantic ranking entirely for course-specific queries.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The AI Tool Plan section gave me concrete, staged prompts for each pipeline component rather than vague goals, which made it easy to direct Claude to generate focused, correctly-scoped functions. Having the Document schema defined upfront in the plan meant every generated component imported from the same models.py rather than redefining fields inconsistently across files.

**One way your implementation diverged from the spec, and why:**
The spec set top-k at 5, but the final implementation fetches 50 candidates and caps at 2 chunks per professor. This was necessary because the chunk imbalance between professors (354 vs 68) caused high-volume professors to dominate every similarity search at lower k values, making retrieval effectively single-professor for most queries.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
I'm building a RAG pipeline over Rate My Professor reviews. Create a models.py file with two TypedDicts:
Professor with fields:

professor_id: str
name: str
Document with fields:

professor_id: str
professor_name: str
rating: float
review_text: str
tags: list[str]
Requirements:

Use typing or typing_extensions for compatibility
No logic, no imports beyond what TypedDict needs
This file will be imported by a GraphQL fetcher, a review chunker, a Chroma ingestion function, and a retrieval function — so keep it flat and stable

- *What it produced:*
from typing import TypedDict, List
 
 
class Professor(TypedDict):
    professor_id: str
    name: str
 
 
class Document(TypedDict):
    professor_id: str
    professor_name: str
    rating: float
    review_text: str
    tags: List[str]

- *What I changed or overrode:*
  Nothing for this one

**Instance 2**

- *What I gave the AI:*
I'm building a RAG pipeline over FIU CS professor reviews. I need you to implement two things:
1. generation.py — generate_response(query: str, context_docs: List[Document]) -> str
Use this exact system prompt, hardcoded:

You are a TA assistant for FIU CS students. Answer questions using only the provided student reviews. Do not use outside knowledge. If the reviews don't contain enough information to answer, say so.

Given these reviews:
{context}

Answer the following question: {query}
Cite ratings where relevant. At the end of your response, list the sources you drew from as:
Sources: [professor_name, rating: X], [professor_name, rating: X], ...
Context is built by joining each Document's review_text, prefixed with [professor_name | rating: X]. Reddit chunks have rating: 0.0 — display those as rating: N/A. Use claude-sonnet-4-6, max_tokens=1024. Import Document from models.py.
2. main.py — Gradio chat interface
Wire retrieve(query, k=5) → generate_response(query, docs) into a Gradio ChatInterface. Single text input, response streams into the chat window. No login, no history persistence needed.
Import from retrieval.py and generation.py. The interface should launch on 0.0.0.0 so it's accessible on the local network.

- *What it produced:*
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

- *What I changed or overrode:*
System prompt clarification about professors vs. students because it kept misidentifying professors names as the actual students who left the reviews(which are anonymous).
