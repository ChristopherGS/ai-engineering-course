import glob
import logging
import sys
import textwrap
from pathlib import Path

from llama_index import (
    Response,
    set_global_tokenizer,
    ServiceContext,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    set_global_handler,
)
from llama_index.core.llms.types import ChatMessage, MessageRole, ChatResponse
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP
from transformers import AutoTokenizer

from shared.settings import DATA_DIR, MISTRAL_7B_FILE

SYSTEM_PROMPT_TEXT = "You are bot that answers questions about podcast transcripts."


def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    set_global_handler("simple")


def load_llm(model_path: Path) -> LlamaCPP:
    return LlamaCPP(
        model_path=str(model_path),
        context_window=4096,
        max_new_tokens=512,
        model_kwargs={"n_gpu_layers": 8},
        verbose=True,
    )


def load_embedding_model() -> HuggingFaceEmbedding:
    return HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")


def save_or_load_index(
    index_dir: Path, service_context: ServiceContext
) -> VectorStoreIndex:
    index_exists = any(item for item in index_dir.iterdir() if item.name != ".gitkeep")
    if index_exists:
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        return load_index_from_storage(
            storage_context=storage_context, service_context=service_context
        )

    transcript_files = glob.glob(str(DATA_DIR / "**/*transcript*"), recursive=True)

    # Filter out files from the test_data subdirectory
    transcript_files = [
        _file for _file in transcript_files if "test_data" not in Path(_file).parts
    ]
    documents = SimpleDirectoryReader(
        input_files=transcript_files, exclude=["test_data/"]
    ).load_data()

    index = VectorStoreIndex.from_documents(
        documents, service_context=service_context, show_progress=True
    )
    # persist the index
    index.storage_context.persist(persist_dir=index_dir)
    return index


def run_inference(
    use_rag: bool,
    messages: list[ChatMessage],
    llm: LlamaCPP,
    embedding_model: HuggingFaceEmbedding | None = None,
) -> ChatResponse | Response:
    if not use_rag:
        return llm.chat(messages=messages)

    set_global_tokenizer(
        AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
    )

    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model=embedding_model, system_prompt=SYSTEM_PROMPT_TEXT
    )

    index_dir = DATA_DIR / "indices"
    index = save_or_load_index(index_dir=index_dir, service_context=service_context)

    query_engine = index.as_query_engine()
    return query_engine.query(messages[1].content)


def main():
    configure_logging()
    system_prompt = ChatMessage(role=MessageRole.SYSTEM, content=SYSTEM_PROMPT_TEXT)

    user_prompt = ChatMessage(
        role=MessageRole.USER,
        # content="According to Dylan Patel, what don't people understand about the semiconductor supply chain?",
        content="What is Kevin's favorite budgetting software?"
    )
    llm = load_llm(model_path=DATA_DIR / MISTRAL_7B_FILE)
    embedding_model = load_embedding_model()
    no_rag_result = ChatResponse = run_inference(
        llm=llm, use_rag=False, messages=[system_prompt, user_prompt]
    )

    rag_result: ChatResponse = run_inference(
        llm=llm,
        embedding_model=embedding_model,
        use_rag=True,
        messages=[system_prompt, user_prompt],
    )

    wrapper = textwrap.TextWrapper(width=80)

    print(f"NO RAG result: {wrapper.fill(no_rag_result.message.content)}")
    print("--------------------------")
    print(f"RAG result: {wrapper.fill(rag_result.response)}")


if __name__ == "__main__":
    main()
