import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patheffects as path_effects

# --- تنظیمات صفحه ---
st.set_page_config(page_title="Telecom Audit Dashboard", layout="wide", page_icon="📡")

# --- استایل CSS سفارشی ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px #ccc; }
    </style>
""", unsafe_allow_html=True)


# --- تابع تولید داده دمو (شبیه‌سازی بیگ دیتا) ---
@st.cache_data
def load_demo_data():
    # تولید 10,000 رکورد نمونه
    dates = pd.date_range(end=pd.Timestamp.now(), periods=10000, freq='h')

    # شبیه‌سازی مقادیر مشابه فایل اصلی
    data = {
        'Date': dates,
        'Duration': np.random.randint(10, 3600, 10000),
        # ضرب در 1000 برای اینکه جمع کل شبیه فایل 1 میلیونی شود (برای تست محور نمودار)
        'Data_Usage': np.random.uniform(5, 500, 10000) * 100,
        'Call_Type': np.random.choice(['Internal', 'International', 'Roaming', 'Emergency'], 10000,
                                      p=[0.6, 0.3, 0.05, 0.05])
    }
    df = pd.DataFrame(data)

    # ایجاد نویز و تقلب
    df.loc[0:50, 'Duration'] = 4000
    df.loc[0:50, 'Data_Usage'] = 60000  # مقدار بالا برای تقلب
    return df


# --- تیتر ---
st.title("📡 Telecom Network Log Analyzer")
st.markdown("Upload your CSV log file to detect fraud and analyze traffic patterns.")

# --- نوار کناری ---
st.sidebar.header("📂 Data Configuration")
uploaded_file = st.sidebar.file_uploader("Upload CSV Log File", type=["csv"])

# --- بارگذاری داده ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'])
        st.sidebar.success("✅ File Uploaded Successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        st.stop()
else:
    st.sidebar.info("ℹ️ Using DEMO DATA (Simulated Big Data Scale).")
    df = load_demo_data()

# --- محاسبات سگمنت‌بندی (Gold/Silver/Bronze) ---
conditions = [
    (df['Data_Usage'] > 450),  # طبق لاجیک main.py
    (df['Data_Usage'] >= 200) & (df['Data_Usage'] <= 450),
    (df['Data_Usage'] < 200)
]
labels = ['Gold', 'Silver', 'Bronze']
df['Segment'] = np.select(conditions, labels, default='Unknown')

# --- داشبورد مدیریتی (KPIs) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_calls = len(df)
total_usage = df['Data_Usage'].sum()
avg_duration = df['Duration'].mean()
fraud_count = len(df[(df['Duration'] > 3300)])

col1.metric("Total Calls", f"{total_calls:,}")
col2.metric("Total Data", f"{total_usage / 1e6:.2f} TB")  # نمایش به ترابایت برای اعداد بزرگ
col3.metric("Avg Duration", f"{avg_duration:.0f} sec")
col4.metric("Fraud Alerts", f"{fraud_count}", delta_color="inverse")

# --- تب‌های تحلیل ---
tab1, tab2, tab3 = st.tabs(["📊 Traffic Analysis", "🚨 Fraud Detection", "📂 Raw Data"])

with tab1:
    # ردیف اول: دو نمودار (میله‌ای و خطی)
    col_chart1, col_chart2 = st.columns(2)

    # --- نمودار ۱: مصرف دیتا (با محور 5M دقیق) ---
    with col_chart1:
        st.subheader("Total Internet Usage by Call Type")
        usage_summary = df.groupby('Call_Type')['Data_Usage'].sum()

        fig1, ax1 = plt.subplots(figsize=(8, 6))
        usage_summary.plot(kind='bar', color=['skyblue', 'orange', 'green', 'red'], ax=ax1)

        # *** اعمال تنظیمات دقیق main.py ***
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x * 1e-6:.0f}M'))
        ax1.yaxis.set_major_locator(mticker.MultipleLocator(5000000))  # فاصله دقیق 5 میلیونی

        ax1.set_ylabel('Usage (MB)')
        ax1.grid(axis='y', linestyle='-', alpha=0.4)
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # --- نمودار ۲: پیک ترافیک (با زوم دینامیک) ---
    with col_chart2:
        st.subheader("Network Traffic (24h Peak Analysis)")
        if 'Date' in df.columns:
            df['Hour'] = df['Date'].dt.hour
            hourly_counts = df.groupby('Hour').size()

            fig2, ax2 = plt.subplots(figsize=(8, 6))
            hourly_counts.plot(kind='line', marker='o', color='purple', linewidth=2, ax=ax2)

            # تنظیم کف نمودار (Dynamic Bottom) طبق main.py
            max_calls = hourly_counts.max()
            min_calls = hourly_counts.min()
            data_range = max_calls - min_calls
            if data_range > 0:
                dynamic_bottom = max(0, min_calls - (data_range * 0.2))
                ax2.set_ylim(bottom=dynamic_bottom)

            ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
            ax2.grid(True, linestyle='--', alpha=0.7)
            ax2.set_xlabel("Hour of Day")
            st.pyplot(fig2)

    # --- ردیف دوم: نمودار دایره‌ای (سگمنت‌ها) ---
    st.markdown("---")
    col_chart3, col_spacer = st.columns([1, 1])  # ستون دوم خالی باشد تا نمودار خیلی بزرگ نشود

    with col_chart3:
        st.subheader("Customer Segmentation (Data Usage)")
        segment_counts = df['Segment'].value_counts()

        color_map = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
        safe_colors = [color_map.get(l, 'grey') for l in segment_counts.index]
        explode = [0.05 if l == 'Gold' else 0 for l in segment_counts.index]

        fig3, ax3 = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax3.pie(
            segment_counts, labels=segment_counts.index, autopct='%1.1f%%',
            startangle=140, colors=safe_colors, explode=explode, shadow=False
        )

        # افکت سایه (Shadow Effect) طبق کد main.py
        for w in wedges:
            w.set_path_effects([
                path_effects.SimplePatchShadow(offset=(3, -3), alpha=0.4, shadow_rgbFace='black'),
                path_effects.Normal()
            ])

        st.pyplot(fig3)

with tab2:
    st.subheader("Suspicious Activity Report")
    st.markdown("Thresholds: **Duration > 55 mins**")

    fraud_df = df[(df['Duration'] > 3300)]

    if not fraud_df.empty:
        st.error(f"⚠️ Found {len(fraud_df)} suspicious records.")
        st.dataframe(fraud_df.head(200).style.highlight_max(axis=0, color='pink'))
    else:
        st.success("✅ Clean Network Status.")

with tab3:
    st.dataframe(df.head(100))