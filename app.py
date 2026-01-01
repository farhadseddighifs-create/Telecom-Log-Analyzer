import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patheffects as path_effects
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Telecom Log Analyzer", layout="wide", page_icon="📡")

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. HELPER FUNCTIONS ---

@st.cache_data
def generate_random_data():
    """Generates demo data if no file is uploaded."""
    # Generate dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # 200,000 records
    num_records = 200000

    # Random timestamps
    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()
    random_timestamps = np.random.uniform(start_ts, end_ts, num_records)
    dates = pd.to_datetime(random_timestamps, unit='s')

    # Random attributes
    types = ['Internal', 'International', 'Roaming', 'Emergency']
    call_types = np.random.choice(types, size=num_records, p=[0.60, 0.30, 0.05, 0.05])
    durations = np.random.randint(10, 3600, size=num_records)
    usage_raw = np.random.uniform(5, 500, num_records)
    zero_mask = np.random.random(num_records) < 0.3
    data_usage = np.where(zero_mask, 0.0, usage_raw)

    return pd.DataFrame({
        'Date': dates,
        'Duration': durations,
        'Data_Usage': np.round(data_usage, 2),
        'Call_Type': call_types
    })


def load_data(uploaded_file):
    """Loads, validates, and cleans user uploaded CSV."""
    try:
        df = pd.read_csv(uploaded_file)

        # 1. Check Columns
        required_cols = {'Date', 'Duration', 'Data_Usage', 'Call_Type'}
        if not required_cols.issubset(df.columns):
            return None, f"Missing columns! File must contain: {', '.join(required_cols)}"

        # 2. Data Cleaning (Similar to main.py logic)
        # Drop empty rows
        df = df.dropna()

        # Filter negative/zero duration (Logic from main.py)
        df = df[df['Duration'] > 0]

        # 3. Type Conversion
        df['Date'] = pd.to_datetime(df['Date'])

        return df, None
    except Exception as e:
        return None, str(e)


# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🔧 Control Panel")

# A. File Uploader
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type=["csv"])

# B. Data Loading Logic
if uploaded_file is not None:
    df, error_msg = load_data(uploaded_file)
    if error_msg:
        st.error(f"Error loading file: {error_msg}")
        st.stop()
    else:
        st.sidebar.success(f"✅ Loaded {len(df):,} records!")
        data_source = "User Uploaded Data"
else:
    df = generate_random_data()
    data_source = "Demo Data (Randomly Generated)"

# C. Filtering
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filter Data")
all_types = df['Call_Type'].unique().tolist()
selected_types = st.sidebar.multiselect("Select Call Types:", all_types, default=all_types)

if not selected_types:
    st.warning("Please select at least one Call Type from the sidebar.")
    st.stop()

# Apply Filter
filtered_df = df[df['Call_Type'].isin(selected_types)]

# --- 4. MAIN DASHBOARD ---
st.title("📡 Telecom Data Analysis Dashboard")
st.markdown(f"**Data Source:** *{data_source}* | **Records Displayed:** `{len(filtered_df):,}`")
st.markdown("---")

# KPI Section
col1, col2, col3, col4 = st.columns(4)
total_usage = filtered_df['Data_Usage'].sum()
avg_duration = filtered_df['Duration'].mean()
fraud_count = len(filtered_df[(filtered_df['Duration'] > 3300) | (filtered_df['Data_Usage'] > 450)])

col1.metric("Total Data Usage", f"{total_usage / 1e6:.2f} TB")
col2.metric("Avg Call Duration", f"{avg_duration / 60:.1f} min")
col3.metric("Total Calls", f"{len(filtered_df):,}")
col4.metric("Potential Fraud", f"{fraud_count}", delta_color="inverse")

# --- 5. CHARTS ROW 1 ---
st.markdown("### 📊 Traffic & Usage Analysis")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Hourly Traffic (Peak Hours)")
    filtered_df['Hour'] = filtered_df['Date'].dt.hour
    hourly_counts = filtered_df.groupby('Hour').size()

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(hourly_counts.index, hourly_counts.values, marker='o', color='purple', linewidth=2)
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Number of Calls")
    ax1.grid(True, alpha=0.3)

    # Dynamic Y-Limit
    if len(hourly_counts) > 0:
        y_min = max(0, hourly_counts.min() - (hourly_counts.max() * 0.1))
        ax1.set_ylim(bottom=y_min)

    st.pyplot(fig1)

with row1_col2:
    st.subheader("Data Usage by Call Type")
    usage_by_type = filtered_df.groupby('Call_Type')['Data_Usage'].sum()

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    usage_by_type.plot(kind='bar', color=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f'], ax=ax2)
    ax2.set_ylabel("Usage (MB)")
    plt.xticks(rotation=0)

    # Formatter 5M
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x * 1e-6:.1f}M'))
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(5000000))

    st.pyplot(fig2)

# --- 6. SEGMENTATION & FRAUD ---
st.markdown("### 🎯 Segmentation & Security")
row2_col1, row2_col2 = st.columns([1, 2])

with row2_col1:
    st.subheader("Customer Segments")
    conditions = [
        (filtered_df['Data_Usage'] > 450),
        (filtered_df['Data_Usage'] >= 200) & (filtered_df['Data_Usage'] <= 450),
        (filtered_df['Data_Usage'] < 200)
    ]
    labels = ['Gold', 'Silver', 'Bronze']
    filtered_df['Segment'] = np.select(conditions, labels, default='Unknown')
    segment_counts = filtered_df['Segment'].value_counts()

    fig3, ax3 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax3.pie(segment_counts, labels=segment_counts.index, autopct='%1.1f%%',
                                       colors=['#FFD700', '#C0C0C0', '#CD7F32'], startangle=140)
    # Shadow effect
    for w in wedges:
        w.set_path_effects([path_effects.SimplePatchShadow(), path_effects.Normal()])

    st.pyplot(fig3)

with row2_col2:
    st.subheader("🚨 Suspicious Transactions (Fraud Alert)")
    fraud_df = filtered_df[(filtered_df['Duration'] > 3300) | (filtered_df['Data_Usage'] > 450)]

    if not fraud_df.empty:
        st.dataframe(fraud_df[['Date', 'Call_Type', 'Duration', 'Data_Usage', 'Segment']].head(100), height=300)
        st.warning(f"Displaying top 100 out of {len(fraud_df)} suspicious records.")
    else:
        st.success("No suspicious activity detected in the selected data.")
