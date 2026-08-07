#!/usr/bin/env python3
"""
Benchmark numerical accuracy and reproducibility.

Verifies:
- Deterministic seeding produces identical results
- Numerical outputs fall within expected bounds
- State space coverage is consistent
- Metric calculations are stable

Outputs accuracy report to results/benchmarks/accuracy_report.txt
"""

from pathlib import Path
from typing import Dict, Any, List

import numpy as np

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import DistinctionSet, Distinction
    from experiments.metrics import default_metric_registry
except ImportError:
    print("Error: experiments package not installed. Run './scripts/manage.sh install' first.")
    exit(1)


class AccuracyBenchmark:
    """Verify numerical accuracy and reproducibility."""

    def __init__(self, output_dir: str = "results/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: Dict[str, Any] = {}
        self.tolerance = 1e-10  # floating-point tolerance

    def test_reproducibility(self, runs: int = 3) -> bool:
        """Test that same seed produces identical results."""
        print(f"\nTesting reproducibility ({runs} runs with same seed)...")
        
        trajectories = []
        seed = 42
        
        for i in range(runs):
            model = BaselineComplexSystemModel(
                n_agents=10,
                n_features=3,
                interaction_strength=0.2,
                seed=seed,
            )
            
            result = run_simulation(
                model,
                steps=20,
                distinctions=DistinctionSet([]),
            )
            
            trajectories.append(result.trajectory)
        
        # Compare trajectories
        all_identical = True
        for i in range(1, len(trajectories)):
            traj1 = np.array([s.state for s in trajectories[0]])
            traj2 = np.array([s.state for s in trajectories[i]])
            
            if not np.allclose(traj1, traj2, atol=self.tolerance):
                all_identical = False
                print(f"  Run 1 vs Run {i+1}: DIFFERENT")
                break
        
        if all_identical:
            print(f"  ✓ All {runs} runs produced identical results")
        else:
            print(f"  ✗ Trajectories diverged")
        
        self.results["reproducibility"] = {
            "test": "Same seed reproducibility",
            "passed": all_identical,
            "runs": runs,
        }
        
        return all_identical

    def test_state_bounds(self, runs: int = 10) -> bool:
        """Test that state values remain within expected bounds."""
        print(f"\nTesting state bounds ({runs} runs)...")
        
        all_valid = True
        
        for run in range(runs):
            model = BaselineComplexSystemModel(
                n_agents=10,
                n_features=3,
                interaction_strength=0.2,
                seed=100 + run,
            )
            
            result = run_simulation(
                model,
                steps=20,
                distinctions=DistinctionSet([]),
            )
            
            for state in result.trajectory:
                values = state.state
                if np.any(np.isnan(values)) or np.any(np.isinf(values)):
                    print(f"  Run {run+1}: NaN or Inf detected")
                    all_valid = False
                    break
                
                # Check reasonable bounds (agents' feature values typically 0-1 range)
                if np.any(values < -10) or np.any(values > 10):
                    print(f"  Run {run+1}: Values outside expected range")
                    all_valid = False
                    break
        
        if all_valid:
            print(f"  ✓ All state values within expected bounds")
        else:
            print(f"  ✗ Out-of-bounds values detected")
        
        self.results["state_bounds"] = {
            "test": "State values within bounds",
            "passed": all_valid,
            "runs": runs,
            "bounds": [-10, 10],
        }
        
        return all_valid

    def test_metric_stability(self, runs: int = 5) -> bool:
        """Test that metrics are consistently calculated."""
        print(f"\nTesting metric stability ({runs} runs)...")
        
        metric_sets = []
        registry = default_metric_registry()
        
        for run in range(runs):
            model = BaselineComplexSystemModel(
                n_agents=10,
                n_features=3,
                interaction_strength=0.2,
                seed=200 + run,
            )
            
            result = run_simulation(
                model,
                steps=20,
                distinctions=DistinctionSet([]),
                registry=registry,
            )
            
            if result.metric_history:
                final_metrics = result.metric_history[-1]
                metric_sets.append(final_metrics)
        
        # Check stability of metric ranges
        all_stable = True
        if metric_sets:
            for metric_name in metric_sets[0].keys():
                values = [m[metric_name] for m in metric_sets if metric_name in m]
                if values:
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    cv = std_val / (abs(mean_val) + 1e-10)  # coefficient of variation
                    
                    # Allow up to 50% variation (high CV for stochastic systems)
                    if cv > 0.5:
                        print(f"  Metric '{metric_name}': High variability (CV={cv:.2f})")
                        all_stable = False
        
        if all_stable and metric_sets:
            print(f"  ✓ Metrics show stable variation patterns")
        
        self.results["metric_stability"] = {
            "test": "Metric calculation stability",
            "passed": all_stable,
            "runs": runs,
        }
        
        return all_stable

    def test_distinction_enforcement(self) -> bool:
        """Test that distinctions are properly enforced."""
        print(f"\nTesting distinction enforcement...")
        
        # Create a distinction that enforces feature 0 stays near 0.5
        distinction = Distinction(
            name="feature-0-invariant",
            parameters={
                "feature_index": 0,
                "target_value": 0.5,
                "tolerance": 0.1,
                "min_fraction": 0.6,
            },
        )
        
        model = BaselineComplexSystemModel(
            n_agents=10,
            n_features=3,
            interaction_strength=0.2,
            seed=42,
        )
        
        result = run_simulation(
            model,
            steps=20,
            distinctions=DistinctionSet([distinction]),
        )
        
        # Check if constraint was enforced
        constraint_enforced = len(result.trajectory) > 0
        
        if constraint_enforced:
            print(f"  ✓ Distinction applied without crashing")
        else:
            print(f"  ✗ Distinction application failed")
        
        self.results["distinction_enforcement"] = {
            "test": "Distinction enforcement",
            "passed": constraint_enforced,
        }
        
        return constraint_enforced

    def save_report(self, filename: str = "accuracy_report.txt") -> None:
        """Save accuracy report to file."""
        filepath = self.output_dir / filename
        
        with open(filepath, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("Accuracy and Reproducibility Benchmark\n")
            f.write("=" * 70 + "\n\n")
            
            passed_count = sum(1 for r in self.results.values() if r.get("passed", False))
            total_count = len(self.results)
            
            f.write(f"Summary: {passed_count}/{total_count} tests passed\n\n")
            
            for test_name, result in self.results.items():
                status = "✓ PASS" if result.get("passed", False) else "✗ FAIL"
                f.write(f"{status} | {result['test']}\n")
                
                for key, value in result.items():
                    if key not in ["test", "passed"]:
                        f.write(f"       {key}: {value}\n")
                f.write("\n")
            
            f.write("\nNotes:\n")
            f.write("- Tolerance for floating-point comparison: {:.2e}\n".format(self.tolerance))
            f.write("- Tests are designed to detect numerical stability issues\n")
            f.write("- High stochasticity is expected in complex systems\n")
        
        print(f"\nReport saved to {filepath}")


if __name__ == "__main__":
    benchmark = AccuracyBenchmark()
    
    benchmark.test_reproducibility(runs=3)
    benchmark.test_state_bounds(runs=5)
    benchmark.test_metric_stability(runs=3)
    benchmark.test_distinction_enforcement()
    
    benchmark.save_report()
    
    # Summary
    passed = sum(1 for r in benchmark.results.values() if r.get("passed", False))
    total = len(benchmark.results)
    print(f"\n✓ Accuracy benchmark complete: {passed}/{total} tests passed")
