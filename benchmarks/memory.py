#!/usr/bin/env python3
"""
Benchmark memory usage across system sizes.

Profiles peak memory consumption for simulations at varying scales using:
- psutil for system memory tracking
- tracemalloc for Python memory allocation

Outputs memory data to results/benchmarks/memory_results.csv
"""

import csv
import tracemalloc
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

try:
    import psutil
except ImportError:
    print("Error: psutil not installed. Run: pip install psutil")
    exit(1)

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import DistinctionSet
except ImportError:
    print("Error: experiments package not installed. Run './scripts/manage.sh install' first.")
    exit(1)


class MemoryBenchmark:
    """Profile memory usage across various system sizes."""

    def __init__(self, output_dir: str = "results/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[Dict[str, Any]] = []
        self.process = psutil.Process()

    def measure_memory(self, n_agents: int, n_features: int, steps: int) -> Tuple[float, float]:
        """Measure peak memory usage for a single simulation."""
        # Warm up
        self.process.memory_info()
        
        tracemalloc.start()
        baseline_mem = self.process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            model = BaselineComplexSystemModel(
                n_agents=n_agents,
                n_features=n_features,
                interaction_strength=0.2,
                seed=42,
            )
            
            result = run_simulation(
                model,
                steps=steps,
                distinctions=DistinctionSet([]),
            )
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            peak_mem = self.process.memory_info().rss / 1024 / 1024  # MB
            delta_mem = peak_mem - baseline_mem
            
            return peak_mem, delta_mem
        except Exception as e:
            tracemalloc.stop()
            raise e

    def benchmark_agents(self, agent_counts: List[int], steps: int = 30) -> None:
        """Benchmark memory with varying agent counts."""
        print(f"\nBenchmarking agent memory usage ({len(agent_counts)} sizes)...")
        
        for n_agents in agent_counts:
            try:
                peak_mem, delta_mem = self.measure_memory(n_agents, 3, steps)
                print(f"  n_agents={n_agents}: peak={peak_mem:.1f} MB, delta={delta_mem:.1f} MB")
                
                self.results.append({
                    "dimension": "agents",
                    "size": n_agents,
                    "n_features": 3,
                    "steps": steps,
                    "peak_memory_mb": peak_mem,
                    "delta_memory_mb": delta_mem,
                })
            except Exception as e:
                print(f"  n_agents={n_agents}: ERROR - {e}")

    def benchmark_features(self, feature_counts: List[int], steps: int = 30) -> None:
        """Benchmark memory with varying feature counts."""
        print(f"\nBenchmarking feature memory usage ({len(feature_counts)} sizes)...")
        
        for n_features in feature_counts:
            try:
                peak_mem, delta_mem = self.measure_memory(10, n_features, steps)
                print(f"  n_features={n_features}: peak={peak_mem:.1f} MB, delta={delta_mem:.1f} MB")
                
                self.results.append({
                    "dimension": "features",
                    "size": n_features,
                    "n_agents": 10,
                    "steps": steps,
                    "peak_memory_mb": peak_mem,
                    "delta_memory_mb": delta_mem,
                })
            except Exception as e:
                print(f"  n_features={n_features}: ERROR - {e}")

    def benchmark_steps(self, step_counts: List[int]) -> None:
        """Benchmark memory with varying simulation steps."""
        print(f"\nBenchmarking step memory usage ({len(step_counts)} sizes)...")
        
        for steps in step_counts:
            try:
                peak_mem, delta_mem = self.measure_memory(10, 3, steps)
                print(f"  steps={steps}: peak={peak_mem:.1f} MB, delta={delta_mem:.1f} MB")
                
                self.results.append({
                    "dimension": "steps",
                    "size": steps,
                    "n_agents": 10,
                    "n_features": 3,
                    "peak_memory_mb": peak_mem,
                    "delta_memory_mb": delta_mem,
                })
            except Exception as e:
                print(f"  steps={steps}: ERROR - {e}")

    def save_results(self, filename: str = "memory_results.csv") -> None:
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
    benchmark = MemoryBenchmark()
    
    # Test with small ranges
    benchmark.benchmark_agents([5, 10, 20], steps=20)
    benchmark.benchmark_features([2, 3, 5], steps=20)
    benchmark.benchmark_steps([10, 25, 50], )
    
    benchmark.save_results()
    print("\n✓ Memory benchmark complete")
