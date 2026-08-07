#!/usr/bin/env python3
"""
Basic complex-systems model without distinctions.

Demonstrates:
- Initializing BaselineComplexSystemModel
- Running simulation with run_simulation()
- Inspecting trajectory and metrics
- Visualizing results
"""

import sys
from pathlib import Path

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


def main():
    print("=" * 70)
    print("Example: Baseline Complex-Systems Model (No Distinctions)")
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
    
    # Create model
    print(f"\nInitializing model...")
    model = BaselineComplexSystemModel(
        n_agents=n_agents,
        n_features=n_features,
        interaction_strength=interaction_strength,
        seed=seed,
    )
    print(f"  Model initialized successfully")
    print(f"  Initial state shape: {model.get_state().state.shape}")
    
    # Run simulation
    print(f"\nRunning simulation for {steps} steps...")
    result = run_simulation(
        model,
        steps=steps,
        distinctions=DistinctionSet([]),  # No distinctions
    )
    
    print(f"  Simulation complete")
    print(f"  Trajectory length: {len(result.trajectory)}")
    
    # Analyze trajectory
    print(f"\nAnalyzing trajectory...")
    trajectory_array = np.array([s.state for s in result.trajectory])
    
    print(f"  Shape: {trajectory_array.shape}")
    print(f"  Mean state value: {np.mean(trajectory_array):.4f}")
    print(f"  Std deviation: {np.std(trajectory_array):.4f}")
    print(f"  Min value: {np.min(trajectory_array):.4f}")
    print(f"  Max value: {np.max(trajectory_array):.4f}")
    
    # Check for divergence (spreading of states)
    initial_state = trajectory_array[0]
    final_state = trajectory_array[-1]
    divergence = np.linalg.norm(final_state - initial_state)
    print(f"  Divergence from initial: {divergence:.4f}")
    
    # Visualize if possible
    try:
        print(f"\nGenerating visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Baseline Complex-Systems Model", fontsize=14, fontweight='bold')
        
        # Plot 1: Feature average over time
        ax = axes[0, 0]
        feature_means = np.mean(trajectory_array, axis=1)  # Average across agents
        ax.plot(feature_means, linewidth=2, alpha=0.7)
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean Feature Value")
        ax.set_title("Global Feature Average")
        ax.grid(True, alpha=0.3)
        
        # Plot 2: State variance over time
        ax = axes[0, 1]
        feature_vars = np.var(trajectory_array, axis=1)
        ax.plot(feature_vars, linewidth=2, alpha=0.7, color='orange')
        ax.set_xlabel("Step")
        ax.set_ylabel("Variance")
        ax.set_title("State Variance Over Time")
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Heatmap of final state
        ax = axes[1, 0]
        im = ax.imshow(trajectory_array[-1].reshape(n_agents, n_features), aspect='auto', cmap='viridis')
        ax.set_xlabel("Feature")
        ax.set_ylabel("Agent")
        ax.set_title("Final State Heatmap")
        plt.colorbar(im, ax=ax)
        
        # Plot 4: Cumulative divergence
        ax = axes[1, 1]
        divergence_over_time = []
        for t in range(len(trajectory_array)):
            div = np.linalg.norm(trajectory_array[t] - initial_state)
            divergence_over_time.append(div)
        ax.plot(divergence_over_time, linewidth=2, alpha=0.7, color='red')
        ax.set_xlabel("Step")
        ax.set_ylabel("Divergence")
        ax.set_title("Cumulative Divergence from Initial State")
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_path = Path("results/examples/baseline_model_output.png")
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
