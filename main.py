import pandas as pd
import random
from datetime import datetime, timedelta

RED = "\x1b[31m"
END = "\x1b[0m"

def generate_data():
    num_records = 100
    start_time = datetime.now()

    data = {
        'Date': [start_time - timedelta(days=x) for x in range(num_records)],
        'Duration_Seconds': [random.randint(10, 1200) for _ in range(num_records)],
        'Data_Usage_MB': [random.uniform(0, 500) for _ in range(num_records)],
        'Call_Type': [random.choice(['Internal', 'International', 'Roaming']) for _ in range(num_records)]
    }
    df = pd.DataFrame(data)
    df.to_csv('report_output.csv', index=False)
    print("✅ داده‌های جدید تولید و در فایل ذخیره شدند.")
    return df

def analyze_data(df):
    print(f"\n{'=' * 40}\n📊(Management Report)\n{'=' * 40}"
          f"\n1. The first five rows:\n{RED}{df.head()}{END}")
    print(f"\n2. Statistics:\n{RED}{df.describe()}{END}")
    print(f"\n3. Number of long calls (over 10 minutes):\n{RED}{len(df[df['Duration_Seconds']>600])}{END}")
    print(f"\n4. Average internet usage by call type:\n{RED}{df.groupby('Call_Type')['Data_Usage_MB'].mean()}{END}")


if __name__ == "__main__":
    print(f"---{RED} START PROGRAM {END}---")
    df = generate_data()
    analyze_data(df)

