from compare import results_to_rows, run_phase1_suite, summarize_rows


def test_comparison_suite_contains_all_required_configurations(small_environment):
    results = run_phase1_suite(small_environment, seed=5, quick=True)
    assert len(results) == 11
    rows = results_to_rows(results, 5)
    summary = summarize_rows(rows)
    assert len(summary) == 11
    assert {row["family"] for row in summary} == {"uninformed", "informed", "local"}
