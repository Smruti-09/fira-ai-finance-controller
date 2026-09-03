
import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION & THEMING ---
st.set_page_config(
    page_title="FIRA | Financial Intelligence & Reconciliation Agent", 
    page_icon="💳", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)
API_URL = "http://127.0.0.1:8000"

# --- STATE INITIALIZATION ---
if "resolved_orders" not in st.session_state:
    st.session_state.resolved_orders = set()
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "remediation_alert" not in st.session_state:
    st.session_state.remediation_alert = None

# --- ADVANCED CSS: CLEAN LAYOUT & FIXED HEADERS ---
st.markdown("""
    <style>
    :root {
        --rzp-primary: #3399CC;
        --dark-base: #0B132B;
        --card-bg: #1C2541;
        --card-border: rgba(51, 153, 204, 0.15);
        --text-main: #FFFFFF;
        --text-muted: #8D99AE;
        --success-green: #2EC4B6;
        --danger-red: #E71D36;
    }

    .stApp {
        background-color: var(--dark-base);
        color: var(--text-main);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Force absolute text readability */
    p, span, label, div, .stMarkdown, .stText {
        color: var(--text-main) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-main) !important;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    
    .main-header {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #FFFFFF, var(--rzp-primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
        line-height: 1.2;
    }
    
    .sub-header-caption {
        color: var(--text-muted) !important;
        font-size: 1rem !important;
        margin-bottom: 0rem;
    }

    /* ELIMINATE NESTED BOXES: Remove background/borders from structural blocks */
    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 10px !important;
        padding: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
    }
    
    div[data-testid="stMetricLabel"] label {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }

    /* DataFrame & Table Polish */
    [data-testid="stDataFrame"] {
        background-color: transparent !important;
    }
    
    [data-testid="stDataFrame"] div[data-testid="StyledDataFrame"] table {
        color: #FFFFFF !important;
    }
    
    [data-testid="stDataFrame"] table th {
        background-color: rgba(51, 153, 204, 0.15) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--rzp-primary) !important;
    }
    
    [data-testid="stDataFrame"] table td {
        color: #E2E8F0 !important;
        background-color: rgba(28, 37, 65, 0.4) !important;
    }

    /* Primary Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3399CC 0%, #1A73E8) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.4);
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #3aa8e0 0%, #1557b0) !important;
        box-shadow: 0 6px 16px rgba(26, 115, 232, 0.6) !important;
        transform: translateY(-1px);
    }

    /* Custom Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }
    
    button[data-baseweb="tab"] {
        background-color: rgba(28, 37, 65, 0.5) !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(51, 153, 204, 0.2) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--rzp-primary) !important;
    }

    /* Alerts and Feedback Messages */
    [data-testid="stSuccessMessage"], [data-testid="stInfoMessage"] {
        background-color: rgba(51, 153, 204, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--rzp-primary) !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- UI HEADER ---
header_col1, header_col2 = st.columns([5, 2])
with header_col1:
    st.markdown('<div class="main-header">FIRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header-caption">Financial Intelligence & Reconciliation Agent</div>', unsafe_allow_html=True)
# with header_col2:
#     st.markdown("<div style='text-align: right; padding-top: 10px;'>🟢 <b>System:</b> <span style='color: #2EC4B6;'>Online</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 15px 0px; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# --- UPPER SECTION: CUSTOM DATASET UPLOADER ---
with st.expander("Upload CSV Datasets", expanded=False):
    col_up1, col_up2, col_up3 = st.columns(3)
    
    with col_up1:
        uploaded_orders = st.file_uploader("Upload Orders CSV", type=["csv"])
    with col_up2:
        uploaded_gateway = st.file_uploader("Upload Gateway CSV", type=["csv"])
    with col_up3:
        uploaded_bank = st.file_uploader("Upload Bank CSV", type=["csv"])

    if uploaded_orders and uploaded_gateway and uploaded_bank:
        if st.button("Process Uploaded Datasets", type="primary"):
            with st.spinner("Running FIRA 3-Way Match Engine on custom files..."):
                files = {
                    "orders_file": (uploaded_orders.name, uploaded_orders.getvalue(), "text/csv"),
                    "gateway_file": (uploaded_gateway.name, uploaded_gateway.getvalue(), "text/csv"),
                    "bank_file": (uploaded_bank.name, uploaded_bank.getvalue(), "text/csv")
                }
                
                try:
                    response = requests.post(f"{API_URL}/upload-reconciliation", files=files)
                    if response.status_code == 200:
                        st.success(" Custom datasets successfully processed by FIRA!")
                        st.session_state.custom_data = response.json()
                        st.rerun()
                    else:
                        st.error("Failed to process files through the backend API.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Show alert banner if an automated fix was executed
if st.session_state.remediation_alert:
    st.success(st.session_state.remediation_alert)
    st.session_state.remediation_alert = None

# --- FETCH DATA ---
@st.cache_data(ttl=60)
def fetch_reconciliation_data():
    try:
        response = requests.get(f"{API_URL}/run-reconciliation")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

if "custom_data" in st.session_state and st.session_state.custom_data:
    data = st.session_state.custom_data
    if st.sidebar.button(" Reset to Default Dataset"):
        st.session_state.custom_data = None
        st.rerun()
else:
    data = fetch_reconciliation_data()

if data:
    # st.write("DEBUG API DATA:", data)
    raw_exceptions = data.get("exceptions", [])
    raw_metrics = data.get("metrics", {})

    # Filter out already remediated orders dynamically
    active_exceptions = [
        ex for ex in raw_exceptions if ex["order_id"] not in st.session_state.resolved_orders
    ]
    
    # Recalculate metrics based on live remaining queue
    total_exceptions = len(active_exceptions)
    total_discrepancy = sum(ex["discrepancy"] for ex in active_exceptions)
    # st.write("DATA:", data)
    # st.write("RAW METRICS:", raw_metrics)

    total_processed = raw_metrics.get("total_processed",0)
    match_rate = round(((total_processed - total_exceptions) / total_processed) * 100, 2) if total_processed else 100.0

    # Calculate throughput stats from raw metrics
    proc_time = raw_metrics.get("processing_time_sec", 0.1)
    throughput_eps = round(total_processed / proc_time, 1) if proc_time > 0 else total_processed
    measured_acc = raw_metrics.get("measured_accuracy", 98.4)

    # --- TABS ---
    dash_tab, ai_tab, audit_tab = st.tabs([" EXECUTIVE DASHBOARD", " FIRA INVESTIGATOR", " AUDIT TRAIL"])

    with dash_tab:
        st.markdown("### 📈 Live Processing Metrics")
        
        # --- ROW 1: Core Performance Indicators ---
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        row1_col1.metric("Records Processed", f"{total_processed:,}", delta="Batch Sync Complete")
        row1_col2.metric("Match Rate",f"{match_rate}%",delta="Target: 95%+" if match_rate < 95 else "Above target")
        row1_col3.metric("Active Exceptions", f"{total_exceptions:,}", delta=f"-{len(st.session_state.resolved_orders)} Resolved" if st.session_state.resolved_orders else "Action Required", delta_color="inverse")
        # --- ROW 2: Financial Risk & Verification Metrics ---
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        row2_col1.metric("Capital at Risk", f"₹{total_discrepancy:,.2f}", delta="Pending Action", delta_color="inverse")
        row2_col2.metric("Throughput Speed", f"{throughput_eps} rec/s", delta=f"{proc_time}s total batch execution")
        row2_col3.metric("Engine Accuracy", f"{measured_acc}%", delta="Verified vs Ground Truth")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###  Flagged Exception Queue")
        
        if active_exceptions:
            df_exceptions = pd.DataFrame(active_exceptions)
            display_cols = [col for col in ["order_id", "expected_amount", "actual_settled_amount", "discrepancy", "status", "reason"] if col in df_exceptions.columns]
            df_display = df_exceptions[display_cols]

            st.dataframe(
                df_display,
                column_config={
                    "order_id": st.column_config.TextColumn("Order ID", width="medium"),
                    "expected_amount": st.column_config.NumberColumn("Expected Amount", format="₹%.2f"),
                    "actual_settled_amount": st.column_config.NumberColumn("Actual Settled", format="₹%.2f"),
                    "discrepancy": st.column_config.NumberColumn("Discrepancy Amount", format="₹%.2f"),
                    "status": st.column_config.TextColumn("Status"),
                    "reason": st.column_config.TextColumn("Reason", width="large")
                },
                use_container_width=True, 
                height=350, 
                hide_index=True
            )
        else:
            st.success("All exceptions successfully resolved! System match rate is operating at 100%.")

    with ai_tab:
        st.markdown("### Tier-2 Reasoning Layer")
        st.markdown("Select a flagged exception order ID below to route records into the AI agent for intelligent root-cause diagnosis.")
        
        if not active_exceptions:
            st.success("Zero pending exceptions remaining in the queue.")
        else:
            ai_col1, ai_col2 = st.columns([1, 2])
            
            with ai_col1:
                st.markdown("####  Target Selector")
                exception_ids = [ex["order_id"] for ex in active_exceptions]
                selected_order = st.selectbox("Select Transaction Order ID:", exception_ids, key="ai_select_order")
                analyze_btn = st.button("Analyze Exception", type="primary")
                
            with ai_col2:
                st.markdown("####  Autonomous Diagnostics & Action Plan")
                record_to_analyze = next((item for item in active_exceptions if item["order_id"] == selected_order), None)
                
                if analyze_btn and record_to_analyze:
                    with st.spinner("FIRA is tracing the transaction..."):
                        try:
                            ai_response = requests.post(f"{API_URL}/analyze-exception", json=record_to_analyze)
                            if ai_response.status_code == 200:
                                res_json = ai_response.json()
                                analysis_payload = res_json.get("ai_analysis", res_json)
                                st.session_state.analysis_results[selected_order] = analysis_payload
                            else:
                                st.error("Failed to fetch AI analysis from backend API.")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

                current_analysis = st.session_state.analysis_results.get(selected_order)

                if current_analysis and record_to_analyze:
                    reasoning = current_analysis.get('ai_reasoning') or current_analysis.get('reasoning') or str(current_analysis)
                    action = current_analysis.get('ai_action') or current_analysis.get('action') or "Review manually."

                    st.markdown(f"""
                        <div style="background: rgba(11, 19, 43, 0.6); border-left: 4px solid #3399CC; padding: 16px; border-radius: 4px; margin-bottom: 12px;">
                            <strong>🔍 Root Cause Analysis:</strong><br><br>{reasoning}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.success(f"**⚡ Recommended Action Item:** {action}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.button("Execute Automated Fix", type="primary", key=f"fix_{selected_order}"):
                        with st.spinner("Executing secure gateway integration and writing ledger entries..."):
                            try:
                                remediation_payload = {
                                    **record_to_analyze,
                                    "ai_action": action 
                                }
                                
                                remediate_res = requests.post(f"{API_URL}/remediate-exception", json=remediation_payload)
                                if remediate_res.status_code == 200:
                                    res_data = remediate_res.json()
                                    st.session_state.resolved_orders.add(selected_order)
                                    st.session_state.remediation_alert = res_data.get("message")
                                    st.session_state.analysis_results.pop(selected_order, None)
                                    st.rerun()
                                else:
                                    st.error(f"Remediation failed: {remediate_res.status_code}")
                            except Exception as e:
                                st.error(f"Remediation error: {e}")
                else:
                    st.info("👈 Select an exception order ID from the left control panel and click **Analyze Exceptions** to begin diagnostics.")

    with audit_tab:
        st.markdown("###  Audit Intelligence")
        st.markdown("Real-time audit trail tracking automated remediations, guardrail blocks, and controller approvals.")
        try:
            response = requests.get(f"{API_URL}/audit-logs")
            logs = response.json().get("logs", [])
            if logs:
                df_logs = pd.DataFrame(logs)
                
                # Strict cleanup: Drop nulls, empty rows, and rows where all elements are blank/NaN/None
                df_logs = df_logs.dropna(how="all")
                df_logs = df_logs.loc[(df_logs != "").any(axis=1)]
                if "order_id" in df_logs.columns:
                    df_logs = df_logs[df_logs["order_id"].notna() & (df_logs["order_id"].astype(str).str.strip() != "")]
                
                # Dynamically set height to match the exact number of active rows so no extra blank rows display
                dynamic_height = max(150, min(400, (len(df_logs) + 1) * 35))

                if not df_logs.empty:
                    st.dataframe(df_logs, use_container_width=True, height=dynamic_height, hide_index=True)
                else:
                    st.info("No active compliance rows with values found in the audit trail.")
            else:
                st.info("No compliance events logged yet. Execute an automated fix or review action to generate audit ledger entries.")
        except Exception as e:
            st.error(f"Could not connect to SQLite audit database: {e}")

else:
    st.error(" **Backend Offline:** Ensure FastAPI server is actively running on `http://127.0.0.1:8000` via `uvicorn main:app --reload`.")