"""CRUD operations for test_files table."""

from uuid import uuid4
from db.client import get_supabase_client


async def create_test_file_records(
    run_id: str,
    generated_tests: dict[str, str],
    test_results: list[dict],
):
    """Batch insert test file records for a run."""
    client = get_supabase_client()
    results_by_file = {r["source_file"]: r for r in test_results}

    records = []
    for source_file, test_content in generated_tests.items():
        result = results_by_file.get(source_file, {})
        records.append({
            "id": str(uuid4()),
            "run_id": run_id,
            "source_file": source_file,
            "test_file_path": f"tests/test_{source_file.split('/')[-1]}",
            "test_content": test_content,
            "tests_passed": result.get("passed", 0),
            "tests_failed": result.get("failed", 0),
            "coverage_pct": result.get("coverage_pct", 0.0),
        })

    if records:
        client.table("test_files").insert(records).execute()
