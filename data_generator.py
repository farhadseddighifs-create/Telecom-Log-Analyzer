import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

RED = '\033[91m'
GREEN = '\033[3;2;32m'
ITALIC = '\033[3m'
END = '\033[0m'


def generate_large_dataset(filename, num_records=10000):
    print(f"\n--- {RED}Starting data generation for {num_records} records ---{END}")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    date_list = []
    for _ in range(num_records):
        random_days = random.randint(0, 30)
        random_seconds = random.randint(0, 86400)
        random_date = start_date + timedelta(days=random_days, seconds=random_seconds)
        date_list.append(random_date)

    types = ['Internal', 'International', 'Roaming', 'Emergency']
    call_types = random.choices(types, weights=[60, 30, 5, 5], k=num_records)
    durations = np.random.randint(10, 3600, size=num_records)

    data_usage = []
    for _ in range(num_records):
        if random.random() < 0.3:
            data_usage.append(0.0)
        else:
            data_usage.append(round(random.uniform(5, 500), 2))

    df = pd.DataFrame({
        'Date': date_list,
        'Duration': durations,
        'Data_Usage': data_usage,
        'Call_Type': call_types,
    })

    random_indices = np.random.choice(df.index, 5, replace=False)
    df.loc[random_indices, 'Duration'] = -100

    random_indices_null = np.random.choice(df.index, 5, replace=False)
    df.loc[random_indices_null, 'Data_Usage'] = np.nan

    df.to_csv(filename, index=False)
    print(f"\nSUCCESSFULLY CREATED {GREEN}'{filename}'{END} WITH {GREEN}{len(df)}{END} RECORDS.")
    print(f"\n{RED}--- Data generation complete ---{END}")


if __name__ == "__main__":
    generate_large_dataset('telecom_data_large.csv', num_records=1000000)
