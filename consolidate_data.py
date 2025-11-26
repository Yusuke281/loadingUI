
import pandas as pd
import glob
import os
import json
import re

# --- 定数定義 ---
# script.jsからコピーした実験試行データ
EXPERIMENT_TRIALS_JSON = """
[
    { "taskHTML": "<strong>ブロッコリー</strong>と<strong>クッキー</strong>をカートに入れてください", "loader": "bar-color", "time": 5000 },
    { "taskHTML": "<strong>なす</strong>と<strong>オレンジジュース</strong>をカートに入れてください", "loader": "bar", "time": 5000 },
    { "taskHTML": "<strong>トマト</strong>と<strong>りんご</strong>をカートに入れてください", "loader": "none", "time": 1500 },
    { "taskHTML": "<strong>キウイ</strong>と<strong>コーラ</strong>をカートに入れてください", "loader": "spinner", "time": 3000 },
    { "taskHTML": "<strong>ピーマン</strong>と<strong>ケーキ</strong>をカートに入れてください", "loader": "none", "time": 3000 },
    { "taskHTML": "<strong>ほうれん草</strong>と<strong>オレンジ</strong>をカートに入れてください", "loader": "skeleton-color", "time": 5000 },
    { "taskHTML": "<strong>バナナ</strong>と<strong>チーズケーキ</strong>をカートに入れてください", "loader": "spinner", "time": 1500 },
    { "taskHTML": "<strong>にんじん</strong>と<strong>コーヒー</strong>をカートに入れてください", "loader": "bar-color", "time": 1500 },
    { "taskHTML": "<strong>ブロッコリー</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "none", "time": 5000 },
    { "taskHTML": "<strong>きゅうり</strong>と<strong>クッキー</strong>をカートに入れてください", "loader": "bar", "time": 3000 },
    { "taskHTML": "<strong>カリフラワー</strong>と<strong>メロン</strong>をカートに入れてください", "loader": "bar", "time": 1500 },
    { "taskHTML": "<strong>プリン</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "skeleton", "time": 5000 },
    { "taskHTML": "<strong>ピーマン</strong>と<strong>ポテトチップス</strong>をカートに入れてください", "loader": "spinner-color", "time": 3000 },
    { "taskHTML": "<strong>キウイ</strong>と<strong>なす</strong>をカートに入れてください", "loader": "skeleton-color", "time": 1500 },
    { "taskHTML": "<strong>チョコレート</strong>と<strong>にんじん</strong>をカートに入れてください", "loader": "spinner", "time": 5000 },
    { "taskHTML": "<strong>チーズケーキ</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "skeleton-color", "time": 3000 },
    { "taskHTML": "<strong>オレンジ</strong>と<strong>アイスクリーム</strong>をカートに入れてください", "loader": "skeleton", "time": 1500 },
    { "taskHTML": "<strong>りんご</strong>と<strong>ケーキ</strong>をカートに入れてください", "loader": "spinner-color", "time": 5000 },
    { "taskHTML": "<strong>トマト</strong>と<strong>いちご</strong>をカートに入れてください", "loader": "spinner-color", "time": 1500 },
    { "taskHTML": "<strong>バナナ</strong>と<strong>チョコレート</strong>をカートに入れてください", "loader": "bar-color", "time": 3000 },
    { "taskHTML": "<strong>パイナップル</strong>と<strong>ほうれん草</strong>をカートに入れてください", "loader": "skeleton", "time": 3000 }
]"""
EXPERIMENT_TRIALS = json.loads(EXPERIMENT_TRIALS_JSON)
OUTPUT_FILENAME = 'all_data.csv'

