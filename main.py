import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import time
import numpy as np

RED = '\033[91m'
GREEN = '\033[3;4;32m'
END = '\033[0m'
ITALIC = '\033[3m'
InputFile = "telecom_data_large.csv"


def load_data(filename):
    try:
        print(f"\n{GREEN}Loading data from {filename}...{END}")
        df = pd.read_csv(filename)
        print(f"{filename} loaded successfully with {len(df)} rows")
        return df
    except FileNotFoundError:
        print(f"{RED}File {filename} not found.{END}")
        return None


def clean_data(df):
    print(f"\n{GREEN}Cleaning data...{END}")
    initial_count = len(df)
    df_clean = df.dropna()
    print(f"Removed {initial_count - len(df_clean)} rows with empty data.")
    df_negative_zero = df_clean[df_clean['Duration'] <= 0]
    df_clean = df_clean[df_clean['Duration'] > 0]
    print(f"Removed {len(df_negative_zero)} records with negative or zero duration seconds.")
    print(f"\n{ITALIC}Final data ready for analysis: {len(df_clean)} records{END}")
    return df_clean


def analyze_data(df):
    print(f"\n{RED}--- FINAL REPORT ---\n{END}")
    intl_calls = df[df['Call_Type'] == 'International']
    avg_usage = intl_calls['Data_Usage'].mean()
    print(f"{GREEN}Average internet usage for international calls:{END} {avg_usage:.2f} MB")

    print("\nDrawing diagram...")
    usage_summary = df.groupby('Call_Type')['Data_Usage'].sum()
    print(f"usage summary: \n{usage_summary}")

    fig, ax = plt.subplots(figsize=(10, 6))
    usage_summary.plot(kind='bar', color=['skyblue', 'orange', 'green', 'red'], ax=ax)
    plt.xticks(rotation=45, ha='right')

    ax.set_title('Total Internet Usage by Call Type (Big Data Scale)')
    ax.set_xlabel('Call Type')
    ax.set_ylabel('Usage (MB)')

    # --- اصلاح مهم: حذف Locator ثابت و استفاده از Formatter هوشمند ---
    # این تابع اعداد محور عمودی را کوتاه می‌کند (مثلاً 1000000 را تبدیل به 1M می‌کند)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,pos: f'{x*1e-6:.0f}M'))
    # خط زیر حذف شد چون باعث کرش سیستم در داده‌های میلیونی می‌شد:
    # ax.yaxis.set_major_locator(mticker.MultipleLocator(50000))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(5000000))

    ax.grid(axis='y', linestyle='-', alpha=0.4)
    plt.tight_layout()
    plt.savefig('report_type_usage.png', dpi=300)  # ذخیره با کیفیت بالا
    print(f"{GREEN}   -> Chart saved as 'report_type_usage.png'{END}")
    plt.show()


def detect_fraud(df):
    print(f"\n{RED}--- SECURITY CHECK: FRAUD DETECTION ---{END}")
    high_duration_limit = 3300  # ثانیه (۵۵ دقیقه)
    high_data_limit = 450

    suspicious_df = df[(df['Duration'] > high_duration_limit) | (df['Data_Usage'] > high_data_limit)]
    count = len(suspicious_df)

    if count > 0:
        print(f"{RED}⚠️ WARNING: Found {count} suspicious records!{END}")
        print(f"   - Criteria: Duration > {high_duration_limit}s OR Data > {high_data_limit}MB")

        output_file = "suspicious_report.csv"
        suspicious_df.to_csv(output_file, index=False)

        print(f"{GREEN}   -> Detailed report saved to '{output_file}'{END}")
        print(f"\n{ITALIC}Top 5 Suspicious Transactions:{END}")
        print(suspicious_df.head(5))
    else:
        print(f"{GREEN}✅ No suspicious activity detected.{END}")


def analyze_peak_hours(df):
    print(f"\n{GREEN}--- NETWORK TRAFFIC ANALYSIS: PEAK HOURS ---{END}")

    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour

    hourly_traffic = df.groupby('Hour').size()

    busy_hour = hourly_traffic.idxmax()
    max_calls = hourly_traffic.max()

    print(f"📈 Busiest Hour of the day: {RED}{busy_hour}:00 to {busy_hour + 1}:00{END}")
    print(f"   Total calls in this hour: {max_calls}")

    print("Drawing traffic chart...")
    plt.figure(figsize=(10, 6))
    hourly_traffic.plot(kind='line', marker='o', color='purple', linewidth=2)

    plt.title('Network Traffic by Hour (24h) - 1 Million Records')
    plt.xlabel('Hour of Day (0-23)')
    plt.ylabel('Number of Calls')
    plt.ylim(bottom=40000)

    # فرمت‌دهی محور Y برای تعداد تماس‌های زیاد (مثلاً 40K)
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(range(0, 24))

    plt.fill_between(hourly_traffic.index, hourly_traffic.values, color='purple', alpha=0.1)

    plt.tight_layout()
    plt.savefig('report_peak_hours.png', dpi=300)  # ذخیره با کیفیت بالا
    print(f"{GREEN}   -> Chart saved as 'report_peak_hours.png'{END}")
    plt.show()


def segment_customers(df):
    print(f"\n{GREEN}--- MARKETING ANALYSIS: CUSTOMER SEGMENTATION ---{END}")

    conditions = [
        (df['Data_Usage'] > 450),
        (df['Data_Usage'] >= 200) & (df['Data_Usage'] <= 450),
        (df['Data_Usage'] < 200)
    ]
    labels = ['Gold', 'Silver', 'Bronze']

    df['Segment'] = np.select(conditions, labels, default='Unknown')
    segment_counts = df['Segment'].value_counts()

    print("Customer Segments Breakdown:")
    print(segment_counts)

    color_map = {
        'Gold': '#FFD700',  # کد دقیق رنگ Gold استاندارد
        'Silver': '#C0C0C0',  # کد دقیق رنگ Silver استاندارد
        'Bronze': '#CD7F32'  # کد رنگ برنزی (که اسم ندارد)
    }

    safe_colors = [color_map[label] for label in segment_counts.index]

    print("Drawing segmentation chart...")
    plt.figure(figsize=(8, 8))
    explode = [0.1 if label == 'Gold' else 0 for label in segment_counts.index]

    segment_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140,
                        colors=safe_colors, explode=explode, shadow=True)

    plt.title('Customer Segmentation (Data Usage)')
    plt.ylabel('')
    plt.savefig('customer_segment.png', dpi=300)  # ذخیره با کیفیت بالا
    print(f"{GREEN}   -> Chart saved as 'customer_segment.png'{END}")
    plt.show()


if __name__ == "__main__":
    print(f'\n{RED}--- START PROGRAM ---{END}\n')
    print(f"Processing File: {InputFile}...")
    start_time = time.time()

    try:
        raw_data = load_data(InputFile)
        clean_dataframe = clean_data(raw_data)
        analyze_data(clean_dataframe)
        detect_fraud(clean_dataframe)
        analyze_peak_hours(clean_dataframe)
        segment_customers(clean_dataframe)

        print(f"\n✅{ITALIC} All analysis completed successfully.{END}")

    except Exception as e:
        print(f"\n❌{RED} Critical Error: {e}{END}")
