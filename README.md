# Task\_04\_Descriptive\_Stats

This project aims to build a data summarizing system to explore and summarize a real-world dataset.
The core task is to perform descriptive statistical analysis on social media data related to the 2024 US Presidential election using three different technical strategies—**Pure Python**, **Pandas**, and **Polars**—to produce identical numerical results. \[cite: 2, 4, 15, 16]

---

## 📊 Key Findings & Comparison

As required by the research task, this project not only generates statistical results but also compares the development process and performance of the three methods:

### Pure Python

* **Pros**:
  No third-party library dependencies, ensuring maximum portability and deployment flexibility. The implemented **single-pass** streaming approach is highly memory-efficient, theoretically capable of processing files much larger than RAM.

* **Cons**:
  The code is the most verbose and complex. All statistical logic (e.g., grouped aggregations) must be implemented manually, leading to the longest development time and a higher potential for errors.

### Pandas

* **Pros**:
  Features a mature, intuitive API and a vast ecosystem. Functions like `.describe()` and `.groupby().agg()` can complete analysis tasks with minimal code. Its widespread use means abundant online resources and community support, making it the easiest tool to get started with.

* **Cons**:
  Tends to load the entire dataset into memory, which can lead to performance bottlenecks or out-of-memory issues when handling extremely large files.

### Polars

* **Pros**:
  Offers the best performance of the three. Its query engine, built on Rust, utilizes parallel processing and lazy execution, resulting in outstanding memory efficiency and computation speed. Its Expression API is modern and powerful.

* **Cons**:
  For beginners, its Expression API might have a slightly steeper learning curve compared to Pandas.

---

#### **Recommendation for a Junior Analyst**

If coaching a junior data analyst, I would recommend starting with **Pandas**. Its intuitive syntax and vast learning resources help newcomers build confidence and produce results quickly. Once comfortable with data manipulation concepts, transitioning to **Polars** would be a logical next step to gain significant performance advantages.

---

## 📂 Project Structure

* `pure_python_stats.py`
  Pure Python script with no Pandas/Polars dependency. It automatically detects column types and performs descriptive statistics for numeric, categorical, and complex fields.

* `pandas_stats.py`
  Script using the Pandas library for concise and efficient data loading and analysis.

* `polars_stats.py`
  Script using the Polars library, offering the highest performance among the three.

---

## 📈 Dataset Source

This project does **NOT** include the raw dataset.
Please download it from the link below and place the CSV file in the project's root directory.

