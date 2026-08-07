#!/usr/bin/env python3
"""
Explore parameter sensitivity through systematic sweeps.

Demonstrates:
- Varying model parameters across ranges
- Measuring impact on key metrics
- Identifying sensitive dimensions
- Visualizing parameter space
"""

import sys
from pathlib import Path
from itertools import product

import numpy as np
import matplotlib.pyplot as plt

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import DistinctionSet
except ImportError:
    print("Error: experiments package not installed.")
    print("Run: ./scripts/manage.sh install")
    sys.exit(1)


def sweep_parameter(param_name, param_values, other_params, steps=50, seed=42):
    """Run simulations across a range of parameter values."""
    print(f"\nSweeping {param_name}: {param_values}")
    
    results = []
    
    for param_value in param_values:
        params = other_params.copy()
        params[param_name] = param_value
        
        try:
            model = BaselineComplexSystemModel(
                n_agents=params.get('n_agents', 20),
                n_features=params.get('n_features', 3),
                interaction_strength=params.get('interaction_strength', 0.3),
                seed=seed,
            )
            
            result = run_simulation(
                model,
                steps=steps,
                distinctions=DistinctionSet([]),
            )
            
            trajectory = np.array([s.state for s in result.trajectory])
            
            metrics = {
                'param_value': param_value,
                'mean_state': np.mean(trajectory),
                'std_state': np.std(trajectory),
                'divergence': np.linalg.norm(trajectory[-1] - trajectory[0]),
                'stability': 1.0 / (1.0 + np.mean(np.var(trajectory, axis=0))),
            }
            results.append(metrics)
            
            print(f"  {param_name}={param_value}: mean={metrics['mean_state']:.4f}, std={metrics['std_state']:.4f}")
        
        except Exception as e:
            print(f"  {param_name}={param_value}: ERROR - {e}")
    
    return results


def main():
    print("=" * 70)
    print("Example: Parameter Sensitivity Analysis")
    print("=" * 70)
    
    print(f"\nConfiguration:")
    print(f"  Base agents: 20")
    print(f"  Base features: 3")
    print(f"  Base interaction strength: 0.3")
    print(f"  Steps: 50")
    print(f"  Random seed: 42")
    
    base_params = {
        'n_agents': 20,
        'n_features': 3,
        'interaction_strength': 0.3,
    }
    
    # Define parameter ranges to explore
    sweeps = {
        'n_agents': list(range(5, 51, 5)),  # 5, 10, 15, ..., 50
        'n_features': [1, 2, 3, 4, 5, 6],
        'interaction_strength': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    }
    
    # Run sweeps
    all_results = {}
    for param_name, param_values in sweeps.items():
        other_params = base_params.copy()
        del other_params[param_name]
        
        sweep_result = sweep_parameter(param_name, param_values, other_params)
        all_results[param_name] = sweep_result
    
    # Visualize
    try:
        print(f"\nGenerating visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Parameter Sensitivity Analysis", fontsize=14, fontweight='bold')
        
        metric_names = ['mean_state', 'std_state', 'divergence', 'stability']
        
        for idx, (param_name, results) in enumerate(all_results.items()):
            ax = axes[idx // 2, idx % 2]
            
            if results:
                param_values = [r['param_value'] for r in results]
                
                for metric_name in metric_names:
                    metric_values = [r[metric_name] for r in results]
                    ax.plot(param_values, metric_values, marker='o', label=metric_name, alpha=0.7, linewidth=2)
            
            ax.set_xlabel(param_name)
            ax.set_ylabel("Metric Value")
            ax.set_title(f"Sensitivity to {param_name}")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_path = Path("results/examples/parameter_sweep_output.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        print(f"  Visualization saved to {output_path}")
        
        plt.show()
    
    except ImportError:
        print("  matplotlib not available; skipping visualization")
    
    # Print summary
    print(f"\nSensitivity Summary:")
    for param_name, results in all_results.items():
        if results:
            divergences = [r['divergence'] for r in results]
            print(f"  {param_name}:")
            print(f"    Divergence range: [{min(divergences):.4f}, {max(divergences):.4f}]")
            print(f"    Most sensitive to: {results[np.argmax(divergences)]['param_value']}")
    
    print(f"\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
