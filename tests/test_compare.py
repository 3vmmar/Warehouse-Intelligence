from compare import results_to_rows, run_search_suite, summarize_rows


def test_comparison_suite_contains_all_required_configurations(small_environment):
    results = run_search_suite(small_environment, seed=5, quick=True)
    assert len(results) == 11
    rows = results_to_rows(results, 5)
    summary = summarize_rows(rows)
    assert len(summary) == 11
    assert {row["family"] for row in summary} == {"uninformed", "informed", "local"}
    assert all(row["mean_memory_units"] > 0 for row in summary)
    assert all(row["std_memory_units"] >= 0 for row in summary)
    expected = sum(row["memory_units"] for row in rows if row["algorithm"] == "bfs")
    assert (
        next(row for row in summary if row["algorithm"] == "bfs")["mean_memory_units"] == expected
    )
