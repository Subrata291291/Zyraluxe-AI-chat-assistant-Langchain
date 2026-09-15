import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MONITORING_DIR = (
    PROJECT_ROOT
    / "data"
    / "monitoring"
)

REQUEST_FILE = MONITORING_DIR / "requests.json"
ERROR_FILE = MONITORING_DIR / "errors.json"


class MonitoringDashboard:

    def __init__(
        self,
        request_file=REQUEST_FILE,
        error_file=ERROR_FILE
    ):

        self.request_file = request_file
        self.error_file = error_file

    def load_json(self, file_path):

        if not file_path.exists():

            return []

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def build_summary(self):

        requests = self.load_json(
            self.request_file
        )

        errors = self.load_json(
            self.error_file
        )

        successful = sum(
            1
            for request in requests
            if request["success"]
        )

        failed = sum(
            1
            for request in requests
            if not request["success"]
        )

        total_requests = len(requests)

        success_rate = 0

        if total_requests:

            success_rate = round(
                (successful / total_requests) * 100,
                2
            )

        average_response_time = 0

        if requests:

            total_time = sum(
                request["response_time"]
                for request in requests
            )

            average_response_time = round(
                total_time / total_requests,
                3
            )

        provider_usage = Counter(
            request["provider"]
            for request in requests
        )

        error_types = Counter(
            error["error_type"]
            for error in errors
        )

        provider_errors = Counter(
            error["provider"]
            for error in errors
        )

        return {
            "requests": {
                "total": total_requests,
                "successful": successful,
                "failed": failed,
                "success_rate": success_rate,
                "average_response_time": (
                    average_response_time
                )
            },
            "providers": dict(provider_usage),
            "errors": {
                "total": len(errors),
                "types": dict(error_types),
                "providers": dict(provider_errors)
            }
        }


if __name__ == "__main__":

    dashboard = MonitoringDashboard()

    summary = dashboard.build_summary()

    print("=" * 60)
    print("ZYRA LUXE - MONITORING DASHBOARD")
    print("=" * 60)

    print()
    print("REQUESTS")
    print("-" * 40)

    print(
        f"Total: "
        f"{summary['requests']['total']}"
    )

    print(
        f"Successful: "
        f"{summary['requests']['successful']}"
    )

    print(
        f"Failed: "
        f"{summary['requests']['failed']}"
    )

    print(
        f"Success Rate: "
        f"{summary['requests']['success_rate']}%"
    )

    print(
        f"Average Response Time: "
        f"{summary['requests']['average_response_time']} sec"
    )

    print()
    print("PROVIDER USAGE")
    print("-" * 40)

    for provider, count in (
        summary["providers"].items()
    ):

        print(
            f"{provider}: {count}"
        )

    print()
    print("ERRORS")
    print("-" * 40)

    print(
        f"Total Errors: "
        f"{summary['errors']['total']}"
    )

    print()
    print("Error Types")

    for error_type, count in (
        summary["errors"]["types"].items()
    ):

        print(
            f"{error_type}: {count}"
        )

    print()
    print("Error Providers")

    for provider, count in (
        summary["errors"]["providers"].items()
    ):

        print(
            f"{provider}: {count}"
        )

    print()
    print("=" * 60)
    print("MONITORING DASHBOARD CHECK COMPLETED")
    print("=" * 60)