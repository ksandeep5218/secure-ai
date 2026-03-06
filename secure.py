import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib
from datetime import datetime
import random
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NEURAL-SHIELD PREMIUM",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. PREMIUM THEME & CHAT STYLING ---
st.markdown("""
<style>

/* MAIN APP BACKGROUND */
.stApp{
background: radial-gradient(circle at top,#0f172a,#020617);
color:white;
font-family: "Segoe UI", sans-serif;
}

/* SIDEBAR */
section[data-testid="stSidebar"]{
background:#020617;
color:white;
border-right:1px solid #1e293b;
}

/* METRICS */
div[data-testid="stMetricValue"]{
color:#38bdf8 !important;
font-weight:800 !important;
font-size:28px !important;
}

/* CHAT CONTAINER */
.chat-container{
padding:18px;
border-radius:14px;
margin-bottom:12px;
border-left:6px solid;
background:#1e293b;
color:white;
box-shadow:0px 5px 15px rgba(0,0,0,0.4);
transition:0.3s;
}

.chat-container:hover{
transform:scale(1.02);
box-shadow:0px 8px 20px rgba(56,189,248,0.4);
}

/* DEPLOYMENT SHIELD BOX */
.shield-box{
background:#111827;
border:2px solid #38bdf8;
border-radius:18px;
padding:26px;
text-align:center;
color:white;
box-shadow:0px 0px 20px rgba(56,189,248,0.3);
}

/* PREMIUM TAG */
.premium-tag{
background:linear-gradient(90deg,#f59e0b,#fbbf24);
color:black;
padding:4px 12px;
border-radius:20px;
font-size:12px;
font-weight:bold;
}

/* TABLE STYLE */
[data-testid="stTable"]{
background:#1e293b;
color:white;
border-radius:10px;
}

/* BUTTON */
button{
background:#0284c7 !important;
color:white !important;
border-radius:10px !important;
border:none !important;
}

/* INPUT BOX */
input{
background:#020617 !important;
color:white !important;
border:1px solid #334155 !important;
}

/* CHAT INPUT */
textarea{
background:#020617 !important;
color:white !important;
border:1px solid #334155 !important;
}

</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "cooldown" not in st.session_state:
    st.session_state.cooldown = 0


def add_audit_log(operation, status):
    timestamp = datetime.now().strftime("%H:%M:%S")
    trace_id = hashlib.md5(f"{timestamp}{operation}".encode()).hexdigest()[:8].upper()
    st.session_state.audit_logs.insert(0, {"TIMESTAMP": timestamp, "OPERATION": operation, "STATUS": status,
                                           "TRACE_ID": trace_id})


# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ NEURAL-SHIELD")
    st.markdown("<span class='premium-tag'>Premium Free Trial</span>", unsafe_allow_html=True)
    api_key = st.text_input("Enter Gemini API Access Key:", type="password")
    selected_model = None
    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            selected_model = next((m for m in models if '1.5-flash' in m), models[0] if models else None)
            if selected_model:
                st.success(f"NODE ONLINE")
        except:
            st.error("AUTH FAILED")


# --- 5. UTILITIES ---
def get_text(file):
    try:
        if file.name.endswith('.pdf'):
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        return file.read().decode("utf-8")
    except:
        return "Extraction Error"


# --- 6. MAIN INTERFACE ---
st.title("🌐 AI Security Operations Center")
st.markdown("---")

v1, v2, v3, v4 = st.columns(4)
v1.metric("Latency", f"{random.randint(25, 40)}ms", "-3ms")
v2.metric("Pipeline Integrity", "100%", "Secure")
v3.metric("XAI Confidence", "0.97", "Optimal")

success_rate = 100
if st.session_state.audit_logs:
    logs_df = pd.DataFrame(st.session_state.audit_logs)
    success_rate = (len(logs_df[logs_df['STATUS'] == 'SUCCESS']) / len(logs_df)) * 100
v4.metric("System Health", f"{int(success_rate)}%", "Live")

tab1, tab2, tab3 = st.tabs(["⚡ NEURAL ENGINE", "🏗️ STRATEGY LAB", "🚀 EXTENSION HUB"])

# TAB 1: NEURAL ENGINE
with tab1:
    l, r = st.columns([2, 1])
    with l:
        st.subheader("🤖 Neural Processing Unit")
        uploaded_file = st.file_uploader("Ingest secure document stream", type=['pdf', 'txt'])

        if time.time() < st.session_state.cooldown:
            remaining = int(st.session_state.cooldown - time.time())
            st.error(f"SYSTEM OVERLOAD: Rate limit active. Recovery in {remaining}s")
            time.sleep(1)
            st.rerun()

        colors = ["#0ea5e9", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b"]
        for i, chat in enumerate(st.session_state.chat_history):
            color = colors[i % len(colors)]
            st.markdown(f"""
                <div class="chat-container" style="border-left-color: {color};">
                    <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">Query {i + 1}</p>
                    <p style="font-size: 0.9rem; color: #64748b;"><b>Q:</b> {chat['question']}</p>
                    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #f1f5f9;">
                    <p style="font-size: 0.95rem;"><b>A:</b> {chat['answer']}</p>
                </div>
            """, unsafe_allow_html=True)

        if prompt := st.chat_input("Enter query for neural analysis..."):
            if not selected_model:
                st.warning("Please provide API key.")
            else:
                try:
                    doc_text = get_text(uploaded_file) if uploaded_file else ""
                    model = genai.GenerativeModel(selected_model)
                    res = model.generate_content(f"Data: {doc_text}\n\nTask: {prompt}" if doc_text else prompt)
                    st.session_state.chat_history.append({"question": prompt, "answer": res.text})
                    add_audit_log("Neural Inference", "SUCCESS")
                    st.rerun()
                except Exception as e:
                    if "429" in str(e):
                        st.session_state.cooldown = time.time() + 60
                        add_audit_log("Inference", "FAILED (429)")
                        st.rerun()
                    else:
                        st.error(f"Error: {e}")
                        add_audit_log("Inference", "FAILED")
    with r:
        st.markdown(f"""
        <div class="shield-box">
            <h3 style='color: #0369a1;'>🛡️ Deployment Shield</h3>
            <p>Node: <b>Premium Proxy</b></p>
            <p>Tier: <span class='premium-tag'>Free Trial Active</span></p>
            <hr>
            <p style='font-size: 0.8rem; color: #64748b;'>Analysis auto-saved to session logs.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Clear History"):
            st.session_state.chat_history = []
            st.rerun()

# TAB 2: ARCHITECTURE STRATEGY LAB (WITH GRAPH)
with tab2:
    st.subheader("🏗️ Architecture Strategy Lab")
    st.markdown("Analyze infrastructure trade-offs for AI deployment.")

    strategy = st.select_slider("Select Deployment Target:", options=["Public Cloud", "Hybrid Cloud", "Private Cloud"])

    # Define Data for Graph
    # Format: [Scalability, Security, Transparency, Cost-Effectiveness, Compliance]
    strat_data = {
        "Public Cloud": [100, 40, 30, 90, 50],
        "Hybrid Cloud": [75, 80, 70, 60, 85],
        "Private Cloud": [30, 100, 100, 20, 100]
    }
    metrics = ['Scalability', 'Security', 'Transparency', 'Cost-Effectiveness', 'Compliance']

    c1, c2 = st.columns([1, 1])
    with c1:
        st.info(f"Recommended Protocol for **{strategy}** active.")
        st.markdown(f"The **{strategy}** model provides a specific balance of risk and performance.")

        # Display matching table
        eval_df = pd.DataFrame({
            "Metric": metrics,
            "Value Score": strat_data[strategy]
        })
        st.table(eval_df)

    with c2:
        # Create Radar Chart
        fig_strat = go.Figure()
        fig_strat.add_trace(go.Scatterpolar(
            r=strat_data[strategy],
            theta=metrics,
            fill='toself',
            name=strategy,
            line_color='#0ea5e9'
        ))
        fig_strat.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=f"Architecture Profile: {strategy}",
            height=400
        )
        st.plotly_chart(fig_strat, use_container_width=True)

