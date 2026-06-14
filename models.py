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
