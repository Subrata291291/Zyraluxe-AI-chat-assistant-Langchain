import time
import uuid
import logging
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "zyra_luxe.log"


logger = logging.getLogger("zyra_request_tracker")
logger.setLevel(logging.INFO)

if not logger.handlers:

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


class RequestTracker:

    def __init__(self):

        self.requests = []

    def start_request(self):

        request_id = str(uuid.uuid4())

        start_time = time.perf_counter()

        logger.info(
            f"Request started | "
            f"request_id={request_id}"
        )

        return request_id, start_time

    def finish_request(
        self,
        request_id,
        start_time,
        provider,
        model,
        success
    ):

        response_time = (
            time.perf_counter()
            - start_time
        )

        request_data = {
            "request_id": request_id,
            "provider": provider,
            "model": model,
            "success": success,
            "response_time": round(
                response_time,
                3
            )
        }

        self.requests.append(request_data)

        if success:

            logger.info(
                f"Request completed | "
                f"request_id={request_id} | "
                f"provider={provider} | "
                f"model={model} | "
                f"response_time={response_time:.3f}s"
            )

        else:

            logger.error(
                f"Request failed | "
                f"request_id={request_id} | "
                f"provider={provider} | "
                f"model={model} | "
                f"response_time={response_time:.3f}s"
            )

        return request_data


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - TRACKING + LOGGER")
    print("=" * 60)

    tracker = RequestTracker()

    request_id, start_time = (
        tracker.start_request()
    )

    time.sleep(1)

    result = tracker.finish_request(
        request_id=request_id,
        start_time=start_time,
        provider="groq",
        model="openai/gpt-oss-20b",
        success=True
    )

    print()
    print("Request Result")
    print("-" * 40)

    print(f"Request ID: {result['request_id']}")
    print(f"Provider: {result['provider']}")
    print(f"Model: {result['model']}")
    print(f"Success: {result['success']}")
    print(
        f"Response Time: "
        f"{result['response_time']} sec"
    )

    print()
    print(f"Log file: {LOG_FILE}")

    print()
    print("=" * 60)
    print("TRACKING + LOGGER CHECK COMPLETED")
    print("=" * 60)