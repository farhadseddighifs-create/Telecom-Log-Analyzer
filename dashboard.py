import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Telecom Analytics", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Telecom Data Analysis Dashboard")
st.markdown(
    "Interactive dashboard analyzing **1 Million Records** (Real-time Simulation logic synced with Data Generator).")


# --- 1. Load & Generate Data (Exact logic from data_generator.py) ---
@st.cache_data
def load_data():
    """
    Tries to load 'telecom_data_large.csv'.
    If not found (e.g., on Hugging Face), it generates 1M records using
    the EXACT logic from data_generator.py.
    """
    try:
        # 1. Try Loading Local File
        df = pd.read_csv('telecom_data_large.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        source = "Local CSV"

    except FileNotFoundError:
        # 2. Generate Data (Fallback for Server) - Logic from data_generator.py
        source = "Generated In-Memory"
        num_records = 1000000

        # Date Logic
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_ts = start_date.timestamp()
        end_ts = end_date.timestamp()

        random_timestamps = np.random.uniform(start_ts, end_ts, num_records)
        dates = pd.to_datetime(random_timestamps, unit='s')

        # Call Type Logic (Weighted)
        types = ['Internal', 'International', 'Roaming', 'Emergency']
        call_types = np.random.choice(types, size=num_records, p=[0.60, 0.30, 0.05, 0.05])

        # Duration Logic
        durations = np.random.randint(10, 3600, size=num_records)

        # Data Usage Logic (with 30% zeros)
        usage_raw = np.random.uniform(5, 500, num_records)
        zero_mask = np.random.random(num_records) < 0.3
        data_usage = np.where(zero_mask, 0.0, usage_raw)
        data_usage = np.round(data_usage, 2)

        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Duration': durations,
            'Data_Usage': data_usage,
            'Call_Type': call_types,
        })

        # Inject Noise (Exact Logic)
        random_indices = np.random.choice(df.index, 20, replace=False)
        df.loc[random_indices, 'Duration'] = -100

        random_indices_null = np.random.choice(df.index, 20, replace=False)
        df.loc[random_indices_null, 'Data_Usage'] = np.nan

    # --- Preprocessing & Cleaning (Applied to both Loaded and Generated data) ---
    initial_count = len(df)

    # 1. Handle NaNs (from noise injection)
    df = df.dropna(subset=['Data_Usage'])

    # 2. Handle Negative Duration (from noise injection)
    df = df[df['Duration'] > 0]

    # 3. Add Hour column
    df['Hour'] = df['Date'].dt.hour

    cleaned_count = len(df)
    removed_rows = initial_count - cleaned_count

    return df, removed_rows, source


# Execute Load
with st.spinner('Processing 1 Million Records...'):
    df, removed_rows, data_source = load_data()

# FarhadSeddighi Telecom_log1
if df is not None:
    # --- 2. KPI Section ---
    st.subheader(f"📌 Key Performance Indicators (Source: {data_source})")

    # Fraud Definition
    high_duration_limit = 3000
    high_data_limit = 400
    # Note: Using copy() to avoid SettingWithCopyWarning on slices
    fraud_df = df[(df['Duration'] > high_duration_limit) | (df['Data_Usage'] > high_data_limit)].copy()
    fraud_count = len(fraud_df)

    # Layout Columns
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_data_tb = df['Data_Usage'].sum() / 1024 / 1024  # Convert MB to TB

    kpi1.metric("Total Active Records", f"{len(df):,}", delta=f"-{removed_rows} noise cleaned")
    kpi2.metric("Total Data Traffic", f"{total_data_tb:.2f} TB")
    kpi3.metric("Avg Duration", f"{df['Duration'].mean():.0f} sec")
    kpi4.metric("⚠️ Suspicious Activity", f"{fraud_count}", delta_color="inverse")

    st.divider()

    # --- 3. Charts Row 1 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Hourly Network Traffic")
        hourly_traffic = df.groupby('Hour').size()
        st.line_chart(hourly_traffic)
        st.caption("Peak traffic hours based on call frequency.")

    with col2:
        st.subheader("📊 Call Type Distribution")
        # Matches logic: Internal, International, Roaming, Emergency
        type_counts = df['Call_Type'].value_counts()
        st.bar_chart(type_counts)
        st.caption("Volume comparison by connection type.")

    st.divider()

    # --- 4. Advanced Analysis ---
    col3, col4 = st.columns([1, 2])

    with col3:
        st.subheader("🍰 Usage Segmentation")

        # Segmentation Logic
        conditions = [
            (df['Data_Usage'] > 300),
            (df['Data_Usage'] >= 100) & (df['Data_Usage'] <= 300),
            (df['Data_Usage'] < 100)
        ]
        labels = ['High User', 'Medium User', 'Low User']
        df['Segment'] = np.select(conditions, labels, default='Unknown')
        segment_counts = df['Segment'].value_counts()

        # Pie Chart
        fig, ax = plt.subplots(figsize=(6, 6))
        # Custom colors for segments
        colors = ['#ff9999', '#66b3ff', '#99ff99']

        wedges, texts, autotexts = ax.pie(
            segment_counts, labels=segment_counts.index, autopct='%1.1f%%',
            startangle=140, colors=colors, shadow=False
        )

        # Styling pie chart text
        plt.setp(autotexts, size=10, weight="bold", color="white")
        for w in wedges:
            w.set_path_effects([path_effects.SimplePatchShadow(), path_effects.Normal()])

        st.pyplot(fig)
        st.caption("Segments based on Data Usage (MB)")

    with col4:
        st.subheader("🚨 Anomaly Report")
        st.info(f"Showing top records exceeding {high_duration_limit}s duration OR {high_data_limit}MB data.")

        if not fraud_df.empty:
            st.dataframe(
                fraud_df[['Date', 'Call_Type', 'Duration', 'Data_Usage', 'Hour']].
                sort_values(by='Data_Usage', ascending=False).head(100),
                height=300, use_container_width=True
            )
        else:
            st.success("No anomalies detected.")

else:
    st.error("Error loading data.")
