import pydantic
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from app import usecases
from app.api import dependencies

rag_router = APIRouter()

@rag_router.post("/save-document/", status_code=201)
def save_document(file: UploadFile = File(...),
                        rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Guardar la información del archivo en MongoDB
    rag_service.save_document(file)
    return {"status": "Document saved successfully"}

@rag_router.get("/get-document/")
def get_document(document_id: str,
                 rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    document = rag_service.get_document(document_id)
    if document:
        return document
    return {"status": "Document not found"}

@rag_router.get("/get-vectors/", status_code=201)
def get_vectors(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return rag_service.get_vectors()
