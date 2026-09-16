import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SYNC_FILE = (
    PROJECT_ROOT
    / "ingestion"
    / "08_knowledge_sync.py"
)


def main():

    print("=" * 60)
    print("ZYRA LUXE - SCHEDULED KNOWLEDGE SYNC")
    print("=" * 60)

    print(
        f"Running: {SYNC_FILE}"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SYNC_FILE)
        ],
        cwd=PROJECT_ROOT,
        check=False
    )

    print()
    print(
        f"Sync process finished "
        f"with exit code: {result.returncode}"
    )

    if result.returncode != 0:
        raise SystemExit(
            result.returncode
        )


if __name__ == "__main__":
    main()