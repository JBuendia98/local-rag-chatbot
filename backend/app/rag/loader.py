from pathlib import Path
from typing import List
from pypdf import PdfReader

def load_documents(data_dir: Path) -> List[str]:
    
    if not data_dir.exists() or not data_dir.is_dir():
        raise ValueError(f"{data_dir} does not exist or is not a directory.")

    documents = []

    for file_path in data_dir.iterdir():
        if file_path.suffix.lower() == ".txt":
            text = file_path.read_text(encoding="utf-8")
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            documents.extend(paragraphs)
        elif file_path.suffix.lower() == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            documents.extend(paragraphs)
        else:
            print(f"Skipping unsupported file type: {file_path.name}")

    return documents
