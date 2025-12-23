from pathlib import Path
from typing import List
from pypdf import PdfReader
from .chunker import chunk_text


def load_documents(data_dir: Path) -> List[str]:
    if not data_dir.exists() or not data_dir.is_dir():
        raise ValueError(f"{data_dir} does not exist or is not a directory.")

    documents = []

    for file_path in data_dir.iterdir():
        if file_path.suffix.lower() == ".txt":
            text = file_path.read_text(encoding="utf-8")
            documents.extend(chunk_text(text))

        elif file_path.suffix.lower() == ".pdf":
            reader = PdfReader(file_path)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            documents.extend(chunk_text(full_text))

    return documents
