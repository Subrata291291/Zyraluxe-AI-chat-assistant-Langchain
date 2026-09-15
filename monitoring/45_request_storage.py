import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "monitoring"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REQUEST_FILE = DATA_DIR / "requests.json"


class RequestStorage:

    def __init__(self, file_path=REQUEST_FILE):

        self.file_path = file_path

    def load_requests(self):

        if not self.file_path.exists():

            return []

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save_request(self, request):

        requests = self.load_requests()

        requests.append(request)

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                requests,
                file,
                indent=4
            )

    def get_requests(self):

        return self.load_requests()


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - REQUEST STORAGE")
    print("=" * 60)

    storage = RequestStorage()

    request = {
        "request_id": "req-005",
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "success": True,
        "response_time": 0.95
    }

    storage.save_request(request)

    requests = storage.get_requests()

    print()
    print(f"Total Stored Requests: {len(requests)}")

    print()
    print("Latest Request")
    print("-" * 40)

    print(requests[-1])

    print()
    print(f"Storage File: {REQUEST_FILE}")

    print()
    print("=" * 60)
    print("REQUEST STORAGE CHECK COMPLETED")
    print("=" * 60)