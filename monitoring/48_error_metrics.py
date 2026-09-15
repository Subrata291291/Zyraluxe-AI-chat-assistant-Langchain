import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ERROR_FILE = (
    PROJECT_ROOT
    / "data"
    / "monitoring"
    / "errors.json"
)


class ErrorMetrics:

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

    def total_errors(self):

        return len(self.errors)

    def error_type_usage(self):

        return Counter(
            error["error_type"]
            for error in self.errors
        )

    def provider_failures(self):

        return Counter(
            error["provider"]
            for error in self.errors
        )

    def model_failures(self):

        return Counter(
            error["model"]
            for error in self.errors
        )

    def get_summary(self):

        self.errors = self.load_errors()

        return {
            "total_errors": self.total_errors(),
            "error_types": dict(
                self.error_type_usage()
            ),
            "provider_failures": dict(
                self.provider_failures()
            ),
            "model_failures": dict(
                self.model_failures()
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - ERROR METRICS")
    print("=" * 60)

    metrics = ErrorMetrics()

    summary = metrics.get_summary()

    print()
    print(f"Data Source: {ERROR_FILE}")

    print()
    print(
        f"Total Errors: "
        f"{summary['total_errors']}"
    )

    print()
    print("Error Type Usage")
    print("-" * 40)

    for error_type, count in (
        summary["error_types"].items()
    ):

        print(
            f"{error_type}: {count}"
        )

    print()
    print("Provider Failures")
    print("-" * 40)

    for provider, count in (
        summary["provider_failures"].items()
    ):

        print(
            f"{provider}: {count}"
        )

    print()
    print("Model Failures")
    print("-" * 40)

    for model, count in (
        summary["model_failures"].items()
    ):

        print(
            f"{model}: {count}"
        )

    print()
    print("=" * 60)
    print("ERROR METRICS CHECK COMPLETED")
    print("=" * 60)