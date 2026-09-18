# Execution and reproduction audit

## Verified commits and runs

- Scientific source commit: `31ad0b642d47f7070466e2b92140aa86f331a830`.
- First clean GitHub Actions run: `35305238982`; generated-output commit: `395601fa949c4c28c337ad14a66c897713f42a06`.
- Final editorial build run: `35305680166`; generated-output commit: `78303ad870cf05aa312503c2a6201c561bff4081`.
- Final official-style manuscript: 17 pages, with seven pages of main text. PDF SHA-256: `fbea43cf0e2b20814dc304316f834aa11b50ceaeba616a7e036794a40cd6b0dd`.

## Verified evidence

83 local tests passed; all 83 also passed on both clean GitHub runs, with zero errors, failures, or skips. The local strict reproduction checker regenerated all 12 scientific CSVs byte-for-byte. The clean GitHub runner regenerated the same results: 11 CSVs were byte-identical to the local originals; `exhaustive_worlds.csv` differed only in floating-point residuals, with maximum absolute difference 1.11022302463e-16. The second run also checked the previously committed scientific reference values.

The official ICLR 2027 style matched Git blob hash `f61ad7efce0855557694078c0945e6c33feb8236`. Both official-style builds completed without undefined citations/references or overfull boxes. The final source files were byte-identical to the locally rendered and visually reviewed manuscript. The PDF is labeled a research draft, not under review.

The final editorial pass removed title hyphenation, kept the reproduction command block together, and tightened disclosure/conclusion prose. It changed no theorem, algorithm, experimental configuration, data, or numerical result. The layout helper was then simplified and checked locally by executing it twice: both final manuscript source files remained byte-identical. That final helper-only cleanup was not a new scientific experiment or a third CI execution.

Conditional-on-history baseline risks and marginalized clean-gate risks are labeled separately in `workflow_results.csv`. Pilot acquisition costs are not included in deployment-only savings; the manuscript reports them explicitly.

## What execution checks do not establish

A clean execution is not independent mathematical peer review. The same AI-assisted process developed and self-checked the arguments. External validity for actual LLM agents, complete novelty relative to all related literature, and author approval for submission remain outstanding.
