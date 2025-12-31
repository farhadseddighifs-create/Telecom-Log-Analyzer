import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from data_generator import generate_large_dataset

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Telecom Analytics Dashboard",
    layout="wide",
    page_icon="📡",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #0d47a1;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. Helper Functions ---

@st.cache_data
def load_data(file_path):
    """
    Loads the CSV data and performs basic cleaning.
    """
    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        # Basic Cleaning
        df = df.dropna()
        df = df[df['Duration'] > 0]
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# --- 4. Main Application ---

def main():
    # Header Section
    st.title("📡 Telecom Network Traffic Analyzer")
    st.markdown("### Executive Dashboard for Call Logs & Fraud Detection")
    st.markdown("Use the controls below to analyze network performance and detect anomalies.")
    st.markdown("---")

    # --- Sidebar (Control Panel) ---
    st.sidebar.header("🔧 Control Panel")
    st.sidebar.markdown("Manage dataset and settings.")

    # Data Generation Button
    if st.sidebar.button("🔄 Generate New Dataset"):
        with st.spinner('Simulating 50,000 records...'):
            # Generating a smaller set for the web demo speed (50k instead of 1M)
            generate_large_dataset('telecom_data_large.csv', num_records=50000)
        st.sidebar.success("New dataset generated successfully!")
        st.cache_data.clear()  # Clear cache to force reload

    # Load Data
    filename = 'telecom_data_large.csv'
    df = load_data(filename)

    if df is None:
        st.warning(f"⚠️ Data file '{filename}' not found. Please click **Generate New Dataset** in the sidebar.")
        return

    # --- KPI Metrics Section ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Calls", f"{len(df):,}")
    with col2:
        total_gb = df['Data_Usage'].sum() / 1024
        st.metric("Total Data Usage", f"{total_gb:,.1f} GB")
    with col3:
        avg_dur = df['Duration'].mean() / 60
        st.metric("Avg Duration", f"{avg_dur:.1f} min")
    with col4:
        # Simple fraud criteria for KPI
        fraud_kpi = len(df[(df['Duration'] > 3300) | (df['Data_Usage'] > 450)])
        st.metric("Risk Alerts", f"{fraud_kpi}", delta_color="inverse")

    st.markdown("---")

    # --- Analysis Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Usage Analytics", "⏰ Peak Hours", "🚨 Fraud Detection"])

    # TAB 1: Usage Analysis
    with tab1:
        st.subheader("Internet Usage by Call Type")

        col_chart, col_data = st.columns([2, 1])

        with col_chart:
            usage_summary = df.groupby('Call_Type')['Data_Usage'].sum()

            fig, ax = plt.subplots(figsize=(8, 4))
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            usage_summary.plot(kind='bar', color=colors, ax=ax, edgecolor='black', alpha=0.8)

            ax.set_title('Total Data Consumption (MB)', fontsize=12)
            ax.set_xlabel('Call Type')
            ax.set_ylabel('Usage (MB)')
            ax.grid(axis='y', linestyle='--', alpha=0.5)

            # Format Y-axis to Millions (M)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x * 1e-6:.1f}M'))
            plt.xticks(rotation=0)

            st.pyplot(fig)

        with col_data:
            st.write("**Data Summary:**")
            st.dataframe(usage_summary, use_container_width=True)

    # TAB 2: Peak Hours
    with tab2:
        st.subheader("Network Traffic Analysis (24 Hours)")

        df['Hour'] = df['Date'].dt.hour
        hourly_traffic = df.groupby('Hour').size()

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        hourly_traffic.plot(kind='line', marker='o', color='#673AB7', linewidth=2.5, ax=ax2)

        ax2.set_title('Call Volume per Hour', fontsize=12)
        ax2.set_xlabel('Hour of Day (0-23)')
        ax2.set_ylabel('Number of Calls')
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.fill_between(hourly_traffic.index, hourly_traffic.values, color='#673AB7', alpha=0.1)

        st.pyplot(fig2)

        busiest_hour = hourly_traffic.idxmax()
        st.info(f"💡 Insight: The network experiences maximum load at **{busiest_hour}:00**.")

    # TAB 3: Fraud Detection
    with tab3:
        st.subheader("Security Audit & Anomaly Detection")
        st.markdown("Identify users with unusual behavior based on duration and data limits.")

        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            threshold_duration = st.slider("Max Duration Threshold (Seconds)", 1000, 5000, 3300)
        with col_filter2:
            threshold_data = st.slider("Max Data Usage Threshold (MB)", 100, 1000, 450)

        # Filtering logic
        suspicious_df = df[(df['Duration'] > threshold_duration) | (df['Data_Usage'] > threshold_data)]

        if len(suspicious_df) > 0:
            st.error(f"🚨 Alert: {len(suspicious_df)} suspicious records detected!")
            st.dataframe(suspicious_df.head(100), use_container_width=True)
            st.caption("Showing top 100 records only.")

            # Download Button
            csv_data = suspicious_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Fraud Report (CSV)",
                data=csv_data,
                file_name="fraud_report.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ System Secure: No anomalies detected with current thresholds.")


if __name__ == "__main__":
    main()