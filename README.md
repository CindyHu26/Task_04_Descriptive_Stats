# Task\_04\_Descriptive\_Stats

This project aims to build a data summarizing system to explore and summarize a real-world dataset.
The core task is to perform descriptive statistical analysis on social media data related to the 2024 US Presidential election using three different technical strategies—**Pure Python**, **Pandas**, and **Polars**—to produce identical numerical results.

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
#### Challenges and Solutions

In implementing this descriptive statistical analysis system, practical challenges were encountered, particularly when dealing with real-world, non-standardized data formats, and in ensuring that the three distinct strategies (Pure Python, Pandas, Polars) produced **identical numerical results**.

1.  **Complex Column Data Parsing**:
    * **Challenge**: The dataset contains **complex nested structured data** in columns like `demographic_distribution` and `publisher_platforms`. For instance, the `publisher_platforms` column stores Python lists as strings (e.g., `['facebook', 'instagram']`), while the `demographic_distribution` column stores Python dictionaries as strings, containing various gender-age groups with corresponding spend and impression data. Directly using these columns for statistics would lead to inaccurate results, as they are not simple categorical or numeric values.
    * **Solution**:
        * A unified approach was adopted to parse these complex string data:
            * The built-in Python function `ast.literal_eval()` was used to safely convert string representations of lists or dictionaries into actual Python objects.
            * For `publisher_platforms`, after parsing, the code further leveraged Pandas' `explode()` or Polars' equivalent operation to unnest each platform from the list into individual rows, thereby accurately counting the frequency and total spend per platform.
            * While the `demographic_distribution` column was not subjected to deep numerical aggregation in the current scripts (due to its more complex structure), the `safe_literal_eval` function has laid the groundwork for handling such data.

2.  **Consistent Data Type Inference and Cleaning**:
    * **Challenge**：Different libraries exhibit variations in inferring data types for basic columns in CSV files. For example, certain numeric columns might contain non-numeric characters, which, if unhandled, can lead to type errors or inaccurate calculations. Ensuring that all tools process this "imperfect" data consistently is crucial for generating identical results.
    * **Solution**:
        * **Numeric Conversion**: For potentially numeric columns (e.g., `estimated_spend`), explicit conversion to a numeric type was performed. Unconvertible values were coerced to `NaN` (in Pandas) or skipped (in Pure Python) to ensure only valid numbers participate in calculations.
        * **Custom Type Detection**: The Pure Python script implements a custom `detect_column_types` function that uses sample-based judgment logic. It also explicitly corrects the type for the `publisher_platforms` column, ensuring it is recognized as a `complex` type to trigger special parsing logic.
        * **Library-level Parameters**: Pandas' `low_memory=False` and Polars' `infer_schema_length=10000` parameters assist in more accurate type inference during data loading.

3.  **Subtle Standard Deviation Differences**:
    * **Challenge**: Although Pandas' and Polars' `std()` functions both default to the unbiased estimate using $N-1$ (sample standard deviation), floating-point operations can lead to very minor discrepancies for extreme data or small sample sizes.
    * **Solution**: The Pure Python implementation explicitly uses the sample standard deviation formula (dividing by `count - 1`), ensuring transparency and alignment of the calculation logic with other libraries.

4.  **Unifying Data Structure After Grouped Aggregation**:
    * **Challenge**: Different libraries may output results in varying data structures after performing grouped aggregations, particularly concerning nested dictionaries' keys and organization. To produce "identical numerical results" and output them in a unified JSON format, additional transformation of the aggregation output was required.
    * **Solution**:
        * Pandas' `groupby().agg().to_dict('index')` and Polars' `group_by().agg().to_dicts()` both generate DataFrame/list structures that required further processing.
        * Post-processing logic was written to convert these raw outputs into a unified nested dictionary format, where group keys were converted to strings for seamless JSON serialization and cross-method comparison.

#### Extending the System to Handle Arbitrary Datasets

The provided scripts are already designed with a degree of generality, allowing them to process arbitrary CSV datasets, not strictly limited to the given 2024 US Presidential Election dataset.

* **Automated Column Type Detection**: The `detect_column_types` function in `pure_python_stats.py` is a key feature. It automatically analyzes a sample of the data to determine if a column is numeric, categorical, or a parsable complex string. This removes the need for pre-defined column types, enhancing generality.
* **Flexible Grouping and Aggregation**: All scripts allow the user to input arbitrary grouping columns, as long as these columns exist in the dataset.
* **Dynamic Column Processing**: The scripts iterate through all columns in the dataset (excluding some complex text columns skipped in specific cases) and apply the appropriate statistical methods based on their detected type.

