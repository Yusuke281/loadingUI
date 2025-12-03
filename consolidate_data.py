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
    
    # 'task_timings_p*.csv'のパターンに一致するすべてのファイルを探す
    # このファイルには、すでに行動データとアンケートデータが含まれている
    participant_files = sorted(glob.glob('task_timings_p*.csv'))
    
    if not participant_files:
        print("エラー: 'task_timings_p*.csv' のパターンに一致するファイルが見つかりません。")
        print("実験データCSVの命名規則が 'task_timings_p1.csv' のようになっているか確認してください。")
        return

    print(f"{len(participant_files)} 人の被験者データが見つかりました。")

    for p_file in participant_files:
        # ファイル名から被験者IDを抽出 (例: task_timings_p1.csv -> p1)
        match = re.search(r'task_timings_(p\d+)\.csv', p_file)
        if not match:
            print(f"警告: ファイル名 '{p_file}' から被験者IDを抽出できませんでした。スキップします。")
            continue
        participant_id = match.group(1)
        
        print(f"--- 被験者ID: {participant_id} のデータ ({p_file}) を処理中 ---")

        try:
            # --- データの読み込み ---
            df_participant = pd.read_csv(p_file)
            
            # --- 被験者ID列を追加 ---
            df_participant['participant_id'] = participant_id

            all_participants_data.append(df_participant)

        except Exception as e:
            print(f"エラー: 被験者 {participant_id} のデータ処理中にエラーが発生しました: {e}")
            continue
            
    if not all_participants_data:
        print("統合できる有効なデータがありませんでした。処理を終了します。")
        return

    # 全被験者のデータを結合
    df_all = pd.concat(all_participants_data, ignore_index=True)
    
    # データ型を調整
    # errors='coerce'は、数値に変換できない値をNaN（Not a Number）にする
    df_all['perceivedLoadingTime'] = pd.to_numeric(df_all['perceivedLoadingTime'], errors='coerce')
    df_all['satisfaction'] = pd.to_numeric(df_all['satisfaction'], errors='coerce')
    df_all['simulatedLoadingTime_sec'] = df_all['simulatedLoadingTime'] / 1000
    df_all['taskDuration_sec'] = df_all['taskDuration'] / 1000
    
    # 満足度列の名前を 'satisfaction_score' に変更して他のスクリプトとの一貫性を保つ
    df_all.rename(columns={'satisfaction': 'satisfaction_score'}, inplace=True)

    # 欠損値を含む行を削除（アンケートに回答しなかった場合など）
    df_all.dropna(subset=['perceivedLoadingTime', 'satisfaction_score'], inplace=True)
    
    # 最終的な列の順序を定義
    # 'trial' を 'executionOrder' と 'originalTrialNumber' に変更
    final_columns = [
        'participant_id', 'executionOrder', 'originalTrialNumber', 
        'loaderType', 'simulatedLoadingTime', 'simulatedLoadingTime_sec',
        'rageClicks', 'mouseDistance', 'taskDuration', 'taskDuration_sec',
        'perceivedLoadingTime', 'satisfaction_score'
    ]
    # df_allに存在する列のみを抽出して順序を適用
    df_final = df_all[[col for col in final_columns if col in df_all.columns]]

    # 統合したデータをCSVファイルに保存
    df_final.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8')
    
    print("\n" + "="*50)
    print("すべての被験者データの統合が完了しました。")
    print(f"出力ファイル: {OUTPUT_FILENAME}")
    print(f"総試行回数: {len(df_final)}")
    print(f"ユニーク被験者数: {df_final['participant_id'].nunique()}")
    print("\n--- 統合後データ (最初の5行) ---")
    print(df_final.head())
    print("="*50)

if __name__ == '__main__':
    consolidate_data()
