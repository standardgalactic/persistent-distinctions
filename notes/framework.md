# Research Framework

## Core Theoretical Issues

### 1. Definition and Scope

**Persistent Distinctions** as defined here means:
- A constraint or organizational principle that maintains a specific state or relationship
- Applied to a subset of a complex system (e.g., agents' feature values)
- Enforced continuously or periodically throughout the simulation
- Observable through measurable differences in system trajectory

**Key distinction**: This is NOT about:
- Labels or naming conventions (that would be merely terminological)
- Static classifications (distinctions must persist *through time* under dynamics)
- Ad-hoc interventions (the constraint must be systematic and reproducible)

### 2. Operationalization Strategy

The current framework operationalizes "persistent distinctions" as:

```
Constraint(feature_index, target_value, tolerance, min_fraction)
```

This means:
- Maintain `feature_index` within ±`tolerance` of `target_value`
- For at least `min_fraction` of agents
- At each time step

**Why this operationalization?**
- Minimal: only specifies what is constrained, not how agents achieve it
- Measurable: produces a binary outcome (constraint satisfied or violated)
- Falsifiable: can test whether this constraint produces predicted effects

### 3. What Counts as Evidence?

**Observable consequences** that would support the hypothesis:
1. **Stability**: Systems with distinctions show lower trajectory divergence
2. **Resilience**: Constrained systems recover faster from perturbations
3. **Reduced state space**: Distinctions compress reachable region of state space
4. **Emergent coherence**: Constrained systems show coordinated behavior not present in baseline
5. **Altered power spectra**: Frequency analysis reveals new timescales
6. **Predictability**: Constrained trajectories are more predictable (lower entropy)

**Non-evidence** (merely terminological or trivial):
- The constraint is satisfied (tautological)
- Agents spend time near the target value (definitional)
- Distinction prevents unlimited divergence (mathematical inevitability)

## Experimental Design Considerations

### 4. Baseline Selection

The **minimal baseline** must be:
- Stochastic (to test whether distinctions reduce noise)
- Multi-agent (to test whether coordination matters)
- Dynamical (to test whether constraints affect evolution)
- Multi-dimensional (to test whether constraints on one dimension affect others)

Current baseline: `BaselineComplexSystemModel`
- 20 agents, each with 3 independent features
- Random interactions with strength parameter
- Deterministic update rule + stochastic perturbation

**Candidate alternates:**
- Pure noise: all features random walk (should show constraint effect clearly)
- Coupled system: features interact (should show cross-dimensional effects)
- Noise floor: random walk frozen at zero (control for tautology)

### 5. Falsification Experiments

**What would falsify the hypothesis?**

1. **Distinction has no measurable effect** on any metric
   - → Theory is empty; constraint is inconsequential
   
2. **Effect is entirely local**
   - Constrained feature changes but others unaffected
   - → Theory only applies to constrained dimension
   
3. **Effect reverses at scaling limit**
   - Small systems show stability; large systems show instability
   - → Theory is size-dependent and requires revision
   
4. **Effect appears in unconstrained baseline**
   - Control runs show same properties as constrained runs
   - → Effect is artifact of model structure, not distinctions
   
5. **Simpler model explains results**
   - Same outcomes from just setting feature to constant value
   - → Distinction mechanism is unnecessary

### 6. Theory vs. Implementation

**Belongs to theory** (model-independent):
- "Persistent constraints reduce trajectory divergence"
- "Maintaining distinctions costs expressiveness"
- "Constraints create attractors in state space"

**Belongs to implementation** (specific to this model):
- The interaction strength parameter (0.3)
- The number of agents (20)
- The feature dimensionality (3)
- The Gaussian perturbation model
- The linear update rule

**Research question**: Which of these assumptions are essential vs. contingent?
- Varies implementation to test robustness
- Replaces components systematically
- Identifies which assumptions driving results

## Measurement Strategy

### 7. Key Metrics

**Trajectory Metrics:**
- **Divergence**: `||x(T) - x(0)||` (distance from initial state)
- **Variance**: `var(x(t))` over time (spread of system states)
- **Entropy**: Shannon entropy of state space coverage
- **Predictability**: Autocorrelation or information-theoretic measures

**Constraint Metrics:**
- **Compliance**: % of steps where constraint is satisfied
- **Violation magnitude**: How far violations exceed tolerance
- **Frequency**: How often constraint is violated

**Cross-dimensional Metrics:**
- **Correlation**: Between constrained and unconstrained features
- **Causality**: Granger causality from constraint to others
- **Information transfer**: Mutual information across dimensions

### 8. Statistical Validation

**Significance testing**:
- Each experiment run 3+ times with different seeds
- Report mean ± std, not single trajectories
- Use non-parametric tests (Mann-Whitney U) for robustness

**Effect size**:
- Distinction effect should be substantive, not microscopic
- Compare against baseline variation
- Report Cohen's d or similar

**Reproducibility**:
- Fix random seeds in `reproducibility/seed_values.json`
- Compute hashes of outputs in `reproducibility/expected_hashes.json`
- Document parameters in `reproducibility/experiment_parameters.json`

## Interpretation Framework

### 9. Potential Outcomes and Implications

**Scenario A: Strong Effect**
- Distinctions cause measurable changes across multiple metrics
- Effect size increases with constraint strength
- Effect is robust to model variations
- **Implication**: Theory has merit; deserves deeper investigation

**Scenario B: Weak or Local Effect**
- Distinctions affect only the constrained dimension
- Effect diminishes with system size
- Effect disappears with model variations
- **Implication**: Theory is fragile; may be model artifact

**Scenario C: Null Effect**
- No measurable differences between constrained and baseline
- Constraint is satisfied but has no systemic consequences
- **Implication**: Theory is empty; constraint is tautological

**Scenario D: Paradoxical Effect**
- Distinctions reduce some metrics (e.g., divergence) but increase others (e.g., variance)
- Effects reverse depending on parameter regime
- **Implication**: Theory needs revision; more nuanced conditions required

### 10. Revision vs. Reinterpretation

**What requires reinterpretation only?**
- Effect is quantitatively weaker than predicted
- Effect appears only at certain parameter values
- Effect is mediated by unexpected mechanisms
- → Keep theoretical framework, adjust predictions

**What requires theoretical revision?**
- Effect is opposite of predicted (distinctions *increase* divergence)
- Effect depends on model details we thought irrelevant
- Effect disappears with small model changes
- Effect is smaller than noise
- → Theory needs reconceptualization or rejection

## Open Questions

### 11. Beyond Initial Operationalization

1. **Hierarchy**: Can distinctions of distinctions (meta-constraints) produce higher-order effects?
2. **Conflict**: What happens when multiple distinctions conflict?
3. **Adaptation**: Can systems *learn* to enforce distinctions? (currently imposed externally)
4. **Emergence**: Do distinctions spontaneously organize without external enforcement?
5. **Scaling**: Does theory scale to realistic complex systems (networks, populations)?
6. **Evolution**: How would distinctions affect evolutionary dynamics?

### 12. Methodological Extensions

- **Sensitivity analysis**: Which parameters matter most? (see `examples/parameter_sweep.py`)
- **Bifurcation analysis**: Where do system behaviors change qualitatively?
- **Attractor analysis**: What attractors exist with/without distinctions?
- **Control theory**: What's the minimum control needed to maintain distinctions?
- **Information geometry**: How do distinctions reshape the space of possible trajectories?

---

**Next Steps:**
1. Run all examples and benchmarks with current operationalization
2. Gather baseline data showing effects (or null results)
3. Based on outcomes, refine theory and run sensitivity experiments
4. Document results in ROADMAP.md with evidence for/against hypothesis
