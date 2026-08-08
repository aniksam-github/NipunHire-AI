"""CLI entry point for running NipunHire AI evaluation pipeline.

Usage:
    python -m eval.run_evaluation
    python -m eval.run_evaluation --feature resume_matching
    python -m eval.run_evaluation --skip-judge --verbose
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path if invoked directly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from eval.runner import EvaluationRunner, load_previous_run


def format_report(current_run, previous_run=None, verbose: bool = False) -> str:
    """Format evaluation run report into a clear console summary."""
    lines = []
    lines.append("=" * 80)
    lines.append(" NIPUNHIRE AI FEATURE EVALUATION REPORT ")
    lines.append("=" * 80)
    lines.append(f"Run ID:         {current_run.run_id}")
    lines.append(f"Timestamp:      {current_run.timestamp}")
    lines.append(f"Model Version:  {current_run.model_version}")
    lines.append(f"Duration:       {current_run.duration_seconds} seconds")
    lines.append("-" * 80)

    # Feature Breakdown
    feature_counts: dict[str, dict[str, int]] = {}
    for res in current_run.results:
        feat = res.feature.value
        if feat not in feature_counts:
            feature_counts[feat] = {"total": 0, "passed": 0, "failed": 0}
        feature_counts[feat]["total"] += 1
        if res.passed:
            feature_counts[feat]["passed"] += 1
        else:
            feature_counts[feat]["failed"] += 1

    lines.append("FEATURE SUMMARY:")
    for feat, counts in feature_counts.items():
        rate = (counts['passed'] / counts['total']) * 100 if counts['total'] > 0 else 0
        lines.append(
            f"  * {feat:<20}: {counts['passed']}/{counts['total']} passed ({rate:.1f}%)"
        )
    lines.append("-" * 80)

    # Test Cases Detail
    lines.append("TEST CASE RESULTS:")
    for res in current_run.results:
        status_tag = "[ PASS ]" if res.passed else "[ FAIL ]"
        lines.append(f"  {status_tag} {res.case_id:<32} ({res.execution_time_seconds:.2f}s) - {res.description[:45]}")

        if not res.passed or verbose:
            if res.error:
                lines.append(f"            +-- ERROR: {res.error}")
            for check in res.deterministic_checks:
                if not check.passed or verbose:
                    chk_tag = "PASS" if check.passed else "FAIL"
                    lines.append(f"            +-- [{chk_tag}] {check.name}: {check.message}")
            if res.ai_judge_check:
                if not res.ai_judge_check.passed or verbose:
                    judge_tag = "PASS" if res.ai_judge_check.passed else "FAIL"
                    lines.append(f"            +-- [{judge_tag}] AI Judge: {res.ai_judge_check.message}")

    lines.append("-" * 80)

    # Aggregate Pass Rate & Token Usage
    tokens = current_run.token_usage
    lines.append("AGGREGATE METRICS:")
    lines.append(f"  * Total Test Cases : {current_run.total_cases}")
    lines.append(f"  * Passed Cases     : {current_run.passed_cases}")
    lines.append(f"  * Failed Cases     : {current_run.failed_cases}")
    lines.append(f"  * Aggregate Pass Rate: {current_run.aggregate_pass_rate:.2f}%")
    lines.append("")
    lines.append("TOKEN USAGE & COST ESTIMATION:")
    lines.append(f"  * Prompt Tokens    : {tokens.prompt_tokens:,}")
    lines.append(f"  * Completion Tokens: {tokens.completion_tokens:,}")
    lines.append(f"  * Total Tokens     : {tokens.total_tokens:,}")
    lines.append(f"  * Estimated Cost   : ${tokens.estimated_cost_usd:.6f} USD")
    lines.append("-" * 80)

    # Comparison with Previous Run
    if previous_run:
        lines.append("HISTORICAL COMPARISON (vs Previous Run):")
        delta = current_run.aggregate_pass_rate - previous_run.aggregate_pass_rate
        sign = "+" if delta >= 0 else ""
        lines.append(f"  * Previous Pass Rate: {previous_run.aggregate_pass_rate:.2f}%")
        lines.append(f"  * Pass Rate Change  : {sign}{delta:.2f}%")

        # Regressions & Fixes tracking
        prev_results_map = {r.case_id: r.passed for r in previous_run.results}
        regressions = []
        fixes = []
        for curr_res in current_run.results:
            if curr_res.case_id in prev_results_map:
                was_passed = prev_results_map[curr_res.case_id]
                is_passed = curr_res.passed
                if was_passed and not is_passed:
                    regressions.append(curr_res.case_id)
                elif not was_passed and is_passed:
                    fixes.append(curr_res.case_id)

        if regressions:
            lines.append(f"  [REGRESSIONS DETECTED] ({len(regressions)}):")
            for cid in regressions:
                lines.append(f"     - {cid}")
        else:
            lines.append("  * Regressions: None")

        if fixes:
            lines.append(f"  [RECOVERED / FIXED] ({len(fixes)}):")
            for cid in fixes:
                lines.append(f"     - {cid}")

        lines.append("-" * 80)
    else:
        lines.append("HISTORICAL COMPARISON: First recorded run (no previous run found)")
        lines.append("-" * 80)

    lines.append("=" * 80)
    return "\n".join(lines)


async def main_async() -> int:
    parser = argparse.ArgumentParser(description="NipunHire AI Feature Evaluation Pipeline Runner")
    parser.add_argument(
        "--feature",
        "-f",
        choices=["resume_parsing", "resume_matching", "resume_screening"],
        default=None,
        help="Filter evaluation to a single feature",
    )
    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Skip AI-judge subjective evaluation calls for fast deterministic testing",
    )
    parser.add_argument(
        "--no-mock",
        action="store_true",
        help="Disable mock fallback and force live OpenAI API calls",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display detailed check-level outputs for all test cases",
    )

    args = parser.parse_args()

    previous_run = load_previous_run()
    runner = EvaluationRunner(use_mock_fallback=not args.no_mock)

    try:
        run_report = await runner.run_evaluation(
            feature_filter=args.feature,
            skip_judge=args.skip_judge,
        )
        report_str = format_report(run_report, previous_run, verbose=args.verbose)
        print(report_str)

        # Return exit code 0 if all cases passed, non-zero if failures occurred
        return 0 if run_report.failed_cases == 0 else 1

    except Exception as exc:
        print(f"\n❌ Evaluation Runner Failed: {exc}\n", file=sys.stderr)
        return 2


def main() -> None:
    exit_code = asyncio.run(main_async())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
