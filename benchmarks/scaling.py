#!/usr/bin/env python3
"""
Analyze algorithmic scaling behavior.

Fits timing data to power-law models: T(n) = a * n^b
Estimates computational complexity and predicts performance at larger scales.

Outputs scaling analysis to results/benchmarks/scaling_analysis.txt
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np
from numpy.polynomial import Polynomial


class ScalingAnalysis:
    """Analyze computational complexity from timing data."""

    def __init__(self, output_dir: str = "results/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[Dict[str, Any]] = []

    @staticmethod
    def fit_power_law(sizes: List[float], times: List[float]) -> Tuple[float, float, float]:
        """
        Fit data to power-law model: T(n) = a * n^b
        
        Returns:
            (a, b, r2): coefficient, exponent, R-squared fit quality
        """
        if len(sizes) < 2:
            return 0.0, 0.0, 0.0
        
        log_sizes = np.log(sizes)
        log_times = np.log(times)
        
        # Linear regression in log-log space
        coeffs = np.polyfit(log_sizes, log_times, 1)
        poly = Polynomial.fit(log_sizes, log_times, 1)
        
        b = coeffs[0]  # exponent
        log_a = coeffs[1]  # log(coefficient)
        a = np.exp(log_a)
        
        # R-squared
        y_pred = poly(log_sizes)
        ss_res = np.sum((log_times - y_pred) ** 2)
        ss_tot = np.sum((log_times - np.mean(log_times)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return a, b, r2

    @staticmethod
    def complexity_label(exponent: float) -> str:
        """Describe computational complexity based on exponent."""
        if abs(exponent) < 0.5:
            return "O(1) - Constant"
        elif abs(exponent - 1.0) < 0.3:
            return "O(n) - Linear"
        elif abs(exponent - 1.5) < 0.3:
            return "O(n^1.5) - Superlinear"
        elif abs(exponent - 2.0) < 0.3:
            return "O(n²) - Quadratic"
        elif abs(exponent - 3.0) < 0.3:
            return "O(n³) - Cubic"
        else:
            return f"O(n^{exponent:.2f}) - Power-law"

    def analyze_agent_scaling(self, sizes: List[float], times: List[float]) -> None:
        """Analyze scaling with respect to agent count."""
        if len(sizes) < 2:
            print("Insufficient data for agent scaling analysis")
            return
        
        a, b, r2 = self.fit_power_law(sizes, times)
        complexity = self.complexity_label(b)
        
        result = {
            "dimension": "agents",
            "coefficient_a": a,
            "exponent_b": b,
            "r_squared": r2,
            "complexity": complexity,
            "model": f"T(n) = {a:.4e} * n^{b:.2f}",
        }
        self.results.append(result)
        
        print(f"\n=== Agent Count Scaling ===")
        print(f"Model: {result['model']}")
        print(f"Complexity: {complexity}")
        print(f"Fit quality (R²): {r2:.4f}")

    def analyze_feature_scaling(self, sizes: List[float], times: List[float]) -> None:
        """Analyze scaling with respect to feature count."""
        if len(sizes) < 2:
            print("Insufficient data for feature scaling analysis")
            return
        
        a, b, r2 = self.fit_power_law(sizes, times)
        complexity = self.complexity_label(b)
        
        result = {
            "dimension": "features",
            "coefficient_a": a,
            "exponent_b": b,
            "r_squared": r2,
            "complexity": complexity,
            "model": f"T(n) = {a:.4e} * n^{b:.2f}",
        }
        self.results.append(result)
        
        print(f"\n=== Feature Count Scaling ===")
        print(f"Model: {result['model']}")
        print(f"Complexity: {complexity}")
        print(f"Fit quality (R²): {r2:.4f}")

    def predict_time(self, dimension: str, a: float, b: float, size: float) -> float:
        """Predict execution time at a given size."""
        return a * (size ** b)

    def save_results(self, filename: str = "scaling_analysis.txt") -> None:
        """Save analysis to text file."""
        filepath = self.output_dir / filename
        
        with open(filepath, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("Algorithmic Scaling Analysis\n")
            f.write("=" * 70 + "\n\n")
            
            for result in self.results:
                f.write(f"Dimension: {result['dimension'].upper()}\n")
                f.write(f"Model: {result['model']}\n")
                f.write(f"Complexity: {result['complexity']}\n")
                f.write(f"Fit Quality (R²): {result['r_squared']:.4f}\n")
                f.write("\n")
            
            f.write("\nInterpretation:\n")
            f.write("- R² close to 1.0 indicates good fit to power-law model\n")
            f.write("- Exponent b describes algorithmic complexity\n")
            f.write("- Linear (b≈1) is best, quadratic (b≈2) or worse requires optimization\n")
        
        print(f"\nAnalysis saved to {filepath}")


if __name__ == "__main__":
    print("Scaling analysis requires pre-computed timing data.")
    print("Run 'python benchmarks/runtime.py' first to generate timing data.")
    print("\nExample usage:")
    print("  analysis = ScalingAnalysis()")
    print("  analysis.analyze_agent_scaling([5, 10, 20, 40], [0.1, 0.2, 0.4, 0.8])")
    print("  analysis.save_results()")
