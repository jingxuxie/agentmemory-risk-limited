# Execution and reproduction audit

The scientific source commit is `31ad0b642d47f7070466e2b92140aa86f331a830`.
The first clean GitHub Actions execution is run `35305238982`, with generated-output commit `395601fa949c4c28c337ad14a66c897713f42a06`.

## Verified evidence

- 83 local tests passed; all 83 also passed on the clean GitHub runner (zero errors, failures, or skips in its JUnit report).
- The local strict reproduction checker regenerated all 12 scientific CSVs byte-for-byte.
- The clean GitHub runner regenerated the same scientific results. Comparing its downloaded artifact against the local results: 11 CSVs were byte-identical; the remaining `exhaustive_worlds.csv` differed only in floating-point residuals, with maximum absolute difference 1.11022302463e-16. All scientific columns agree numerically.
- The official ICLR 2027 style was fetched and its Git blob hash matched `f61ad7efce0855557694078c0945e6c33feb8236`.
- The official-style build completed with no undefined citations/references or overfull boxes. The manuscript is explicitly labeled a research draft, not under review.
- Whole-run verification includes both conditional-on-history baseline risks and marginalized clean-gate risks; those are labeled separately in `workflow_results.csv`.

A final editorial pass removes title hyphenation, keeps the reproduction command block together, and tightens disclosure/conclusion prose. It changes no theorem, algorithm, experimental configuration, data, or numerical result. The workflow repeats the full scientific and PDF checks after that pass.

## What execution checks do not establish

A clean execution is not independent mathematical peer review. The same AI-assisted process developed and self-checked the arguments. External validity for actual LLM agents, complete novelty relative to all related literature, and author approval for submission remain outstanding.
