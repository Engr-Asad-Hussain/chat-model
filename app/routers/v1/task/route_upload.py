from typing import Any, Dict

from fastapi import APIRouter, UploadFile

from app.database import redis as db
from app.utils import utils

router = APIRouter()
index_name = f"db-index"
prefix = f"document"


@router.post(path="/upload")
async def upload_file(file: UploadFile) -> Dict[str, Any]:

    # Reading file
    content = await file.read()
    file_contents = [(content, file.filename.split(".")[-1])]

    # Process file
    df = utils.intermediate_processor(file_contents)
    print("Completed intermediate_process")
    df = utils.primary_processor(df)
    print("Primary processor")

    # Sanity check
    if db.index_exists(index_name):
        db.delete_index(index_name)

    # Create index in Redis and load documents into the index
    db.create_index(index_name, prefix)
    db.load_documents(df, prefix)

    return {
        "status": "success",
        "message": "Files uploaded and stored in Redis",
        "index_name": index_name,
    }
