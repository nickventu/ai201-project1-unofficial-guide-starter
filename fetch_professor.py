"""
fetch_professor.py

Fetches all Rate My Professor reviews for a given professor ID,
paginating through the GraphQL API until exhausted.

Usage:
    from fetch_professor import fetch_professor
    from chunk_reviews import chunk_reviews

    raw  = await fetch_professor("1935348")
    docs = chunk_reviews(raw, "1935348")
"""

import asyncio
import base64
from typing import Optional

import httpx

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "authorization": "Basic dGVzdDp0ZXN0",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "origin": "https://www.ratemyprofessors.com",
    "referer": "https://www.ratemyprofessors.com/",
}

# Exact query captured from the RMP web client.
RATINGS_QUERY = """
query RatingsListQuery(
  $count: Int!
  $id: ID!
  $courseFilter: String
  $cursor: String
) {
  node(id: $id) {
    __typename
    ... on Teacher {
      ...RatingsList_teacher_4pguUW
    }
    id
  }
}

fragment CourseMeta_rating on Rating {
  attendanceMandatory
  wouldTakeAgain
  grade
  textbookUse
  isForOnlineClass
  isForCredit
}

fragment NoRatingsArea_teacher on Teacher {
  lastName
  ...RateTeacherLink_teacher
}

fragment ProfessorNoteEditor_rating on Rating {
  id
  legacyId
  class
  teacherNote {
    id
    teacherId
    comment
  }
}

fragment ProfessorNoteEditor_teacher on Teacher {
  id
}

fragment ProfessorNoteFooter_note on TeacherNotes {
  legacyId
  flagStatus
}

fragment ProfessorNoteFooter_teacher on Teacher {
  legacyId
  isProfCurrentUser
}

fragment ProfessorNoteHeader_note on TeacherNotes {
  createdAt
  updatedAt
}

fragment ProfessorNoteHeader_teacher on Teacher {
  lastName
}

fragment ProfessorNoteSection_rating on Rating {
  teacherNote {
    ...ProfessorNote_note
    id
  }
  ...ProfessorNoteEditor_rating
}

fragment ProfessorNoteSection_teacher on Teacher {
  ...ProfessorNote_teacher
  ...ProfessorNoteEditor_teacher
}

fragment ProfessorNote_note on TeacherNotes {
  comment
  ...ProfessorNoteHeader_note
  ...ProfessorNoteFooter_note
}

fragment ProfessorNote_teacher on Teacher {
  ...ProfessorNoteHeader_teacher
  ...ProfessorNoteFooter_teacher
}

fragment RateTeacherLink_teacher on Teacher {
  legacyId
  numRatings
  lockStatus
}

fragment RatingFooter_rating on Rating {
  id
  comment
  adminReviewedAt
  flagStatus
  legacyId
  thumbsUpTotal
  thumbsDownTotal
  thumbs {
    thumbsUp
    thumbsDown
    computerId
    id
  }
  teacherNote {
    id
  }
  ...Thumbs_rating
}

fragment RatingFooter_teacher on Teacher {
  id
  legacyId
  lockStatus
  isProfCurrentUser
  ...Thumbs_teacher
}

fragment RatingHeader_rating on Rating {
  legacyId
  date
  class
  helpfulRating
  clarityRating
  isForOnlineClass
}

fragment RatingSuperHeader_rating on Rating {
  legacyId
}

fragment RatingSuperHeader_teacher on Teacher {
  firstName
  lastName
  legacyId
  school {
    name
    id
  }
}

fragment RatingTags_rating on Rating {
  ratingTags
}

fragment RatingValues_rating on Rating {
  helpfulRating
  clarityRating
  difficultyRating
}

fragment Rating_rating on Rating {
  comment
  flagStatus
  createdByUser
  teacherNote {
    id
  }
  ...RatingHeader_rating
  ...RatingSuperHeader_rating
  ...RatingValues_rating
  ...CourseMeta_rating
  ...RatingTags_rating
  ...RatingFooter_rating
  ...ProfessorNoteSection_rating
}

fragment Rating_teacher on Teacher {
  ...RatingFooter_teacher
  ...RatingSuperHeader_teacher
  ...ProfessorNoteSection_teacher
}

fragment RatingsList_teacher_4pguUW on Teacher {
  id
  legacyId
  lastName
  numRatings
  school {
    id
    legacyId
    name
    city
    state
    avgRating
    numRatings
  }
  ...Rating_teacher
  ...NoRatingsArea_teacher
  ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {
    edges {
      cursor
      node {
        ...Rating_rating
        id
        __typename
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

fragment Thumbs_rating on Rating {
  id
  comment
  adminReviewedAt
  flagStatus
  legacyId
  thumbsUpTotal
  thumbsDownTotal
  thumbs {
    computerId
    thumbsUp
    thumbsDown
    id
  }
  teacherNote {
    id
  }
}

fragment Thumbs_teacher on Teacher {
  id
  legacyId
  lockStatus
  isProfCurrentUser
}
"""

PAGE_SIZE = 20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _encode_professor_id(raw_id: str) -> str:
    """Base64-encode 'Teacher-{raw_id}' -> e.g. 'VGVhY2hlci0xOTM1MzQ4'."""
    return base64.b64encode(f"Teacher-{raw_id}".encode()).decode()


def _build_payload(encoded_id: str, cursor: Optional[str] = None) -> dict:
    return {
        "operationName": "RatingsListQuery",
        "query": RATINGS_QUERY,
        "variables": {
            "id": encoded_id,
            "count": PAGE_SIZE,
            "courseFilter": None,
            "cursor": cursor,   # None on first request; endCursor on subsequent pages
        },
    }


# ---------------------------------------------------------------------------
# Core fetch function
# ---------------------------------------------------------------------------

async def fetch_professor(professor_id: str) -> dict:
    """
    Fetch all reviews for a professor from Rate My Professors.

    Paginates until exhausted and returns a single teacher dict whose
    `ratings.edges` contains every review edge. Pass the result directly
    to chunk_reviews() to get Document objects.

    Args:
        professor_id: Raw integer ID as a string, e.g. "1935348".

    Returns:
        Teacher node dict with all paginated edges merged under
        data["ratings"]["edges"].

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
        KeyError:              If the response shape is unexpected.
    """
    encoded_id = _encode_professor_id(professor_id)
    all_edges: list = []
    teacher: Optional[dict] = None
    cursor: Optional[str] = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            payload  = _build_payload(encoded_id, cursor)
            response = await client.post(GRAPHQL_URL, headers=HEADERS, json=payload)
            response.raise_for_status()

            body = response.json()
            page_teacher = body["data"]["node"]

            if teacher is None:
                teacher = page_teacher  # capture top-level fields (name, legacyId, …)

            ratings_conn = page_teacher["ratings"]
            all_edges.extend(ratings_conn["edges"])

            if not ratings_conn["pageInfo"]["hasNextPage"]:
                break

            cursor = ratings_conn["pageInfo"]["endCursor"]

    # Merge all edges back onto the teacher dict so chunk_reviews sees one object.
    teacher["ratings"]["edges"] = all_edges
    return teacher


# ---------------------------------------------------------------------------
# Quick smoke-test  (python fetch_professor.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from chunk_reviews import chunk_reviews

    async def _main() -> None:
        raw  = await fetch_professor("1935348")
        docs = chunk_reviews(raw, "1935348")
        print(f"Fetched {len(docs)} reviews")
        for d in docs[:5]:
            print(d)

    asyncio.run(_main())
