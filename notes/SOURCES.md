# Primary-source and format verification

Checked 2026-09-17. The manuscript cites only primary research or official policy for external claims. Bibliographic versions below are deliberately specified as preprints when a venue was not verified.

- Upadhyay, Busa-Fekete, Kotlowski, Pal, Szorenyi (2019), *Learning to Crawl*, arXiv:1905.12781. Unknown constant Poisson changes, intermittent binary observations, confidence intervals, average freshness. Do not claim these ingredients are new. https://arxiv.org/abs/1905.12781
- Avrachenkov, Patil, Thoppe (2020), *Change Rate Estimation and Optimal Freshness in Web Page Crawling*, arXiv:2004.02167. https://arxiv.org/abs/2004.02167
- Kriouile, Assaad (2022), *Minimizing the Age of Incorrect Information for Unknown Markovian Source*, arXiv:2210.09681. https://arxiv.org/abs/2210.09681
- Nakayashiki (2026), *When Stale Constraints Go Unchecked: Budgeted Verification Failures in Inherited Agent Memory*, arXiv:2608.25553. Recent motivating agent study, not evidence for this paper's theorem. https://arxiv.org/abs/2608.25553
- Mansoor, Ahmad, Yoon (2026), *Risk-Constrained Freshness-Aware Semantic Caching for Open-Web Retrieval-Augmented LLMs*, arXiv:2607.04281. Close systems prior: explicitly risk/freshness-aware; not omitted. https://arxiv.org/abs/2607.04281
- Coolen, Coolen-Schrijner (2005), *Non-parametric predictive reliability demonstration for failure-free periods*, IMA Journal of Management Mathematics 16(1):1–11. https://doi.org/10.1093/imaman/dph025
- Wilson, Farrow (2019), *Assurance for sample size determination in reliability demonstration testing*, arXiv:1905.08659. https://arxiv.org/abs/1905.08659
- Howard, Ramdas, McAuliffe, Sekhon (2021), *Time-uniform, nonparametric, nonasymptotic confidence sequences*, Annals of Statistics 49(2):1055–1080. https://doi.org/10.1214/20-AOS1991
- Clopper, Pearson (1934), *The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial*, Biometrika 26(4):404–413. https://doi.org/10.1093/biomet/26.4.404

## Official ICLR formatting / disclosure

- https://iclr.cc/Conferences/2027/AuthorGuidelines
- https://iclr.cc/Conferences/2027/AIPolicyForAuthors
- Official style source: https://github.com/ICLR/Master-Template/blob/master/iclr2027/iclr2027_conference.sty
- Pinned official style Git blob SHA: f61ad7efce0855557694078c0945e6c33feb8236.

The fallback `draft_layout.sty` is explicitly not an official conference style. The official build fetches and verifies the unmodified style. A draft header overrides the template's "under review" text so the PDF does not falsely claim submission. The AI-use statement discloses proofs, coding, experiments, and drafting, and does not claim independent human review has already taken place.
