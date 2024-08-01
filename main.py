from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import os
from src.utils import Utils  # Assuming you've renamed the class file to utils.py

app = FastAPI()
utils = Utils()

class Query(BaseModel):
    id: str
    query: str
    index_name: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload_doc")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
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
    try:
        indexes = utils.get_all_indexes()
        return indexes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa")
async def question_answering(query: Query):
    try:
        context = utils.similarity_search(query.query, query.index_name)
        new_query = utils.rephrase({"id": query.id, "query": query.query})
        response = utils.qa(new_query, context)
        
        # Save the conversation
        conv = [
            {"role": "user", "content": new_query},
            {"role": "assistant", "content": response}
        ]
        utils.save_conv(query.id, conv)
        
        return {"query": new_query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_convs")
async def get_conv(id: str):
    try:
        conv = utils.get_all_convs()
        return conv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")