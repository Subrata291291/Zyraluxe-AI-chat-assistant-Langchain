import importlib.util
from pathlib import Path

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from pinecone import Pinecone


CONFIG_FILE = (
    Path(__file__).parent / "18_config.py"
)


def load_config():

    spec = importlib.util.spec_from_file_location(
        "zyra_config",
        CONFIG_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Could not load configuration."
        )

    config = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(config)

    return config


def create_llm(config):

    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        temperature=0
    )


def create_embeddings(config):

    return GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL
    )


def create_pinecone_index(config):

    pc = Pinecone(
        api_key=config.PINECONE_API_KEY
    )

    return pc.Index(
        config.PINECONE_INDEX_NAME
    )


def create_components(config):

    llm = create_llm(config)

    embeddings = create_embeddings(config)

    index = create_pinecone_index(config)

    return {
        "llm": llm,
        "embeddings": embeddings,
        "index": index
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RAG SERVICE FACTORY")
    print("=" * 60)

    config = load_config()

    components = create_components(
        config
    )

    print()
    print("Components created successfully.")

    print()
    print(
        f"LLM: "
        f"{config.LLM_MODEL}"
    )

    print(
        f"Embeddings: "
        f"{config.EMBEDDING_MODEL}"
    )

    print(
        f"Pinecone Index: "
        f"{config.PINECONE_INDEX_NAME}"
    )

    print()
    print(
        f"LLM object: "
        f"{type(components['llm']).__name__}"
    )

    print(
        f"Embeddings object: "
        f"{type(components['embeddings']).__name__}"
    )

    print(
        f"Index object: "
        f"{type(components['index']).__name__}"
    )

    print()
    print("=" * 60)
    print("FACTORY CHECK COMPLETED")
    print("=" * 60)