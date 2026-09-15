import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUEST_FILE = (
    PROJECT_ROOT
    / "data"
    / "monitoring"
    / "requests.json"
)


class PersistentMetrics:

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

    def total_requests(self):

        return len(self.requests)

    def successful_requests(self):

        return sum(
            1
            for request in self.requests
            if request["success"]
        )

    def failed_requests(self):

        return sum(
            1
            for request in self.requests
            if not request["success"]
        )

    def success_rate(self):

        if not self.requests:

            return 0

        return round(
            (
                self.successful_requests()
                / self.total_requests()
            ) * 100,
            2
        )

    def average_response_time(self):

        if not self.requests:

            return 0

        total_time = sum(
            request["response_time"]
            for request in self.requests
        )

        return round(
            total_time / self.total_requests(),
            3
        )

    def provider_usage(self):

        return Counter(
            request["provider"]
            for request in self.requests
        )

    def get_summary(self):

        self.requests = self.load_requests()

        return {
            "total_requests": self.total_requests(),
            "successful_requests": self.successful_requests(),
            "failed_requests": self.failed_requests(),
            "success_rate": self.success_rate(),
            "average_response_time": (
                self.average_response_time()
            ),
            "provider_usage": dict(
                self.provider_usage()
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PERSISTENT METRICS")
    print("=" * 60)

    metrics = PersistentMetrics()

    summary = metrics.get_summary()

    print()
    print(f"Data Source: {REQUEST_FILE}")

    print()
    print("Metrics")
    print("-" * 40)

    print(
        f"Total Requests: "
        f"{summary['total_requests']}"
    )

    print(
        f"Successful Requests: "
        f"{summary['successful_requests']}"
    )

    print(
        f"Failed Requests: "
        f"{summary['failed_requests']}"
    )

    print(
        f"Success Rate: "
        f"{summary['success_rate']}%"
    )

    print(
        f"Average Response Time: "
        f"{summary['average_response_time']} sec"
    )

    print()
    print("Provider Usage")
    print("-" * 40)

    for provider, count in (
        summary["provider_usage"].items()
    ):

        print(
            f"{provider}: {count}"
        )

    print()
    print("=" * 60)
    print("PERSISTENT METRICS CHECK COMPLETED")
    print("=" * 60)