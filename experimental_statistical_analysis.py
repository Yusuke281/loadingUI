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
OUTPUT_DIR = 'statistical_analysis_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォントの設定
plt.rcParams['font.family'] = 'Yu Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='Yu Gothic')

def write_report_header(f):
    f.write("# 実験データ統計分析レポート (高度な5ステップ分析)\n\n")
    f.write("このレポートは、実験データのロードマップに従って実行された詳細な統計分析の結果をまとめたものです。\n\n")
    f.write("## 分析ロードマップ\n")
    f.write("1. **【Step 1】前処理**：主観評価（VAS）の「個人内正規化」\n")
    f.write("2. **【Step 2】前提検証**：「球面性の仮定」のチェック\n")
    f.write("3. **【Step 3】主検定**：「二元配置反復測定分散分析（Two-Way RM-ANOVA）」\n")
    f.write("4. **【Step 4】事後検定**：「多重比較（Post-hoc Test）」による条件間の特定および読み込み時間別分析\n")
    f.write("5. **【Step 5】行動・心理分析**：「混合効果モデル（LMM）」によるメカニズム解明\n\n")
    f.write("---\n\n")

def run_analysis():
    print("--- 統計分析スクリプトを開始します ---")
    
    # データの読み込み
    try:
        df = pd.read_csv(INPUT_FILENAME)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_FILENAME}' が見つかりません。")
        return
    
    # レポートファイルの作成
    report_path = os.path.join(OUTPUT_DIR, 'analysis_report.md')
    report_file = open(report_path, 'w', encoding='utf-8')
    write_report_header(report_file)
    
    # 心理指標と行動指標の定義
    psych_metrics = ['perceivedLoadingTime', 'discomfort', 'reliability']
    behavioral_metrics = ['rageClicks', 'mouseDistance', 'taskDuration_sec']
    
    # ==========================================
    # 【Step 1】前処理：主観評価（VAS）の「個人内正規化」
    # ==========================================
    print("\n[Step 1] 主観評価の個人内正規化を実行中...")
    report_file.write("## 【Step 1】前処理：主観評価（VAS）の「個人内正規化」\n\n")
    report_file.write("主観評価値（VAS）は被験者ごとに評価基準やスケールの使い方が異なる（個人内バイアスがある）ため、被験者ごとに平均0、標準偏差1とする**個人内正規化（Ipsative Standardization / Zスコア化）**を適用しました。これにより、被験者間の絶対値のズレを排し、純粋な条件間の差異を検出します。\n\n")
    
    df_norm = df.copy()
    
    # 心理指標の個人内正規化 (Zスコア)
    for col in psych_metrics:
        # 被験者ごとの平均・標準偏差でZスコア化
        df_norm[f'{col}_z'] = df_norm.groupby('participant_id')[col].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-9)
        )
    
    # 行動指標の全体標準化 (モデル用にスケールを合わせるため)
    for col in behavioral_metrics:
        df_norm[f'{col}_z'] = (df_norm[col] - df_norm[col].mean()) / (df_norm[col].std() + 1e-9)
        
    # 正規化前後の分布比較プロットの作成
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    for i, col in enumerate(psych_metrics):
        # 正規化前
        sns.histplot(data=df_norm, x=col, hue='participant_id', kde=True, ax=axes[i, 0], legend=False, palette='tab10', alpha=0.3)
        axes[i, 0].set_title(f'{col} の生データ分布 (被験者別)')
        axes[i, 0].set_xlabel('生値 (0-100 または VASスケール)')
        
        # 正規化後
        sns.histplot(data=df_norm, x=f'{col}_z', hue='participant_id', kde=True, ax=axes[i, 1], legend=False, palette='tab10', alpha=0.3)
        axes[i, 1].set_title(f'{col} の個人内正規化後分布 (Zスコア)')
        axes[i, 1].set_xlabel('Zスコア')
        
    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, 'step1_normalization_comparison.png')
    plt.savefig(plot_path)
    plt.close()
    
    report_file.write(f"正規化前後のデータ分布比較プロットを保存しました: `step1_normalization_comparison.png`  \n")
    report_file.write("※プロットでは、被験者ごとに異なる色で分布を示しています。正規化後は被験者の分布が平均0、分散1に揃っていることがわかります。\n\n")
    report_file.write("---\n\n")
    
    # ==========================================
    # 【Step 2】前提検証：「球面性の仮定」のチェック
    # ==========================================
    print("[Step 2] 球面性の仮定の検証を実行中...")
    report_file.write("## 【Step 2】前提検証：「球面性の仮定」のチェック\n\n")
    report_file.write("反復測定分散分析（RM-ANOVA）を適用するにあたり、条件間の差の分散が均一であるという**「球面性の仮定（Sphericity Assumption）」**を満たしているかを検証するため、**Mauchlyの球面性検定（Mauchly's Test of Sphericity）**を実行しました。\n\n")
    report_file.write("Mauchlyの検定で $p < 0.05$（有意）となった場合は球面性の仮定が棄却されるため、**Greenhouse-Geisser (GG) 補正**を適用して自由度を調整し、F値およびp値を補正します。\n\n")
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        report_file.write(f"### 指標: {col} (Zスコア)\n")
        
        # loaderType 要因 (水準数 7) の球面性検定
        try:
            spher_loader, _, chi2_loader, dof_loader, p_loader = pg.sphericity(
                data=df_norm, dv=col_z, within='loaderType', subject='participant_id'
            )
            report_file.write(f"- **loaderType要因**:\n")
            report_file.write(f"  - 球面性の仮定が満たされるか: {spher_loader}\n")
            report_file.write(f"  - $\chi^2$値: {chi2_loader:.4f}, 自由度: {dof_loader}, p値: {p_loader:.4e}\n")
        except Exception as e:
            report_file.write(f"- **loaderType要因**: 球面性検定の実行に失敗しました ({e})\n")
            
        # simulatedLoadingTime 要因 (水準数 3) の球面性検定
        try:
            spher_time, _, chi2_time, dof_time, p_time = pg.sphericity(
                data=df_norm, dv=col_z, within='simulatedLoadingTime', subject='participant_id'
            )
            report_file.write(f"- **simulatedLoadingTime要因**:\n")
            report_file.write(f"  - 球面性の仮定が満たされるか: {spher_time}\n")
            report_file.write(f"  - $\chi^2$値: {chi2_time:.4f}, 自由度: {dof_time}, p値: {p_time:.4e}\n")
        except Exception as e:
            report_file.write(f"- **simulatedLoadingTime要因**: 球面性検定の実行に失敗しました ({e})\n")
            
        report_file.write("\n")
        
    report_file.write("※注: pingouinの `rm_anova` を用いた主検定では、交互作用項も含め球面性の仮定が棄却された場合、自動的にGreenhouse-Geisser補正されたp値（`p_GG_corr`）が計算されます。以下の主検定結果では自動補正を考慮した値を使用します。\n\n")
    report_file.write("---\n\n")

    # ==========================================
    # 【Step 3】主検定：「二元配置反復測定分散分析（Two-Way RM-ANOVA）」
    # ==========================================
    print("[Step 3] 二元配置反復測定分散分析を実行中...")
    report_file.write("## 【Step 3】主検定：「二元配置反復測定分散分析（Two-Way RM-ANOVA）」\n\n")
    report_file.write("被験者内要因として**ローダータイプ (`loaderType` : 7水準)**および**待ち時間 (`simulatedLoadingTime` : 3水準)**を設定し、個人内正規化した各心理指標に対する**二元配置反復測定分散分析（Two-Way Repeated Measures ANOVA）**を行いました。\n\n")
    
    anova_results = {}
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        report_file.write(f"### 目的変数: {col} (個人内正規化Zスコア)\n")
        
        # 二元配置RM-ANOVAの実行
        aov = pg.rm_anova(
            data=df_norm, dv=col_z, 
            within=['loaderType', 'simulatedLoadingTime'], 
            subject='participant_id', detailed=True
        )
        
        # 結果の保存
        anova_results[col] = aov
        csv_path = os.path.join(OUTPUT_DIR, f'step3_rm_anova_{col}.csv')
        aov.to_csv(csv_path, index=False)
        
        # マークダウンへのテーブル出力
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
    # 【Step 4】事後検定：「多重比較（Post-hoc Test）」による条件間の特定
    # ==========================================
    print("[Step 4] 事後検定（多重比較）および読み込み時間別分析を実行中...")
    report_file.write("## 【Step 4】事後検定：「多重比較（Post-hoc Test）」および読み込み時間別分析\n\n")
    report_file.write("主検定（Two-Way RM-ANOVA）の結果に基づいて、有意な効果に対する事後検定（多重比較）を実行しました。\n")
    report_file.write("被験者内デザインのため、**対応のあるt検定（Paired t-test）**を使用し、第一種の過誤（偽陽性）を制御するために**Holm補正**によりp値を調整しました。\n\n")
    
    for col in psych_metrics:
        col_z = f'{col}_z'
        aov = anova_results[col]
        
        # 主効果と交互作用の有意性チェック
        p_loader = aov.loc[aov['Source'] == 'loaderType', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'loaderType', 'p_GG_corr'].values[0]):
            p_loader = aov.loc[aov['Source'] == 'loaderType', 'p_GG_corr'].values[0]
            
        p_time = aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_GG_corr'].values[0]):
            p_time = aov.loc[aov['Source'] == 'simulatedLoadingTime', 'p_GG_corr'].values[0]
            
        p_inter = aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_unc'].values[0]
        if 'p_GG_corr' in aov.columns and not pd.isna(aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_GG_corr'].values[0]):
            p_inter = aov.loc[aov['Source'] == 'loaderType * simulatedLoadingTime', 'p_GG_corr'].values[0]
            
        report_file.write(f"### 指標: {col}\n")
        report_file.write(f"- 主効果 (loaderType): p = {p_loader:.4f} ({'有意' if p_loader < 0.05 else '有意ではない'})\n")
        report_file.write(f"- 主効果 (simulatedLoadingTime): p = {p_time:.4f} ({'有意' if p_time < 0.05 else '有意ではない'})\n")
        report_file.write(f"- 交互作用 (loaderType * simulatedLoadingTime): p = {p_inter:.4f} ({'有意' if p_inter < 0.05 else '有意ではない'})\n\n")
        
        # 1. 常に読み込み時間（simulatedLoadingTime）別の多重比較を実行
        report_file.write("#### **読み込み時間（待ち時間）別のローダータイプ間多重比較**\n\n")
        report_file.write("実務的な観点から、交互作用の有意性にかかわらず、各待ち時間（1.0秒、2.5秒、5.0秒）においてどのローダーが優れているかを特定するため、読み込み時間別の多重比較（対応のあるt検定、Holm補正）を実行しました。\n\n")
        
        posthoc_list = []
        for time_val in sorted(df_norm['simulatedLoadingTime'].unique()):
            time_sec = time_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == time_val]
            ph = pg.pairwise_tests(
                data=sub_df, dv=col_z, within='loaderType', 
                subject='participant_id', padjust='holm'
            )
            ph['simulatedLoadingTime_sec'] = time_sec
            posthoc_list.append(ph)
            
            # 各時間ごとの有意差をレポートに記載
            ph_sig = ph[ph['p_corr'] < 0.05]
            report_file.write(f"##### 待ち時間: {time_sec}秒 におけるローダー間比較\n")
            if not ph_sig.empty:
                cols_to_show = ['A', 'B', 'T', 'dof', 'alternative', 'p_unc', 'p_corr', 'hedges']
                report_file.write(ph_sig[cols_to_show].to_markdown(index=False) + "\n\n")
            else:
                ph_sorted = ph.sort_values(by='p_corr').head(3)
                report_file.write("Holm補正後に統計的有意差（$p < 0.05$）に達したペアはありませんでした。以下は比較的差異が大きかったペア（補正前 $p$ 値の小さい上位3ペア）です：\n\n")
                cols_to_show = ['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']
                report_file.write(ph_sorted[cols_to_show].to_markdown(index=False) + "\n\n")
                
        df_posthoc = pd.concat(posthoc_list, ignore_index=True)
        csv_path = os.path.join(OUTPUT_DIR, f'step4_posthoc_by_time_{col}.csv')
        df_posthoc.to_csv(csv_path, index=False)
        report_file.write(f"すべての時間別の多重比較結果は `{os.path.basename(csv_path)}` に保存しました。\n\n")
        
        # 2. ローダータイプ全体の主効果多重比較
        if p_loader < 0.05:
            report_file.write("#### **ローダータイプ全体の主効果の多重比較（全待ち時間をプールした比較）**\n\n")
            ph_loader = pg.pairwise_tests(
                data=df_norm, dv=col_z, within='loaderType', 
                subject='participant_id', padjust='holm'
            )
            df_posthoc_sig = ph_loader[ph_loader['p_corr'] < 0.05].copy()
            
            csv_path = os.path.join(OUTPUT_DIR, f'step4_posthoc_loader_overall_{col}.csv')
            ph_loader.to_csv(csv_path, index=False)
            
            report_file.write(f"すべての全体的な多重比較結果は `{os.path.basename(csv_path)}` に保存しました。以下は有意な差が見られたペアです：\n\n")
            if not df_posthoc_sig.empty:
                cols_to_show = ['A', 'B', 'T', 'dof', 'alternative', 'p_unc', 'p_corr', 'hedges']
                report_file.write(df_posthoc_sig[cols_to_show].to_markdown(index=False) + "\n\n")
            else:
                ph_sorted = ph_loader.sort_values(by='p_corr').head(3)
                report_file.write("Holm補正後に有意差が認められたペアはありませんでした。以下は比較的差異が大きかったペア（上位3ペア）です：\n\n")
                cols_to_show = ['A', 'B', 'T', 'dof', 'p_unc', 'p_corr', 'hedges']
                report_file.write(ph_sorted[cols_to_show].to_markdown(index=False) + "\n\n")
                
        # 3. 待ち時間の主効果の多重比較
        if p_time < 0.05:
            report_file.write("#### **待ち時間（simulatedLoadingTime）の主効果の多重比較**を行います。\n\n")
            ph_time = pg.pairwise_tests(
                data=df_norm, dv=col_z, within='simulatedLoadingTime', 
                subject='participant_id', padjust='holm'
            )
            
            csv_path = os.path.join(OUTPUT_DIR, f'step4_posthoc_time_{col}.csv')
            ph_time.to_csv(csv_path, index=False)
            report_file.write(ph_time.to_markdown(index=False) + "\n\n")
            
        # 4. 読み込み時間別の詳細可視化プロット (1.0s, 2.5s, 5.0s の3枚パネル)
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        times = sorted(df_norm['simulatedLoadingTime'].unique())
        
        for idx, time_val in enumerate(times):
            time_sec = time_val / 1000.0
            sub_df = df_norm[df_norm['simulatedLoadingTime'] == time_val]
            
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
            
        plt.suptitle(f'読み込み時間別 ローダータイプの比較 ({col} Zスコア)', fontsize=16)
        plt.tight_layout()
        time_plot_path = os.path.join(OUTPUT_DIR, f'step4_time_specific_comparison_{col}.png')
        plt.savefig(time_plot_path)
        plt.close()
        
        report_file.write(f"読み込み時間別の比較プロットを保存しました: `step4_time_specific_comparison_{col}.png`  \n\n")
        report_file.write("\n")
        
    report_file.write("---\n\n")

    # ==========================================
    # 【Step 5】行動・心理分析：「混合効果モデル（LMM）」によるメカニズム解明
    # ==========================================
    print("[Step 5] 混合効果モデル(LMM)の分析を実行中...")
    report_file.write("## 【Step 5】行動・心理分析：「混合効果モデル（LMM）」によるメカニズム解明\n\n")
    report_file.write("実験デザイン（`loaderType`, `simulatedLoadingTime`）に加え、ユーザーの実際の**操作・行動指標（レイジクリック数、マウス移動距離、純タスク時間）**が、主観的評価（不快感や信頼度）にどのような影響を及ぼしているかを包括的に分析するため、**線形混合効果モデル（Linear Mixed Effects Model: LMM）**を構築しました。\n\n")
    report_file.write("- 被験者（`participant_id`）を**ランダム効果（ランダム切片）**として設定し、個人特有の回答基準のばらつきを吸収します。\n")
    report_file.write("- 固定効果には以下の変数を投入しました：\n")
    report_file.write("  - `loaderType`（質的変数。ローダー画面なしの `none` を基準とするダミー変数に変換）\n")
    report_file.write("  - `simulatedLoadingTime_sec`（秒単位の実際の待ち時間：連続変数）\n")
    report_file.write("  - `rageClicks_z`（全体で標準化したレイジクリック数：連続変数）\n")
    report_file.write("  - `mouseDistance_z`（全体で標準化したマウス移動距離：連続変数）\n")
    report_file.write("- これにより、異なるスケールの行動指標（クリック数 vs ピクセル数）が心理評価に与える影響力を、係数（標準化偏回帰係数に近い形式）の大きさで直接比較できます。\n\n")
    
    # 混合効果モデルの適用
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
    print("--- 統計分析が完了しました。レポートが生成されました ---")
    print(f"レポートファイル: {report_path}")

if __name__ == '__main__':
    run_analysis()
