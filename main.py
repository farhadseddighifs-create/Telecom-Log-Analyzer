import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import time

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

    fig, ax = plt.subplots(figsize=(8, 5))
    usage_summary.plot(kind='bar', color=['skyblue', 'orange', 'green', 'red'], ax=ax)
    plt.xticks(rotation=45, ha='right')

    ax.set_title('Total Internet Usage by Call Type')
    ax.set_xlabel('Call Type')
    ax.set_ylabel('Usage (MB)')
    ax.yaxis.set_major_locator(mticker.MultipleLocator(50000))

    ax.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
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
    df['Date']= pd.to_datetime(df['Date'])
    df['Hour']= df['Date'].dt.hour
    # شمارش تعداد تماس‌ها در هر ساعت
    hourly_traffic = df.groupby('Hour').size()

    # پیدا کردن شلوغ‌ترین ساعت (Busy Hour)
    busy_hour = hourly_traffic.idxmax()
    max_calls = hourly_traffic.max()

    print(f"📈 Busiest Hour of the day: {RED}{busy_hour}:00 to {busy_hour + 1}:00{END}")
    print(f"   Total calls in this hour: {max_calls}")

    # رسم نمودار ترافیک
    print("Drawing traffic chart...")
    plt.figure(figsize=(10, 6))
    hourly_traffic.plot(kind='line', marker='o', color='purple', linewidth=2)

    plt.title('Network Traffic by Hour (24h)')
    plt.xlabel('Hour of Day (0-23)')
    plt.ylabel('Number of Calls')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(range(0, 24))  # نمایش تمام ساعات زیر نمودار

    # پر رنگ کردن ناحیه زیر نمودار
    plt.fill_between(hourly_traffic.index, hourly_traffic.values, color='purple', alpha=0.1)

    plt.tight_layout()
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

        end_time = time.time()
        print(f"\n⏱️{GREEN} Total Execution Time: {end_time - start_time:.4f} seconds.{END}")

    except Exception as e:
        print(f"\n❌{RED} Critical Error: {e}{END}")
