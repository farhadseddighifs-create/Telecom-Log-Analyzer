import pandas as pd

RED = '\033[91m'
GREEN = '\033[3;4;32m'
END = '\033[0m'
ITALIC = '\033[3m'


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
    df_negative_zero = df_clean[df_clean['Duration_Seconds'] <= 0]
    df_clean = df_clean[df_clean['Duration_Seconds'] > 0]
    print(f"Removed {len(df_negative_zero)} records with negative or zero duration seconds.")
    print(f"\n{ITALIC}Final data ready for analysis: {len(df_clean)} records{END}")
    return df_clean


def analyze_data(df):
    print(f"\n{RED}--- FINAL REPORT ---\n{END}")
    intl_calls = df[df['Call_Type'] == 'International']
    avg_usage = intl_calls['Data_Usage_MB'].mean()
    print(f"{GREEN}Average internet usage for international calls:{END} {avg_usage} MB")


print(f'{RED}--- START PROGRAM ---{END}')
raw_data = load_data('telecom_data.csv')

if raw_data is not None:
    clean_dataframe = clean_data(raw_data)
    analyze_data(clean_dataframe)
