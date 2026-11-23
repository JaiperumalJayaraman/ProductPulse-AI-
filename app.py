import re
from collections import Counter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ProductPulse AI", page_icon="📡", layout="wide")
st.markdown("""<style>.block-container{padding-top:1.5rem}div[data-testid="stMetric"]{background:#f3f6fc;border-radius:12px;padding:14px}</style>""",unsafe_allow_html=True)
st.title("📡 ProductPulse AI")
st.caption("From customer signals to defensible product decisions • Interactive portfolio demonstration")
st.info("DEMO MODE — All included customer feedback and business estimates are synthetic. Scores are decision aids, not predictions.")
FEEDBACK = [
("F01","The checkout page freezes when I apply a coupon","Checkout","Enterprise",1),
("F02","Checkout keeps crashing on my phone","Checkout","SMB",1),
("F03","I cannot complete payment after entering a discount","Checkout","Startup",1),
("F04","Please add dark mode to the dashboard","Appearance","SMB",0),
("F05","Dark theme would help at night","Appearance","Startup",0),
("F06","Exporting reports as CSV would save our finance team hours","Reporting","Enterprise",0),
("F07","Need to download reports to Excel","Reporting","SMB",0),
("F08","Search doesn't find my saved projects","Search","Enterprise",1),
("F09","Project search returns irrelevant results","Search","SMB",0),
("F10","Invite teammates with different permissions","Collaboration","Enterprise",0),
("F11","Role-based access for our team is essential","Collaboration","SMB",0),
("F12","The mobile dashboard takes too long to load","Performance","Startup",1),
]
DEFAULT = pd.DataFrame(FEEDBACK,columns=["id","feedback","theme","segment","urgent"])
OPTIONS = pd.DataFrame([
("Fix checkout reliability","Checkout",1100,3,0.9,2.0,5,4,"Activation"),
("CSV / Excel exports","Reporting",800,2,0.8,1.5,4,2,"Retention"),
("Improve project search","Search",650,2,0.8,2.0,4,3,"Engagement"),
("Role-based permissions","Collaboration",450,3,0.65,3.0,5,4,"Enterprise adoption"),
("Improve mobile performance","Performance",900,2,0.7,2.5,4,3,"Retention"),
("Dark mode","Appearance",300,1,0.8,1.0,2,1,"Satisfaction"),
],columns=["feature","theme","reach","impact","confidence","effort","business_value","risk","goal"])
if "feedback" not in st.session_state: st.session_state.feedback=DEFAULT.copy()
if "options" not in st.session_state: st.session_state.options=OPTIONS.copy()
if "decisions" not in st.session_state: st.session_state.decisions={}
tabs=st.tabs(["📊 Overview","💬 Voice of Customer","🎯 Prioritization","🗺️ Roadmap & Decisions","🧪 Experiment Design"])
feedback=st.session_state.feedback
with tabs[0]:
    a,b,c,d=st.columns(4)
    a.metric("Feedback signals",len(feedback));b.metric("Themes",feedback.theme.nunique());c.metric("Urgent signals",int(feedback.urgent.sum()));d.metric("Candidate initiatives",len(st.session_state.options))
    left,right=st.columns(2)
    with left:
        st.subheader("Top customer themes")
        st.bar_chart(feedback.theme.value_counts())
    with right:
        st.subheader("Segment mix")
        st.bar_chart(feedback.segment.value_counts())
    st.subheader("The product problem")
    st.write("A product team receives scattered requests but has limited engineering capacity. Which customer problems deserve attention first, and why?")
    st.write("**North-star demonstration metric:** weekly successful core workflows per active account. Supporting metrics: activation, task success, retention and support contact rate.")
