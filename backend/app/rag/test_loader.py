from pathlib import Path
from loader import load_documents

if __name__ == "__main__":
    # Relative path to the `data` folder
    data_dir = Path(__file__).parent.parent / "data"

    # Load documents
    docs = load_documents(data_dir)

    print(f"Loaded {len(docs)} documents")
    print("Documents:")
    for i, doc in enumerate(docs[:2]):
        print(f"{i+1}: {doc}\n{'-'*40}")