def consolidate_data():
    """
    複数の被験者の行動データとアンケートデータを統合し、
    単一のCSVファイルとして出力する。
    """
    all_participants_data = []
    
    # 'task_timings_p*.csv' のパターンに一致するファイルを探す
    behavior_files = sorted(glob.glob('task_timings_p*.csv'))
    
    if not behavior_files:
        print("エラー: 'task_timings_p*.csv' のパターンに一致するファイルが見つかりません。")
        print("ファイルの命名規則が 'task_timings_p1.csv' のようになっているか確認してください。")
        return

    print(f"{len(behavior_files)} 人の被験者データが見つかりました。")

    for behavior_file in behavior_files:
        # ファイル名から被験者IDを抽出 (例: task_timings_p1.csv -> p1)
        match = re.search(r'task_timings_(p\d+)\.csv', behavior_file)
        if not match:
            print(f"警告: ファイル名 '{behavior_file}' から被験者IDを抽出できませんでした。スキップします。")
            continue
        participant_id = match.group(1)
        
        survey_file = f'survey_{participant_id}.csv'
        
        print(f"--- 被験者ID: {participant_id} のデータを処理中 ---")
        print(f"行動データ: {behavior_file}")
        print(f"アンケートデータ: {survey_file}")

        if not os.path.exists(survey_file):
            print(f"警告: 対応するアンケートファイル '{survey_file}' が見つかりません。被験者 {participant_id} をスキップします。")
            continue

        try:
            # --- データの読み込み ---
            df_behavior = pd.read_csv(behavior_file)
            df_survey_raw = pd.read_csv(survey_file, encoding='utf-8')

            # --- アンケートデータの整形 ---
            tidy_data = []
            # アンケートデータは被験者ごとに複数行存在する可能性があるため、各行を処理
            for index, row in df_survey_raw.iterrows():
                # Google Formが自動的に付与する被験者の回答名を取得
                participant_form_name = row.iloc[1]
                for i in range(len(EXPERIMENT_TRIALS)):
                    perceived_time_col = 3 + (i * 2)
                    satisfaction_col = 4 + (i * 2)

                    if satisfaction_col < len(row):
                        tidy_data.append({
                            'participant_form_name': participant_form_name,
                            'trial_survey': i + 1,
                            'perceivedLoadingTime': row.iloc[perceived_time_col],
                            'satisfaction': row.iloc[satisfaction_col]
                        })
            df_survey_tidy = pd.DataFrame(tidy_data)
            
            # --- データの結合と整形 ---
            if len(df_behavior) != len(df_survey_tidy):
                print(f"警告: 被験者 {participant_id} の行動データ ({len(df_behavior)}行) とアンケートデータ ({len(df_survey_tidy)}行) の行数が一致しません。スキップします。")
                continue

            df_merged = df_behavior.reset_index().merge(df_survey_tidy.reset_index(), on='index')
            
            # 被験者ID列を追加
            df_merged['participant_id'] = participant_id

            all_participants_data.append(df_merged)

        except Exception as e:
            print(f"エラー: 被験者 {participant_id} のデータ処理中にエラーが発生しました: {e}")
            continue
            
    if not all_participants_data:
        print("統合できる有効なデータがありませんでした。処理を終了します。")
        return

    # 全被験者のデータを結合
    df_all = pd.concat(all_participants_data, ignore_index=True)
    
    # 満足度を数値に変換
    satisfaction_mapping = {'不満': 1, 'やや不満': 2, 'どちらでもない': 3, 'やや満足': 4, '満足': 5}
    df_all['satisfaction_score'] = df_all['satisfaction'].map(satisfaction_mapping)
    df_all['perceivedLoadingTime'] = pd.to_numeric(df_all['perceivedLoadingTime'], errors='coerce')
    
    # データ型を調整
    df_all['simulatedLoadingTime_sec'] = df_all['simulatedLoadingTime'] / 1000
    df_all['taskDuration_sec'] = df_all['taskDuration'] / 1000

    # 不要な列を整理
    final_columns = [
        'participant_id', 'trial', 'loaderType', 'simulatedLoadingTime', 
        'rageClicks', 'mouseDistance', 'taskDuration',
        'perceivedLoadingTime', 'satisfaction_score',
        'simulatedLoadingTime_sec', 'taskDuration_sec'
    ]
    # 'participant_form_name' のような中間列は除外
    df_final = df_all[[col for col in final_columns if col in df_all.columns]]

    # 欠損値を含む行を削除
    df_final.dropna(subset=['perceivedLoadingTime', 'satisfaction_score'], inplace=True)
    
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
