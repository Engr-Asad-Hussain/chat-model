from typing import Any, Dict

from fastapi import APIRouter

from app.database import redis as db
from app.utils import llm, llm_completion, models

router = APIRouter()
index_name = f"db-index"
prefix = f"document"


@router.get(path="/question")
async def get_answer(question: str, rag: bool = False) -> Dict[str, Any]:

    # Conditional
    if rag is True:
        # Get the embedding of the task
        query_vector = models.get_embedding(question)

        # List all documents in Redis
        all_documents = db.list_documents(index_name)

        # Search Redis for relevant documents
        search_results = db.search_index(
            index_name,
            query_vector,
            return_fields=["document_name", "text_chunks"],
        )
        search_results = []

        # If no search results, use all documents
        if len(search_results) == 0:
            search_results = all_documents

        # Get the most relevant document
        relevant_doc = search_results[0]

        # Extract text chunks from the relevant document
        text_chunks = relevant_doc["text_chunks"]

        # Use documents_agent to generate an answer
        answer = llm.documents_agent(text_chunks, question)

    else:
        answer = llm_completion.get_direct_response(question)

    # Return the task and its answer
    return {"task": question, "answer": answer}
