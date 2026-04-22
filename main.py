import ui
import location
import sqlite3
import mapview
from datetime import datetime
import math

class TrackerApp(ui.View):
    def __init__(self):
        # 設定
        self.db_name = 'dbwork.sqlite'
        self.table_name = 'test_T_hosuu_app' # スキーマ風に接頭辞を付与
        self.height_cm = 168
        # 歩幅の計算式（一般的に 身長 * 0.45 程度とされる）
        self.stride_m = self.height_cm * 0.45 / 100 
        
        self.setup_db()
        
        # UI構築
        self.name = 'GPS Walker Tracker'
        self.background_color = '#f0f0f2'
        
        # 歩数表示
        self.step_label = ui.Label(frame=(20, 20, 300, 40))
        self.step_label.text = 'Steps: 0'
        self.step_label.font = ('<system-bold>', 32)
        self.add_subview(self.step_label)
        
        # 速度・距離表示
        self.info_label = ui.Label(frame=(20, 65, 300, 30))
        self.info_label.text = 'Speed: 0.0 m/s  Dist: 0.0 m'
        self.add_subview(self.info_label)
        
        # マップ (下半分)
        self.mv = mapview.MapView(frame=(0, self.height*0.5, self.width, self.height*0.5))
        self.mv.flex = 'WH'
        self.mv.shows_user_location = True
        self.add_subview(self.mv)
        
        self.path_points = []
        self.total_distance = 0.0
        self.total_steps = 0
        self.last_loc = None

    def setup_db(self):
        """データベースとテーブルの初期化"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ymd TEXT,
                    hhmmss TEXT,
                    lat REAL,
                    lon REAL,
                    speed REAL,
                    distance_delta REAL,
                    steps_delta INTEGER,
                    total_steps_current INTEGER
                )
            ''')
            conn.commit()

    def save_data(self, lat, lon, speed, dist_delta, steps_delta):
        """詳細な日時と歩数データをDBに保存"""
        now = datetime.now()
        ymd = now.strftime('%Y%m%d')
        hhmmss = now.strftime('%H%M%S')
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {self.table_name} 
                (ymd, hhmmss, lat, lon, speed, distance_delta, steps_delta, total_steps_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ymd, hhmmss, lat, lon, speed, dist_delta, steps_delta, self.total_steps))
            conn.commit()

    def calculate_distance(self, p1, p2):
        """2点間の距離(m)を計算（簡易的な三平方の定理）"""
        # 緯度1度 ≒ 111km, 経度1度 ≒ 91km (日本付近)
        dx = (p1[1] - p2[1]) * 91000 
        dy = (p1[0] - p2[0]) * 111000
        return math.sqrt(dx**2 + dy**2)

    def update_location(self):
        """GPS情報を取得・計算して更新"""
        loc = location.get_location()
        if not loc: return
        
        curr_lat, curr_lon = loc['latitude'], loc['longitude']
        speed = max(0, loc.get('speed', 0))
        dist_delta = 0.0
        steps_delta = 0
        
        # 移動距離と歩数の計算
        if self.last_loc:
            dist_delta = self.calculate_distance(self.last_loc, (curr_lat, curr_lon))
            # GPSの誤差（微細な揺れ）を除外するため 0.5m 以上の移動のみカウント
            if dist_delta > 0.5:
                self.total_distance += dist_delta
                # 距離 ÷ 歩幅 = 歩数
                steps_delta = int(dist_delta / self.stride_m)
                self.total_steps += steps_delta
        
        self.last_loc = (curr_lat, curr_lon)
        
        # UI更新
        self.step_label.text = f'Steps: {self.total_steps}'
        self.info_label.text = f'Speed: {speed:.1f} m/s  Dist: {self.total_distance:.1f} m'
        
        # DB保存
        self.save_data(curr_lat, curr_lon, speed, dist_delta, steps_delta)
        
        # 地図更新
        self.path_points.append((curr_lat, curr_lon))
        if len(self.path_points) > 1:
            line = mapview.Polyline(self.path_points)
            line.stroke_color = 'red'
            line.line_width = 4
            self.mv.add_layer(line)
        self.mv.center_coordinate = (curr_lat, curr_lon)

    def will_close(self):
        location.stop_updates()

# 実行
v = TrackerApp()
v.present('full_screen')
location.start_updates()

def update_loop():
    if v.on_screen:
        v.update_location()
        ui.delay(update_loop, 2)

update_loop()
