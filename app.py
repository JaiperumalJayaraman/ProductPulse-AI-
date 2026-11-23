"""ProductPulse AI — from noisy feedback to documented product bets."""
import io
import re

import pandas as pd
import streamlit as st

from product_intelligence import (
    THEME_EXAMPLES,
    rank_initiatives,
    suggest_themes,
    validate_feedback_upload,
)

st.set_page_config(page_title="ProductPulse AI | Product Intelligence", page_icon="📡", layout="wide")
st.markdown(
    """<style>
    .block-container {padding-top: 1.8rem; max-width: 1380px;}
    [data-testid="stMetric"] {border:1px solid rgba(125,125,125,.22);border-radius:14px;padding:14px;}
    h1,h2,h3 {letter-spacing:-.025em;}
    </style>""",
    unsafe_allow_html=True,
)

SEED_FEEDBACK = [
    ("F01", "The checkout page freezes when I apply a coupon", "Checkout", "Enterprise", 1),
    ("F02", "Checkout keeps crashing on my phone", "Checkout", "SMB", 1),
    ("F03", "I cannot complete payment after entering a discount", "Checkout", "Startup", 1),
    ("F04", "Please add dark mode to the dashboard", "Appearance", "SMB", 0),
    ("F05", "Dark theme would help at night", "Appearance", "Startup", 0),
    ("F06", "Exporting reports as CSV would save our finance team hours", "Reporting", "Enterprise", 0),
    ("F07", "Need to download reports to Excel", "Reporting", "SMB", 0),
    ("F08", "Search doesn't find my saved projects", "Search", "Enterprise", 1),
    ("F09", "Project search returns irrelevant results", "Search", "SMB", 0),
    ("F10", "Invite teammates with different permissions", "Collaboration", "Enterprise", 0),
    ("F11", "Role-based access for our team is essential", "Collaboration", "SMB", 0),
    ("F12", "The mobile dashboard takes too long to load", "Performance", "Startup", 1),
]
SEED_OPTIONS = [
    ("Fix checkout reliability", "Checkout", 1100, 3, .90, 2, 5, 4, "Activation"),
    ("CSV / Excel exports", "Reporting", 800, 2, .80, 1.5, 4, 2, "Retention"),
    ("Improve project search", "Search", 650, 2, .80, 2, 4, 3, "Engagement"),
    ("Role-based permissions", "Collaboration", 450, 3, .65, 3, 5, 4, "Enterprise adoption"),
    ("Improve mobile performance", "Performance", 900, 2, .70, 2.5, 4, 3, "Retention"),
    ("Dark mode", "Appearance", 300, 1, .80, 1, 2, 1, "Satisfaction"),
]
OPTION_COLUMNS = [
    "feature", "theme", "reach", "impact", "confidence", "effort",
    "business_value", "risk", "goal",
]
if "feedback" not in st.session_state:
    st.session_state.feedback = pd.DataFrame(
        SEED_FEEDBACK, columns=["id", "feedback", "theme", "segment", "urgent"]
    )
if "options" not in st.session_state:
    st.session_state.options = pd.DataFrame(SEED_OPTIONS, columns=OPTION_COLUMNS)
if "decisions" not in st.session_state:
    st.session_state.decisions = {}
if "experiment_notes" not in st.session_state:
    st.session_state.experiment_notes = {}

st.title("📡 ProductPulse AI")
st.caption("Listen → detect patterns → prioritize trade-offs → record a decision → define success")
st.info(
    "PORTFOLIO DEMO · All seeded customer feedback, user counts and commercial "
    "assumptions are synthetic. AI suggestions are advisory, not validated classifications."
)

with st.sidebar:
    st.header("Workspace")
    st.write("**Product:** fictional B2B collaboration SaaS")
    st.write("**PM challenge:** limited capacity, competing customer requests")
    st.divider()
    st.markdown("**How to use**")
    st.write("1. Import or add feedback\n\n2. Review AI suggestions\n\n3. Adjust RICE assumptions\n\n4. Record a roadmap decision\n\n5. Draft a success experiment")
    st.divider()
    st.caption("No external API keys required. No user data is transmitted to an LLM.")
    if st.button("Reset demo data", help="Clears imported signals and in-session decisions"):
        st.session_state.feedback = pd.DataFrame(
            SEED_FEEDBACK, columns=["id", "feedback", "theme", "segment", "urgent"]
        )
        st.session_state.options = pd.DataFrame(SEED_OPTIONS, columns=OPTION_COLUMNS)
        st.session_state.decisions = {}
        st.session_state.experiment_notes = {}
        st.rerun()

