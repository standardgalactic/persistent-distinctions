#!/usr/bin/env python3
"""
Benchmark execution time across system sizes.

Measures wall-clock time for simulations at varying scales:
- Number of agents (n_agents)
- Number of features (n_features)
- Simulation steps

Outputs timing data to results/benchmarks/runtime_results.csv
"""

import csv
import time
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import DistinctionSet
except ImportError:
    print("Error: experiments package not installed. Run './scripts/manage.sh install' first.")
    exit(1)


class RuntimeBenchmark:
    """Measure execution time across various system sizes."""

    def __init__(self, output_dir: str = "results/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[Dict[str, Any]] = []

    def benchmark_agents(self, agent_counts: List[int], steps: int = 50, runs: int = 3) -> None:
        """Benchmark with varying agent counts."""
        print(f"\nBenchmarking agent scaling ({len(agent_counts)} sizes, {runs} runs each)...")
        
        for n_agents in agent_counts:
            times = []
            for run in range(runs):
                try:
                    model = BaselineComplexSystemModel(
                        n_agents=n_agents,
                        n_features=3,
                        interaction_strength=0.2,
                        seed=42 + run,
                    )
                    
                    start = time.perf_counter()
                    result = run_simulation(
                        model,
                        steps=steps,
                        distinctions=DistinctionSet([]),
                    )
                    elapsed = time.perf_counter() - start
                    
                    times.append(elapsed)
                    print(f"  n_agents={n_agents}, run={run+1}: {elapsed:.4f}s")
                except Exception as e:
                    print(f"  n_agents={n_agents}, run={run+1}: ERROR - {e}")
            
            if times:
                self.results.append({
                    "dimension": "agents",
                    "size": n_agents,
                    "steps": steps,
                    "runs": len(times),
                    "mean_time_s": np.mean(times),
                    "std_time_s": np.std(times),
                    "min_time_s": np.min(times),
                    "max_time_s": np.max(times),
                })

    def benchmark_features(self, feature_counts: List[int], steps: int = 50, runs: int = 3) -> None:
        """Benchmark with varying feature counts."""
        print(f"\nBenchmarking feature scaling ({len(feature_counts)} sizes, {runs} runs each)...")
        
        for n_features in feature_counts:
            times = []
            for run in range(runs):
                try:
                    model = BaselineComplexSystemModel(
                        n_agents=10,
                        n_features=n_features,
                        interaction_strength=0.2,
                        seed=42 + run,
                    )
                    
                    start = time.perf_counter()
                    result = run_simulation(
                        model,
                        steps=steps,
                        distinctions=DistinctionSet([]),
                    )
                    elapsed = time.perf_counter() - start
                    
                    times.append(elapsed)
                    print(f"  n_features={n_features}, run={run+1}: {elapsed:.4f}s")
                except Exception as e:
                    print(f"  n_features={n_features}, run={run+1}: ERROR - {e}")
            
            if times:
                self.results.append({
                    "dimension": "features",
                    "size": n_features,
                    "steps": steps,
                    "runs": len(times),
                    "mean_time_s": np.mean(times),
                    "std_time_s": np.std(times),
                    "min_time_s": np.min(times),
                    "max_time_s": np.max(times),
                })

    def benchmark_steps(self, step_counts: List[int], runs: int = 3) -> None:
        """Benchmark with varying simulation steps."""
        print(f"\nBenchmarking step scaling ({len(step_counts)} sizes, {runs} runs each)...")
        
        for steps in step_counts:
            times = []
            for run in range(runs):
                try:
                    model = BaselineComplexSystemModel(
                        n_agents=10,
                        n_features=3,
                        interaction_strength=0.2,
                        seed=42 + run,
                    )
                    
                    start = time.perf_counter()
                    result = run_simulation(
                        model,
                        steps=steps,
                        distinctions=DistinctionSet([]),
                    )
                    elapsed = time.perf_counter() - start
                    
                    times.append(elapsed)
                    print(f"  steps={steps}, run={run+1}: {elapsed:.4f}s")
                except Exception as e:
                    print(f"  steps={steps}, run={run+1}: ERROR - {e}")
            
            if times:
                self.results.append({
                    "dimension": "steps",
                    "size": steps,
                    "steps": steps,
                    "runs": len(times),
                    "mean_time_s": np.mean(times),
                    "std_time_s": np.std(times),
                    "min_time_s": np.min(times),
                    "max_time_s": np.max(times),
                })

    def save_results(self, filename: str = "runtime_results.csv") -> None:
        """Save results to CSV."""
        filepath = self.output_dir / filename
        
        if not self.results:
            print("No results to save.")
            return
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"\nResults saved to {filepath}")


if __name__ == "__main__":
    benchmark = RuntimeBenchmark()
    
    # Test with small ranges first
    benchmark.benchmark_agents([5, 10, 20, 40], steps=30, runs=2)
    benchmark.benchmark_features([2, 3, 5, 8], steps=30, runs=2)
    benchmark.benchmark_steps([10, 25, 50, 100], runs=2)
    
    benchmark.save_results()
    print("\n✓ Runtime benchmark complete")
