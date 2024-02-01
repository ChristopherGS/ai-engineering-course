import glob
import logging
import textwrap
from pathlib import Path
import sys
from llama_index import (
    ServiceContext,
    set_global_handler,
    set_global_tokenizer,
    StorageContext,
    load_index_from_storage,
    SimpleDirectoryReader,
    VectorStoreIndex,
    Response,
)
from llama_index.core.llms.types import ChatMessage, MessageRole, ChatResponse
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP
from transformers import AutoTokenizer

from shared.settings import DATA_DIR
from shared.timer_utils import timer


# Configure logging
def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    set_global_handler("simple")


def log_wrapped_message(logger, message, line_length=80):
    for line in textwrap.wrap(message, line_length):
        logger.info(line)


# Load LlamaCPP model
def load_llm() -> LlamaCPP:
    model_path = DATA_DIR / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    return LlamaCPP(
        model_path=str(model_path),
        context_window=4096,
        max_new_tokens=512,
        model_kwargs={"n_gpu_layers": 10},
        verbose=True,
    )


# Load embedding model
def load_embedding_model() -> HuggingFaceEmbedding:
    return HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")


# Save or load the index
def save_or_load_index(
    index_dir: Path, service_context: ServiceContext
) -> VectorStoreIndex:
    index_exists = any(item for item in index_dir.iterdir() if item.name != ".gitkeep")
    if index_exists:
        logging.info(f"Loading persisted index from: {index_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        return load_index_from_storage(storage_context, service_context=service_context)
    else:
        logging.info("Persisted index not found, creating a new index...")
        transcript_files = glob.glob(str(DATA_DIR / "**/*transcript*"), recursive=True)
        documents = SimpleDirectoryReader(input_files=transcript_files).load_data()
        index = VectorStoreIndex.from_documents(
            documents, service_context=service_context, show_progress=True
        )
        index.storage_context.persist(persist_dir=index_dir)
        return index


@timer
def run_inference(
    use_rag: bool, messages: list[ChatMessage]
) -> ChatResponse | Response:
    llm = load_llm()
    embedding_model = load_embedding_model()
    if not use_rag:
        return llm.chat(messages=messages)

    set_global_tokenizer(
        AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2").encode
    )
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embedding_model,
        system_prompt="You are a bot that answers questions about podcast transcripts",
    )
    index_dir = DATA_DIR / "indices"
    file_to_delete = index_dir / ".DS_Store"
    if file_to_delete.exists():
        file_to_delete.unlink()

    index = save_or_load_index(index_dir=index_dir, service_context=service_context)
    query_engine = index.as_query_engine()
    return query_engine.query(messages[1].content)


def main():
    configure_logging()
    system_prompt = ChatMessage(
        role=MessageRole.SYSTEM,
        content="You are a bot that answers questions about podcast transcripts",
    )
    user_prompt = ChatMessage(
        role=MessageRole.USER,
        content="According to Dylan Patel, what don't people understand about the semiconductor supply chain?",
    )
    no_rag_result: ChatResponse = run_inference(
        use_rag=False, messages=[system_prompt, user_prompt]
    )
    result: Response = run_inference(
        use_rag=True, messages=[system_prompt, user_prompt]
    )

    # Now, print the results wrapping the lines with textwrap
    wrapper = textwrap.TextWrapper(width=80)

    print(f"No RAG result: {wrapper.fill(no_rag_result.message.content)}")
    print("------------------------------")
    print(f"RAG result: {wrapper.fill(result.response)}")


if __name__ == "__main__":
    main()