feedback = st.session_state.feedback
tabs = st.tabs([
    "📊 Executive view",
    "💬 Customer signals",
    "🤖 AI theme review",
    "🎯 Prioritization",
    "🗺️ Roadmap",
    "🧪 Experiment plan",
])

with tabs[0]:
    st.subheader("From feedback volume to product judgment")
    a, b, c, d = st.columns(4)
    a.metric("Customer signals", len(feedback))
    b.metric("Reviewed themes", int(feedback.loc[feedback.theme != "Needs review", "theme"].nunique()))
    c.metric("Blocking signals", int(feedback.urgent.sum()))
    d.metric("Candidate bets", len(st.session_state.options))
    left, right = st.columns(2)
    with left:
        st.markdown("**What problems keep appearing?**")
        counts = feedback.theme.value_counts()
        if not counts.empty:
            st.bar_chart(counts, horizontal=True)
        else:
            st.info("No feedback available")
    with right:
        st.markdown("**Who is reporting issues?**")
        mix = feedback.segment.value_counts()
        if not mix.empty:
            st.bar_chart(mix, horizontal=True)
        else:
            st.info("No feedback available")
    st.markdown("### Decision brief")
    top = feedback.loc[feedback.urgent.eq(1), "theme"].value_counts()
    if len(top):
        st.write(
            f"**Investigate first:** {top.index[0]} is the most frequent theme "
            f"among signals manually tagged as blocking ({top.iloc[0]} signals). "
            "Volume is not a substitute for affected-user counts, severity, or revenue exposure."
        )
    else:
        st.write("No blocking workflow signals have been tagged yet.")
    st.write(
        "**Proposed north-star metric:** weekly successful core workflows per active account. "
        "**Supporting metrics:** activation, repeat use, support contact rate and latency."
    )
    st.caption("This is a synthetic scenario. Real discovery would need interviews, telemetry and account-level denominators.")

with tabs[1]:
    st.subheader("Voice of customer")
    st.write("Inspect raw evidence before building a roadmap. Tags below are human-reviewed labels.")
    search = st.text_input("Search feedback text", placeholder="e.g. checkout, report, search")
    segments = sorted(feedback.segment.dropna().unique().tolist())
    selected = st.multiselect("Customer segments", segments, default=segments)
    matching = feedback.loc[
        feedback.segment.isin(selected)
        & feedback.feedback.astype(str).str.contains(re.escape(search), case=False, na=False)
    ]
    st.dataframe(matching, hide_index=True, use_container_width=True)
    st.download_button(
        "Export current feedback",
        feedback.to_csv(index=False).encode("utf-8"),
        "productpulse_feedback.csv",
        mime="text/csv",
    )
    with st.expander("Import customer feedback from CSV", expanded=False):
        st.write("Upload a CSV with **feedback** and **segment** columns; optional **urgent** column.")
        uploaded = st.file_uploader("Choose CSV", type=["csv"], key="upload")
        if uploaded:
            try:
                incoming = validate_feedback_upload(pd.read_csv(uploaded))
                st.success(f"{len(incoming)} valid rows ready to import.")
                st.dataframe(incoming.head(5), hide_index=True, use_container_width=True)
                if st.button("Import and queue for AI review"):
                    incoming["id"] = [
                        f"I{i:06d}"
                        for i in range(len(feedback) + 1, len(feedback) + len(incoming) + 1)
                    ]
                    st.session_state.feedback = pd.concat(
                        [feedback, incoming], ignore_index=True
                    )
                    st.rerun()
            except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
                st.error(f"Cannot import CSV: {exc}")
    with st.form("new_signal", clear_on_submit=True):
        st.markdown("**Add one customer signal**")
        message = st.text_area("Exact customer language")
        col1, col2, col3 = st.columns(3)
        segment = col1.selectbox("Segment", ["Enterprise", "SMB", "Startup"])
        theme = col2.selectbox("Human-reviewed theme", ["Needs review"] + list(THEME_EXAMPLES))
        urgent = col3.checkbox("Blocks a core workflow")
        submitted = st.form_submit_button("Add signal", type="primary")
        if submitted:
            if len(message.strip()) < 3:
                st.warning("Enter at least 3 characters of feedback.")
            else:
                identifier = f"N{len(feedback) + 1:06d}"
                row = pd.DataFrame([{
                    "id": identifier, "feedback": message.strip()[:2000],
                    "theme": theme, "segment": segment, "urgent": int(urgent)
                }])
                st.session_state.feedback = pd.concat([feedback, row], ignore_index=True)
                st.rerun()

