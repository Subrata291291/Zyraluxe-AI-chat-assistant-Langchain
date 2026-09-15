import importlib.util
from pathlib import Path


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


def show_configuration(config):

    print("=" * 60)
    print("ZYRA LUXE - CONFIGURATION INTEGRATION")
    print("=" * 60)

    print()
    print(f"LLM Model: {config.LLM_MODEL}")

    print(
        f"Embedding Model: "
        f"{config.EMBEDDING_MODEL}"
    )

    print(
        f"Pinecone Index: "
        f"{config.PINECONE_INDEX_NAME}"
    )

    print(
        f"Namespace: "
        f"{config.PINECONE_NAMESPACE}"
    )

    print(
        f"Retrieval Top K: "
        f"{config.RETRIEVAL_TOP_K}"
    )

    print(
        f"Minimum Score: "
        f"{config.MIN_RETRIEVAL_SCORE}"
    )

    print(
        f"Maximum Context Chunks: "
        f"{config.MAX_CONTEXT_CHUNKS}"
    )

    print()
    print("=" * 60)
    print("CONFIGURATION INTEGRATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":

    config = load_config()

    show_configuration(config)