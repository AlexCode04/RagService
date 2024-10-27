import os
from fastapi import UploadFile
from app.core.models import Document, User
from app.core import ports
from app.helpers.strategies_poc import FileReader


class RAGService:
    def __init__(
        self,
        db: ports.DatabasePort,
        document_repo: ports.DocumentRepositoryPort,
        openai_adapter: ports.LlmPort,
    ) -> None:
        self.db = db
        self.document_repo = document_repo
        self.openai_adapter = openai_adapter

    def save_document(self, file: UploadFile) -> None:
        file_name = file.filename
        os.makedirs("media", exist_ok=True)

        # Guardar el archivo en la carpeta 'media' con manejo de errores
        file_path = os.path.join("media", file_name)
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            raise

        # Crear modelo documento y leer contenido
        document = Document(nombre=file_name, ruta=file_path)
        content = FileReader(document.ruta).read_file() if document.ruta else ""
        content = content if content is not None else ""  # Manejo si no hay contenido

        print(f"Texto del documento: {content}")
        # Guardar el documento en la base de datos
        self.document_repo.save_document(document, content, self.openai_adapter)

    def get_vectors(self) -> dict:
        vectors = self.document_repo.get_vectors()
        return {
            "embeddings": vectors.get("embeddings", []),
            "documents": vectors.get("documents", []),
            "metadatas": vectors.get("metadatas", []),
        }

    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query, self.openai_adapter)
        if not documents:
            print("No documents found for the query.")
            return "No se encontraron documentos relevantes para la consulta."

        context = " ".join(
            [doc.content for doc in documents if doc.content is not None]
        )
        return self.openai_adapter.generate_text(
            prompt=query, retrieval_context=context
        )

    def sing_up(self, username: str, password: str, rol: str) -> None:
        user = User(username=username, password=password, rol=rol)
        print(f"Generated user_id: {user.user_id}")
        self.db.save_user(user)

    def get_user(self, username: str, password: str) -> User:
        user = self.db.get_user(username, password)
        if user is None:
            raise ValueError("User not found")
        return user  # Retorna el modelo User directamente
