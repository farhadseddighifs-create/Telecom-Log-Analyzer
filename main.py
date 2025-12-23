import pandas as pd

# 1. شبیه‌سازی داده‌های لاگ مخابرات (Data Simulation)
# این بخش جایگزین فایل‌های اکسل یا دیتابیس قدیمی می‌شود
data = {
    'Call_ID': [1001, 1002, 1003, 1004, 1005],
    'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-02'],
    'Duration_Seconds': [120, 450, 300, 60, 500],  # مدت زمان مکالمه
    'Status': ['Successful', 'Dropped', 'Successful', 'Successful', 'Dropped'],
    'Region': ['Tehran', 'Isfahan', 'Tehran', 'Shiraz', 'Tehran']
}

# 2. تبدیل به DataFrame (جدول هوشمند پایتون)
df = pd.DataFrame(data)

print("--- داده‌های خام (Raw Data) ---")
print(df)
print("\n" + "="*40 + "\n")

# 3. تحلیل داده‌ها: محاسبه میانگین زمان مکالمه برای هر شهر
# معادل دستورات SQL Group By یا Pivot Table در اکسل
report = df.groupby('Region')['Duration_Seconds'].mean().reset_index()

print("--- گزارش میانگین مکالمه بر حسب منطقه ---")
print(report)

# 4. ذخیره گزارش در یک فایل CSV (اتوماسیون)
report.to_csv('report_output.csv', index=False)
print("\n>>> فایل گزارش با نام 'report_output.csv' ذخیره شد.")