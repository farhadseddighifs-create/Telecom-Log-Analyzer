import pandas as pd
import numpy as np
from datetime import datetime, timedelta

RED = '\033[91m'
GREEN = '\033[3;2;32m'
ITALIC = '\033[3m'
END = '\033[0m'


def generate_large_dataset(filename, num_records=1000000):
    print(f"\n--- {RED}Starting data generation for {num_records} records ---{END}")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()

    print("Generating Dates...")
    random_timestamps = np.random.uniform(start_ts, end_ts, num_records)
    dates = pd.to_datetime(random_timestamps, unit='s')

    # 3. تولید نوع تماس (با احتمالات وزن‌دار)
    print("Generating Call Types...")
    types = ['Internal', 'International', 'Roaming', 'Emergency']
    call_types = np.random.choice(types, size=num_records, p=[0.60, 0.30, 0.05, 0.05])

    print("Generating Durations...")
    durations = np.random.randint(10, 3600, size=num_records)

    print("Generating Data Usage...")
    usage_raw = np.random.uniform(5, 500, num_records)
    zero_mask = np.random.random(num_records) < 0.3

    data_usage = np.where(zero_mask, 0.0, usage_raw)
    data_usage = np.round(data_usage, 2)

    print("Creating DataFrame...")
    df = pd.DataFrame({
        'Date': dates,
        'Duration': durations,
        'Data_Usage': data_usage,
        'Call_Type': call_types,
    })

    print("Injecting Noise (Errors)...")
    random_indices = np.random.choice(df.index, 20, replace=False)
    df.loc[random_indices, 'Duration'] = -100

    random_indices_null = np.random.choice(df.index, 20, replace=False)
    df.loc[random_indices_null, 'Data_Usage'] = np.nan

    print(f"Saving to CSV ({filename})...")
    df.to_csv(filename, index=False)

    file_size_mb = len(df) * 50 / (1024 * 1024)  # تخمین تقریبی حجم
    print(f"\nSUCCESSFULLY CREATED {GREEN}'{filename}'{END} WITH {GREEN}{len(df)}{END} RECORDS.")
    print(f"{ITALIC}File size is approx {file_size_mb:.1f} MB{END}")
    print(f"\n{RED}--- Data generation complete ---{END}")


if __name__ == "__main__":
    generate_large_dataset('telecom_data_large.csv', num_records=1000000)
