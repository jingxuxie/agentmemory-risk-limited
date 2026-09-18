# Proof audit and claim map

This audit was performed in the same AI-assisted research session that developed the results. It is not independent human or formal proof verification.

## Exact adaptive stable-instance frontier

Condition on internal random seed; take the all-zero-change trajectory. First-change-at-a-skipped-use events are disjoint and force failure before any distinguishing observation. Their sum is minimized by latest skipped times. Audit-prefix/reuse-tail gates attain that sum. Convex interpolation over integer skip counts gives simultaneous dominance by adjacent tail counts for every hazard. The distribution is chosen before seeing history. Smooth Jensen yields the closed bound; integer attainability controls the rounding gap.

Scope: one source used every step; fixed historical span; rate-independent labels; truthful immediate audit; no additional change side channel. Cost objective evaluated only at rate zero, with risk constrained uniformly over all rates. General nonzero-rate expected-cost optimality is NOT claimed.

Checks: all 1,856 deterministic trees through horizon four; exact polynomial extrema; ten finite-grid LP upper relaxations augmented by the analytic active hazard; all match the theorem's finite predictions. The LP grid does not establish continuum feasibility by itself.

## Exposure and joint gate

Each skipped use exposes its elementary preceding inter-use gap. Audit-only gaps do not contribute; union of all potentially stale-use intervals equals their disjoint sum. Fixed-calendar survival is the probability of no change anywhere in this union. Joint gating multiplies this by independent historical cleanliness. With x=sum(m*lambda) and y=sum(E*lambda), y<=r*x; maximize exp(-x)*(1-exp(-r*x)). A single maximizing-ratio source attains the bound. Handle m=0/E>0 and E=0 explicitly.

Scope: fixed group and calendar before gate history; independent sources and time increments; versions do not revert. A marginal-history gate may have conditional admitted risk exceeding delta. No post-selection of favorable histories.

Checks: 60 exhaustive two-source calendars/71,808 change worlds; 300 joint witnesses; 300 disjoint-group witnesses; source calendar brute-force tests.

## Composition and learned groups

Group failure events depend on disjoint independent source histories and futures. Product survival is exact; combining group witnesses attains its worst case. Condition on an independent pilot: chosen partitions/calendars are now fixed, and the gate data retain their law. Utility estimation can be wrong without invalidating the bound. The DP considers all predecessor split positions and all grid budget splits, proving optimality only in the ordered/grid family.

Checks: five brute-force partition/grid problems; bound asserted on every experiment output. Negative pilot results are included.

## Conditional certificate

The history-dependent rule has only safe fallback and a fixed accepted calendar. Let c=-log(1-rho). When accepted-calendar risk exceeds rho, y>c and x>=y/r>c/r. Worst false issuance probability approaches exp(-c/r), with a maximizing-ratio witness. This gives necessary/sufficient r<=c/log(1/alpha) in this gate class.

CP baseline: transform a fixed-sample binomial one-sided confidence bound. An all-changed sample must give hazard upper endpoint one (tested); floating-point clipping to below one would invalidate the guarantee. No optional stopping is used.

## Counterexamples and deliberate exclusions

- Choosing the first clean among N sources changes gate acceptance to 1-(1-a)^N.
- Shared change streams invalidate independence and can multiply future exposure without multiplying historical evidence.
- Deployment hazard shift invalidates stationarity.
- More available data cannot hurt an unrestricted optimum; longer *mandated clean windows* can hurt this particular gate.
- Pilot and endpoint costs are not hidden in deployment savings.
- Repeated workflows require separate global-risk accounting.
- No causal claim about real LLM agent reliability is made.
