import glob
from pathlib import Path
from typing import List

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config import TRANSCRIPT_DIR

BASE_DIR: Path = Path(__file__).resolve().parent.parent
INDEX_DIR: Path = BASE_DIR / "app" / "index_store"

def load_embedding_model() -> HuggingFaceEmbedding:
    """
    Loads and returns a HuggingFaceEmbedding model configured with a predefined model name.

    Returns:
        HuggingFaceEmbedding: The loaded embedding model instance.
    """
    return HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")

def generate_rag_index(index_dir: Path, embed_model: HuggingFaceEmbedding) -> VectorStoreIndex:
    """
    Generates or loads a VectorStoreIndex from the specified index directory using the provided embedding model.
    If an index already exists in the directory, it is loaded; otherwise, a new index is created from transcripts.

    Args:
        index_dir (Path): The directory where the index is stored or will be stored.
        embed_model (HuggingFaceEmbedding): The embedding model to use for document encoding.

    Returns:
        VectorStoreIndex: The generated or loaded vector store index.
    """
    index_exists = any(item for item in index_dir.iterdir() if item.name != ".gitkeep")
    if index_exists:
        storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
        return load_index_from_storage(storage_context=storage_context, embed_model=embed_model)

    transcript_files: List[str] = glob.glob(str(TRANSCRIPT_DIR / "*.txt"))
    # Filter out files from the test_data subdirectory
    transcript_files = [_file for _file in transcript_files]
    documents = SimpleDirectoryReader(input_files=transcript_files, exclude=["test_data/"]).load_data()

    index: VectorStoreIndex = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)
    index.storage_context.persist(persist_dir=index_dir)
    return index

def main():
    """
    Main function to load the embedding model and generate or load the RAG index.
    """
    embedding_model: HuggingFaceEmbedding = load_embedding_model()
    generate_rag_index(embed_model=embedding_model, index_dir=INDEX_DIR)

if __name__ == "__main__":
    main()
