import csv
import math
import ast
import json
from collections import Counter

def _initialize_stats_structure(column_types):
    """
    輔助函式：根據欄位類型初始化一個統計容器。
    Helper function: Initializes a statistics container based on column types.
    """
    stats_structure = {}
    for col_name, col_type in column_types.items():
        if col_type == 'numeric':
            stats_structure[col_name] = {'count': 0, 'sum': 0.0, 'sum_sq': 0.0, 'min': float('inf'), 'max': float('-inf')}
        elif col_type == 'categorical':
            stats_structure[col_name] = {'counter': Counter()}
        elif col_type == 'complex':
            # 僅針對特定的複雜欄位進行初始化。
            # Initialize only for specific complex columns.
            if col_name == 'publisher_platforms':
                stats_structure[col_name] = {'counter': Counter()}
    return stats_structure

def _calculate_final_stats(stats, col_type):
    """
    輔助函式：從累計的統計數據中計算最終結果。
    Helper function: Calculates final results from accumulated statistics.
    """
    final_stats = {}
    if col_type == 'numeric':
        count = stats.get('count', 0)
        if count > 0:
            mean = stats['sum'] / count
            final_stats['count'] = count
            final_stats['mean'] = mean
            final_stats['min'] = stats['min'] if stats['min'] != float('inf') else 0
            final_stats['max'] = stats['max'] if stats['max'] != float('-inf') else 0
            if count > 1:
                variance = (stats['sum_sq'] / count) - (mean ** 2)
                # 確保變異數非負（可能因浮點數精度問題發生）。
                # Ensure variance is non-negative (can happen due to float precision).
                variance = max(0, variance)
                final_stats['stdev'] = math.sqrt(variance * (count / (count - 1)))
            else:
                final_stats['stdev'] = 0
    
    elif col_type == 'categorical' or (col_type == 'complex' and 'counter' in stats):
        final_stats['count'] = sum(stats['counter'].values())
        final_stats['unique_count'] = len(stats['counter'])
        final_stats['most_common'] = stats['counter'].most_common(5)
    
    return final_stats

def detect_column_types(data, header, sample_size=100):
    """
    自動偵測欄位類型（數值、類別或複雜/可解析）。
    Automatically detects column types (numeric, categorical, or complex/parsable).
    """
    print("開始偵測欄位類型...")
    print("Starting column type detection...")
    
    column_types = {}
    # 為了效率，僅取樣部分資料進行偵測。
    # For efficiency, take a sample of data for detection.
    sample = data[:sample_size]

    for i, col_name in enumerate(header):
        numeric_count = 0
        parsable_count = 0
        
        for row in sample:
            if len(row) <= i: continue
            value = row[i]
            if not value: continue 

            # 嘗試將值轉換為數值。
            # Try to convert the value to a numeric type.
            try:
                float(value)
                numeric_count += 1
                continue
            except ValueError:
                pass

            # 嘗試判斷是否為可解析的字串（如 list 或 dict）。
            # Try to determine if it's a parsable string (like a list or dict).
            if (value.startswith('{') and value.endswith('}')) or \
               (value.startswith('[') and value.endswith(']')):
                try:
                    ast.literal_eval(value)
                    parsable_count += 1
                except (ValueError, SyntaxError):
                    pass
        
        # 基於多數原則進行判斷。
        # Judge the type based on majority rule.
        if numeric_count / len(sample) > 0.8:
            column_types[col_name] = 'numeric'
        elif parsable_count / len(sample) > 0.8:
            column_types[col_name] = 'complex'
        else:
            column_types[col_name] = 'categorical'

    print("欄位類型偵測完畢。")
    print("Column type detection complete.")
    print(json.dumps(column_types, indent=2, ensure_ascii=False))
    return column_types

