#!/usr/bin/env python3
"""
Side-by-side comparison of baseline vs. distinction models.

Demonstrates:
- Running multiple models with different configurations
- Computing metrics for both conditions
- Comparing outcomes quantitatively
- Interpreting results
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import Distinction, DistinctionSet
    from experiments.metrics import default_metric_registry
except ImportError:
    print("Error: experiments package not installed.")
    print("Run: ./scripts/manage.sh install")
    sys.exit(1)


def run_condition(name, distinction_set, n_agents=20, n_features=3, steps=100, seed=42):
    """Run a single experimental condition and return results."""
    print(f"\n  Running {name}...")
    
    model = BaselineComplexSystemModel(
        n_agents=n_agents,
        n_features=n_features,
        interaction_strength=0.3,
        seed=seed,
    )
    
    result = run_simulation(
        model,
        steps=steps,
        distinctions=distinction_set,
        registry=default_metric_registry(),
    )
    
    return result


def compute_metrics(result, label):
    """Compute summary metrics from a simulation result."""
    trajectory = np.array([s.state for s in result.trajectory])
    
    metrics = {
        "label": label,
        "steps": len(result.trajectory),
        "mean_state": np.mean(trajectory),
        "std_state": np.std(trajectory),
        "min_state": np.min(trajectory),
        "max_state": np.max(trajectory),
        "state_range": np.max(trajectory) - np.min(trajectory),
    }
    
    # Divergence from initial
    initial = trajectory[0]
    final = trajectory[-1]
    metrics["divergence"] = np.linalg.norm(final - initial)
    
    # Stability (inverse of trajectory variance)
    state_variance = np.var(trajectory, axis=0)
    metrics["stability"] = 1.0 / (1.0 + np.mean(state_variance))
    
    return metrics


def main():
    print("=" * 70)
    print("Example: Baseline vs. Distinction Comparison")
    print("=" * 70)
    
    print(f"\nConfiguration:")
    print(f"  Agents: 20")
    print(f"  Features per agent: 3")
    print(f"  Steps: 100")
    print(f"  Random seed: 42")
    
    # Define conditions
    conditions = {
        "Baseline (No Constraint)": DistinctionSet([]),
        "With Distinction (Feature 0 @ 0.5)": DistinctionSet([
            Distinction(
                name="feature-0-invariant",
                parameters={
                    "feature_index": 0,
                    "target_value": 0.5,
                    "tolerance": 0.15,
                    "min_fraction": 0.6,
                },
            )
        ]),
        "With Distinction (Feature 1 @ 0.3)": DistinctionSet([
            Distinction(
                name="feature-1-invariant",
                parameters={
                    "feature_index": 1,
                    "target_value": 0.3,
                    "tolerance": 0.15,
                    "min_fraction": 0.6,
                },
            )
        ]),
    }
    
    # Run experiments
    print(f"\nRunning experiments...")
    results = {}
    for condition_name, distinction_set in conditions.items():
        result = run_condition(condition_name, distinction_set)
        results[condition_name] = result
    
    # Compute metrics
    print(f"\nComputing metrics...")
    all_metrics = {}
    for condition_name, result in results.items():
        metrics = compute_metrics(result, condition_name)
        all_metrics[condition_name] = metrics
        
        print(f"\n  {condition_name}:")
        print(f"    Mean state: {metrics['mean_state']:.4f}")
        print(f"    Std state: {metrics['std_state']:.4f}")
        print(f"    Divergence: {metrics['divergence']:.4f}")
        print(f"    Stability: {metrics['stability']:.4f}")
    
    # Visualize
    try:
        print(f"\nGenerating visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Baseline vs. Distinction Comparison", fontsize=14, fontweight='bold')
        
        colors = ['blue', 'orange', 'green']
        
        # Plot 1: Mean state over time
        ax = axes[0, 0]
        for (condition_name, result), color in zip(results.items(), colors):
            trajectory = np.array([s.state for s in result.trajectory])
            mean_trajectory = np.mean(trajectory, axis=1)
            ax.plot(mean_trajectory, linewidth=2, label=condition_name, alpha=0.7, color=color)
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean State Value")
        ax.set_title("Mean State Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: State variance over time
        ax = axes[0, 1]
        for (condition_name, result), color in zip(results.items(), colors):
            trajectory = np.array([s.state for s in result.trajectory])
            variance = np.var(trajectory, axis=1)
            ax.plot(variance, linewidth=2, label=condition_name, alpha=0.7, color=color)
        ax.set_xlabel("Step")
        ax.set_ylabel("Variance")
        ax.set_title("State Variance Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Metric comparison
        ax = axes[1, 0]
        metric_names = list(all_metrics[list(all_metrics.keys())[0]].keys())
        metric_names = [m for m in metric_names if m not in ['label', 'steps']]
        
        # Normalize metrics for comparison
        normalized_metrics = {}
        for metric_name in metric_names:
            values = [all_metrics[cond][metric_name] for cond in all_metrics.keys()]
            max_val = max(values) if max(values) != 0 else 1
            normalized_metrics[metric_name] = [v / max_val for v in values]
        
        x = np.arange(len(all_metrics))
        width = 0.15
        
        for i, metric_name in enumerate(metric_names[:4]):  # Show first 4 metrics
            offset = (i - 1.5) * width
            values = [normalized_metrics[metric_name][j] for j in range(len(all_metrics))]
            ax.bar(x + offset, values, width, label=metric_name, alpha=0.7)
        
        ax.set_xlabel("Condition")
        ax.set_ylabel("Normalized Value")
        ax.set_title("Metric Comparison (Normalized)")
        ax.set_xticks(x)
        ax.set_xticklabels([name.split('(')[0].strip() for name in all_metrics.keys()], rotation=15)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Distribution comparison
        ax = axes[1, 1]
        for (condition_name, result), color in zip(results.items(), colors):
            trajectory = np.array([s.state for s in result.trajectory])
            ax.hist(trajectory.flatten(), bins=30, alpha=0.4, label=condition_name, color=color, density=True)
        ax.set_xlabel("State Value")
        ax.set_ylabel("Frequency (normalized)")
        ax.set_title("State Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save figure
        output_path = Path("results/examples/comparison_output.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        print(f"  Visualization saved to {output_path}")
        
        plt.show()
    
    except ImportError:
        print("  matplotlib not available; skipping visualization")
    
    print(f"\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
