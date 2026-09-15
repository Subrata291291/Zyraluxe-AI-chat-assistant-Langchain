import logging
from pathlib import Path


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "zyra_luxe.log"


def create_logger():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(
        "zyra_luxe"
    )

    logger.setLevel(logging.INFO)

    if not logger.handlers:

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )

        file_handler.setFormatter(
            formatter
        )

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

        logger.addHandler(
            console_handler
        )

    return logger


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - APPLICATION LOGGER")
    print("=" * 60)

    logger = create_logger()

    logger.info(
        "Application started"
    )

    logger.info(
        "User request received"
    )

    logger.warning(
        "Primary LLM quota is low"
    )

    logger.error(
        "Example provider error"
    )

    logger.info(
        "Fallback provider selected"
    )

    logger.info(
        "Application finished"
    )

    print()
    print(f"Log file: {LOG_FILE}")

    print()
    print("=" * 60)
    print("APPLICATION LOGGER CHECK COMPLETED")
    print("=" * 60)