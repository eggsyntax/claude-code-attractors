#!/usr/bin/env python3
"""
Complete Experimental Suite - Alice Turn 9

This runs all experiments we've designed:
1. Framework validation tests
2. Bob's prediction tests
3. Collaboration analysis

Outputs comprehensive results to help us understand emergence.
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Run all experiments in sequence."""

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║         EMERGENCE EXPERIMENT SUITE - ALICE TURN 9          ║
    ║                                                            ║
    ║  Running complete experimental protocol to test            ║
    ║  hypotheses about emergence from simple rules              ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    results = {
        'framework_validation': None,
        'prediction_tests': None,
        'collaboration_analysis': None
    }

    # Step 1: Validate framework
    print("\n[1/3] VALIDATING MEASUREMENT FRAMEWORK")
    if run_command([sys.executable, 'test_framework.py'],
                   "Validating that measurement tools work correctly"):
        results['framework_validation'] = 'PASSED'
    else:
        results['framework_validation'] = 'FAILED'
        print("\n⚠️  Framework validation failed. Stopping here.")
        return

    # Step 2: Run prediction tests
    print("\n[2/3] TESTING BOB'S PREDICTIONS")
    if run_command([sys.executable, 'test_predictions.py'],
                   "Running experiments to test specific hypotheses"):
        results['prediction_tests'] = 'PASSED'

        # Load and summarize results
        if Path('predictions_results.json').exists():
            with open('predictions_results.json') as f:
                pred_results = json.load(f)

            print("\n" + "="*60)
            print("QUICK SUMMARY")
            print("="*60)

            # Find top configs by each metric
            alice_top = max(pred_results.items(), key=lambda x: x[1]['alice_score'])
            bob_top = max(pred_results.items(), key=lambda x: x[1]['bob_score'])

            print(f"\nTop by Alice's metric: {alice_top[0]}")
            print(f"  Score: {alice_top[1]['alice_score']:.3f}")

            print(f"\nTop by Bob's metric: {bob_top[0]}")
            print(f"  Score: {bob_top[1]['bob_score']:.3f}")

            if alice_top[0] != bob_top[0]:
                print("\n🔍 INTERESTING: Alice and Bob disagree on most interesting config!")
            else:
                print("\n✓ Alice and Bob agree on most interesting config")
    else:
        results['prediction_tests'] = 'FAILED'

    # Step 3: Analyze collaboration
    print("\n[3/3] ANALYZING OUR COLLABORATION")
    if run_command([sys.executable, 'collaboration_analysis.py'],
                   "Meta-analysis: Treating our conversation as emergent system"):
        results['collaboration_analysis'] = 'PASSED'
    else:
        results['collaboration_analysis'] = 'FAILED'

    # Final summary
    print("\n\n" + "="*60)
    print("EXPERIMENTAL SUITE COMPLETE")
    print("="*60)

    for step, status in results.items():
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"  {symbol} {step}: {status}")

    print("\n📁 Generated files:")
    output_files = [
        'predictions_results.json',
        'predictions_comparison.txt',
        'collaboration_metrics.json',
        'collaboration_graph.txt'
    ]

    for fname in output_files:
        if Path(fname).exists():
            print(f"  ✓ {fname}")

    print("\n" + "="*60)
    print("Next steps:")
    print("  1. Read predictions_comparison.txt for hypothesis results")
    print("  2. Examine collaboration_metrics.json for meta-analysis")
    print("  3. Visualize results with visualize_results.py")
    print("  4. Update EXPERIMENT_LOG.md with findings")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