To further enhance generality, the following could be considered:
* **Error Handling Flexibility**: While existing `try-except` blocks and null value handling provide robustness, more flexible logic could be added for different data cleaning scenarios (e.g., outlier handling, datetime parsing).
* **Configuration/Metadata Driven**: For truly arbitrary datasets, if a configuration file containing "metadata" about the dataset (e.g., which columns are IDs, which need special parsing, which to ignore) could be provided, it would further automate the analysis process and reduce manual input and assumptions.
* **Performance Timing**: As suggested in the task, adding time measurement counters could quantify the relative performance of different approaches across various dataset sizes.

#### AI Coding Tool Recommendations

When asked to generate descriptive statistics code, AI coding tools like ChatGPT typically exhibit the following patterns:

* **Default Recommended Approach**: These tools usually **prioritize recommending Pandas**. The reason is straightforward: Pandas is the most widely used library in the Python data science ecosystem, boasting extensive documentation, tutorials, and community support. Its API is intuitive and powerful, allowing common tasks like descriptive statistics to be accomplished with minimal code.
* **Template Code Generation**: AI tools are indeed capable of providing ready-to-use template code. For instance, when prompted to "calculate descriptive statistics for a CSV file using Pandas," it will likely offer examples similar to `pd.read_csv()` and `df.describe()`. For grouped statistics, it will suggest patterns like `groupby().agg()`. These templates can significantly accelerate the initial development phase.
* **Agreement with Recommendations**:
    * **Agreement**: For scenarios involving medium-sized datasets (that fit comfortably in memory), it is **agreed** that Pandas is the optimal recommendation. Its relatively gentle learning curve, intuitive syntax, and abundant resources empower newcomers to quickly gain proficiency and confidence.
    * **Disagreement (with caveats)**: However, if the dataset is exceptionally large (exceeding computer memory) or if there are stringent performance requirements, recommending only Pandas would be insufficient. In such cases, Polars or Pure Python's streaming approach would be superior choices. AI tools might not account for these extreme performance and memory considerations in their initial recommendations, necessitating the user to provide more specific context in their prompts. Therefore, as a data analyst, one needs to understand the strengths and limitations of different tools and not blindly accept the AI's default recommendations.

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
---
#### 挑戰與解決方案

在實現這個描述性統計分析系統的過程中，遇到了一些實際的挑戰，特別是在處理真實世界的、非標準格式的數據時，以及在確保三種不同策略（純 Python、Pandas、Polars）能產生**完全相同的數值結果**時。

1.  **複雜的欄位數據解析**:
    * **挑戰**：數據集中包含 `demographic_distribution` 和 `publisher_platforms` 等**複雜的巢狀結構數據**。例如，`publisher_platforms` 欄位以字串形式儲存 Python 列表（如 `['facebook', 'instagram']`），而 `demographic_distribution` 欄位則以字串形式儲存 Python 字典，內部包含多個性別-年齡組別及其對應的花費和曝光數據。直接使用這些欄位進行統計會導致不準確的結果，因為它們不是簡單的類別或數值。
    * **解決方案**：
        * 採取了統一的方法來解析這些複雜的字串數據：
            * 使用 Python 內建的 `ast.literal_eval()` 函式 來安全地將字串形式的列表或字典轉換為實際的 Python 物件。
            * 對於 `publisher_platforms`，在解析後，程式碼進一步利用 Pandas 的 `explode()` 或 Polars 的等效操作 將每個平台從列表中「展開」成單獨的行，從而正確地計算每個平台的頻率和總花費。
            * 雖然 `demographic_distribution` 欄位在當前腳本中未進行深入的數值聚合（因其結構更複雜），但 `safe_literal_eval` 函式 已為處理此類數據打下基礎。

2.  **數據類型推斷和清洗的一致性**:
    * **挑戰**：不同庫對 CSV 中基礎欄位的數據類型推斷有差異。例如，某些數值欄位可能包含非數字字符，這在未經處理時可能導致類型錯誤或計算不準確。確保所有工具都以相同的方式處理這些「不完美」的數據是產生相同結果的關鍵。
    * **解決方案**：
        * **數值轉換**：對於數值欄位（例如 `estimated_spend`），明確將其轉換為數值類型，並在轉換失敗時將錯誤值強制設為 `NaN` (Pandas) 或跳過 (純 Python)，確保只有有效數字參與計算。
        * **自定義類型偵測**：純 Python 腳本實現了自定義的 `detect_column_types` 函式，基於樣本數據的判斷邏輯，並對 `publisher_platforms` 欄位進行了明確的類型修正，確保其被識別為 `complex` 類型，從而啟動特殊的解析邏輯。
        * **庫級參數**：Pandas 的 `low_memory=False` 和 Polars 的 `infer_schema_length=10000` 幫助它們在載入時更準確地推斷類型。

