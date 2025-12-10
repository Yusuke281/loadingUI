import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- 定数定義 ---
INPUT_FILENAME = 'all_data.csv'
OUTPUT_DIR = 'advanced_analysis_results'

# --- 分析関数 ---
def run_correlation_analysis(df):
    """相関分析を実行し、結果を可視化・保存する"""
    print("\n--- 1. 相関分析 ---")
    
    # a. 実際の待ち時間 vs 体感待ち時間
    corr_time = df[['simulatedLoadingTime_sec', 'perceivedLoadingTime']].corr().iloc[0, 1]
    print(f"実際の待ち時間と体感待ち時間の相関係数: {corr_time:.4f}")

    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x='simulatedLoadingTime_sec', y='perceivedLoadingTime', hue='loaderType', style='loaderType', s=100, alpha=0.7)
    # y=xの補助線とmax_valの計算は、Y軸がVASスケールになったため不適切であり、削除
    plt.title('実際の待ち時間 vs 体感時間 (VAS評価)', fontsize=16)
    plt.xlabel('実際の待ち時間 (秒)', fontsize=12)
    plt.ylabel('体感時間 (VAS評価 0-100)', fontsize=12)
    plt.legend(title='ローダーの種類', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_simulated_vs_perceived_time.png'))
    plt.close()

    # b. 客観指標 vs 満足度
    # participant_idは相関分析に不要なため除外
    corr_satisfaction = df.drop(columns=['participant_id']).corr(numeric_only=True)['satisfaction_score']
    print("\n客観指標と満足度の相関係数:")
    print(corr_satisfaction)
    
    plt.figure(figsize=(10, 6))
    sns.lmplot(data=df, x='taskDuration_sec', y='satisfaction_score', aspect=1.5)
    plt.title('タスク時間と満足度の関係', fontsize=16)
    plt.xlabel('純粋なタスク時間 (秒)', fontsize=12)
    plt.ylabel('満足度スコア', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_duration_vs_satisfaction.png'))
    plt.close()
    
    print("相関分析の結果を保存しました。")

def run_multiple_regression(df):
    """重回帰分析を実行し、結果を出力する"""
    print("\n--- 2. 重回帰分析 (満足度予測モデル) ---")
    
    # カテゴリカル変数をダミー変数に変換
    df_reg = pd.get_dummies(df, columns=['loaderType'], drop_first=True, dtype=int)
    
    # participant_idはモデルに含めない
    X_cols = [col for col in df_reg.columns if col.startswith('loaderType_') or col in ['simulatedLoadingTime_sec', 'mouseDistance', 'rageClicks']]
    X = df_reg[X_cols]
    X = sm.add_constant(X)
    y = df_reg['satisfaction_score']
    
    model = sm.OLS(y, X).fit()
    
    print(model.summary())
    
    with open(os.path.join(OUTPUT_DIR, 'multiple_regression_summary.txt'), 'w', encoding='utf-8') as f:
        f.write(model.summary().as_text())
        
    print("重回帰分析の結果を保存しました。")

def run_interaction_analysis(df):
    """二元配置分散分析を実行し、交互作用を分析・可視化する"""
    print("\n--- 3. 交互作用効果の分析 (二元配置分散分析) ---")
    
    df_anova = df.copy()
    df_anova['duration_cat'] = df_anova['simulatedLoadingTime'].astype(str)

    print("\n--- ANOVA Cell Counts (loaderType vs duration_cat) ---")
    crosstab = pd.crosstab(df_anova['loaderType'], df_anova['duration_cat'])
    print(crosstab)

    # 交互作用モデルの実行
    # 注: この分析は、各セルのサンプル数が2以上の場合にのみ有効な結果を返します。
    # consolidate_data.pyで複数の被験者データを統合した後に実行することを想定しています。
    try:
        model = ols('satisfaction_score ~ C(loaderType) + C(duration_cat) + C(loaderType):C(duration_cat)', data=df_anova).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        print("\n満足度スコアに関する二元配置分散分析 (交互作用あり):")
        print(anova_table)

        with open(os.path.join(OUTPUT_DIR, 'two_way_anova_summary.txt'), 'w', encoding='utf-8') as f:
            f.write("Satisfaction Score Two-Way ANOVA (with Interaction)\n\n")
            f.write("Cell Counts:\n")
            f.write(str(crosstab) + "\n\n")
            f.write("ANOVA Results:\n")
            f.write(str(anova_table))
        
        # 交互作用プロットの作成
        plt.figure(figsize=(12, 8))
        sns.pointplot(data=df_anova, x='loaderType', y='satisfaction_score', hue='duration_cat', dodge=True,
                      markers=['o', 's', 'D'], linestyles=['-', '--', ':'])
        plt.title('ローダー種類と待ち時間の交互作用プロット (満足度スコア)', fontsize=16)
        plt.xlabel('ローダーの種類', fontsize=12)
        plt.ylabel('平均満足度スコア', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='待ち時間 (ms)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'interaction_plot_satisfaction.png'))
        plt.close()
        
        print("二元配置分散分析（交互作用あり）の結果とプロットを保存しました。")

    except ValueError as e:
        print("\nエラー: 交互作用を含む二元配置分散分析を実行できませんでした。")
        print("このエラーは、多くの場合、各条件の組み合わせ（セル）に十分なサンプルサイズがない（n=1など）場合に発生します。")
        print(f"詳細: {e}")
        # エラーが発生した場合、主効果のみのモデルを試行
        print("\n...交互作用を含まない主効果のみのモデルを試行します...")
        model = ols('satisfaction_score ~ C(loaderType) + C(duration_cat)', data=df_anova).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print("\n満足度スコアに関する二元配置分散分析 (主効果のみ):")
        print(anova_table)
        with open(os.path.join(OUTPUT_DIR, 'two_way_anova_summary.txt'), 'w', encoding='utf-8') as f:
            f.write("Satisfaction Score Two-Way ANOVA (Main Effects Only)\n\n")
            f.write("Cell Counts:\n")
            f.write(str(crosstab) + "\n\n")
            f.write("ANOVA Results (Interaction model failed, fallback to main effects):\n")
            f.write(str(anova_table))
        print("主効果のみの分析結果を保存しました。")


# --- メイン処理 ---
def main():
    """メインの実行関数"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.rcParams['font.family'] = 'Yu Gothic'

    print("--- 高度な分析スクリプト開始 ---")
    
    try:
        df_all = pd.read_csv(INPUT_FILENAME)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_FILENAME}' が見つかりません。")
        print("先に `consolidate_data.py` を実行して、統合データファイルを作成してください。")
        return
    
    print(f"'{INPUT_FILENAME}' を読み込みました。総試行回数: {len(df_all)}")
    
    # 各分析の実行
    run_correlation_analysis(df_all)
    run_multiple_regression(df_all)
    run_interaction_analysis(df_all)
    
    print("\n--- すべての分析が完了しました ---")
    print(f"結果は '{OUTPUT_DIR}' フォルダに保存されています。")

if __name__ == '__main__':
    main()