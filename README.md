# 📡 Telecom Log Analyzer & Fraud Detection

A professional data analysis dashboard designed for Telecommunication Engineers to simulate, visualize, and audit network traffic logs. This project transforms raw CSV logs into actionable insights using Python.

## 🔗 Live Demo
🚀 **[Click here to view the Interactive Dashboard](https://telecom-log-analyzer-vwubvxeavlszgbh5mk6m6t.streamlit.app/)**

---

## 🎯 Project Overview
In the telecom industry, analyzing call detail records (CDRs) is crucial for network optimization and revenue assurance. This tool provides:
1.  **Data Simulation:** Generates synthetic telecom logs (Voice calls, Data usage, Roaming, etc.).
2.  **Traffic Analysis:** Identifies peak hours and busiest network times.
3.  **Fraud Detection:** Automatically flags suspicious activities based on specific thresholds (e.g., Long duration calls > 55 mins or High Data Usage).
4.  **Reporting:** detailed CSV exports for audit teams.

## 🛠 Tech Stack
*   **Core Logic:** Python 3.x
*   **Data Processing:** Pandas, NumPy
*   **Visualization:** Matplotlib
*   **Web Framework:** Streamlit
*   **Deployment:** Streamlit Cloud

## 📊 Key Features
*   **Executive Dashboard:** Real-time KPIs for Total Calls, Data Volume (GB), and Risk Alerts.
*   **Interactive Controls:** Users can regenerate datasets and adjust fraud detection thresholds dynamically.
*   **Visual Analytics:**
    *   *Usage by Call Type* (International, Roaming, Internal).
    *   *24-Hour Network Load* (identifying peak traffic hours).
*   **Security Audit:** A dedicated tab to filter and download lists of potential fraudulent users.

## 🚀 How to Run Locally

If you want to run this dashboard on your own machine:

1.  **Clone the repository:**
```bash
git clone https://github.com/farhadseddighifs-create/Telecom-Log-Analyzer.git
cd Telecom-Log-Analyzer