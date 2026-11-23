# 📡 ProductPulse AI
### Turn scattered customer feedback into defensible product decisions

**Interactive product-management portfolio case study** | UX × Technology × Business

> **Demo disclaimer:** All seeded feedback, reach estimates, impact assumptions and business values are synthetic. This project does not claim real user interviews, production AI inference or proven product uplift.

## The problem
Product teams collect customer requests from many channels but cannot build everything. APMs must identify the underlying problems, prioritize trade-offs and define how success will be measured.

## What the app does
1. **Understand users:** searchable customer feedback inbox, segment filtering, theme frequency and urgent-workflow signals.
2. **Prioritize:** editable initiative assumptions, transparent RICE calculation and ranking.
3. **Make decisions:** human-owned Now / Next / Later / Investigate / Not planned roadmap with written rationale and CSV export.
4. **Measure outcomes:** experiment hypotheses, baseline/target success rates and guardrail metrics.

## Run locally
```bash
git clone https://github.com/JaiperumalJayaraman/ProductPulse-AI-.git
cd ProductPulse-AI-
pip install -r requirements.txt
streamlit run app.py
```

## Product thinking
**User:** PM managing competing requests. **Job to be done:** choose the next high-value problem to solve and explain why. **North-star (proposed):** weekly successful core workflows per active account. **Guardrails:** reliability, latency and support contacts.

### Prioritization method
RICE = (quarterly reach × impact × confidence) / person-months of effort. Estimates must use comparable units. RICE supports judgment; it cannot replace strategic, technical or compliance review. See [Atlassian's framework overview](https://www.atlassian.com/agile/product-management/prioritization-framework).

### Example decision narrative (hypothetical)
Checkout reliability may deserve priority over dark mode because it blocks a core journey. Before shipping, verify incident frequency, affected segments, engineering complexity and actual business impact. Measure checkout completion and error rates afterward.

## Architecture
Streamlit UI → pandas data tables → deterministic RICE calculation → human roadmap decisions → CSV export.

**AI transparency:** This is an AI-*ready* product intelligence prototype. The current release uses manually reviewed themes and deterministic scoring; it does **not** invoke an LLM. A future version can add optional, audited feedback clustering and summaries with human review.

## Limitations & next steps
- Session-only storage; add SQLite and multi-user authentication.
- Manual theme tagging; add optional NLP clustering with accuracy evaluation.
- Synthetic data; conduct actual interviews and usability testing before making outcome claims.
- No live event analytics; connect product telemetry and test statistically sound experiments.
- Add automated tests, deployment and accessibility audit.

## Interview walkthrough (90 seconds)
1. Show the user problem and the feedback inbox.
2. Explain how recurring checkout pain emerges across segments.
3. Edit RICE assumptions live and show ranking sensitivity.
4. Override the ranking with an evidence-based rationale.
5. Define an experiment, success metric and guardrails.

**Built as a product-management portfolio demonstration.**
