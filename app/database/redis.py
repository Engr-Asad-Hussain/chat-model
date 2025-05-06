from typing import Any, Dict, List

import numpy as np
import pandas as pd
import redis
from redis.commands.search.field import NumericField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from app.core.redis import redis

NUM_VECTORS = 4000
PREFIX = "embedding"
VECTOR_DIM = 1536
DISTANCE_METRIC = "COSINE"


# TODO: This can be async function
def create_index(index_name: str, prefix: str) -> None:
    document_name = TextField(name="document_name")
    text_chunks = TextField(name="text_chunks")
    vector_score = NumericField(name="vector_score")
    embedding = VectorField(
        "text_embeddings",
        "FLAT",
        {
            "TYPE": "FLOAT64",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": 255,
        },
    )

    # Creating index
    redis.ft(index_name).create_index(
        fields=[
            document_name,
            text_chunks,
            embedding,
            vector_score,
        ],
        definition=IndexDefinition(prefix=[prefix], index_type=IndexType.HASH),
    )


# TODO: This can be async function
def load_documents(df: pd.DataFrame, prefix: str) -> None:
    index_documents(df, prefix)
    print("Redis Vector Index Created!")


# TODO: This can be async function
def index_documents(df: pd.DataFrame, prefix: str) -> None:
    pipe = redis.pipeline()
    for index, row in df.iterrows():
        key = f"{prefix}:{row['vector_id']}"
        document_data = {
            "document_name": row["document_name"],
            "text_chunks": row["text_chunks"],
            "text_embeddings": row["text_embeddings"].tobytes(),
        }
        pipe.hset(key, mapping=document_data)
        print(f"Indexing document: {key}, document_data: {document_data}")
    pipe.execute()


# TODO: This can be async function
def index_exists(index_name: str) -> bool:
    indices = redis.execute_command("FT._LIST")
    return index_name in indices


# TODO: This can be async function
def delete_index(index_name: str) -> None:
    redis.execute_command("FT.DROPINDEX", index_name)


def list_documents(index_name: str, k: int = NUM_VECTORS) -> List[Dict[str, Any]]:
    base_query = f"*"
    return_fields = ["document_name", "text_chunks"]
    query = Query(base_query).paging(0, k).return_fields(*return_fields).dialect(2)
    results = redis.ft(index_name).search(query)
    return [process_doc(doc) for doc in results.docs]


def process_doc(doc) -> Dict[str, Any]:
    d = doc.__dict__
    if "vector_score" in d:
        d["vector_score"] = 1 - float(d["vector_score"])

    if isinstance(d["document_name"], bytes):
        d["document_name"] = d["document_name"].decode("utf-8", errors="ignore")
    if isinstance(d["text_chunks"], bytes):
        d["text_chunks"] = d["text_chunks"].decode("utf-8", errors="ignore")

    return d


def search_index(
    index_name: str, query_vector: List[float], return_fields=None, k: int = 5
) -> List[Dict[str, Any]]:
    if return_fields is None:
        return_fields = []

    # base_query = f"*=>[KNN {k} @embedding $vector AS vector_score]"
    # base_query = f"*=>[KNN 5 @vector $query_vector AS vector_score]"
    base_query = "*=>[KNN 5 @embedding $vector AS vector_score]"
    query = (
        Query(base_query)
        .sort_by("vector_score")
        .return_fields(*return_fields)
        .paging(0, k)
        .dialect(2)
    )
    params_dict = {"vector": np.array(query_vector, dtype=np.float64).tobytes()}
    results = redis.ft(index_name).search(query, params_dict)
    return [process_doc(doc) for doc in results.docs]
