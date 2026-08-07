#!/usr/bin/env python3
"""
Complex-systems model with persistent-distinctions constraint.

Demonstrates:
- Creating and applying Distinction constraints
- Comparing constrained vs. unconstrained models
- Monitoring constraint violations
- Measuring constraint impact on system dynamics
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

try:
    from experiments.models.baseline import BaselineComplexSystemModel
    from experiments.models import run_simulation
    from experiments.core import Distinction, DistinctionSet
except ImportError:
    print("Error: experiments package not installed.")
    print("Run: ./scripts/manage.sh install")
    sys.exit(1)


def main():
    print("=" * 70)
    print("Example: Complex-Systems Model with Persistent Distinctions")
    print("=" * 70)
    
    # Configuration
    n_agents = 20
    n_features = 3
    interaction_strength = 0.3
    steps = 100
    seed = 42
    
    print(f"\nConfiguration:")
    print(f"  Agents: {n_agents}")
    print(f"  Features per agent: {n_features}")
    print(f"  Interaction strength: {interaction_strength}")
    print(f"  Simulation steps: {steps}")
    print(f"  Random seed: {seed}")
    
    # Define distinction: Keep feature 0 close to 0.5 for at least 60% of agents
    distinction = Distinction(
        name="feature-0-invariant",
        description="Maintain feature 0 near 0.5 for majority of agents",
        parameters={
            "feature_index": 0,
            "target_value": 0.5,
            "tolerance": 0.15,
            "min_fraction": 0.6,
        },
    )
    
    print(f"\nDistinction Definition:")
    print(f"  Name: {distinction.name}")
    print(f"  Description: {distinction.description}")
    print(f"  Parameters: {distinction.parameters}")
    
    # Create model
    print(f"\nInitializing model...")
    model = BaselineComplexSystemModel(
        n_agents=n_agents,
        n_features=n_features,
        interaction_strength=interaction_strength,
        seed=seed,
    )
    print(f"  Model initialized successfully")
    
    # Run simulation with distinction
    print(f"\nRunning simulation WITH distinction...")
    result_with_distinction = run_simulation(
        model,
        steps=steps,
        distinctions=DistinctionSet([distinction]),
    )
    
    print(f"  Simulation complete")
    print(f"  Trajectory length: {len(result_with_distinction.trajectory)}")
    
    # Analyze trajectory
    print(f"\nAnalyzing constrained trajectory...")
    trajectory_array = np.array([s.state for s in result_with_distinction.trajectory])
    
    print(f"  Shape: {trajectory_array.shape}")
    print(f"  Mean state value: {np.mean(trajectory_array):.4f}")
    print(f"  Std deviation: {np.std(trajectory_array):.4f}")
    
    # Analyze feature 0 specifically (the constrained feature)
    feature_0 = trajectory_array[:, ::n_features]  # Every n_features-th element
    agents_near_target = np.sum(
        np.abs(feature_0 - 0.5) <= 0.15, axis=1
    ) / n_agents * 100
    
    print(f"\nFeature 0 Analysis (constrained feature):")
    print(f"  Mean value over time: {np.mean(feature_0):.4f}")
    print(f"  Std deviation: {np.std(feature_0):.4f}")
    print(f"  Avg agents in tolerance: {np.mean(agents_near_target):.1f}%")
    print(f"  Min agents in tolerance: {np.min(agents_near_target):.1f}%")
    print(f"  Max agents in tolerance: {np.max(agents_near_target):.1f}%")
    
    # Compare with baseline
    print(f"\nFor comparison, running baseline (no distinction)...")
    model_baseline = BaselineComplexSystemModel(
        n_agents=n_agents,
        n_features=n_features,
        interaction_strength=interaction_strength,
        seed=seed,
    )
    
    result_baseline = run_simulation(
        model_baseline,
        steps=steps,
        distinctions=DistinctionSet([]),
    )
    
    trajectory_baseline = np.array([s.state for s in result_baseline.trajectory])
    feature_0_baseline = trajectory_baseline[:, ::n_features]
    agents_near_target_baseline = np.sum(
        np.abs(feature_0_baseline - 0.5) <= 0.15, axis=1
    ) / n_agents * 100
    
    print(f"\nBaseline Feature 0 Analysis:")
    print(f"  Mean value over time: {np.mean(feature_0_baseline):.4f}")
    print(f"  Std deviation: {np.std(feature_0_baseline):.4f}")
    print(f"  Avg agents in tolerance: {np.mean(agents_near_target_baseline):.1f}%")
    print(f"  Min agents in tolerance: {np.min(agents_near_target_baseline):.1f}%")
    print(f"  Max agents in tolerance: {np.max(agents_near_target_baseline):.1f}%")
    
    # Visualize comparison
    try:
        print(f"\nGenerating comparison visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Distinction vs. Baseline Comparison", fontsize=14, fontweight='bold')
        
        # Plot 1: Feature 0 trajectories
        ax = axes[0, 0]
        ax.plot(np.mean(feature_0, axis=1), linewidth=2, label='With Distinction', alpha=0.7)
        ax.plot(np.mean(feature_0_baseline, axis=1), linewidth=2, label='Baseline', alpha=0.7)
        ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Target (0.5)')
        ax.fill_between(range(len(feature_0)), 0.35, 0.65, alpha=0.1, color='green', label='Tolerance')
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean Feature 0 Value")
        ax.set_title("Feature 0 (Constrained Feature) Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Agents in tolerance
        ax = axes[0, 1]
        ax.plot(agents_near_target, linewidth=2, label='With Distinction', alpha=0.7)
        ax.plot(agents_near_target_baseline, linewidth=2, label='Baseline', alpha=0.7)
        ax.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='Min Constraint (60%)')
        ax.set_xlabel("Step")
        ax.set_ylabel("% Agents in Tolerance")
        ax.set_title("Constraint Compliance Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 100])
        
        # Plot 3: Overall dynamics
        ax = axes[1, 0]
        mean_with = np.mean(trajectory_array, axis=1)
        mean_baseline = np.mean(trajectory_baseline, axis=1)
        ax.plot(mean_with, linewidth=2, label='With Distinction', alpha=0.7)
        ax.plot(mean_baseline, linewidth=2, label='Baseline', alpha=0.7)
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean State Value")
        ax.set_title("Global System Dynamics")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Distribution comparison
        ax = axes[1, 1]
        ax.hist(trajectory_array.flatten(), bins=30, alpha=0.5, label='With Distinction', density=True)
        ax.hist(trajectory_baseline.flatten(), bins=30, alpha=0.5, label='Baseline', density=True)
        ax.set_xlabel("State Value")
        ax.set_ylabel("Frequency (normalized)")
        ax.set_title("State Value Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save figure
        output_path = Path("results/examples/distinction_model_output.png")
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
