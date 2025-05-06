from typing import List, Tuple

import openai
import pandas as pd
from langchain.text_splitter import TokenTextSplitter

from app.core.config import settings
from app.utils import models
from app.utils.extract_pdf import extract_text_from_pdf


def intermediate_processor(file_contents: List[Tuple[bytes, str]]) -> pd.DataFrame:
    df = pd.DataFrame({"document_name": [], "text_extracted": [], "text_chunks": []})
    df = df.pipe(extract_text_from_files, file_contents).pipe(split_text_chunks)
    return df


def extract_text_from_files(
    df: pd.DataFrame, file_contents: List[Tuple[bytes, str]]
) -> pd.DataFrame:
    for file_content, file_extension in file_contents:
        text = extract_text_from_pdf(file_content)
        new_row = pd.DataFrame(
            {"document_name": [file_content], "text_extracted": [text]}
        )
        df = pd.concat([df, new_row], ignore_index=True)
    return df


def split_text_chunks(df: pd.DataFrame) -> pd.DataFrame:
    text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)
    df["text_chunks"] = ""

    for index, row in df.iterrows():
        document_name = row["document_name"]
        text_extracted = row["text_extracted"]
        if isinstance(text_extracted, bytes):
            text_extracted = text_extracted.decode("utf-8")
        text_chunks = text_splitter.split_text(text_extracted)

        comma_separated_chunks = ", ".join(text_chunks)

        df.at[index, "text_chunks"] = comma_separated_chunks

    return df


def primary_processor(df: pd.DataFrame) -> pd.DataFrame:
    openai.api_key = settings.OPENAI_API_KEY

    def embed_text(text, model="text-embedding-ada-002"):
        return models.get_embedding(text, model=model)

    def assign_vector_id():
        return list(range(len(df)))

    df["text_embeddings"] = df["text_chunks"].apply(
        lambda x: embed_text(str(x), model="text-embedding-ada-002")
    )
    df["document_name_embeddings"] = df["document_name"].apply(
        lambda x: embed_text(str(x), model="text-embedding-ada-002")
    )
    df["vector_id"] = assign_vector_id()
    return df
