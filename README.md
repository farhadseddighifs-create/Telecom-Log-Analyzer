# 📡 Telecom Log Analyzer (SaaS Web App)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b)
![Status](https://img.shields.io/badge/Status-Live-success)

A professional data analysis dashboard designed to process telecommunication logs, detect fraud, and visualize network traffic patterns. Now deployed as a **SaaS Web Application** allowing users to upload and analyze their own datasets.

## 🔗 Live Demo
👉 **[Click here to view the Live App](LNK_APP_KHOD_RA_INJA_BEZARID)**

---

## 🚀 Key Features

### 1. 📂 Interactive Data Loading (SaaS Ready)
*   **File Uploader:** Users can upload their own `.csv` files directly via the sidebar.
*   **Smart Validation:** The app automatically cleans data, removing empty rows and invalid durations (negative values).
*   **Demo Mode:** If no file is uploaded, the app generates 200,000 realistic records for demonstration.

### 2. 📊 Dynamic Visualizations
*   **Traffic Analysis:** Line charts showing peak hours with dynamic scaling.
*   **Usage Distribution:** Bar charts showing data usage by Call Type (Internal, International, Roaming).
*   **Segmentation:** Pie charts categorizing users into Gold, Silver, and Bronze segments based on usage.

### 3. 🛡️ Fraud Detection System
*   **Automatic Flagging:** Identifies suspicious records based on logic:
    *   Duration > 55 mins (3300s)
    *   Data Usage > 450 MB
*   **Security Report:** Displays a filtered dataframe of potential fraud cases.

---

## 🛠 Tech Stack
*   **Core:** Python 3.11
*   **Data Processing:** Pandas, NumPy
*   **Visualization:** Matplotlib (Custom Tickers, Path Effects)
*   **Web Framework:** Streamlit
*   **Deployment:** Streamlit Cloud

---

## 💻 How to Run Locally

1. **Clone the repository:**
```bash
   git clone https://github.com/farhadseddighifs-create/Telecom-Log-Analyzer.git
   cd Telecom-Log-Analyzer