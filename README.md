# Risk-Limited Memory Reuse

**Research draft:** *Risk-Limited Memory Reuse: Sharp Cold-Start Limits and Joint-History Audit Schedules*.

This is a theorem-first, entirely synthetic CPU project. It studies stale remembered information with unknown source-change rates, truthful audits, and known finite-workflow dependencies. No model training, LLM API calls, external datasets, or GPU are used in the experiments.

## Results and scope

1. **Exact adaptive stable-instance normal form.** Among all randomized adaptive single-source policies with a uniform whole-workflow failure constraint, stable-environment audit saving is optimized by a mixture of two adjacent audit-prefix/reuse-tail policies. At a 5% risk target with no prior history, at least 87.28% of checks are necessary in expectation even on a perfectly stable source. This is not an optimal-cost theorem at every nonzero hazard.
2. **Sharp joint-history gate.** For a fixed group and calendar, marginal failure is `exp(-sum(m_i lambda_i)) * (1-exp(-sum(E_i lambda_i)))`. Its exact worst case depends on `max_i(E_i/m_i)`, not a union bound over the number of sources.
3. **Selection-safe grouping.** Disjoint groups have an exact product risk composition. An independent pilot may select groups; the implementation exactly optimizes a contiguous partition and discretized log-budget objective. Reusing the gate histories for this selection is not valid.
4. **Explicit limitations.** Marginal risk is not conditional safety for every admitted memory. Independence, stationary hazards, nonreverting versions, and perfect immediate audits matter. The paper includes counterexamples and negative experimental results.

## Completed validation

- 83 passing unit/property tests.
- 1,856 exhaustively enumerated adaptive policies (horizons 1–4).
- 10 randomized-policy LP cross-checks.
- 71,808 explicit change worlds across 60 tiny calendars.
- 300 joint-gate and 300 composition sharpness witnesses.
- 900 workflow/method evaluations, 54,000 explicit workflow rollouts.
- 1,200 fixed-sample confidence-bound calibration datasets.
- 12 scientific CSV files with fixed seeds and SHA-256 hashes.

At history span 1,000 in the mixed-rate synthetic setting, pilot grouping saves **59.1% of deployment audit cost**, versus **31.3%** for separate-source gates and **1.9%** for one joint gate; its mean exact marginal failure probability is **0.01784**. These are not net acquisition-cost savings: the pilot costs more than one fully audited workflow. At span 5,000 the learned grouping underperforms separate-source gates (44.0% versus 52.4% saved). All comparisons and failures are retained.

## Reproduce

Python 3.10+; a CPU is sufficient. From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python experiments/run_all.py
python experiments/additional_checks.py
python experiments/make_figures.py
python scripts/check_reproduction.py --strict
```

`--strict` expects identical CSV bytes in an identical numerical environment. Without it, the checker allows small cross-platform floating-point differences. Runtime metadata and PDF timestamps are not scientific outcomes.

For the manuscript (a LaTeX installation is needed):

```bash
make paper
```

This fetches the unmodified official ICLR 2027 style and checks its pinned Git blob hash. The style download is the only network-dependent build step. Once vendored, all commands can run offline. `make paper-draft` permits the explicitly labeled local fallback layout if the conference style is unavailable. No claim of official formatting should be made from that fallback build.

## Files

- `paper/main.tex`, `paper/appendix.tex`: manuscript and full proofs.
- `paper/main.pdf`: compiled manuscript when build outputs are present.
- `risk_memory/`: certificate, scheduling, baseline, and independent simulator code.
- `experiments/`: deterministic CSV generation, finite-oracle checks, figures.
- `results/`: raw scientific CSVs, manifests, exact risks and measured rollouts.
- `notes/PROOF_AUDIT.md`: assumptions, theorem audit, and validation map.
- `notes/READINESS.md`: candid submission-readiness and novelty checks.
- `notes/SOURCES.md`: verified primary literature and official formatting provenance.

## Status and disclosure

This is a substantive research draft with completed derivations and synthetic validation, not a claim of acceptance or independently certified submission readiness. Independent human proof/novelty review and author sign-off remain necessary. Generative AI was used extensively for ideation, proofs, coding, experiment execution, and writing; the manuscript discloses that use. Numerical tests are not an independent mathematical proof review. There are no language-model-agent empirical results.