* **Dataset Link**: [2024 Facebook Ads, Facebook Posts, and Twitter Posts](https://drive.google.com/file/d/1Jq0fPb-tq76Ee_RtM58fT0_M3o-JDBwe/view?usp=sharing)

---

## 🚀 Installation and Execution

### 1. Install Dependencies

This project requires Pandas and Polars.

```bash
pip install pandas polars-lts-cpu
```

> **Note:** `polars-lts-cpu` is the general CPU compatibility version of Polars, which avoids errors on older machines that do not support AVX2 instruction sets.

---

### 2. Run Analysis Scripts

You can run any of the following scripts. The program will interactively prompt you for the source CSV filename, the output JSON filename, and optional grouping columns.

* Pure Python version

  ```bash
  python pure_python_stats.py
  ```

* Pandas version

  ```bash
  python pandas_stats.py
  ```

* Polars version

  ```bash
  python polars_stats.py
  ```

**Example Run:**

```
Enter the CSV file name to analyze: 2024_fb_ads_president_scored_anon.csv
Enter the output JSON file name: 2024_fb_ads_president_scored_anon_analysis_results.json
Enter grouping columns, comma-separated, or press Enter for no grouping: page_id
```

---

---

# Task\_04\_Descriptive\_Stats

本專案旨在建立一個資料總結分析系統，並針對真實世界的資料集進行探索與摘要。
專案的核心任務是使用三種不同的技術策略——**純 Python**、**Pandas** 和 **Polars**——對 2024 年美國總統大選相關的社群媒體資料進行描述性統計分析，並產生相同的數值結果。

---

## 📊 主要發現與比較

根據任務要求，本專案不僅產出統計結果，也對三種方法的開發流程與效能進行了比較：

### 純 Python

* **優點**：
  無任何第三方函式庫依賴，具備最佳的移植性與部署彈性。此次實作採用\*\*單遍掃描（single-pass）\*\*的流式處理方法，記憶體效率極高，理論上能處理遠超出記憶體大小的檔案。

* **缺點**：
  程式碼最為冗長、複雜。所有統計邏輯（如分組聚合）皆需手動實作，開發時間最長，且較容易出錯。

### Pandas

* **優點**：
  API 成熟直觀，生態系龐大。使用 `.describe()` 和 `.groupby().agg()` 等方法能用極少的程式碼快速完成分析任務。其廣泛的應用代表著豐富的線上資源與社群支援，使其成為最容易上手的工具。

* **缺點**：
  習慣一次將整個資料集載入記憶體，在處理極大型檔案時可能會遇到效能瓶頸或記憶體不足的問題。

### Polars

* **優點**：
  效能是三者中最強的。其查詢引擎基於 Rust 開發並採用了平行處理與延遲執行（lazy execution）等技術，記憶體使用效率和運算速度都非常出色。其表達式 API（Expression API）語法現代且功能強大。

* **缺點**：
  對於初學者來說，其表達式 API 的學習曲線可能比 Pandas 稍微陡峭一些。

---

#### **給初階資料分析師的建議**

如果指導一位初階分析師，我會推薦從 **Pandas** 開始。它直觀的語法和豐富的教學資源能幫助新人快速建立信心並產出成果。當對資料處理流程熟悉後，再學習 **Polars** 作為進階工具，以應對更嚴苛的效能需求。

---

## 📂 專案結構

* `pure_python_stats.py`
  純 Python 腳本，不依賴 Pandas/Polars。自動偵測欄位型別並執行描述性統計，能夠處理數值、類別及複雜欄位。

* `pandas_stats.py`
  使用 Pandas 函式庫載入與分析資料的腳本，程式碼簡潔高效。

* `polars_stats.py`
  使用 Polars 函式庫的腳本，為三者中效能最佳的方案。

---

## 📈 資料來源

本專案**不包含**原始資料集。
請從下方連結下載，並將 CSV 檔案放置於專案根目錄。

* **資料集連結**：[2024 Facebook Ads, Facebook Posts, and Twitter Posts](https://drive.google.com/file/d/1Jq0fPb-tq76Ee_RtM58fT0_M3o-JDBwe/view?usp=sharing)

---

## 🚀 安裝與執行

### 1. 安裝依賴套件

本專案需要安裝 Pandas 和 Polars。

```bash
pip install pandas polars-lts-cpu
```

> **註：**`polars-lts-cpu` 是 Polars 的通用 CPU 相容版本，可避免在不支援 AVX2 指令集的舊款電腦上出錯。

---

### 2. 執行分析腳本

你可以執行以下任一腳本。程式會以互動方式提示你輸入來源 CSV 檔名、輸出 JSON 檔名以及分組依據的欄位（可選）。

* 執行純 Python 版本

  ```bash
  python pure_python_stats.py
  ```

* 執行 Pandas 版本

  ```bash
  python pandas_stats.py
  ```

* 執行 Polars 版本

  ```bash
  python polars_stats.py
  ```

**執行範例：**

```
請輸入要分析的 CSV 檔案名稱: 2024_fb_ads_president_scored_anon.csv
請輸入輸出的 JSON 檔案名稱: 2024_fb_ads_president_scored_anon_analysis_results.json
請輸入分組欄位（用逗號分隔，若不分組請直接按 Enter）: page_id
```
