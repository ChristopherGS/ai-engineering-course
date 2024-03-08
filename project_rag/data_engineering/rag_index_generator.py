import glob
from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config import TRANSCRIPT_DIR

BASE_DIR = Path(__file__).resolve().parent.parent


INDEX_DIR = BASE_DIR / "app" / "index_store"


def load_embedding_model() -> HuggingFaceEmbedding:
    return HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")


def generate_rag_index(
    index_dir: Path, embed_model: HuggingFaceEmbedding
) -> VectorStoreIndex:
    index_exists = any(item for item in index_dir.iterdir() if item.name != ".gitkeep")
    if index_exists:
        storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
        return load_index_from_storage(
            storage_context=storage_context, embed_model=embed_model
        )

    transcript_files = glob.glob(str(TRANSCRIPT_DIR / "*.txt"))

    # Filter out files from the test_data subdirectory
    transcript_files = [
        _file for _file in transcript_files
    ]
    documents = SimpleDirectoryReader(
        input_files=transcript_files, exclude=["test_data/"]
    ).load_data()

    index = VectorStoreIndex.from_documents(
        documents, embed_model=embed_model, show_progress=True
    )
    index.storage_context.persist(persist_dir=index_dir)
    return index

def main():
    embedding_model = load_embedding_model()
    generate_rag_index(embed_model=embedding_model, index_dir=INDEX_DIR)



if __name__ == "__main__":
    main()