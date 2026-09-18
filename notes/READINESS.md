# Submission-readiness checklist

## Completed in this research pass

- Full statements and self-checked proofs of the single-source adaptive normal form, sharp joint-history gate, conditional-guarantee separation, disjoint composition, and restricted compiler optimality.
- Synthetic implementation, independent state simulator, finite policy and world enumeration, negative controls, baseline calibration, reproducible CSVs and figures.
- Complete manuscript with AI-use disclosure, explicit assumptions, negative results, limitations, and primary references.
- Local test and reproduction reports. Remote CI status must be read from GitHub, not inferred from workflow creation.

## Not established / requires review before submission

1. Independent mathematical review of the first-change/adjacent-mixture theorem and its observation-model assumptions. Numerical enumeration is not proof review.
2. Independent novelty review against reliability demonstration, inspection scheduling, crawling, and freshness-aware semantic caching. The paper does not claim to invent rate estimation, no-change probabilities, or risk gating.
3. Human author review of all claims, citations, and substantial AI assistance. The current draft explicitly says that this review has not yet occurred.
4. Assessment of ICLR relevance: the work is an abstract verification-controller theory paper, not an LLM-memory benchmark paper. Synthetic validation is appropriate to the formal claims but leaves real-agent external validity open.
5. General unknown-rate utility optimality, adaptive multi-source scheduling, and optimal evidence acquisition are NOT solved by the current theorems.
6. Large deployment savings should not be described as total-cost savings: the 768-unit pilot outweighs one 384-unit fully audited workflow.
7. Confirm the final official-template main-text page count, anonymization, primary citations, and conference-specific disclosure after any edits. Public repository links reveal identity and must not be placed in a double-blind manuscript or anonymized supplement.

## Concrete scientific interpretation

The strongest result is the exact stable-instance policy normal form. The multi-source gate and compiler are constructive consequences with sharp risk, not a theorem that the proposed heuristic is best for all source processes. The pilot grouping has mixed utility: do not remove its long-history losses or compare weaker and stronger reliability goals without stating the difference.
