from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
from src.utils import Utils

app = FastAPI()
utils = Utils()


class Query(BaseModel):
    """
    Represents a query with an ID, the query string, and the index name.
    """

    id: str
    query: str
    index_name: str


@app.get("/")
async def root():
    """
    Handles the root endpoint, returning a simple message.
    """
    return {"message": "Hello World"}


@app.post("/upload_doc")
async def upload_document(file: UploadFile = File(...)):
    """
    Handles the upload of a document, saving it temporarily, processing it, and removing the temporary file.
    """
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        temp_file_path = temp_file_path.replace(" ", "_")
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Upload the document using Utils
        result = utils.upload_doc(temp_file_path)

        # Remove the temporary file
        os.remove(temp_file_path)

        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/get_indexes", response_model=List[str])
async def get_indexes():
    """
    Retrieves all available indexes.
    """
    try:
        indexes = utils.get_all_indexes()
        return indexes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qa")
async def question_answering(query: Query):
    """
    Handles question answering based on a given query.
    """
    try:
        context = utils.similarity_search(query.query, query.index_name)
        new_query = utils.rephrase({"id": query.id, "query": query.query})
        response = utils.qa(new_query, context)

        # Save the conversation
        conv = [
            {"role": "user", "content": new_query},
            {"role": "assistant", "content": response},
        ]
        utils.save_conv(query.id, conv)
        print(f"BOT: {response}")
        return {"query": new_query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_convs")
async def get_conv(id: str):
    """
    Retrieves a conversation history based on the given ID.
    """
    try:
        conv = utils.get_all_convs()
        return conv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000, log_level="info")
