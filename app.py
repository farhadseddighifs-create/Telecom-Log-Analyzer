import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patheffects as path_effects
from datetime import datetime, timedelta

# --- تنظیمات صفحه ---
st.set_page_config(page_title="Telecom Audit Dashboard", layout="wide", page_icon="📡")

# --- استایل CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px #ccc; }
    </style>
""", unsafe_allow_html=True)


# --- تابع تولید داده (اصلاح شده: شبیه سازی دقیق بیگ دیتا) ---
@st.cache_data
def load_demo_data():
    # تعداد رکوردها: 200 هزار (کافی برای نمایش گرافیک دقیق و سبک برای سرور)
    num_records = 200000

    # 1. تولید زمان‌های تصادفی در 30 روز گذشته (برای شکل‌گیری صحیح نمودار ساعت)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()

    random_timestamps = np.random.uniform(start_ts, end_ts, num_records)
    dates = pd.to_datetime(random_timestamps, unit='s')

    # 2. تولید مقادیر
    # ضریب 5: چون تعداد 200هزارتاست (یک پنجم 1 میلیون)، دیتا را 5 برابر می‌کنیم تا اعداد محورها مثل فایل اصلی باشد
    data_usage = np.random.uniform(5, 500, num_records) * 5

    # 3. توزیع وزن‌دار انواع تماس (مثل فایل اصلی)
    types = ['Internal', 'International', 'Roaming', 'Emergency']
    call_types = np.random.choice(types, num_records, p=[0.6, 0.3, 0.05, 0.05])

    df = pd.DataFrame({
        'Date': dates,
        'Duration': np.random.randint(10, 3600, num_records),
        'Data_Usage': data_usage,
        'Call_Type': call_types
    })

    # اضافه کردن نویز برای تشخیص تقلب
    # رکوردهای با مدت زمان و مصرف بسیار بالا
    fraud_indices = np.random.choice(df.index, 50, replace=False)
    df.loc[fraud_indices, 'Duration'] = 4000
    df.loc[fraud_indices, 'Data_Usage'] = df.loc[fraud_indices, 'Data_Usage'] * 10

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
    st.sidebar.info("ℹ️ Using DEMO DATA (Simulated Big Data Scale - 30 Days).")
    df = load_demo_data()

# --- محاسبات سگمنت‌بندی ---
# آستانه‌ها را با توجه به اسکیل دیتا تنظیم می‌کنیم
conditions = [
    (df['Data_Usage'] > 2000),  # مقادیر به دلیل ضریب 5 تغییر کرده‌اند تا نمودار دایره‌ای درست دربیاید
    (df['Data_Usage'] >= 1000) & (df['Data_Usage'] <= 2000),
    (df['Data_Usage'] < 1000)
]
labels = ['Gold', 'Silver', 'Bronze']
df['Segment'] = np.select(conditions, labels, default='Unknown')

# --- داشبورد مدیریتی (KPIs) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_calls = len(df)
total_usage_mb = df['Data_Usage'].sum()
avg_duration = df['Duration'].mean()
fraud_count = len(df[(df['Duration'] > 3300)])

col1.metric("Total Calls", f"{total_calls:,}")
col2.metric("Total Data", f"{total_usage_mb / 1e6:.1f} TB")
col3.metric("Avg Duration", f"{avg_duration:.0f} sec")
col4.metric("Fraud Alerts", f"{fraud_count}", delta_color="inverse")

# --- تب‌های تحلیل ---
tab1, tab2, tab3 = st.tabs(["📊 Traffic Analysis", "🚨 Fraud Detection", "📂 Raw Data"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)

    # --- نمودار ۱: مصرف دیتا (میله‌ای) ---
    with col_chart1:
        st.subheader("Total Internet Usage by Call Type")
        usage_summary = df.groupby('Call_Type')['Data_Usage'].sum()

        fig1, ax1 = plt.subplots(figsize=(8, 6))
        usage_summary.plot(kind='bar', color=['skyblue', 'orange', 'green', 'red'], ax=ax1)

        # فرمت محور Y: نمایش به صورت میلیون (M)
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x * 1e-6:.0f}M'))

        # تنظیم خطوط افقی: تلاش برای تقسیم‌بندی تمیز
        # حدود ماکسیمم دیتا را می‌گیریم تا فاصله خطوط را داینامیک تنظیم کنیم
        y_max = usage_summary.max()
        if y_max > 0:
            # فاصله خطوط را طوری می‌گیریم که حدود 5 تا خط داشته باشیم
            locator_step = y_max / 5
            ax1.yaxis.set_major_locator(mticker.MultipleLocator(locator_step))

        ax1.set_ylabel('Usage (MB)')
        ax1.grid(axis='y', linestyle='-', alpha=0.4)
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # --- نمودار ۲: ترافیک شبکه (ساعت پیک) ---
    with col_chart2:
        st.subheader("Network Traffic (Peak Hours Analysis)")
        if 'Date' in df.columns:
            df['Hour'] = df['Date'].dt.hour
            # شمارش تعداد تماس در هر ساعت از شبانه‌روز (تجمیع ۳۰ روز)
            hourly_counts = df.groupby('Hour').size()

            fig2, ax2 = plt.subplots(figsize=(8, 6))
            hourly_counts.plot(kind='line', marker='o', color='purple', linewidth=2, ax=ax2)

            # تنظیم کف نمودار برای برجسته شدن نوسانات
            max_calls = hourly_counts.max()
            min_calls = hourly_counts.min()
            data_range = max_calls - min_calls
            if data_range > 0:
                dynamic_bottom = max(0, min_calls - (data_range * 0.2))
                ax2.set_ylim(bottom=dynamic_bottom)

            ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
            ax2.grid(True, linestyle='--', alpha=0.7)
            ax2.set_xlabel("Hour of Day (0-23)")
            ax2.set_xticks(range(0, 24, 2))  # نمایش ساعت‌ها به صورت زوج
            st.pyplot(fig2)

    # --- ردیف دوم: نمودار دایره‌ای ---
    st.markdown("---")
    col_chart3, col_spacer = st.columns([1, 1])

    with col_chart3:
        st.subheader("Customer Segmentation")
        segment_counts = df['Segment'].value_counts()

        color_map = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
        safe_colors = [color_map.get(l, 'grey') for l in segment_counts.index]
        explode = [0.05 if l == 'Gold' else 0 for l in segment_counts.index]

        fig3, ax3 = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax3.pie(
            segment_counts, labels=segment_counts.index, autopct='%1.1f%%',
            startangle=140, colors=safe_colors, explode=explode, shadow=False
        )

        for w in wedges:
            w.set_path_effects([
                path_effects.SimplePatchShadow(offset=(3, -3), alpha=0.4, shadow_rgbFace='black'),
                path_effects.Normal()
            ])

        st.pyplot(fig3)

with tab2:
    st.subheader("Suspicious Activity Report")
    fraud_df = df[(df['Duration'] > 3300)]

    if not fraud_df.empty:
        st.error(f"⚠️ Found {len(fraud_df)} suspicious records (Duration > 55 min).")
        st.dataframe(fraud_df.head(200).style.highlight_max(axis=0, color='pink'))
    else:
        st.success("✅ Clean Network Status.")

with tab3:
    st.dataframe(df.head(100))