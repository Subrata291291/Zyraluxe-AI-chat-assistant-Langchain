import importlib.util
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "18_config.py"


def load_config():

    spec = importlib.util.spec_from_file_location(
        "zyra_config",
        CONFIG_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Could not load configuration."
        )

    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    return config


def show_retry_configuration(config):

    print("=" * 60)
    print("ZYRA LUXE - RETRY POLICY CONFIGURATION")
    print("=" * 60)

    print()
    print(
        f"Maximum LLM Retries: "
        f"{config.MAX_LLM_RETRIES}"
    )

    print(
        f"Retry Base Delay: "
        f"{config.RETRY_BASE_DELAY} seconds"
    )

    print()

    for attempt in range(
        config.MAX_LLM_RETRIES
    ):

        delay = (
            config.RETRY_BASE_DELAY
            * (2 ** attempt)
        )

        print(
            f"Retry {attempt + 1}: "
            f"wait {delay} seconds"
        )

    print()
    print("=" * 60)
    print("RETRY POLICY CONFIGURATION CHECK COMPLETED")
    print("=" * 60)


if __name__ == "__main__":

    config = load_config()

    show_retry_configuration(config)