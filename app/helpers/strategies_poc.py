import abc
from abc import abstractmethod
from typing import Type, Optional
import re
import PyPDF2
import docx


class FileManager(abc.ABC):
    @abstractmethod
    def __init__(self, path: str):
        self.path = path

    @abstractmethod
    def read(self) -> Optional[str]:
        pass


class PDFFileManager(FileManager):
    def __init__(self, path: str):
        super().__init__(path)

    def read(self) -> Optional[str]:
        try:
            with open(self.path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()

                cleaned_text = self.clean_text(text)
                return cleaned_text

        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the PDF: {e}"

    def clean_text(self, text: str) -> str:
        # Reemplaza los saltos de línea dentro de frases por un espacio.
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        # Reemplaza múltiples saltos de línea consecutivos por uno solo.
        text = re.sub(r"\n+", "\n", text)
        # Opcionalmente, puedes eliminar espacios innecesarios adicionales.
        text = re.sub(r"[ \t]+", " ", text)
        return text


class WordFileManager(FileManager):
    def __init__(self, path: str):
        super().__init__(path)

    def read(self) -> Optional[str]:
        try:
            doc = docx.Document(self.path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the Word file: {e}"


class TextFileManager(FileManager):
    def __init__(self, path: str):
        super().__init__(path)

    def read(self) -> Optional[str]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the text file: {e}"


strategies: dict[str, Type[FileManager]] = {
    "pdf": PDFFileManager,
    "docx": WordFileManager,
    "txt": TextFileManager,
}


class FileReader:
    def __init__(self, path: str):
        extension = path.split(".")[-1]
        if extension not in strategies:
            raise ValueError(f"Unsupported file type: {extension}")
        self.manager = strategies[extension](path)

    def read_file(self) -> Optional[str]:
        return self.manager.read()
