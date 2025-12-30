import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np

# Page Configuration
st.set_page_config(page_title="Telecom Analytics", page_icon="📊", layout="wide")

# Custom CSS for styling
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

# Title
st.title("📊 Telecom Data Analysis Dashboard")
st.markdown("Interactive dashboard based on `main.py` logic (Fraud Detection & Segmentation).")


# --- 1. Load & Clean Data (Logic from main.py) ---
@st.cache_data
def load_data():
    try:
        # اولویت با فایل اصلی (برای کامپیوتر خودتان)
        data = pd.read_csv('telecom_data_large.csv')
    except FileNotFoundError:
        try:
            # اگر فایل اصلی نبود (در سرور آنلاین)، فایل نمونه خوانده شود
            data = pd.read_csv('telecom_data_sample.csv')
        except FileNotFoundError:
            return None, 0

    # ادامه کد قبلی...
    data['Date'] = pd.to_datetime(data['Date'])
    data['Hour'] = data['Date'].dt.hour

    initial_count = len(data)
    data = data[data['Duration'] > 0]
    cleaned_count = len(data)

    return data, initial_count - cleaned_count


# Execute Load
with st.spinner('Loading and Processing Data...'):
    df, removed_rows = load_data()

if df is not None:
    # --- 2. KPI Section ---
    st.subheader("📌 Key Performance Indicators")

    # Calculate Fraud (Logic from main.py: detect_fraud)
    high_duration_limit = 3300
    high_data_limit = 450
    fraud_df = df[(df['Duration'] > high_duration_limit) | (df['Data_Usage'] > high_data_limit)]
    fraud_count = len(fraud_df)

    # Layout Columns
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_records = len(df)
    total_data_tb = df['Data_Usage'].sum() / 1024 / 1024  # Convert MB to TB

    kpi1.metric("Total Active Records", f"{total_records:,}", delta=f"-{removed_rows} cleaned")
    kpi2.metric("Total Data Traffic", f"{total_data_tb:.2f} TB")
    kpi3.metric("Avg Duration", f"{df['Duration'].mean():.0f} sec")
    kpi4.metric("⚠️ Fraud/Suspicious", f"{fraud_count}", delta_color="inverse")

    st.divider()

    # --- 3. Charts Row 1: Traffic & Call Types ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Hourly Network Traffic")
        # Logic from main.py: analyze_peak_hours
        hourly_traffic = df.groupby('Hour').size()
        st.line_chart(hourly_traffic)
        st.caption("Peak traffic hours based on call frequency.")

    with col2:
        st.subheader("📊 Call Type Distribution")
        # Logic from main.py: analyze_data
        type_counts = df['Call_Type'].value_counts()
        st.bar_chart(type_counts)
        st.caption("Volume comparison: Data vs Voice vs SMS vs International.")

    st.divider()

    # --- 4. Advanced Analysis: Segmentation & Fraud ---
    col3, col4 = st.columns([1, 2])

    with col3:
        st.subheader("🍰 Customer Segmentation")

        # LOGIC from main.py: segment_customers
        conditions = [
            (df['Data_Usage'] > 450),
            (df['Data_Usage'] >= 200) & (df['Data_Usage'] <= 450),
            (df['Data_Usage'] < 200)
        ]
        labels = ['Gold', 'Silver', 'Bronze']
        df['Segment'] = np.select(conditions, labels, default='Unknown')
        segment_counts = df['Segment'].value_counts()

        # Replicating matplotlib chart from main.py to keep style consistency
        fig, ax = plt.subplots(figsize=(6, 6))

        color_map = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
        colors = [color_map.get(label, 'grey') for label in segment_counts.index]
        explode = [0.05 if label == 'Gold' else 0 for label in segment_counts.index]

        wedges, texts, autotexts = ax.pie(
            segment_counts, labels=segment_counts.index, autopct='%1.1f%%',
            startangle=140, colors=colors, explode=explode, shadow=False
        )

        # Apply shadow effect
        for w in wedges:
            w.set_path_effects([
                path_effects.SimplePatchShadow(offset=(2, -2), alpha=0.4, shadow_rgbFace='black'),
                path_effects.Normal()
            ])

        st.pyplot(fig)
        st.caption("Gold: >450MB | Silver: 200-450MB | Bronze: <200MB")

    with col4:
        st.subheader("🚨 Fraud Detection Report")
        st.warning(
            f"Displaying top suspicious records (Duration > {high_duration_limit}s OR Data > {high_data_limit}MB)")

        if not fraud_df.empty:
            # Show interactive table for fraud
            st.dataframe(
                fraud_df[['Date', 'Call_Type', 'Duration', 'Data_Usage']].sort_values(by='Data_Usage',
                                                                                      ascending=False).head(100),
                use_container_width=True,
                height=300
            )

            # Download Button for Fraud Report
            csv = fraud_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Suspicious Report (CSV)",
                data=csv,
                file_name='suspicious_report_dashboard.csv',
                mime='text/csv',
            )
        else:
            st.success("No suspicious activity detected.")

else:
    st.error("Error: 'telecom_data_large.csv' not found. Please run data_generator.py first.")