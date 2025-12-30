# 📡 Telecom Data Analysis Dashboard

A full-stack data analysis project that simulates, processes, and visualizes telecommunication traffic data to detect potential fraud and optimize network usage.

## 🔗 Live Demo
Check out the running application here: **[Link to your Hugging Face Space]**
*(Replace this text with your actual Hugging Face URL)*

## 🎯 Project Overview
This project demonstrates an end-to-end data pipeline:
1.  **Data Generation:** Simulating 10000 telecom records (Voice/Data/SMS).
2.  **Data Cleaning & Processing:** Handling datetimes, segmentation based on usage.
3.  **Fraud Detection:** Identifying suspicious activities based on duration (>3300s) and data usage (>450MB) anomalies.
4.  **Visualization:** Interactive web dashboard deployed on the cloud.

## 🛠 Tech Stack
*   **Language:** Python 3.11
*   **Data Manipulation:** Pandas, NumPy
*   **Visualization:** Matplotlib, Seaborn
*   **Web Framework:** Streamlit
*   **Deployment:** Docker, Hugging Face Spaces (Cloud)

## 📊 Key Features
*   **Real-time Metrics:** KPIs for total traffic, average duration, and fraud count.
*   **Interactive Charts:** Hourly traffic analysis and call type distribution.
*   **Fraud Alert System:** A dedicated table highlighting suspicious users exceeding the 95th percentile of usage.
*   **Data Export:** Capability to download the fraud report as CSV.

## 🚀 How to Run Locally

1. **Clone the repository:**
```bash
   git clone https://github.com/farhadseddighifs-create/Telecom-Log-Analyzer