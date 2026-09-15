import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "monitoring"
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ERROR_FILE = DATA_DIR / "errors.json"


class ErrorTracker:

    def __init__(self, file_path=ERROR_FILE):

        self.file_path = file_path

    def load_errors(self):

        if not self.file_path.exists():

            return []

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def record_error(
        self,
        request_id,
        provider,
        model,
        error_type,
        error_message
    ):

        errors = self.load_errors()

        error_data = {
            "request_id": request_id,
            "provider": provider,
            "model": model,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }

        errors.append(error_data)

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                errors,
                file,
                indent=4
            )

        return error_data

    def get_errors(self):

        return self.load_errors()


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - ERROR TRACKING")
    print("=" * 60)

    tracker = ErrorTracker()

    error = tracker.record_error(
        request_id="req-error-001",
        provider="gemini",
        model="gemini-3.5-flash",
        error_type="rate_limit",
        error_message="429 RESOURCE_EXHAUSTED"
    )

    print()
    print("Error Recorded")
    print("-" * 40)

    print(
        f"Request ID: "
        f"{error['request_id']}"
    )

    print(
        f"Provider: "
        f"{error['provider']}"
    )

    print(
        f"Model: "
        f"{error['model']}"
    )

    print(
        f"Error Type: "
        f"{error['error_type']}"
    )

    print(
        f"Error Message: "
        f"{error['error_message']}"
    )

    print(
        f"Timestamp: "
        f"{error['timestamp']}"
    )

    print()
    print(f"Error File: {ERROR_FILE}")

    print()
    print("=" * 60)
    print("ERROR TRACKING CHECK COMPLETED")
    print("=" * 60)