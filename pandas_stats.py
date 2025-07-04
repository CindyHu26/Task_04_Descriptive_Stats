import pandas as pd
import json
import ast

def analyze_with_pandas(file_path, output_filename, group_by_columns=None):
    """
    使用 pandas 函式庫分析資料集，支援整體分析與分組聚合分析。
    Analyzes the dataset using the pandas library, supporting both overall and grouped aggregation analysis.
    """
    try:
        # --- 步驟 1: 讀取資料 ---
        # --- Step 1: Load the data ---
        print(f"正在使用 pandas 讀取檔案: {file_path}")
        print(f"Loading file with pandas: {file_path}")
        # 使用 pandas 的 read_csv 函式，並將型別不一致的欄位視為字串（object）處理。
        # Use pandas' read_csv function, treating columns with mixed types as strings (object).
        df = pd.read_csv(file_path, low_memory=False)
        print("檔案讀取完畢。")
        print("File loading complete.")

        final_results = {}
        analysis_metadata = {
            'total_rows_processed': len(df),
            'analysis_type': 'grouped' if group_by_columns else 'overall',
        }
        if group_by_columns:
            analysis_metadata['grouped_by'] = group_by_columns
        
        final_results['analysis_metadata'] = analysis_metadata

        # --- 步驟 2: 執行分析 ---
        # --- Step 2: Perform analysis ---
        if not group_by_columns:
            # --- 整體分析 (Overall Analysis) ---
            print("\n進行整體分析（無分組）...")
            print("Performing overall analysis (no grouping)...")
            
            overall_analysis = {}
            # 使用 describe() 函式一次性取得所有數值欄位的核心統計數據。
            # Use the describe() function to get core statistics for all numeric columns at once.
            numeric_stats = df.describe(include='number').to_dict()
            
            # 處理類別欄位的統計。
            # Process statistics for categorical columns.
            categorical_cols = df.select_dtypes(include=['object']).columns
            categorical_stats = {}
            for col in categorical_cols:
                # 跳過過於複雜或不適合進行常規類別分析的欄位。
                # Skip columns that are too complex or not suitable for regular categorical analysis.
                if col in ['ad_creative_bodies', 'ad_creative_link_captions', 'ad_creative_link_titles', 'ad_creative_link_descriptions']:
                    continue

                # 特別處理 'publisher_platforms' 欄位。
                # Special handling for the 'publisher_platforms' column.
                if col == 'publisher_platforms':
                    # 安全地將字串轉換為列表，並計算每個平台出現的次數。
                    # Safely convert strings to lists and count occurrences of each platform.
                    try:
                        platforms = df[col].dropna().apply(ast.literal_eval)
                        platform_counts = platforms.explode().value_counts()
                        categorical_stats[col] = {
                            'count': int(platform_counts.sum()),
                            'unique_count': len(platform_counts),
                            'most_common': platform_counts.head(5).to_dict()
                        }
                    except (ValueError, SyntaxError) as e:
                        print(f"警告：處理 '{col}' 欄位時發生錯誤，將其視為一般類別欄位。錯誤: {e}")
                        print(f"Warning: Error processing column '{col}', treating as a regular categorical column. Error: {e}")
                        # 如果解析失敗，則退回為標準的計數方法。
                        # Fallback to standard value counting if parsing fails.
                        counts = df[col].value_counts()
                        categorical_stats[col] = {
                            'count': int(df[col].count()),
                            'unique_count': int(df[col].nunique()),
                            'most_common': counts.head(5).to_dict()
                        }
                else:
                    counts = df[col].value_counts()
                    categorical_stats[col] = {
                        'count': int(df[col].count()),
                        'unique_count': int(df[col].nunique()),
                        'most_common': counts.head(5).to_dict()
                    }

            # 組合數值與類別統計結果。
            # Combine numeric and categorical statistics.
            overall_analysis.update(numeric_stats)
            overall_analysis.update(categorical_stats)
            final_results['overall_analysis'] = overall_analysis

        else:
            # --- 分組分析 (Grouped Analysis) ---
            print(f"\n進行分組分析，分組依據: {group_by_columns}...")
            print(f"Performing grouped analysis, grouping by: {group_by_columns}...")

            # 檢查分組欄位是否存在。
            # Check if grouping columns exist.
            for col in group_by_columns:
                if col not in df.columns:
                    print(f"錯誤：分組欄位 '{col}' 不存在於資料集中。")
                    print(f"Error: Grouping column '{col}' not found in the dataset.")
                    return

            grouped = df.groupby(group_by_columns)
            
            # 對數值欄位進行分組聚合。
            # Perform grouped aggregation on numeric columns.
            numeric_cols = df.select_dtypes(include='number').columns
            agg_funcs = ['count', 'mean', 'min', 'max', 'std']
            grouped_numeric_stats = grouped[numeric_cols].agg(agg_funcs).to_dict('index')

            # 將結果轉換為與純 Python 版本相似的巢狀結構。
            # Convert the results to a nested structure similar to the pure Python version.
            nested_stats = {}
            for group_key, stats in grouped_numeric_stats.items():
                # 如果只有一個分組欄位，group_key 不是元組，將其標準化。
                # If there's only one grouping column, group_key is not a tuple; standardize it.
                key_tuple = group_key if isinstance(group_key, tuple) else (group_key,)
                nested_stats[str(key_tuple)] = {}
                for multi_level_col, value in stats.items():
                    col, stat_name = multi_level_col
                    if col not in nested_stats[str(key_tuple)]:
                        nested_stats[str(key_tuple)][col] = {}
                    nested_stats[str(key_tuple)][col][stat_name] = value

            final_results['grouped_analysis'] = nested_stats
            
            # 注意：Pandas 的分組類別統計相對複雜，此處僅提供數值分組作為主要實現。
            # Note: Grouped categorical statistics in Pandas are relatively complex. 
            # This implementation focuses on numeric grouping as the primary feature.

        # --- 步驟 3: 輸出結果 ---
        # --- Step 3: Output the results ---
        print("\n分析完成，正在將結果寫入檔案...")
        print("Analysis complete, writing results to file...")
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            # 使用 default=str 來處理無法被序列化的資料型別（如 numpy 的數值型別）。
            # Use default=str to handle non-serializable data types (like numpy numeric types).
            json.dump(final_results, outfile, indent=4, ensure_ascii=False, default=str)

        print(f"結果已成功儲存至 '{output_filename}'")
        print(f"Results successfully saved to '{output_filename}'")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'。")
        print(f"Error: File not found at '{file_path}'.")
    except Exception as e:
        print(f"處理過程中發生未預期的錯誤: {e}")
        print(f"An unexpected error occurred during processing: {e}")

if __name__ == '__main__':
    input_file = input("請輸入要分析的 CSV 檔案名稱 (Enter the CSV file name to analyze): ")
    output_file = input("請輸入輸出的 JSON 檔案名稱 (Enter the output JSON file name): ")
    
    group_by_str = input("請輸入分組欄位 (用逗號分隔，若不分組請直接按 Enter)\n(Enter grouping columns, comma-separated, or press Enter for no grouping): ")
    group_by_cols = None
    if group_by_str:
        group_by_cols = [col.strip() for col in group_by_str.split(',') if col.strip()]

    analyze_with_pandas(input_file, output_file, group_by_columns=group_by_cols)