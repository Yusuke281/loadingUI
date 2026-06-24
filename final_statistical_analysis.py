import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pingouin as pg
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# --- 設定 ---
INPUT_FILENAME = 'all_data.csv'
OUTPUT_DIR = 'final_statistical_analysis_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォントと可視化のテーマ設定
plt.rcParams['font.family'] = 'Yu Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='Yu Gothic')

def write_report_header(f):
    f.write("# ローディングUI実験データ：最終統計分析レポート (決定版)\n\n")
    f.write("本レポートは、被験者データ（10名、総試行数210回）に対する、学術的厳密さと実務的UX意思決定を両立させた**「統合統計分析パッケージ」**の最終実行結果です。\n\n")
    f.write("## 分析ロードマップ\n")
    f.write("1. **【Step 1】前処理（個人内正規化）**：VAS主観評価値の個人バイアスの排除\n")
    f.write("2. **【Step 2】前提検証（球面性のチェック）**：RM-ANOVAの前提検証とGreenhouse-Geisser補正の適用要否判断\n")
    f.write("3. **【Step 3】主検定（二元配置RM-ANOVA）**：ローダー種類と待ち時間が心理指標に与える影響の全体的検証\n")
    f.write("4. **【Step 4】事後検定（多重比較）**：\n")
    f.write("   - **統計的厳密版**：対応のあるt検定 ＋ **Holm補正** (待ち時間別＆プール全体)\n")
    f.write("   - **実務的可視化版**：**TukeyのHSD法**による同時信頼区間の推定 (待ち時間別＆プール全体)\n")
    f.write("5. **【Step 5】行動・心理分析（混合効果モデル：LMM）**：個人差を制御したUI効果量と行動影響の定量推定\n\n")
    f.write("---\n\n")

