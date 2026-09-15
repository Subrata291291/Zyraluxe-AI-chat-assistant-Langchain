import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "monitoring"
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

HEALTH_FILE = DATA_DIR / "health_history.json"


class HealthHistory:

    def __init__(self, file_path=HEALTH_FILE):

        self.file_path = file_path

    def load_history(self):

        if not self.file_path.exists():
            return []

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save_check(self, results):

        history = self.load_history()

        record = {
            "timestamp": datetime.now().isoformat(),
            "services": results
        }

        history.append(record)

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4
            )

        return record

    def get_history(self):

        return self.load_history()


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - HEALTH HISTORY")
    print("=" * 60)

    history = HealthHistory()

    results = {
        "gemini": {
            "status": "unhealthy",
            "message": "429 RESOURCE_EXHAUSTED"
        },
        "groq": {
            "status": "healthy",
            "message": "API available"
        },
        "openrouter": {
            "status": "healthy",
            "message": "API available"
        },
        "openai": {
            "status": "unhealthy",
            "message": "429 insufficient_quota"
        },
        "pinecone": {
            "status": "healthy",
            "message": "API available"
        }
    }

    record = history.save_check(results)

    print()
    print("Health Check Saved")
    print("-" * 40)

    print(
        f"Timestamp: "
        f"{record['timestamp']}"
    )

    for service, result in (
        record["services"].items()
    ):

        print(
            f"{service}: "
            f"{result['status']}"
        )

    print()
    print(
        f"Total Health Checks: "
        f"{len(history.get_history())}"
    )

    print()
    print(f"History File: {HEALTH_FILE}")

    print()
    print("=" * 60)
    print("HEALTH HISTORY CHECK COMPLETED")
    print("=" * 60)