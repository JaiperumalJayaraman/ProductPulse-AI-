# 📡 ProductPulse AI
### From noisy customer feedback to defensible product decisions

**A hands-on Associate Product Manager portfolio case study: UX × Technology × Business.**

[Launch instructions](#run-locally) · [Demo walkthrough](#90-second-interview-walkthrough) · [How the AI works](#how-the-ai-works)

> **Honest demo disclosure:** The built-in product, customer feedback, business estimates and success targets are **synthetic**. The local AI classifier is a real TF-IDF similarity-based model, not an LLM. Its similarity scores are *not calibrated probabilities* and no benchmark accuracy, customer interviews, business outcomes or production adoption are claimed.

## The product problem

Imagine a B2B collaboration SaaS with dozens of customer requests, urgent failures and limited engineering capacity. A PM needs to separate **symptoms from underlying needs**, compare competing bets, explain why one deserves investment, and define how success will be proven.

**Primary user:** an early-career product manager triaging customer signals.

**Job to be done:** *When many customers ask for different things, help me quickly identify recurring pain, prioritize evidence-backed initiatives and explain my decision to engineering and leadership.*

## What you can actually do

| Area | Hands-on behavior | PM skill demonstrated |
| --- | --- | --- |
| Executive view | Explore six customer themes, segment mix and blockers | Product sense and signal synthesis |
| Customer signals | Filter/search customer comments, add a signal, import CSV, export CSV | Customer empathy and discovery workflow |
| AI theme review | Run explainable local theme suggestions, inspect similarity and approve/override labels | Technical judgment and human-in-the-loop UX |
| Prioritization | Edit reach, impact, confidence and effort; recalculate RICE and export ranking | Quantitative prioritization and trade-offs |
| Roadmap | Commit an Investigate / Now / Next / Later / Not planned call with documented rationale | Stakeholder alignment and ownership |
| Experiment plan | Specify baseline, target, eligibility, observation window and guardrails; export brief | Metrics, experimentation and outcome thinking |

**No API key is required.** User-provided feedback is processed locally in the running Streamlit server, not sent to an external LLM.

## Run locally

Requires Python 3.10+.

```bash
git clone https://github.com/JaiperumalJayaraman/ProductPulse-AI-.git
cd ProductPulse-AI-
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit, usually `http://localhost:8501`.

To test CSV importing, use [data/sample_feedback.csv](data/sample_feedback.csv). Download a copy of any changes before closing the tab; the demo is intentionally session-only.

## How the AI works

1. The model includes a small, transparent dictionary of example feedback sentences for six product themes: Checkout, Reporting, Search, Collaboration, Performance and Appearance.
2. `TfidfVectorizer` builds unigram/bigram TF-IDF features across examples and incoming comments.
3. Cosine similarity measures each incoming comment against each example.
4. The most similar **example** determines the suggested theme; results below a configurable similarity threshold are flagged for manual review.
5. A PM can accept, correct or leave the label unreviewed.

**This is genuine classical NLP, not generative AI.** Scores are lexical similarity, not certainty, customer truth or model-quality validation. The model can miss synonyms, sarcasm, multi-topic complaints and language variants. No personal data should be uploaded to a public demo.

Code: [product_intelligence.py](product_intelligence.py). Tests: [tests/test_product_intelligence.py](tests/test_product_intelligence.py).

## Prioritization framework

`RICE = (quarterly reach × impact × confidence) / person-months of effort`

| Variable | Meaning |
| --- | --- |
| Reach | Estimated unique users affected per quarter |
| Impact | Hypothesized impact on user outcome; relative 0.25–3 scale |
| Confidence | 0–1 measure of evidence strength |
| Effort | Estimated engineering/product person-months |

The score is a **conversation starter**, not an automatic roadmap. Security issues, core reliability, contractual needs, dependencies and strategic commitments may override the score. All numerical inputs in the initial demo are made up.

See [Atlassian's prioritization framework overview](https://www.atlassian.com/agile/product-management/prioritization-framework).

## UX × Technology × Business

**UX:** Searchable evidence inbox, clear progress from insight to decision, selective disclosure in tabs and manual review of uncertain AI labels.

**Technology:** Streamlit frontend, pandas tables, scikit-learn TF-IDF, cosine similarity, pure tested RICE functions, CSV ingestion/export and GitHub Actions CI.

**Business:** Explicit customer segments, value hypotheses, activation/retention/engagement outcomes, cost-aware trade-offs and a roadmap decision log.

**Proposed north-star:** weekly successful core workflows per active account. **Guardrails:** reliability, latency, support contact rate.

## An example product decision (illustrative only)

**Problem:** multiple segments report failures while completing checkout. **Bet:** investigate checkout reliability before investing in a visual dark-mode enhancement. **Why:** core-flow blockers can destroy activation; however, volume alone is not evidence of commercial impact.

**What to validate:** reproduce the bug, estimate users affected, compare affected segments, examine funnel analytics and determine engineering dependencies.

**Success plan:** improve the rate of completed eligible checkout attempts; guard against rising payment errors, latency or support contacts. Agree on baseline and sample size before shipment.

## 90-second interview walkthrough

1. **0–20 seconds:** Explain the fragmented-feedback problem, primary user and outcome.
2. **20–40 seconds:** Import [sample feedback](data/sample_feedback.csv), show AI suggestions and override a label. Explain why AI should not silently set product truth.
3. **40–60 seconds:** Adjust RICE inputs. Explain what the score misses and how a critical defect might override it.
4. **60–75 seconds:** Record a Now/Next decision with explicit counterarguments.
5. **75–90 seconds:** Define a success metric, guardrails and experiment evaluation risks.

**What I would build next:** real interviews and usability testing, persistent SQLite storage, account-level analytics, benchmarked multi-label NLP, outcome dashboards and shareable deployment.

## Test

```bash
python -m pip install -r requirements-dev.txt
pytest -q
python -m py_compile app.py product_intelligence.py
```

CI runs these checks on every push via [.github/workflows/tests.yml](.github/workflows/tests.yml).

## Limitations

- Session state is temporary; this is not a production database or collaboration tool.
- Synthetic dataset and estimates are for interactive demonstration, not validated user research.
- NLP has no calibrated confidence, external benchmarking or human-evaluated accuracy report.
- CSV imports are capped at 10,000 rows and normalized to the expected schema.
- The experiment tab plans a study but does not run statistical inference or causal experimentation.

**Made as a transparent, working product-management portfolio exercise.**
