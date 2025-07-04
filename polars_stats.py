import polars as pl
import json
import ast

def analyze_with_polars(file_path, output_filename, group_by_columns=None):
    """
    使用 polars 函式庫分析資料集，支援整體分析與分組聚合分析。
    Analyzes the dataset using the polars library, supporting both overall and grouped aggregation analysis.
    """
    try:
        # --- 步驟 1: 讀取資料 ---
        # --- Step 1: Load the data ---
        print(f"正在使用 polars 讀取檔案: {file_path}")
        print(f"Loading file with polars: {file_path}")
        # 使用 polars 的 read_csv，infer_schema_length 參數有助於更準確地推斷欄位型別。
        # Use polars' read_csv; the infer_schema_length parameter helps in more accurately inferring column types.
        df = pl.read_csv(file_path, infer_schema_length=10000, ignore_errors=True)
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
            # Polars 的 describe() 會回傳一個 DataFrame，我們將其轉換為字典。
            # Polars' describe() returns a DataFrame, which we convert to a dictionary.
            desc_df = df.describe()
            # 將 describe 的結果從列表形式轉換為更易於使用的字典結構。
            # Convert the describe result from a list format to a more usable dictionary structure.
            numeric_stats_raw = desc_df.to_dicts()
            numeric_stats = {}
            for row in numeric_stats_raw:
                stat_name = row['describe']
                for col, val in row.items():
                    if col == 'describe': continue
                    if col not in numeric_stats: numeric_stats[col] = {}
                    # Polars 的 describe() 結果包含 'count' (非空計數), 'mean', 'std', 'min', 'max' 等。
                    # Polars' describe() results include 'count', 'mean', 'std', 'min', 'max', etc.
                    if stat_name in ['count', 'mean', 'std', 'min', 'max']:
                        numeric_stats[col][stat_name] = val
            
            # 處理類別欄位的統計，Polars 中字串型別為 pl.Utf8。
            # Process statistics for categorical columns; the string type in Polars is pl.Utf8.
            categorical_cols = [col.name for col in df if col.dtype == pl.Utf8]
            categorical_stats = {}
            for col in categorical_cols:
                # 跳過複雜欄位，稍後單獨處理。
                # Skip complex columns to be handled separately later.
                if col in ['ad_creative_bodies', 'ad_creative_link_captions', 'ad_creative_link_titles', 'ad_creative_link_descriptions', 'publisher_platforms']:
                    continue
                
                # 使用 Polars 表達式計算統計數據。
                # Use Polars expressions to calculate statistics.
                stats = df.select([
                    pl.col(col).count().alias("count"),
                    pl.col(col).n_unique().alias("unique_count"),
                    pl.col(col).value_counts().head(5).alias("most_common")
                ]).to_dicts()[0]
                # 將 most_common 的 DataFrame 結構轉換為字典。
                # Convert the most_common DataFrame structure into a dictionary.
                most_common_df = stats['most_common']
                stats['most_common'] = dict(zip(most_common_df[col], most_common_df['counts']))
                categorical_stats[col] = stats
            
            # 特別處理 'publisher_platforms' 欄位。
            # Special handling for the 'publisher_platforms' column.
            if 'publisher_platforms' in df.columns:
                try:
                    platforms_series = df.get_column('publisher_platforms').drop_nulls()
                    # 使用 map_elements 安全地解析字串，然後 explode 和 value_counts。
                    # Use map_elements to safely parse the string, then explode and value_counts.
                    platform_counts = platforms_series.map_elements(ast.literal_eval, return_dtype=pl.List(pl.Utf8)) \
                                                    .explode() \
                                                    .value_counts()
                    categorical_stats['publisher_platforms'] = {
                        'count': platform_counts['counts'].sum(),
                        'unique_count': len(platform_counts),
                        'most_common': dict(zip(platform_counts['publisher_platforms'].head(5), platform_counts['counts'].head(5)))
                    }
                except Exception as e:
                     print(f"警告：處理 'publisher_platforms' 欄位時發生錯誤: {e}")
                     print(f"Warning: Error processing 'publisher_platforms' column: {e}")

            # 組合數值與類別統計結果。
            # Combine numeric and categorical statistics.
            overall_analysis.update(numeric_stats)
            overall_analysis.update(categorical_stats)
            final_results['overall_analysis'] = overall_analysis

        else:
            # --- 分組分析 (Grouped Analysis) ---
            print(f"\n進行分組分析，分組依據: {group_by_columns}...")
            print(f"Performing grouped analysis, grouping by: {group_by_columns}...")

            for col in group_by_columns:
                if col not in df.columns:
                    print(f"錯誤：分組欄位 '{col}' 不存在於資料集中。")
                    print(f"Error: Grouping column '{col}' not found in the dataset.")
                    return
            
            # 定義聚合表達式。
            # Define the aggregation expressions.
            numeric_cols = [col.name for col in df if col.dtype in [pl.Int64, pl.Float64]]
            aggs = []
            for col in numeric_cols:
                aggs.extend([
                    pl.col(col).count().alias(f"{col}_count"),
                    pl.col(col).mean().alias(f"{col}_mean"),
                    pl.col(col).min().alias(f"{col}_min"),
                    pl.col(col).max().alias(f"{col}_max"),
                    pl.col(col).std().alias(f"{col}_std")
                ])
            
            # 執行分組與聚合。
            # Perform grouping and aggregation.
            grouped_stats_df = df.group_by(group_by_columns).agg(aggs)
            
            # 將結果轉換為巢狀字典。
            # Convert the result into a nested dictionary.
            grouped_analysis = {}
            for row in grouped_stats_df.to_dicts():
                group_key_parts = [row[col] for col in group_by_columns]
                group_key = str(tuple(group_key_parts))
                grouped_analysis[group_key] = {}
                for col_name in numeric_cols:
                    grouped_analysis[group_key][col_name] = {
                        'count': row.get(f"{col_name}_count"),
                        'mean': row.get(f"{col_name}_mean"),
                        'min': row.get(f"{col_name}_min"),
                        'max': row.get(f"{col_name}_max"),
                        'std': row.get(f"{col_name}_std")
                    }

            final_results['grouped_analysis'] = grouped_analysis

        # --- 步驟 3: 輸出結果 ---
        # --- Step 3: Output the results ---
        print("\n分析完成，正在將結果寫入檔案...")
        print("Analysis complete, writing results to file...")
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            json.dump(final_results, outfile, indent=4, ensure_ascii=False)

        print(f"結果已成功儲存至 '{output_filename}'")
        print(f"Results successfully saved to '{output_filename}'")

    except pl.exceptions.ComputeError as e:
        print(f"Polars 運算錯誤: {e}")
        print(f"Polars compute error: {e}")
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

    analyze_with_polars(input_file, output_file, group_by_columns=group_by_cols)