def analyze_data(file_path, output_filename, group_by_columns=None):
    """
    分析函式，支援對資料集進行整體分析或分組聚合分析。
    Analysis function that supports both overall analysis and grouped aggregation for the dataset.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)
            
            # --- 步驟 1: 預先偵測欄位類型 ---
            # --- Step 1: Pre-detect column types ---
            sample_data = list(csv.reader(open(file_path, mode='r', encoding='utf-8')))[1:101]
            column_types = detect_column_types(sample_data, header)

            # --- 步驟 2: 初始化統計容器與分組設定 ---
            # --- Step 2: Initialize statistics containers and grouping settings ---
            running_stats = {}
            group_by_indices = []
            if group_by_columns:
                print(f"\n進行分組分析，分組依據: {group_by_columns}")
                print(f"Performing grouped analysis, grouping by: {group_by_columns}")
                try:
                    # 取得分組欄位在標頭中的索引位置。
                    # Get the index positions of grouping columns in the header.
                    group_by_indices = [header.index(col) for col in group_by_columns]
                except ValueError as e:
                    print(f"錯誤：分組欄位 '{e}' 不存在於 CSV 標頭中。")
                    print(f"Error: Group-by column '{e}' not found in CSV header.")
                    return
            else:
                print("\n進行整體分析（無分組）。")
                print("Performing overall analysis (no grouping).")
                # 若不分組，則使用單層結構初始化統計容器。
                # If not grouping, initialize the statistics container with a single-level structure.
                running_stats = _initialize_stats_structure(column_types)

            total_rows = 0
            
            # 將檔案讀取指標移回標頭之後。
            # Reset the file reader pointer to after the header.
            infile.seek(0)
            next(reader)

            # --- 步驟 3: 單遍掃描與即時計算 ---
            # --- Step 3: Single-pass scan and on-the-fly calculation ---
            print("\n開始處理資料...")
            print("Starting data processing...")
            
            for row in reader:
                if len(row) < len(header): continue
                total_rows += 1

                # 根據是否分組，決定要更新哪個層級的統計資料。
                # Based on whether grouping is active, determine which level of statistics to update.
                target_stats_container = None
                if group_by_columns:
                    # 產生分組鍵（一個包含分組欄位值的元組）。
                    # Create a group key (a tuple of values from grouping columns).
                    group_key = tuple(row[i] for i in group_by_indices)
                    
                    # 如果是新的群組，為它初始化一個完整的統計結構。
                    # If it's a new group, initialize a full stats structure for it.
                    if group_key not in running_stats:
                        running_stats[group_key] = _initialize_stats_structure(column_types)
                    target_stats_container = running_stats[group_key]
                else:
                    # 不分組時，目標容器就是最外層的 running_stats。
                    # When not grouping, the target container is the main running_stats.
                    target_stats_container = running_stats

                for i, col_name in enumerate(header):
                    # 如果是分組欄位本身，則跳過對其自身的統計。
                    # If the column is a grouping column, skip statistics for it.
                    if group_by_columns and col_name in group_by_columns:
                        continue

                    value_str = row[i]
                    if not value_str: continue

                    col_type = column_types.get(col_name)
                    # 從目標容器中取得對應欄位的統計物件。
                    # Get the statistics object for the corresponding column from the target container.
                    stats_obj = target_stats_container.get(col_name)
                    if not stats_obj: continue

                    if col_type == 'numeric':
                        try:
                            num_val = float(value_str)
                            stats_obj['count'] += 1
                            stats_obj['sum'] += num_val
                            stats_obj['sum_sq'] += num_val ** 2
                            if num_val < stats_obj['min']: stats_obj['min'] = num_val
                            if num_val > stats_obj['max']: stats_obj['max'] = num_val
                        except ValueError:
                            pass
                    
                    elif col_type == 'categorical':
                        stats_obj['counter'][value_str] += 1
                    
                    elif col_type == 'complex' and col_name == 'publisher_platforms':
                        try:
                            platforms = json.loads(value_str.replace("'", '"'))
                            stats_obj['counter'].update(platforms)
                        except (json.JSONDecodeError, TypeError):
                            pass

            print("資料處理完畢。")
            print("Data processing complete.")

            # --- 步驟 4: 整理最終輸出 ---
            # --- Step 4: Finalize and structure the results ---
            final_results = {}
            analysis_metadata = {
                'total_rows_processed': total_rows,
                'analysis_type': 'grouped' if group_by_columns else 'overall',
            }

            if group_by_columns:
                analysis_metadata['grouped_by'] = group_by_columns
                final_results['analysis_metadata'] = analysis_metadata
                final_results['grouped_analysis'] = {}
                
                # 遍歷每個群組的統計結果並進行最終計算。
                # Iterate over the statistics of each group and perform final calculations.
                for group_key, stats_data in running_stats.items():
                    group_final_stats = {}
                    for col_name, stats in stats_data.items():
                        col_final_stats = _calculate_final_stats(stats, column_types[col_name])
                        if col_final_stats:
                             group_final_stats[col_name] = col_final_stats
                    # JSON 的鍵不能是元組，所以將其轉換為字串。
                    # JSON keys cannot be tuples, so convert the group key to a string.
                    final_results['grouped_analysis'][str(group_key)] = group_final_stats

            else:
                final_results['analysis_metadata'] = analysis_metadata
                overall_analysis = {}
                for col_name, stats in running_stats.items():
                    col_final_stats = _calculate_final_stats(stats, column_types[col_name])
                    if col_final_stats:
                        overall_analysis[col_name] = col_final_stats
                final_results['overall_analysis'] = overall_analysis
            
            # --- 步驟 5: 輸出結果 ---
            # --- Step 5: Output the results ---
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                json.dump(final_results, outfile, indent=4, ensure_ascii=False)

            print(f"\n分析完成！結果已儲存至 '{output_filename}'")
            print(f"Analysis complete! Results saved to '{output_filename}'")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'。")
        print(f"Error: File not found at '{file_path}'.")
    except Exception as e:
        print(f"處理過程中發生未預期的錯誤: {e}")
        print(f"An unexpected error occurred during processing: {e}")

if __name__ == '__main__':
    input_file = input("請輸入要分析的 CSV 檔案名稱 (Enter the CSV file name to analyze): ")
    output_file = input("請輸入輸出的 JSON 檔案名稱 (Enter the output JSON file name): ")
    
    # 提示使用者輸入分組欄位。
    # Prompts the user to enter the grouping columns.
    group_by_str = input("請輸入分組欄位 (用逗號分隔，若不分組請直接按 Enter)\n(Enter grouping columns, comma-separated, or press Enter for no grouping): ")
    group_by_cols = None
    if group_by_str:
        # 將輸入的字串轉換為欄位名稱列表。
        # Convert the input string into a list of column names.
        group_by_cols = [col.strip() for col in group_by_str.split(',') if col.strip()]

    analyze_data(input_file, output_file, group_by_columns=group_by_cols)