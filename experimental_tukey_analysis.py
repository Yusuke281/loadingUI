import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# --- 設定 ---
INPUT_FILENAME = 'all_data.csv'
OUTPUT_DIR = 'tukey_hsd_analysis_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォントの設定
plt.rcParams['font.family'] = 'Yu Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='Yu Gothic')

def write_report_header(f):
    f.write("# TukeyのHSD法による多重比較分析レポート\n\n")
    f.write("このレポートは、実験データ（被験者10名、総試行数210回）に対し、多重比較として**TukeyのHSD（Honestly Significant Difference）法**を適用し、全体および読み込み時間別で分析した結果をまとめたものです。\n\n")
    f.write("## 分析の構成\n")
    f.write("1. **【前処理】** 主観評価（VAS）の「個人内正規化」\n")
    f.write("2. **【全体プール分析】** 全待ち時間のデータを統合した、ローダータイプ間のTukey HSD比較\n")
    f.write("3. **【読み込み時間別分析】** 待ち時間（1.0秒 / 2.5秒 / 5.0秒）ごとの、ローダータイプ間のTukey HSD比較\n\n")
    f.write("---\n\n")

def run_tukey_analysis():
    print("--- TukeyのHSD分析スクリプトを開始します ---")
    
    # データの読み込み
    try:
        df = pd.read_csv(INPUT_FILENAME)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_FILENAME}' が見つかりません。")
        return
    
    # レポートファイルの作成
    report_path = os.path.join(OUTPUT_DIR, 'tukey_analysis_report.md')
    report_file = open(report_path, 'w', encoding='utf-8')
    write_report_header(report_file)
    
    # 心理指標と行動指標の定義
    psych_metrics = ['perceivedLoadingTime', 'discomfort', 'reliability']
    
    # 個人内正規化 (Zスコア)
    df_norm = df.copy()
    for col in psych_metrics:
        df_norm[f'{col}_z'] = df_norm.groupby('participant_id')[col].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-9)
        )
        
    report_file.write("## 【前処理】主観評価（VAS）の「個人内正規化」\n\n")
    report_file.write("被験者間の絶対的な主観基準のブレを排除するため、前回の分析と同様に、各被験者（`participant_id`）の心理評価値に対して平均0、標準偏差1とする**個人内正規化（Zスコア化）**を施したデータを用いてTukeyのHSD検定を実行しました。\n\n")
    report_file.write("---\n\n")
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        report_file.write(f"## 目的変数: {col} (個人内Zスコア)\n\n")
        
        # ==========================================
        # 1. 全体プールでのTukey HSD
        # ==========================================
        report_file.write("### 1. 全体プール分析（全待ち時間を統合した比較）\n\n")
        report_file.write("すべての待ち時間のデータをプールし、ローダータイプ間の全体的な影響の差をTukeyのHSD法で検定しました。\n\n")
        
        # Tukey HSDの実行
        tukey_overall = pairwise_tukeyhsd(endog=df_norm[col_z], groups=df_norm['loaderType'], alpha=0.05)
        
        # 結果をデータフレーム化
        data_overall = tukey_overall.summary().data
        df_tukey_overall = pd.DataFrame(data_overall[1:], columns=data_overall[0])
        
        # CSVファイルへ保存
        csv_path_overall = os.path.join(OUTPUT_DIR, f'tukey_overall_{col}.csv')
        df_tukey_overall.to_csv(csv_path_overall, index=False)
        
        # 有意なペアの抽出
        df_sig_overall = df_tukey_overall[df_tukey_overall['reject'] == True].copy()
        
        if not df_sig_overall.empty:
            report_file.write("TukeyのHSD検定により、以下のペアにおいて**統計的に有意な差（$p < 0.05$）**が認められました：\n\n")
            report_file.write(df_sig_overall[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
        else:
            report_file.write("TukeyのHSD検定による全体比較では、統計的有意差に達したペアはありませんでした。以下は比較的差異が大きかったペア（上位3ペア）です：\n\n")
            df_sorted_overall = df_tukey_overall.sort_values(by='p-adj').head(3)
            report_file.write(df_sorted_overall[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
            
        # 全体プールのフォレストプロット（差と信頼区間）の作成
        plt.figure(figsize=(12, 8))
        # 信頼区間のエラーバーを描画
        y_positions = np.arange(len(df_tukey_overall))
        # rejectがTrueのものは色を変える
        colors = ['red' if r else 'royalblue' for r in df_tukey_overall['reject']]
        
        # エラーバーの描画
        for idx, row in df_tukey_overall.iterrows():
            lower_err = row['meandiff'] - row['lower']
            upper_err = row['upper'] - row['meandiff']
            plt.errorbar(
                x=row['meandiff'], y=idx, 
                xerr=np.array([[lower_err], [upper_err]]),
                fmt='o', color=colors[idx], ecolor='lightgray', elinewidth=2, capsize=3
            )
            
        plt.axvline(0, color='darkred', linestyle='--', alpha=0.7)
        plt.yticks(y_positions, df_tukey_overall['group1'] + ' vs ' + df_tukey_overall['group2'], fontsize=9)
        plt.title(f'Tukey HSD 全体比較 信頼区間 ({col} Zスコア)', fontsize=14)
        plt.xlabel('平均値の差 (95% 同時信頼区間付き)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        plot_path_overall = os.path.join(OUTPUT_DIR, f'tukey_overall_forest_plot_{col}.png')
        plt.savefig(plot_path_overall)
        plt.close()
        report_file.write(f"全体プールの信頼区間プロット（フォレストプロット）を保存しました: `tukey_overall_forest_plot_{col}.png`  \n\n")
        
        # ==========================================
        # 2. 読み込み時間別のTukey HSD
        # ==========================================
        report_file.write("### 2. 読み込み時間（待ち時間）別のTukey HSD分析\n\n")
        report_file.write("各待ち時間（1.0秒 / 2.5秒 / 5.0秒）ごとにデータをスライスし、ローダータイプ間のTukey HSD検定を行いました。\n\n")
        
        times = sorted(df_norm['simulatedLoadingTime'].unique())
        posthoc_by_time = []
        
        for time_val in times:
            time_sec = time_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == time_val]
            
            # Tukey HSDの実行
            tukey_time = pairwise_tukeyhsd(endog=sub_df[col_z], groups=sub_df['loaderType'], alpha=0.05)
            data_time = tukey_time.summary().data
            df_tukey_time = pd.DataFrame(data_time[1:], columns=data_time[0])
            df_tukey_time['simulatedLoadingTime_sec'] = time_sec
            posthoc_by_time.append(df_tukey_time)
            
            # 有意なペアの抽出
            df_sig_time = df_tukey_time[df_tukey_time['reject'] == True].copy()
            
            report_file.write(f"#### 待ち時間: {time_sec}秒 における多重比較\n")
            if not df_sig_time.empty:
                report_file.write(f"{time_sec}秒の待ち時間において、以下のペアで**有意な差**が検出されました：\n\n")
                report_file.write(df_sig_time[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
            else:
                report_file.write(f"{time_sec}秒の待ち時間において、統計的有意差に達したペアはありませんでした。以下は比較的差異が大きかったペア（上位3ペア）です：\n\n")
                df_sorted_time = df_tukey_time.sort_values(by='p-adj').head(3)
                report_file.write(df_sorted_time[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
                
        df_tukey_time_all = pd.concat(posthoc_by_time, ignore_index=True)
        csv_path_time = os.path.join(OUTPUT_DIR, f'tukey_by_time_{col}.csv')
        df_tukey_time_all.to_csv(csv_path_time, index=False)
        report_file.write(f"すべての時間別のTukey HSD結果は `{os.path.basename(csv_path_time)}` に保存しました。\n\n")
        
        # 読み込み時間別の平均値プロット (1.0s, 2.5s, 5.0s の3枚パネル、95% CI付き)
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        for idx, time_val in enumerate(times):
            time_sec = time_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == time_val]
            
            # 各時間でのローダー別の平均値と信頼区間
            sns.barplot(
                data=sub_df, x='loaderType', y=col_z, ax=axes[idx],
                errorbar='ci', palette='viridis', alpha=0.85
            )
            axes[idx].set_title(f"待ち時間: {time_sec}秒", fontsize=14)
            axes[idx].set_xlabel('ローダーの種類', fontsize=12)
            if idx == 0:
                axes[idx].set_ylabel(f'{col} (個人内Zスコア)', fontsize=12)
            else:
                axes[idx].set_ylabel('')
            axes[idx].tick_params(axis='x', rotation=45)
            axes[idx].grid(True, linestyle='--', alpha=0.5)
            
        plt.suptitle(f'TukeyのHSD分析に基づく読み込み時間別 ローダーの比較 ({col} Zスコア)', fontsize=16)
        plt.tight_layout()
        time_plot_path = os.path.join(OUTPUT_DIR, f'tukey_time_specific_comparison_{col}.png')
        plt.savefig(time_plot_path)
        plt.close()
        
        report_file.write(f"読み込み時間別の詳細な比較プロットを保存しました: `tukey_time_specific_comparison_{col}.png`  \n\n")
        report_file.write("---\n\n")
        
    report_file.close()
    print("--- TukeyのHSD分析が完了しました。レポートが生成されました ---")
    print(f"レポートファイル: {os.path.join(OUTPUT_DIR, 'tukey_analysis_report.md')}")

if __name__ == '__main__':
    run_tukey_analysis()
