# 分析手順メモ

このプロジェクトのデータ分析を行うための手順です。

## 1. データ収集

1.  各被験者にWebブラウザで実験を実施してもらいます。
    - ローカルサーバーを起動 (`python -m http.server 8000`) し、 `http://localhost:8000` にアクセスしてください。
2.  実験がすべて完了すると、`task_timings.csv` という名前のCSVファイルが自動的にダウンロードされます。
3.  ダウンロードされたファイルを、**`task_timings_pX.csv`** という形式にリネームして、プロジェクトのルートディレクトリに保存してください。
    - `X`には被験者番号を入れてください。(例: `task_timings_p1.csv`, `task_timings_p2.csv`)

## 2. データの統合

すべての被験者のデータ収集が終わったら、ターミナルで以下のコマンドを実行し、個別のCSVファイルを一つのマスターファイル `all_data.csv` に統合します。

```shell
python consolidate_data.py
```

このコマンドが成功すると、`all_data.csv` が生成されます。

## 3. 分析の実行

ステップ2で生成された `all_data.csv` を使って、各種分析スクリプトを実行します。

### 基本的な行動分析

```shell
python analysis.py all_data.csv
```
> `analysis_results` フォルダにグラフが保存されます。

### アンケートデータの分析

```shell
python survey_analysis.py all_data.csv
```
> `survey_analysis_results` フォルダにグラフが保存されます。

### 色の有無による比較分析

```shell
python color_vs_nocolor_analysis.py all_data.csv
```
> `color_analysis_results` フォルダにグラフが保存されます。

### 高度な統計分析（重回帰分析など）

このスクリプトは、デフォルトで `all_data.csv` を読み込むように設定されています。

```shell
python advanced_analysis.py
```
> `advanced_analysis_results` フォルダに結果が出力されます。

---
以上が、データ収集から分析までの全体の流れです。