with tabs[1]:
    st.subheader("Customer evidence inbox")
    search=st.text_input("Search customer feedback")
    segments=st.multiselect("Filter segments",sorted(feedback.segment.unique()),default=sorted(feedback.segment.unique()))
    visible=feedback[feedback.segment.isin(segments)&feedback.feedback.str.contains(re.escape(search),case=False,na=False)]
    st.dataframe(visible,use_container_width=True,hide_index=True)
    with st.form("new_feedback"):
        st.markdown("**Add a customer signal**")
        msg=st.text_area("Feedback text")
        theme=st.selectbox("Theme",["Checkout","Reporting","Search","Collaboration","Performance","Appearance","Other"])
        segment=st.selectbox("Customer segment",["Enterprise","SMB","Startup"])
        urgent=st.checkbox("Blocks a core workflow")
        if st.form_submit_button("Add signal"):
            if msg.strip():
                new=pd.DataFrame([{"id":f"F{len(feedback)+1:02}","feedback":msg.strip(),"theme":theme,"segment":segment,"urgent":int(urgent)}])
                st.session_state.feedback=pd.concat([feedback,new],ignore_index=True)
                st.rerun()
            else: st.warning("Enter feedback first.")
    st.caption("Theme assignment is human-reviewed in this baseline version; no external AI API or hidden model is used.")
with tabs[2]:
    st.subheader("Compare initiatives using RICE")
    st.caption("Reach = estimated users per quarter; Impact = 0.25–3; Confidence = 0–1; Effort = person-months. Edit estimates to explore trade-offs.")
    edited=st.data_editor(st.session_state.options,num_rows="dynamic",use_container_width=True,hide_index=True,key="editor")
    st.session_state.options=edited.copy()
    valid=edited.dropna(subset=["feature","reach","impact","confidence","effort"]).copy()
    valid=valid[(valid.effort>0)&(valid.reach>=0)&(valid.confidence.between(0,1))&(valid.impact>=0)]
    valid["RICE"]=(valid.reach*valid.impact*valid.confidence/valid.effort).round(1)
    valid=valid.sort_values("RICE",ascending=False)
    st.dataframe(valid[["feature","goal","reach","impact","confidence","effort","RICE"]],use_container_width=True,hide_index=True)
    if not valid.empty:
        st.bar_chart(valid.set_index("feature")["RICE"])
        winner=valid.iloc[0]
        st.success(f"Highest RICE candidate: {winner['feature']} ({winner['RICE']:.1f}). Validate assumptions and dependencies before committing.")
    st.warning("RICE alone does not capture contractual obligations, security risk, technical dependencies or strategy. A PM can override rankings with a documented reason.")
with tabs[3]:
    st.subheader("Roadmap decisions — human in control")
    st.write("Record why you choose to build, investigate, defer or reject each initiative.")
    for _,r in st.session_state.options.iterrows():
        name=str(r["feature"])
        with st.expander(name):
            old=st.session_state.decisions.get(name,{"status":"Investigate","reason":""})
            status=st.selectbox("Decision",["Investigate","Now","Next","Later","Not planned"],index=["Investigate","Now","Next","Later","Not planned"].index(old["status"]),key="s"+name)
            reason=st.text_area("Evidence, trade-offs and decision rationale",value=old["reason"],key="r"+name)
            if st.button("Save decision",key="b"+name):
                st.session_state.decisions[name]={"status":status,"reason":reason}
                st.success("Decision saved for this session")
    rows=[{"Initiative":k,"Decision":v["status"],"Rationale":v["reason"]} for k,v in st.session_state.decisions.items()]
    if rows: st.download_button("Export decision log (CSV)",pd.DataFrame(rows).to_csv(index=False),"productpulse_decisions.csv","text/csv")
    st.caption("Session state is temporary; export decisions before closing the app.")
with tabs[4]:
    st.subheader("Turn a roadmap bet into a testable hypothesis")
    choice=st.selectbox("Initiative",st.session_state.options.feature.dropna().tolist())
    st.markdown("**Hypothesis template**")
    st.write(f"If we deliver **{choice}** for the affected segment, then the relevant core-workflow success metric will improve, because a documented user friction is reduced.")
    baseline=st.number_input("Baseline success rate (%)",min_value=0.0,max_value=100.0,value=60.0)
    target=st.number_input("Target success rate (%)",min_value=0.0,max_value=100.0,value=70.0)
    st.metric("Target uplift (percentage points)",f"{target-baseline:+.1f}")
    st.write("**Guardrails:** error rate, support tickets, latency and user complaints. **Evaluation:** compare eligible cohorts over a defined observation window; check sample size and bias before interpreting results.")
    st.caption("Targets are hypothetical; this dashboard does not run an A/B test or claim causal impact.")
