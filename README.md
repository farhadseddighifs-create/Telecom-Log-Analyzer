# Telecom Log Analyzer

## Overview
This project is an advanced data analysis tool for telecommunication log files. It processes a large dataset (1 million records) of call logs to clean data, detect anomalies, and derive actionable business insights. The analysis is performed using Python with Pandas, NumPy, and Matplotlib libraries.

## Key Features
1.  **Data Cleaning & Preparation:** Handles large datasets, removes corrupted entries (e.g., negative call durations, null values), and prepares the data for analysis.
2.  **Fraud Detection:** Implements a security module to identify suspicious activities based on unusually long call durations or high data usage, and generates a report of potential fraud cases.
3.  **Customer & Network Analysis:**
    *   **Customer Segmentation:** Categorizes customers into Gold, Silver, and Bronze tiers based on their data usage.
    *   **Peak Hour Analysis:** Identifies the busiest and quietest hours of network traffic to help with resource management.
    *   **Usage Insights:** Visualizes total data consumption by call type (Internal, International, etc.).

## How to Run
1.  Ensure you have Python and the required libraries installed.
```bash
pip install -r requirements.txt