from typing import List
from models import Document


def chunk_reviews(raw_data: dict, professor_id: str) -> List[Document]:
    """Parse a Rate My Professor GraphQL response into one Document per review.

    Args:
        raw_data:     The teacher node dict from the GraphQL response.
        professor_id: The professor's legacy ID to attach to every Document.

    Returns:
        A list of Documents, one per review edge, with only the fields
        required for RAG (review_text, rating, tags, professor_name, professor_id).
    """
    professor_name = f"{raw_data.get('firstName', '')} {raw_data['lastName']}".strip()

    return [
        Document(
            professor_id=professor_id,
            professor_name=professor_name,
            rating=node["helpfulRating"],
            review_text=node["comment"],
            tags=[t.strip() for t in node["ratingTags"].split("--") if t.strip()],
        )
        for edge in raw_data.get("ratings", {}).get("edges", [])
        if (node := edge["node"]) and node.get("comment")
    ]