def run_final_analysis():
    print("--- 決定版 統合統計分析スクリプトを開始します ---")
    
    # データの読み込み
    try:
        df = pd.read_csv(INPUT_FILENAME)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_FILENAME}' が見つかりません。")
        return
    
    # レポートファイルの作成
    report_path = os.path.join(OUTPUT_DIR, 'final_analysis_report.md')
    report_file = open(report_path, 'w', encoding='utf-8')
    write_report_header(report_file)
    
    psych_metrics = ['perceivedLoadingTime', 'discomfort', 'reliability']
    behavioral_metrics = ['rageClicks', 'mouseDistance', 'taskDuration_sec']
    
    # ==========================================
    # 【Step 1】前処理：個人内正規化
    # ==========================================
    print("\n[Step 1] 主観評価の個人内正規化を実行中...")
    report_file.write("## 1. 【Step 1】前処理：主観評価（VAS）の「個人内正規化」\n\n")
    report_file.write("VAS評価値の個人特有の回答基準（甘さ・辛さ・評価の振れ幅）を取り除き、条件間の差を純粋に評価するため、被験者（`participant_id`）ごとに平均0、標準偏差1とする**個人内正規化（Zスコア化）**を心理指標に施しました。\n\n")
    
    df_norm = df.copy()
    for col in psych_metrics:
        mean_by_p = df_norm.groupby('participant_id')[col].transform('mean')
        std_by_p = df_norm.groupby('participant_id')[col].transform('std')
        df_norm[f'{col}_z'] = (df_norm[col] - mean_by_p) / (std_by_p + 1e-9)
        
    for col in behavioral_metrics:
        df_norm[f'{col}_z'] = (df_norm[col] - df_norm[col].mean()) / (df_norm[col].std() + 1e-9)
        
    # 正規化データの保存
    normalized_csv_path = os.path.join(OUTPUT_DIR, 'consolidated_normalized_data_10p.csv')
    df_norm.to_csv(normalized_csv_path, index=False)
    report_file.write(f"正規化カラムを含む統合データシートを保存しました: `consolidated_normalized_data_10p.csv`  \n")
    
    # 正規化比較プロットの作成
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    for i, col in enumerate(psych_metrics):
        sns.histplot(data=df_norm, x=col, hue='participant_id', kde=True, ax=axes[i, 0], legend=False, palette='tab10', alpha=0.3)
        axes[i, 0].set_title(f'{col} の生データ分布 (被験者別)')
        axes[i, 0].set_xlabel('生値 (VASスケール)')
        
        sns.histplot(data=df_norm, x=f'{col}_z', hue='participant_id', kde=True, ax=axes[i, 1], legend=False, palette='tab10', alpha=0.3)
        axes[i, 1].set_title(f'{col} の個人内正規化後分布 (Zスコア)')
        axes[i, 1].set_xlabel('Zスコア')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'step1_normalization_comparison.png'))
    plt.close()
    report_file.write("正規化前後のデータ分布比較プロットを保存しました: `step1_normalization_comparison.png`  \n\n")
    report_file.write("---\n\n")
    
    # ==========================================
    # 【Step 2】前提検証：「球面性の仮定」
    # ==========================================
    print("[Step 2] 球面性の仮定の検証を実行中...")
    report_file.write("## 2. 【Step 2】前提検証：「球面性の仮定」のチェック\n\n")
    report_file.write("反復測定分散分析の適用前提である球面性の仮定（水準間の差の分散の均一性）を検証するため、**Mauchlyの球面性検定（Mauchly's Test of Sphericity）**を実行しました。有意（$p < 0.05$）となった場合、検定統計量のバイアスを防ぐため、主検定において**Greenhouse-Geisser (GG) 補正**を適用します。\n\n")
    
    anova_results = {}
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        report_file.write(f"### 指標: {col} (Zスコア)\n")
        
        try:
            spher_loader, _, chi2_loader, dof_loader, p_loader = pg.sphericity(
                data=df_norm, dv=col_z, within='loaderType', subject='participant_id'
            )
            report_file.write(f"- **loaderType要因** (水準数 7):\n")
            report_file.write(f"  - 球面性の仮定が満たされるか: {spher_loader}\n")
            report_file.write(f"  - $\chi^2$: {chi2_loader:.4f}, dof: {dof_loader}, p値: {p_loader:.4e} {'(GG補正が必要)' if p_loader < 0.05 else '(球面性を維持)'}\n")
        except Exception as e:
            report_file.write(f"- **loaderType要因**: 球面性検定エラー ({e})\n")
            
        try:
            spher_time, _, chi2_time, dof_time, p_time = pg.sphericity(
                data=df_norm, dv=col_z, within='simulatedLoadingTime', subject='participant_id'
            )
            report_file.write(f"- **simulatedLoadingTime要因** (水準数 3):\n")
            report_file.write(f"  - 球面性の仮定が満たされるか: {spher_time}\n")
            report_file.write(f"  - $\chi^2$: {chi2_time:.4f}, dof: {dof_time}, p値: {p_time:.4e} {'(GG補正が必要)' if p_time < 0.05 else '(球面性を維持)'}\n")
        except Exception as e:
            report_file.write(f"- **simulatedLoadingTime要因**: 球面性検定エラー ({e})\n")
        report_file.write("\n")
        
    report_file.write("---\n\n")
    
    # ==========================================
    # 【Step 3】主検定：二元配置RM-ANOVA
    # ==========================================
    print("[Step 3] 二元配置RM-ANOVAを実行中...")
    report_file.write("## 3. 【Step 3】主検定：「二元配置反復測定分散分析（Two-Way RM-ANOVA）」\n\n")
    report_file.write("被験者内要因として**ローダータイプ (`loaderType` : 7水準)**および**待ち時間 (`simulatedLoadingTime` : 3水準)**を設定し、心理指標に対する二元配置反復測定分散分析を行いました。球面性の仮定が棄却された効果には、自動的にGreenhouse-Geisser補正されたp値（`p_GG_corr`）を採用します。\n\n")
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        report_file.write(f"### 目的変数: {col} (個人内正規化Zスコア)\n")
        
        aov = pg.rm_anova(
            data=df_norm, dv=col_z, 
            within=['loaderType', 'simulatedLoadingTime'], 
            subject='participant_id', detailed=True
        )
        anova_results[col] = aov
        
        # 結果のテーブル表示
        report_file.write(aov.to_markdown(index=False) + "\n\n")
        
        # 交互作用プロットの作成
        plt.figure(figsize=(11, 7))
        df_plot = df_norm.copy()
        df_plot['simulatedLoadingTime_label'] = df_plot['simulatedLoadingTime_sec'].apply(lambda x: f"{x}秒")
        sns.pointplot(
            data=df_plot, x='loaderType', y=col_z, hue='simulatedLoadingTime_label',
            dodge=0.2, markers=['o', 's', 'D'], linestyles=['-', '--', ':'],
            errorbar='ci', palette='muted'
        )
        plt.title(f'ローダー種類と待ち時間の交互作用プロット ({col} Zスコア)', fontsize=14)
        plt.xlabel('ローダーの種類 (loaderType)', fontsize=12)
        plt.ylabel(f'{col} (個人内Zスコア)', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='待ち時間 (秒)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        fig_path = os.path.join(OUTPUT_DIR, f'step3_interaction_plot_{col}.png')
        plt.savefig(fig_path)
        plt.close()
        report_file.write(f"交互作用プロットを保存しました: `step3_interaction_plot_{col}.png`  \n\n")
        
    report_file.write("---\n\n")
    
    # ==========================================
    # 【Step 4】事後検定：多重比較
    # ==========================================
    print("[Step 4] 事後検定（Holm & Tukey）を実行中...")
    report_file.write("## 4. 【Step 4】事後検定：「多重比較（Post-hoc Test）」と読み込み時間別分析\n\n")
    report_file.write("本ステップでは、学術的に厳密な**「対応のあるt検定 ＋ Holm補正」**と、実務的に直感的な**「TukeyのHSD法」**の2つのアプローチを実行しました。\n\n")
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        aov = anova_results[col]
        
        # p値の抽出
        p_loader = aov.loc[aov['Source'] == 'loaderType', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'loaderType', 'p_GG_corr'].values[0]):
            p_loader = aov.loc[aov['Source'] == 'loaderType', 'p_GG_corr'].values[0]
        p_time = aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_GG_corr'].values[0]):
            p_time = aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_GG_corr'].values[0]
        p_inter = aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_GG_corr'].values[0]):
            p_inter = aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_GG_corr'].values[0]
            
        report_file.write(f"### 目的変数: {col}\n")
        report_file.write(f"- 主効果 (loaderType): p = {p_loader:.4f} ({'有意' if p_loader < 0.05 else '有意ではない'})\n")
        report_file.write(f"- 主効果 (simulatedLoadingTime): p = {p_time:.4f} ({'有意' if p_time < 0.05 else '有意ではない'})\n")
        report_file.write(f"- 交互作用: p = {p_inter:.4f} ({'有意' if p_inter < 0.05 else '有意ではない'})\n\n")
        
        # ------------------------------------------
        # 4-1. 統計的厳密版: 対応のあるt-test + Holm補正
        # ------------------------------------------
        report_file.write("#### 4-1. 統計的厳密版：対応のあるt検定 ＋ Holm補正\n\n")
        report_file.write("被験者内デザインを厳密に考慮し、対応のあるt検定にHolmの多重比較補正を適用しました。\n\n")
        
        # 待ち時間別のHolm多重比較
        holm_by_time_list = []
        times = sorted(df_norm['simulatedLoadingTime'].unique())
        for t_val in times:
            t_sec = t_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == t_val]
            ph_holm = pg.pairwise_tests(
                data=sub_df, dv=col_z, within='loaderType', 
                subject='participant_id', padjust='holm'
            )
            ph_holm['simulatedLoadingTime_sec'] = t_sec
            holm_by_time_list.append(ph_holm)
            
            ph_holm_sig = ph_holm[ph_holm['p_corr'] < 0.05]
            report_file.write(f"##### 待ち時間: {t_sec}秒 におけるペア比較 (Holm補正)\n")
            if not ph_holm_sig.empty:
                report_file.write(ph_holm_sig[['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']].to_markdown(index=False) + "\n\n")
            else:
                ph_sorted = ph_holm.sort_values(by='p_corr').head(2)
                report_file.write(f"Holm補正後に有意な差は認められませんでした。以下は傾向のあるペア（上位2ペア）です：\n\n")
                report_file.write(ph_sorted[['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']].to_markdown(index=False) + "\n\n")
                
        df_holm_time_all = pd.concat(holm_by_time_list, ignore_index=True)
        df_holm_time_all.to_csv(os.path.join(OUTPUT_DIR, f'step4_posthoc_holm_by_time_{col}.csv'), index=False)
        
        # 全体プールのHolm多重比較 (主効果用)
        if p_loader < 0.05:
            report_file.write("##### 全体プール（主効果）におけるペア比較 (Holm補正)\n\n")
            ph_holm_overall = pg.pairwise_tests(
                data=df_norm, dv=col_z, within='loaderType', 
                subject='participant_id', padjust='holm'
            )
            ph_holm_overall.to_csv(os.path.join(OUTPUT_DIR, f'step4_posthoc_holm_overall_{col}.csv'), index=False)
            ph_holm_overall_sig = ph_holm_overall[ph_holm_overall['p_corr'] < 0.05]
            if not ph_holm_overall_sig.empty:
                report_file.write(ph_holm_overall_sig[['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']].to_markdown(index=False) + "\n\n")
            else:
                ph_sorted_ov = ph_holm_overall.sort_values(by='p_corr').head(2)
                report_file.write("Holm補正後に有意な差は認められませんでした。以下は傾向のあるペアです：\n\n")
                report_file.write(ph_sorted_ov[['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']].to_markdown(index=False) + "\n\n")
                
        # ------------------------------------------
        # 4-2. 実務的可視化版: TukeyのHSD
        # ------------------------------------------
        report_file.write("#### 4-2. 実務的可視化版：TukeyのHSD法 (同時信頼区間の推定)\n\n")
        report_file.write("ファミリーワイズエラー率を制御しながら、同時信頼区間の広がりを可視化するため、TukeyのHSD法を実行しました。\n\n")
        
        # 全体プールTukey
        tukey_overall = pairwise_tukeyhsd(endog=df_norm[col_z], groups=df_norm['loaderType'], alpha=0.05)
        tukey_ov_data = tukey_overall.summary().data
        df_tukey_overall = pd.DataFrame(tukey_ov_data[1:], columns=tukey_ov_data[0])
        df_tukey_overall.to_csv(os.path.join(OUTPUT_DIR, f'step4_posthoc_tukey_overall_{col}.csv'), index=False)
        
        df_tukey_ov_sig = df_tukey_overall[df_tukey_overall['reject'] == True]
        report_file.write("##### 全体プールにおけるTukey HSD有意ペア\n")
        if not df_tukey_ov_sig.empty:
            report_file.write(df_tukey_ov_sig[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
        else:
            report_file.write("全体比較においてTukey HSDで有意な差はありませんでした。以下は上位2ペアです：\n\n")
            report_file.write(df_tukey_overall.sort_values(by='p-adj').head(2)[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
            
        # Tukey全体フォレストプロットの作成
        plt.figure(figsize=(12, 8))
        y_pos = np.arange(len(df_tukey_overall))
        colors = ['red' if r else 'royalblue' for r in df_tukey_overall['reject']]
        for idx, row in df_tukey_overall.iterrows():
            lower_err = row['meandiff'] - row['lower']
            upper_err = row['upper'] - row['meandiff']
            plt.errorbar(
                x=row['meandiff'], y=idx, 
                xerr=np.array([[lower_err], [upper_err]]),
                fmt='o', color=colors[idx], ecolor='lightgray', elinewidth=2, capsize=3
            )
        plt.axvline(0, color='darkred', linestyle='--', alpha=0.7)
        plt.yticks(y_pos, df_tukey_overall['group1'] + ' vs ' + df_tukey_overall['group2'], fontsize=9)
        plt.title(f'Tukey HSD 全体比較 信頼区間 ({col} Zスコア)', fontsize=14)
        plt.xlabel('平均値の差 (95% 同時信頼区間付き)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'step4_tukey_overall_forest_plot_{col}.png'))
        plt.close()
        report_file.write(f"Tukeyの同時信頼区間プロット（フォレストプロット）を保存しました: `step4_tukey_overall_forest_plot_{col}.png`  \n")
        
        # 待ち時間別のTukey HSD
        tukey_by_time_list = []
        for t_val in times:
            t_sec = t_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == t_val]
            tukey_t = pairwise_tukeyhsd(endog=sub_df[col_z], groups=sub_df['loaderType'], alpha=0.05)
            t_data = tukey_t.summary().data
            df_t_time = pd.DataFrame(t_data[1:], columns=t_data[0])
            df_t_time['simulatedLoadingTime_sec'] = t_sec
            tukey_by_time_list.append(df_t_time)
            
            df_t_sig = df_t_time[df_t_time['reject'] == True]
            report_file.write(f"##### 待ち時間: {t_sec}秒 におけるTukey HSD有意ペア\n")
            if not df_t_sig.empty:
                report_file.write(df_t_sig[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
            else:
                report_file.write("有意な差はありませんでした。以下は上位2ペアです：\n\n")
                report_file.write(df_t_time.sort_values(by='p-adj').head(2)[['group1', 'group2', 'meandiff', 'p-adj', 'lower', 'upper']].to_markdown(index=False) + "\n\n")
                
        df_tukey_time_all = pd.concat(tukey_by_time_list, ignore_index=True)
        df_tukey_time_all.to_csv(os.path.join(OUTPUT_DIR, f'step4_posthoc_tukey_by_time_{col}.csv'), index=False)
        
        # 読み込み時間別の詳細比較プロット
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        for idx, t_val in enumerate(times):
            t_sec = t_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == t_val]
            sns.barplot(data=sub_df, x='loaderType', y=col_z, ax=axes[idx], errorbar='ci', palette='viridis', alpha=0.85)
            axes[idx].set_title(f"待ち時間: {t_sec}秒", fontsize=14)
            axes[idx].set_xlabel('ローダーの種類', fontsize=12)
            if idx == 0:
                axes[idx].set_ylabel(f'{col} (個人内Zスコア)', fontsize=12)
            else:
                axes[idx].set_ylabel('')
            axes[idx].tick_params(axis='x', rotation=45)
            axes[idx].grid(True, linestyle='--', alpha=0.5)
        plt.suptitle(f'読み込み時間別 ローダーの比較 ({col} Zスコア)', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'step4_time_specific_comparison_{col}.png'))
        plt.close()
        report_file.write(f"読み込み時間別の比較プロットを保存しました: `step4_time_specific_comparison_{col}.png`  \n\n")
        report_file.write("---\n\n")
        
    # ==========================================
    # 【Step 5】行動・心理分析：線形混合効果モデル (LMM)
    # ==========================================
    print("[Step 5] 混合効果モデル(LMM)の分析を実行中...")
    report_file.write("## 5. 【Step 5】行動・心理分析：「混合効果モデル（LMM）」によるメカニズム解明\n\n")
    report_file.write("被験者の個人差（ランダム切片）を制御し、実験要因（ローダーの種類、実際の待ち時間）と操作行動（マウス移動距離）が心理的評価（不快感、信頼度）に与える定量的影響（効果量）を混合効果モデル（LMM）で推計しました。\n\n")
    
    for target in ['discomfort', 'reliability']:
        target_z = f'{target}_z'
        report_file.write(f"### モデル: 目的変数 = {target} (個人内Zスコア)\n")
        
        # 固定効果変数の動的構築
        fixed_effects = ["C(loaderType, Treatment('none'))", "simulatedLoadingTime_sec"]
        excluded_features = []
        for feat, label in [('rageClicks_z', 'レイジクリック数 (rageClicks)'), ('mouseDistance_z', 'マウス移動距離 (mouseDistance)')]:
            if df_norm[feat].var() > 1e-5:
                fixed_effects.append(feat)
            else:
                excluded_features.append(label)
                
        formula = f"{target_z} ~ " + " + ".join(fixed_effects)
        
        if excluded_features:
            report_file.write(f"> [!NOTE]  \n")
            report_file.write(f"> 以下の行動指標はすべての試行において値が一定（または分散が極めて小さい）であったため、多重共線性を避けるためにモデルから除外されました: {', '.join(excluded_features)}  \n\n")
            
        try:
            model = smf.mixedlm(formula, data=df_norm, groups=df_norm['participant_id'])
            result = model.fit()
            
            # 結果要約テキストの保存
            summary_txt_path = os.path.join(OUTPUT_DIR, f'step5_lmm_summary_{target}.txt')
            with open(summary_txt_path, 'w', encoding='utf-8') as sf:
                sf.write(result.summary().as_text())
                
            params_df = pd.DataFrame({
                'Coef.': result.params,
                'Std.Err.': result.bse,
                'z': result.tvalues,
                'P>|z|': result.pvalues
            }).drop('Group Var')
            
            params_df['P>|z|'] = params_df['P>|z|'].apply(lambda x: f"{x:.4f}" if x >= 0.0001 else "<0.0001")
            params_df = params_df.reset_index().rename(columns={'index': 'Predictor'})
            
            params_df['Predictor'] = params_df['Predictor'].str.replace("C(loaderType, Treatment('none'))[T.", "loaderType: ", regex=False)
            params_df['Predictor'] = params_df['Predictor'].str.replace("]", "", regex=False)
            
            report_file.write(params_df.to_markdown(index=False) + "\n\n")
            
            # 係数フォレストプロットの描画
            plot_params = params_df[params_df['Predictor'] != 'Intercept'].copy()
            plot_params['Coef.'] = pd.to_numeric(plot_params['Coef.'])
            plot_params['Std.Err.'] = pd.to_numeric(plot_params['Std.Err.'])
            
            plt.figure(figsize=(10, 6))
            plt.errorbar(
                x=plot_params['Coef.'], y=plot_params['Predictor'], 
                xerr=1.96 * plot_params['Std.Err.'], fmt='o', color='royalblue', 
                ecolor='lightcoral', elinewidth=2, capsize=4, ms=8
            )
            plt.axvline(0, color='red', linestyle='--', alpha=0.7)
            plt.title(f'混合効果モデルの固定効果係数 ({target} Zスコアへの影響)', fontsize=14)
            plt.xlabel('固定効果係数 (95% 信頼区間付き)', fontsize=12)
            plt.ylabel('説明変数', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            fig_path = os.path.join(OUTPUT_DIR, f'step5_lmm_coefficients_{target}.png')
            plt.savefig(fig_path)
            plt.close()
            
            report_file.write(f"固定効果係数の信頼区間プロット（フォレストプロット）を保存しました: `step5_lmm_coefficients_{target}.png`  \n")
            report_file.write("※赤い縦の破線(0)をまたいでいない変数（95%信頼区間に0を含まないもの）が、統計的に有意な影響を持つ説明変数です。\n\n")
            
        except Exception as e:
            report_file.write(f"混合効果モデルの分析中にエラーが発生しました: {e}\n\n")
            print(f"LMMエラー ({target}): {e}")
            
    report_file.close()
    print("--- 統合統計分析が完了しました。レポートが生成されました ---")
    print(f"レポートファイル: {report_path}")

if __name__ == '__main__':
    run_final_analysis()