3.  **標準差計算的細微差異**:
    * **挑戰**：儘管 Pandas 和 Polars 的 `std()` 函數預設都使用 $N-1$ 的無偏估計（樣本標準差），但對於極端數據或小樣本，浮點數運算可能導致非常微小的差異。
    * **解決方案**：純 Python 實現中明確地使用樣本標準差公式 (分母為 `count - 1`)，確保計算邏輯的透明性與其他庫對齊。

4.  **分組聚合後數據結構的統一**:
    * **挑戰**：不同庫在執行分組聚合後，其輸出的數據結構（尤其是巢狀字典）的鍵和組織方式可能不同。為了產生「相同的數值結果」並以統一的 JSON 格式輸出，需要對聚合結果進行額外的轉換。
    * **解決方案**：
        * Pandas 的 `groupby().agg().to_dict('index')` 和 Polars 的 `group_by().agg().to_dicts()` 都產生了需要進一步處理的 DataFrame/列表結構。
        * 編寫了後處理邏輯，將這些庫的原始輸出轉換為統一的巢狀字典格式，其中分組鍵被轉換為字串，方便 JSON 序列化和跨方法比較。

#### 擴展系統以處理任意數據集

目前提供的腳本設計已經具有一定的通用性，可以處理任意 CSV 數據集，而不僅限於給定的 2024 美國總統大選數據集。

* **自動欄位類型偵測**：`pure_python_stats.py` 中的 `detect_column_types` 函式 是一個關鍵特性，它會自動分析數據樣本來判斷欄位是數值、類別還是可解析的複雜字串。這使得腳本無需預設欄位類型，增加了通用性。
* **靈活的分組聚合**：所有腳本都允許使用者輸入任意分組欄位，只要這些欄位存在於數據集中即可。
* **動態處理欄位**：腳本會遍歷數據集中的所有欄位（除了在特定情況下跳過的一些複雜文本欄位），並根據其偵測到的類型應用相應的統計方法。

為了進一步增強通用性，可以考慮以下幾點：
* **錯誤處理彈性**：雖然目前有 `try-except` 塊 和對空值的跳過，但可以增加更多針對不同數據清洗情境（如異常值處理、日期時間解析）的彈性邏輯。
* **配置文件/元數據驅動**：對於完全任意的數據集，如果能夠提供一個包含數據集「元數據」的配置文件（例如，哪個欄位是 ID、哪個需要特殊解析、哪些應該被忽略等），將能更好地自動化分析流程，減少手動輸入和假設。
* **性能計時**：如任務所述，可以添加時間測量計數器，以量化不同方法在處理不同大小數據集時的相對性能。

#### AI 編碼工具的建議

當要求像 ChatGPT 這樣的 AI 編碼工具生成描述性統計的程式碼時，觀察到以下趨勢：

* **預設推薦方法**：這些工具通常會**優先推薦使用 Pandas**。原因很簡單：Pandas 是目前 Python 數據科學領域最廣泛使用的庫，擁有豐富的文檔、教程和社區支持。它的 API 直觀且功能強大，對於執行描述性統計等常見任務，只需要少量程式碼即可完成。
* **模板程式碼**：AI 工具確實能夠提供現成的模板程式碼。例如，當你要求它「用 Pandas 計算 CSV 文件的描述性統計」時，它很可能會給出類似於 `pd.read_csv()` 和 `df.describe()` 的範例。對於分組統計，也會提供 `groupby().agg()` 的模式。這些模板確實能大大加快開發的起步階段。
* **對推薦的同意與否**：
    * **同意**：對於處理中小型數據集（能完全載入記憶體）的場景，會**同意** Pandas 是最佳推薦。它的學習曲線相對平緩，有直觀的語法和龐大的資源。
    * **不同意（有但書）**：然而，如果數據集非常龐大（超出電腦記憶體），或者對計算速度有極高要求時，僅推薦 Pandas 就不夠了。在這種情況下，Polars 或純 Python 的流式處理方法會是更優的選擇。AI 工具可能不會在首次推薦時就考慮到這些效能和記憶體的極端場景，這需要使用者在提問時提供更具體的上下文。因此，作為資料分析師，需要了解不同工具的優勢和限制，不能盲目接受 AI 的預設推薦。