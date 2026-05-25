import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import scipy.stats as stats

def create_color_group(df):
    """
    'loaderType'に基づいて'colorGroup'列を作成する関数。
    'none'ローダーは分析対象外とする。
    """
    # 'none'ローダーを除外
    df_filtered = df[df['loaderType'] != 'none'].copy()

    # 色の有無を判定する関数
    def assign_color_group(loader_type):
        if 'color' in loader_type:
            return 'Color'
        else:
            return 'No Color'

    df_filtered['colorGroup'] = df_filtered['loaderType'].apply(assign_color_group)
    return df_filtered

def analyze_color_data(filepath):
    """
    統合済みの実験データ(all_data.csv)を読み込み、「色あり」vs「色なし」で分析する。
    """
    # --- 1. データの読み込み ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        print("ヒント: 先に consolidate_data.py を実行して 'all_data.csv' を生成しましたか？")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました - {e}")
        return

    # --- データの準備 ---
    # 'pureTaskDuration' を計算（もしなければ）
    if 'pureTaskDuration' not in df.columns and 'taskDuration' in df.columns and 'simulatedLoadingTime' in df.columns:
        df['pureTaskDuration'] = (df['taskDuration'] - df['simulatedLoadingTime']).clip(lower=0)

    # 色グループを作成
    df_analysis = create_color_group(df)
    
    if df_analysis.empty:
        print("分析対象のデータ（'none'ローダー以外）がありません。")
        return

    # 分析対象の指標を定義
    all_metrics = [
        'taskDuration', 'pureTaskDuration', 'mouseDistance', 'rageClicks',
        'perceivedLoadingTime', 'discomfort', 'reliability'
    ]
    # 存在する列のみにフィルタリング
    all_metrics = [m for m in all_metrics if m in df_analysis.columns]

    print("--- 「色あり」vs「色なし」グループの基本統計量 ---")
    print(df_analysis.groupby('colorGroup')[all_metrics].describe())
    print("\n" + "="*50 + "\n")

    # --- 2. 仮説検定 (t検定) ---
    print("--- 仮説検定: t検定 (Color vs No Color) ---")
    color_group_df = df_analysis[df_analysis['colorGroup'] == 'Color']
    no_color_group_df = df_analysis[df_analysis['colorGroup'] == 'No Color']

    for metric in all_metrics:
        # 両グループにデータが存在することを確認
        if color_group_df[metric].dropna().empty or no_color_group_df[metric].dropna().empty:
            print(f"{metric}: 片方または両方のグループにデータがないため、t検定をスキップします。")
            continue

        # Welch's t-test (不等分散を仮定)
        t_stat, p_val = stats.ttest_ind(color_group_df[metric], no_color_group_df[metric], equal_var=False, nan_policy='omit')
        print(f"{metric}: t値 = {t_stat:.4f}, p値 = {p_val:.4f}")
        if p_val < 0.05:
            print(f"  -> 統計的に有意な差が見られます。")
    print("\n" + "="*50 + "\n")

    # --- 3. 可視化 ---
    output_dir = 'color_analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"グラフは '{output_dir}' フォルダに保存されます。")

    sns.set_theme(style="whitegrid", font='Yu Gothic')
    
    # グラフ描画の設定
    plot_configs = {
        'taskDuration': {'title': '「色あり/なし」別 タスク時間', 'ylabel': 'タスク時間 (ms)'},
        'pureTaskDuration': {'title': '「色あり/なし」別 純粋なタスク時間', 'ylabel': '純粋なタスク時間 (ms)'},
        'mouseDistance': {'title': '「色あり/なし」別 マウス移動距離', 'ylabel': 'マウス移動距離 (pixels)'},
        'rageClicks': {'title': '「色あり/なし」別 平均レイジクリック数', 'ylabel': '平均レイジクリック数', 'plot_type': 'bar'},
        'perceivedLoadingTime': {'title': '「色あり/なし」別 体感読み込み時間', 'ylabel': '体感時間 (VAS評価 0-100)'},
        'discomfort': {'title': '「色あり/なし」別 不快感スコア', 'ylabel': '不快感スコア (1-5)'},
        'reliability': {'title': '「色あり/なし」別 信頼度スコア', 'ylabel': '信頼度スコア (1-5)'}
    }

    for metric, config in plot_configs.items():
        if metric not in df_analysis.columns:
            print(f"'{metric}' 列がデータにないため、グラフ作成をスキップします。")
            continue
            
        plt.figure(figsize=(8, 6))
        
        if config.get('plot_type') == 'bar':
            sns.barplot(data=df_analysis, x='colorGroup', y=metric, palette=['#4c72b0', '#55a868'], order=['No Color', 'Color'], ci=95)
        else:
            sns.boxplot(data=df_analysis, x='colorGroup', y=metric, palette=['#4c72b0', '#55a868'], order=['No Color', 'Color'])
            
        plt.title(config['title'], fontsize=16)
        plt.xlabel('ローダーのグループ', fontsize=12)
        plt.ylabel(config['ylabel'], fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{metric}_by_color_group.png'))
        plt.close()

    print("\n分析が完了しました。")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='統合済みの実験データ(all_data.csv)を「色あり」vs「色なし」で分析します。')
    parser.add_argument('filepath', type=str, default='all_data.csv', nargs='?',
                        help='分析するCSVファイルのパス (デフォルト: all_data.csv)')
    
    args = parser.parse_args()
    analyze_color_data(args.filepath)
