import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patheffects as path_effects
import seaborn as sns

# --- تنظیمات صفحه ---
st.set_page_config(page_title="Telecom Audit Dashboard", layout="wide", page_icon="📡")

# --- استایل CSS سفارشی ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px #ccc; }
    </style>
""", unsafe_allow_html=True)


# --- تابع تولید داده دمو (اگر فایلی آپلود نشد) ---
@st.cache_data
def load_demo_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=1000, freq='H')
    data = {
        'Date': dates,
        'Duration': np.random.randint(10, 3600, 1000),
        'Data_Usage': np.random.uniform(0, 500, 1000),
        'Call_Type': np.random.choice(['Internal', 'International', 'Roaming'], 1000, p=[0.6, 0.3, 0.1])
    }
    df = pd.DataFrame(data)
    # ایجاد چند رکورد مشکوک و سنگین برای شبیه‌سازی دقیق‌تر
    df.loc[0:20, 'Duration'] = 4000
    df.loc[0:50, 'Data_Usage'] = 600
    # افزایش مقیاس داده‌ها برای اینکه نمودارها میلیونی شوند (شبیه فایل اصلی شما)
    df['Data_Usage'] = df['Data_Usage'] * 10000
    return df


# --- تیتر اصلی ---
st.title("📡 Telecom Network Log Analyzer")
st.markdown("Upload your CSV log file to detect fraud and analyze traffic patterns.")

# --- نوار کناری (Sidebar) برای آپلود ---
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
    st.sidebar.info("ℹ️ Using DEMO DATA. Upload a file to analyze your own data.")
    df = load_demo_data()

# --- داشبورد مدیریتی (KPIs) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_calls = len(df)
total_usage = df['Data_Usage'].sum()
avg_duration = df['Duration'].mean()
# آستانه تقلب
fraud_limit_duration = 3300
fraud_limit_data = 450  # اگر داده‌های شما میلیونی است، این عدد باید متناسب باشد، اما فعلاً طبق کد اصلی

fraud_count = len(df[(df['Duration'] > fraud_limit_duration)])

col1.metric("Total Calls", f"{total_calls:,}")
# نمایش گیگابایت یا ترابایت بسته به حجم
if total_usage > 1e9:
    col2.metric("Total Data", f"{total_usage / 1e9:.2f} PB")  # مقیاس بزرگ
elif total_usage > 1e6:
    col2.metric("Total Data", f"{total_usage / 1e6:.2f} TB")
else:
    col2.metric("Total Data", f"{total_usage / 1024:.2f} GB")

col3.metric("Avg Duration (Sec)", f"{avg_duration:.0f} s")
col4.metric("Potential Fraud Risk", f"{fraud_count}", delta_color="inverse")

# --- تب‌های تحلیل ---
tab1, tab2, tab3 = st.tabs(["📊 Traffic Analysis", "🚨 Fraud Detection", "📂 Raw Data"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)

    # --- نمودار ۱: مصرف دیتا بر اساس نوع تماس (اصلاح شده دقیق) ---
    with col_chart1:
        st.subheader("Total Internet Usage by Call Type")

        usage_summary = df.groupby('Call_Type')['Data_Usage'].sum()

        fig1, ax1 = plt.subplots(figsize=(8, 6))
        usage_summary.plot(kind='bar', color=['skyblue', 'orange', 'green'], ax=ax1)

        # *** اصلاح دقیق محور Y (درخواست کاربر: فاصله 5M) ***
        # فرمت‌دهی به صورت 5M, 10M, ...
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x * 1e-6:.0f}M'))

        # تنظیم دقیق فاصله‌ها روی 5 میلیون (5,000,000)
        ax1.yaxis.set_major_locator(mticker.MultipleLocator(5000000))

        ax1.set_xlabel('Call Type')
        ax1.set_ylabel('Usage (MB)')
        ax1.grid(axis='y', linestyle='-', alpha=0.4)
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # --- نمودار ۲: ساعت‌های شلوغی (اصلاح شده دقیق) ---
    with col_chart2:
        st.subheader("Network Traffic Analysis (24 Hours)")
        if 'Date' in df.columns:
            df['Hour'] = df['Date'].dt.hour
            hourly_counts = df.groupby('Hour').size()

            fig2, ax2 = plt.subplots(figsize=(8, 6))
            hourly_counts.plot(kind='line', marker='o', color='purple', linewidth=2, ax=ax2)

            # *** اصلاح دقیق زوم نمودار (Dynamic Y-Limit) ***
            max_calls = hourly_counts.max()
            min_calls = hourly_counts.min()
            data_range = max_calls - min_calls

            # تنظیم کف نمودار برای دیده شدن نوسانات (دقیقاً مثل main.py)
            if data_range > 0:
                dynamic_bottom = max(0, min_calls - (data_range * 0.2))
                ax2.set_ylim(bottom=dynamic_bottom)

            ax2.grid(True, linestyle='--', alpha=0.7)
            ax2.set_xlabel("Hour of Day")
            ax2.set_ylabel("Number of Calls")
            st.pyplot(fig2)
        else:
            st.warning("Date column not found for Hourly Analysis.")

with tab2:
    st.subheader("Security Audit: Suspicious Activities")
    st.markdown("Thresholds: **Duration > 55 mins**")

    fraud_df = df[(df['Duration'] > 3300)]

    if not fraud_df.empty:
        st.error(f"⚠️ Detected {len(fraud_df)} suspicious records!")
        st.dataframe(fraud_df.head(100).style.highlight_max(axis=0, color='pink'))

        csv = fraud_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Fraud Report",
            csv,
            "fraud_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.success("✅ No suspicious activity detected in this dataset.")

with tab3:
    st.subheader("Data Inspector")
    st.dataframe(df.head(100))