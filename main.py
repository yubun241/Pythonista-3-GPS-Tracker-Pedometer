import ui
import location
import sqlite3
from datetime import datetime
import math

# 地図を表示するためのHTML/JSテンプレート (Leafletを使用)
MAP_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>#map { height: 100vh; width: 100vw; margin: 0; }</style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([0, 0], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        var polyline = L.polyline([], {color: 'red'}).addTo(map);
        var marker = L.marker([0, 0]).addTo(map);

        function updateLocation(lat, lon) {
            var newPos = [lat, lon];
            marker.setLatLng(newPos);
            polyline.addLatLng(newPos);
            map.panTo(newPos);
        }
    </script>
</body>
</html>
'''

class TrackerApp(ui.View):
    def __init__(self):
        self.db_name = 'dbwork.sqlite'
        self.table_name = 'test_T_hosuu_app'
        self.height_cm = 168
        self.stride_m = self.height_cm * 0.45 / 100 
        self.setup_db()
        
        # UI設定
        self.name = 'GPS Tracker (No MapView)'
        
        # ラベル類
        self.step_label = ui.Label(frame=(20, 20, 300, 40), name='step_label')
        self.step_label.text = 'Steps: 0'
        self.step_label.font = ('<system-bold>', 32)
        self.add_subview(self.step_label)
        
        self.info_label = ui.Label(frame=(20, 65, 300, 30), name='info_label')
        self.info_label.text = 'Waiting for GPS...'
        self.add_subview(self.info_label)
        
        # WebViewによる地図表示 (下半分)
        self.webview = ui.WebView(frame=(0, self.height*0.4, self.width, self.height*0.6))
        self.webview.flex = 'WH'
        self.webview.load_html(MAP_HTML)
        self.add_subview(self.webview)
        
        self.total_distance = 0.0
        self.total_steps = 0
        self.last_loc = None

    def setup_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ymd TEXT, hhmmss TEXT, lat REAL, lon REAL, speed REAL,
                    distance_delta REAL, steps_delta INTEGER, total_steps_current INTEGER
                )
            ''')

    def update_location(self):
        loc = location.get_location()
        if not loc: return
        
        lat, lon = loc['latitude'], loc['longitude']
        speed = max(0, loc.get('speed', 0))
        dist_delta = 0.0
        steps_delta = 0
        
        if self.last_loc:
            # 簡易距離計算
            dx = (lat - self.last_loc[0]) * 111000
            dy = (lon - self.last_loc[1]) * 91000
            dist_delta = math.sqrt(dx**2 + dy**2)
            
            if dist_delta > 0.8: # ノイズ除去
                self.total_distance += dist_delta
                steps_delta = int(dist_delta / self.stride_m)
                self.total_steps += steps_delta
        
        self.last_loc = (lat, lon)
        
        # DB保存
        now = datetime.now()
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(f'''
                INSERT INTO {self.table_name} (ymd, hhmmss, lat, lon, speed, distance_delta, steps_delta, total_steps_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (now.strftime('%Y%m%d'), now.strftime('%H%M%S'), lat, lon, speed, dist_delta, steps_delta, self.total_steps))
        
        # UI更新
        self.step_label.text = f'Steps: {self.total_steps}'
        self.info_label.text = f'Speed: {speed:.1f} m/s  Dist: {self.total_distance:.1f} m'
        
        # 地図（WebView内のJS）を更新
        self.webview.evaluate_javascript(f'updateLocation({lat}, {lon})')

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
