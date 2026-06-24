import pandas as pd
import glob
import os
import re

# --- 定数定義 ---
# 将来的に参照する必要がある場合に備えて、元のトライアル定義の構造をコメントとして残す
# EXPERIMENT_TRIALS_JSON = """ ... """
OUTPUT_FILENAME = 'all_data.csv'

def consolidate_data():
    """
    複数の被験者の行動・アンケートデータが統合されたCSVファイルを、
    さらに単一のマスターCSVファイルとして統合する。
    """
    all_participants_data = []
    
    # 探索パターンの定義
    patterns = [
        'task_timings_p*.csv',
        'data/task_timings*.csv'
    ]
    
    participant_files = []
    for pattern in patterns:
        participant_files.extend(glob.glob(pattern))
    
    participant_files = sorted(list(set(participant_files))) # 重複排除とソート
    
    if not participant_files:
        print("エラー: 統合対象のファイルが見つかりません。")
        return

    print(f"{len(participant_files)} 件のデータファイルが見つかりました。")

    for i, p_file in enumerate(participant_files):
        # ファイル名から被験者IDを抽出、または生成
        # 例: task_timings_p1.csv -> p1, task_timings (7).csv -> participant_7
        match = re.search(r'p(\d+)', p_file)
        if match:
            participant_id = f"p{match.group(1)}"
        else:
            # カッコ内の数字を抽出してみる (例: (7) -> participant_7)
            match_paren = re.search(r'\((\d+)\)', p_file)
            if match_paren:
                participant_id = f"participant_{match_paren.group(1)}"
            else:
                participant_id = f"participant_{i+1}"
        
        print(f"--- 処理中: {p_file} (ID: {participant_id}) ---")

        try:
            df_participant = pd.read_csv(p_file)
            
            # カラム名の正規化
            # perceivedTime -> perceivedLoadingTime
            if 'perceivedTime' in df_participant.columns and 'perceivedLoadingTime' not in df_participant.columns:
                df_participant = df_participant.rename(columns={'perceivedTime': 'perceivedLoadingTime'})
            
            df_participant['participant_id'] = participant_id
            all_participants_data.append(df_participant)

        except Exception as e:
            print(f"エラー: {p_file} の処理中にエラーが発生しました: {e}")
            continue
            
    if not all_participants_data:
        print("統合できる有効なデータがありませんでした。")
        return

    df_all = pd.concat(all_participants_data, ignore_index=True)
    
    # データ型を調整
    numeric_cols = ['perceivedLoadingTime', 'discomfort', 'reliability']
    for col in numeric_cols:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')
    
    if 'simulatedLoadingTime' in df_all.columns:
        df_all['simulatedLoadingTime_sec'] = df_all['simulatedLoadingTime'] / 1000
    if 'taskDuration' in df_all.columns:
        df_all['taskDuration_sec'] = df_all['taskDuration'] / 1000
    
    # 必須カラム（心理指標）が揃っている行のみを残す
    # 旧形式(p1)はこれらのカラムがないため、ここで除外される
    df_all.dropna(subset=[col for col in numeric_cols if col in df_all.columns], inplace=True)
    
    # 最終的な列の順序
    final_columns = [
        'participant_id', 'executionOrder', 'originalTrialNumber', 
        'loaderType', 'simulatedLoadingTime', 'simulatedLoadingTime_sec',
        'rageClicks', 'mouseDistance', 'taskDuration', 'taskDuration_sec',
        'totalLoadingTime', 'pureTaskDuration',
        'perceivedLoadingTime', 'discomfort', 'reliability'
    ]
    df_final = df_all[[col for col in final_columns if col in df_all.columns]]

    df_final.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8')
    
    print("\n" + "="*50)
    print("データの統合が完了しました。")
    print(f"出力ファイル: {OUTPUT_FILENAME}")
    print(f"総試行数: {len(df_final)}")
    print(f"ユニーク被験者数: {df_final['participant_id'].nunique()} ({', '.join(df_final['participant_id'].unique())})")
    print("="*50)

if __name__ == '__main__':
    consolidate_data()