with tabs[2]:
    st.subheader("Explainable AI-assisted triage")
    st.write(
        "A local **TF-IDF + cosine similarity** model compares each feedback item with "
        "example phrases for six themes. It provides suggestions and similarity scores; "
        "you approve or correct each label."
    )
    review_only = st.checkbox("Show only unreviewed signals", value=True)
    candidates = feedback.loc[
        feedback.theme.eq("Needs review") if review_only
        else pd.Series(True, index=feedback.index)
    ]
    if candidates.empty:
        st.success("No unreviewed signals. Turn off the filter to audit existing labels.")
    else:
        suggestions = suggest_themes(candidates.feedback.astype(str).tolist())
        reviewed = pd.concat(
            [candidates.reset_index(drop=True), suggestions], axis=1
        )
        st.dataframe(
            reviewed[["id", "feedback", "theme", "suggested_theme", "similarity", "review"]],
            hide_index=True, use_container_width=True
        )
        st.caption(
            "Similarity is NOT a confidence probability. A low score requests human review. "
            "Example phrases are authored for this demo, and no accuracy benchmark is claimed."
        )
        ids = reviewed.id.astype(str).tolist()
        if ids:
            chosen_id = st.selectbox("Select signal to review", ids)
            signal = reviewed.loc[reviewed.id.eq(chosen_id)].iloc[0]
            st.write(f"**Customer said:** {signal['feedback']}")
            suggested = signal["suggested_theme"]
            choices = ["Needs review"] + list(THEME_EXAMPLES)
            default_theme = suggested if suggested in choices else "Needs review"
            assigned = st.selectbox(
                "Approve or override suggested theme",
                choices,
                index=choices.index(default_theme),
                key=f"theme_choice_{chosen_id}",
            )
            if st.button("Save reviewed label", type="primary"):
                st.session_state.feedback.loc[
                    st.session_state.feedback.id.eq(chosen_id), "theme"
                ] = assigned
                st.rerun()
        if st.button("Accept all non-uncertain suggestions", help="You remain responsible for checking classification quality."):
            for _, row in reviewed.iterrows():
                if row["suggested_theme"] != "Needs review":
                    st.session_state.feedback.loc[
                        st.session_state.feedback.id.eq(row["id"]), "theme"
                    ] = row["suggested_theme"]
            st.rerun()

with tabs[3]:
    st.subheader("Prioritization is a hypothesis, not a leaderboard")
    st.markdown(
        "**RICE = Reach × Impact × Confidence / Effort**. "
        "Reach is affected users per quarter; Impact uses the 0.25–3 scale; "
        "Confidence is 0–1; Effort is person-months."
    )
    with st.form("rice_form"):
        edited = st.data_editor(
            st.session_state.options,
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={
                "confidence": st.column_config.NumberColumn(
                    "confidence", min_value=0.0, max_value=1.0, step=.05
                ),
                "effort": st.column_config.NumberColumn(
                    "effort", min_value=.1, step=.5
                ),
                "impact": st.column_config.NumberColumn(
                    "impact", min_value=0.0, max_value=3.0, step=.25
                ),
            },
            key="rice_edit",
        )
        if st.form_submit_button("Recalculate ranking", type="primary"):
            st.session_state.options = edited.reset_index(drop=True)
            st.rerun()
    options = st.session_state.options
    if not options.empty:
        ranked = rank_initiatives(options.dropna(subset=["feature"]).copy())
    else:
        ranked = pd.DataFrame()
    if not ranked.empty:
        st.dataframe(
            ranked[["feature", "goal", "reach", "impact", "confidence", "effort", "RICE"]],
            hide_index=True, use_container_width=True
        )
        st.bar_chart(ranked.set_index("feature")["RICE"], horizontal=True)
        leader = ranked.iloc[0]
        st.success(f"Highest RICE estimate: {leader['feature']} ({leader['RICE']:,.1f})")
        st.download_button(
            "Export prioritized initiatives",
            ranked.to_csv(index=False), "productpulse_priorities.csv", "text/csv"
        )
    else:
        st.warning("Enter at least one initiative with valid, non-zero effort.")
    st.warning(
        "A PM should override RICE for reliability incidents, safety, enterprise commitments, "
        "platform dependencies and strategic fit. Values here are invented, not observed."
    )

