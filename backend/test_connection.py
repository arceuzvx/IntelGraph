"""
IntelGraph — Connection test.

Connects to the VectorAI DB server and prints health information.

Documentation references:
    client.health_check():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/get-collection-info-task
        Section: "Run a health check"
        Returns: dict with 'title' and 'version' keys.

    VectorAIClient context manager:
        https://docs.vectoraidb.actian.com/sdks/python/reference
        "Use VectorAIClient for synchronous code"
"""

from actian_vectorai import VectorAIClient, VectorAIError

from constants import VECTORAI_HOST


def main() -> None:
    """Connect to VectorAI DB and print server health information."""
    try:
        with VectorAIClient(VECTORAI_HOST) as client:
            health = client.health_check()

            print("Connection successful.")
            print(f"  Title:   {health['title']}")
            print(f"  Version: {health['version']}")

    except VectorAIError as exc:
        print(f"Connection failed: {exc.message}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()