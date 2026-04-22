## Pythonista-3-GPS-Tracker-Pedometer
Pythonista 3上で動作する、SQLite データベースを搭載したGPS軌跡記録・歩数計アプリのデモです。 

iOSデバイスのGPS情報を利用して、リアルタイムの速度、移動距離、および歩数を計測し、データベースに保存します。

## 特徴
- **リアルタイムトラッキング**: 位置情報を取得し、Mapビュー上に赤いラインで軌跡を描画します。
  
- **SQLite データベース統合**: 取得したデータは `dbwork.sqlite` に保存され、後から分析が可能です。
  
- **独自歩数計算アルゴリズム**: 身長（168cm）に基づいた歩幅推定を用いて、GPSの移動距離から歩数を算出します。
  
- **データ構造**: 分析しやすいように、日付（YMD）と時刻（HHMMSS）を分離してレコードを保持します。

## インストール・使用方法
1. iOSデバイスで **Pythonista 3** を開きます。
   
3. 本リポジトリの `main.py` (または作成したスクリプト名) を新規ファイルとして作成・貼り付けます。
   
5. アプリを実行すると、位置情報の利用許可を求められるので「許可」してください。
   
7. アプリを起動したまま移動すると、画面下部の地図に軌跡が表示され、上部に歩数と速度が表示されます。

## データベース仕様
データベースファイル名: `dbwork.sqlite`  

テーブル名: `test_T_hosuu_app`

| カラム名 | 型 | 説明 |
| :--- | :--- | :--- |
| id | INTEGER | プライマリキー (自動増分) |
| ymd | TEXT | 記録年月日 (YYYYMMDD) |
| hhmmss | TEXT | 記録時刻 (HHMMSS) |
| lat | REAL | 緯度 |
| lon | REAL | 経度 |
| speed | REAL | 速度 (m/s) |
| distance_delta | REAL | 前回取得時からの移動距離 (m) |
| steps_delta | INTEGER | 前回取得時からの歩数増加量 |
| total_steps_current | INTEGER | 起動時からの累計歩数 |

## 技術スタック
- **Language**: Python 3 (Pythonista 3 Environment)
  
- **Database**: SQLite3
  
- **iOS Modules**:
  
  - `location`: GPS情報の取得
    
  - `ui`: ユーザーインターフェースの構築
    
  - `mapview`: 地図の描画と軌跡（Polyline）の表示


## カスタマイズ

歩幅の計算は以下の設定に基づいています：

- 身長: 168 cm
- 
- 歩幅係数: 0.45 (身長 × 0.45 = 75.6 cm)
- 

ご自身の身長に合わせて調整する場合は、コード内の `self.height_cm` の値を変更してください。