with tabs[4]:
    st.subheader("Now / Next / Later with written accountability")
    initiatives = [
        str(name) for name in st.session_state.options.feature.dropna().tolist()
        if str(name).strip()
    ]
    if not initiatives:
        st.warning("Add an initiative in Prioritization first.")
    else:
        name = st.selectbox("Initiative to decide", initiatives, key="roadmap_select")
        old = st.session_state.decisions.get(name, {})
        states = ["Investigate", "Now", "Next", "Later", "Not planned"]
        with st.form(f"decision_{name}"):
            status = st.selectbox(
                "Decision", states, index=states.index(old.get("status", "Investigate"))
            )
            rationale = st.text_area(
                "Evidence, counterarguments, dependencies and why now",
                value=old.get("rationale", ""),
                placeholder="We chose X because... We are not choosing Y because...",
            )
            owner = st.text_input("Decision owner", value=old.get("owner", "Product team"))
            if st.form_submit_button("Record decision", type="primary"):
                if not rationale.strip():
                    st.error("Write a rationale before saving a product decision.")
                else:
                    st.session_state.decisions[name] = {
                        "status": status,
                        "rationale": rationale.strip(),
                        "owner": owner.strip() or "Product team",
                    }
                    st.success("Decision recorded in this browser session.")
        if st.session_state.decisions:
            log = pd.DataFrame([
                {"initiative": key, **value}
                for key, value in st.session_state.decisions.items()
            ])
            st.markdown("**Decision log**")
            st.dataframe(log, hide_index=True, use_container_width=True)
            st.download_button(
                "Export decision log",
                log.to_csv(index=False),
                "productpulse_decisions.csv", "text/csv"
            )
    st.caption("Decisions persist only for the current Streamlit session. Export CSV to retain them.")

with tabs[5]:
    st.subheader("Define proof before shipping")
    initiatives = st.session_state.options.feature.dropna().astype(str).tolist()
    if not initiatives:
        st.warning("Add a candidate initiative first.")
    else:
        selected = st.selectbox("Initiative under test", initiatives, key="experiment_select")
        st.write(
            f"**Hypothesis:** If we deliver **{selected}** for an eligible user cohort, "
            "then successful completion of the affected workflow will increase because "
            "a known source of friction is removed."
        )
        with st.form("experiment_form"):
            c1, c2, c3 = st.columns(3)
            baseline = c1.number_input("Baseline completion (%)", 0.0, 100.0, 60.0, .5)
            target = c2.number_input("Target completion (%)", 0.0, 100.0, 70.0, .5)
            duration = c3.number_input("Measurement window (days)", 1, 180, 14)
            audience = st.text_input("Eligibility and segment", "Affected active accounts")
            guardrail = st.text_input(
                "Safety / quality guardrails", "Error rate, page latency, support contact rate"
            )
            caveat = st.text_area(
                "Experiment design and risks",
                "Randomly assign eligible accounts where feasible; avoid contamination "
                "between cohorts. Estimate sample size before launch and review "
                "confidence intervals, novelty effects and segment heterogeneity.",
            )
            if st.form_submit_button("Save experiment brief", type="primary"):
                st.session_state.experiment_notes[selected] = {
                    "initiative": selected,
                    "baseline_pct": baseline,
                    "target_pct": target,
                    "uplift_percentage_points": round(target - baseline, 2),
                    "window_days": duration,
                    "audience": audience,
                    "guardrails": guardrail,
                    "design_notes": caveat,
                }
                st.success("Experiment brief saved for this session.")
        st.metric("Proposed uplift", f"{target-baseline:+.1f} percentage points")
        st.caption(
            "This defines a measurement plan; it does not run an experiment, "
            "calculate statistical significance or imply a real-world uplift."
        )
        if selected in st.session_state.experiment_notes:
            brief = st.session_state.experiment_notes[selected]
            st.download_button(
                "Export experiment brief",
                pd.DataFrame([brief]).to_csv(index=False),
                "productpulse_experiment.csv", "text/csv"
            )