# TAB 3: EXTENSION HUB
with tab3:
    st.subheader("🚀 Security & Cost Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(go.Figure(go.Scatterpolar(r=[random.randint(20, 80) for _ in range(5)],
                                                  theta=['Injection', 'Inversion', 'Leakage', 'Poisoning',
                                                         'Side-channel'], fill='toself', line_color='#ef4444')),
                        use_container_width=True)
    with c2:
        st.plotly_chart(
            px.bar(pd.DataFrame({'Cloud': ['Public', 'Hybrid', 'Private'], 'Efficiency': [98, 92, 75]}), x='Cloud',
                   y='Efficiency', color_discrete_sequence=['#0ea5e9']), use_container_width=True)

# --- 7. AUDIT FEED ---
st.divider()
if st.session_state.audit_logs:
    col_t, col_p, col_g = st.columns([2, 1, 1])
    df_logs = pd.DataFrame(st.session_state.audit_logs)
    with col_t: st.table(df_logs)
    with col_p:
        st.plotly_chart(px.pie(df_logs, names='STATUS', hole=0.4,
                               color_discrete_map={'SUCCESS': '#0ea5e9', 'FAILED': '#ef4444',
                                                   'FAILED (429)': '#f59e0b'}), use_container_width=True)
    with col_g:
        st.plotly_chart(go.Figure(
            go.Indicator(mode="gauge+number", value=success_rate, gauge={'bar': {'color': "#0284c7"}})).update_layout(
            height=250), use_container_width=True)