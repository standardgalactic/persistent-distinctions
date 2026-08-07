# Experimental Log

This document tracks hypotheses, experiments run, and results observed.

## Hypothesis 1: Distinctions Reduce Trajectory Divergence

**Prediction**: Systems with persistent distinctions will show lower divergence from initial state compared to baseline systems.

**Rationale**: If distinctions act as constraints, they should anchor the system, preventing large excursions from initial conditions.

**Test**:
- Run baseline model with seed 42 for 100 steps
- Run same model with distinction (feature 0 @ 0.5) with seed 43 for 100 steps
- Measure: `||x(T) - x(0)||` for both
- Expected: Constrained < Unconstrained

**Status**: Pending
**Command**: `python examples/baseline_model.py && python examples/distinction_model.py`

---

## Hypothesis 2: Distinctions Reduce State Variance

**Prediction**: Systems with distinctions will have lower variance in state space (flatter, more stable trajectories).

**Rationale**: Constraints eliminate some degrees of freedom, compressing the accessible state space.

**Test**:
- Run both models (baseline + constrained)
- Measure: `var(x(t))` for all t
- Expected: Constrained variance < Baseline variance

**Status**: Pending
**Command**: `python examples/comparison.py`

---

## Hypothesis 3: Effect Scales with System Size

**Prediction**: The relative effect of distinctions should increase with system size (more agents = stronger relative effect).

**Rationale**: Larger systems have more degrees of freedom; constraining one dimension becomes relatively more important.

**Test**:
- Run models with n_agents in [5, 10, 20, 40, 80]
- For each size, measure divergence and variance
- Plot effect magnitude vs. system size
- Expected: Monotonic increase

**Status**: Pending
**Command**: `python examples/parameter_sweep.py`

---

## Hypothesis 4: Constraint Strength Matters

**Prediction**: Stronger constraints (larger tolerance, lower min_fraction) should produce weaker effects.

**Rationale**: Weaker constraints are easier to satisfy and require less system reorganization.

**Test**:
- Vary tolerance parameter: [0.05, 0.10, 0.15, 0.20, 0.30]
- Measure compliance and effect on divergence
- Expected: Effect magnitude inversely related to tolerance

**Status**: Pending
**Command**: Custom experiment needed

---

## Hypothesis 5: Cross-Dimensional Effects Exist

**Prediction**: Constraining one feature (e.g., feature 0) will affect dynamics of other features (e.g., feature 1, 2).

**Rationale**: If the system is genuinely coupled, constraints on one dimension should ripple through the system.

**Test**:
- Constrain feature 0, measure changes in feature 1 and 2
- Use information-theoretic measures (mutual information, transfer entropy)
- Expected: Non-zero information transfer from constrained to unconstrained dimensions

**Status**: Pending
**Command**: Custom experiment needed

---

## Hypothesis 6: Distinctions Enable Predictability

**Prediction**: Trajectories with distinctions should be more predictable (lower entropy, higher autocorrelation).

**Rationale**: Constraints reduce the space of possible futures, making the system more deterministic.

**Test**:
- Fit AR(1) model to both constrained and baseline trajectories
- Measure: R² of one-step prediction
- Measure: Shannon entropy of trajectory
- Expected: Constrained > Baseline for predictability metrics

**Status**: Pending
**Command**: Custom experiment needed

---

## Hypothesis 7: Distinctions Are Necessary, Not Tautological

**Prediction**: Setting a feature to a constant value should NOT produce the same effects as a distinction.

**Rationale**: If true, it would show that the distinction mechanism (not just the reduced dimensionality) matters.

**Test**:
- Run model with feature 0 locked to 0.5 (zero dynamics)
- Run model with feature 0 constrained to stay near 0.5 (distinction)
- Compare effects on other features
- Expected: Distinction > Locked feature (in terms of system-wide effects)

**Status**: Pending
**Command**: Custom experiment needed

---

## Hypothesis 8: Distinctions Survive Model Changes

**Prediction**: Core effects should persist when we change model details (interaction strength, perturbation, update rule).

**Rationale**: If theory is robust, effects shouldn't depend on specific implementation choices.

**Test**:
- Run with interaction_strength in [0.1, 0.3, 0.5]
- Run with different noise models (Gaussian, uniform, Poisson)
- Run with different update rules (linear, nonlinear)
- Expected: Effect direction and sign consistent across variations

**Status**: Pending
**Command**: `python benchmarks/scaling.py`

---

## Null Hypothesis: No Effect

**Prediction**: Distinctions will show no significant difference from baseline in any metric.

**Rationale**: Conservative assumption that theory is empty or constraint is tautological.

**Test**:
- All experiments above show p > 0.05
- Effect sizes are negligible (Cohen's d < 0.2)
- Distinctions appear as random variation
- **If confirmed**: Theory requires major revision or rejection

**Status**: Pending (assumed false until proven)

---

## Results Summary

| Hypothesis | Status | Effect Size | P-value | Notes |
|-----------|--------|-------------|---------|-------|
| 1. Reduced Divergence | Pending | -- | -- | |
| 2. Reduced Variance | Pending | -- | -- | |
| 3. Size Scaling | Pending | -- | -- | |
| 4. Constraint Strength | Pending | -- | -- | |
| 5. Cross-Dimensional | Pending | -- | -- | |
| 6. Predictability | Pending | -- | -- | |
| 7. Not Tautological | Pending | -- | -- | |
| 8. Robustness | Pending | -- | -- | |
| Null Hypothesis | Pending | -- | -- | |

---

## Interpretation Decision Tree

If results show:

**All hypotheses confirmed (strong effects):**
- → Theory is supported
- → Plan extended investigation into mechanisms
- → Explore Hypothesis 5-8 in more depth

**Most hypotheses confirmed (moderate effects):**
- → Theory is partially supported
- → Identify which conditions enable effects
- → Investigate why other hypotheses failed

**Mixed results:**
- → Theory is fragile or context-dependent
- → Requires refinement and conditional statements
- → Plan bifurcation and sensitivity analysis

**Null hypothesis confirmed (no effects):**
- → Theory is empty or operationalization is wrong
- → Consider alternate operationalizations
- → Revisit core definitions

---

## Experiment Execution Checklist

- [ ] Run all examples and collect outputs
- [ ] Run all benchmarks and generate report
- [ ] Compute SHA256 hashes for reproducibility
- [ ] Update expected_hashes.json
- [ ] Extract summary statistics
- [ ] Create comparison visualizations
- [ ] Write interpretation in ROADMAP.md
- [ ] Update this log with results

