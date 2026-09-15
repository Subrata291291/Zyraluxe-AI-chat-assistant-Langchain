import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI
from pinecone import Pinecone


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "zyra_luxe.log"


logger = logging.getLogger("health_check")
logger.setLevel(logging.INFO)

if not logger.handlers:

    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)


def check_provider(name, create_llm):

    try:

        llm = create_llm()

        llm.invoke("Reply with OK.")

        result = {
            "service": name,
            "status": "healthy",
            "message": "API available"
        }

        logger.info(
            f"Health check | "
            f"service={name} | "
            f"status=healthy | "
            f"message=API available"
        )

        return result

    except Exception as error:

        result = {
            "service": name,
            "status": "unhealthy",
            "message": str(error)
        }

        logger.error(
            f"Health check | "
            f"service={name} | "
            f"status=unhealthy | "
            f"error={error}"
        )

        return result


def check_pinecone():

    try:

        pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )

        pc.list_indexes()

        result = {
            "service": "pinecone",
            "status": "healthy",
            "message": "API available"
        }

        logger.info(
            "Health check | "
            "service=pinecone | "
            "status=healthy | "
            "message=API available"
        )

        return result

    except Exception as error:

        result = {
            "service": "pinecone",
            "status": "unhealthy",
            "message": str(error)
        }

        logger.error(
            f"Health check | "
            f"service=pinecone | "
            f"status=unhealthy | "
            f"error={error}"
        )

        return result


def run_health_checks():

    results = []

    providers = [
        (
            "gemini",
            lambda: ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=os.getenv(
                    "GOOGLE_API_KEY"
                )
            )
        ),
        (
            "groq",
            lambda: ChatGroq(
                model="openai/gpt-oss-20b",
                groq_api_key=os.getenv(
                    "GROQ_API_KEY"
                )
            )
        ),
        (
            "openrouter",
            lambda: ChatOpenRouter(
                model="openai/gpt-oss-20b",
                api_key=os.getenv(
                    "OPENROUTER_API_KEY"
                )
            )
        ),
        (
            "openai",
            lambda: ChatOpenAI(
                model="gpt-5-nano",
                api_key=os.getenv(
                    "OPENAI_API_KEY"
                )
            )
        )
    ]

    for name, create_llm in providers:

        results.append(
            check_provider(
                name,
                create_llm
            )
        )

    results.append(
        check_pinecone()
    )

    return results


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - HEALTH CHECK + LOGGING")
    print("=" * 60)

    results = run_health_checks()

    print()

    for result in results:

        print(
            f"{result['service']}: "
            f"{result['status']} - "
            f"{result['message']}"
        )

    print()
    print(f"Log file: {LOG_FILE}")

    print()
    print("=" * 60)
    print("HEALTH CHECK + LOGGING COMPLETED")
    print("=" * 60)