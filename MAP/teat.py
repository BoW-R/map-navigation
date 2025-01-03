"""
import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Public Transportation Map Navigation')
        self.setGeometry(100, 100, 1200, 800)
        self.api_key = '9b8af7560afa5d4c8e5ba130a931a07a'  # 请确保此处使用的是正确的 API 密钥
        self.initUI()

    def initUI(self):
        self.webview = QWebEngineView()

        self.start_input = QLineEdit(self)
        self.start_input.setPlaceholderText('Enter start location')

        self.end_input = QLineEdit(self)
        self.end_input.setPlaceholderText('Enter end location')

        self.search_button = QPushButton('Search Route', self)
        self.search_button.clicked.connect(self.navigate)

        self.status_label = QLabel('Status:', self)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_input)
        input_layout.addWidget(self.search_button)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def navigate(self):
        start_location = self.start_input.text()
        end_location = self.end_input.text()

        if start_location and end_location:
            try:
                start_coords = self.geocode(start_location)
                end_coords = self.geocode(end_location)

                if start_coords and end_coords:
                    self.get_routes(start_coords, end_coords)
                else:
                    self.status_label.setText('Status: Geocoding failed')
            except Exception as e:
                self.status_label.setText(f'Status: Error - {str(e)}')
                print(f"Error during navigation: {str(e)}")
        else:
            self.status_label.setText('Status: Please enter start and end locations')

    def geocode(self, address):
        url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"Geocode response for {address}: {data}")

            if data['status'] == '1' and data['geocodes']:
                location = data['geocodes'][0]['location']
                return location
            else:
                print(f"Failed to geocode address: {address}. Response: {data}")
                return None
        except Exception as e:
            print(f"Error during geocode: {e}")
            return None

    def get_routes(self, start_coords, end_coords):
        url = f'https://restapi.amap.com/v3/direction/transit/integrated?origin={start_coords}&destination={end_coords}&key={self.api_key}&city=北京'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"Route response: {data}")

            if data['status'] == '1':
                self.routes = data['route']['transits']
                self.display_route()
                self.status_label.setText('Status: Navigation successful')
            else:
                self.status_label.setText(f"Status: Navigation failed - {data['info']}")
        except Exception as e:
            print(f"Error during route planning: {e}")
            self.status_label.setText(f'Status: Error - {str(e)}')

    def display_route(self):
        transit = self.routes[0]
        segments = transit['segments']
        coords = []
        for segment in segments:
            for step in segment['walking']['steps']:
                coords.append(step['polyline'])
            if 'bus' in segment:
                for step in segment['bus']['buslines'][0]['polyline'].split(';'):
                    coords.append(step)
        coords = ';'.join(coords)

        map_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>高德地图</title>
            <style type="text/css">
                body, html {{width: 100%; height: 100%; margin: 0; font-family: "微软雅黑";}}
                #container {{width: 100%; height: 100%;}}
            </style>
            <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={self.api_key}"></script>
        </head>
        <body>
            <div id="container"></div>
            <script type="text/javascript">
                var map = new AMap.Map('container', {{
                    resizeEnable: true,
                    zoom: 10
                }});

                var path = '{coords}'.split(';').map(function(item) {{
                    var parts = item.split(',');
                    return [parseFloat(parts[0]), parseFloat(parts[1])];
                }});

                var polyline = new AMap.Polyline({{
                    path: path,
                    borderWeight: 5,
                    strokeColor: 'blue',
                    lineJoin: 'round'
                }});
                map.add(polyline);
                map.setFitView([polyline]);

                var trafficLayer = new AMap.TileLayer.Traffic({{
                    zIndex: 10,
                    autoRefresh: true,
                    interval: 180
                }});
                map.add(trafficLayer);
            </script>
        </body>
        </html>
        '''
        self.webview.setHtml(map_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())
"""

"""
import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('公共交通地图导航')
        self.setGeometry(100, 100, 1200, 800)
        self.api_key = '9b8af7560afa5d4c8e5ba130a931a07a'  # 请确保此处使用的是正确的 API 密钥
        self.initUI()

    def initUI(self):
        self.webview = QWebEngineView()

        self.start_input = QLineEdit(self)
        self.start_input.setPlaceholderText('输入起点位置')

        self.end_input = QLineEdit(self)
        self.end_input.setPlaceholderText('输入终点位置')

        self.search_button = QPushButton('搜索路线', self)
        self.search_button.clicked.connect(self.navigate)

        self.status_label = QLabel('状态：', self)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_input)
        input_layout.addWidget(self.search_button)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def navigate(self):
        start_location = self.start_input.text()
        end_location = self.end_input.text()

        if start_location and end_location:
            try:
                start_coords = self.geocode(start_location)
                end_coords = self.geocode(end_location)

                if start_coords and end_coords:
                    self.get_routes(start_coords, end_coords)
                else:
                    self.status_label.setText('状态：地理编码失败')
            except Exception as e:
                self.status_label.setText(f'状态：出现错误 - {str(e)}')
                print(f"导航过程中出现错误: {str(e)}")
        else:
            self.status_label.setText('状态：请输入起点和终点位置')

    def geocode(self, address):
        url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"地理编码响应 {address}: {data}")

            if data['status'] == '1' and data['geocodes']:
                location = data['geocodes'][0]['location']
                return location
            else:
                print(f"地理编码失败: {address}. 响应: {data}")
                return None
        except Exception as e:
            print(f"地理编码过程中出现错误: {e}")
            return None

    def get_routes(self, start_coords, end_coords):
        url = f'https://restapi.amap.com/v3/direction/transit/integrated?origin={start_coords}&destination={end_coords}&key={self.api_key}&city=苏州市'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"路线响应: {data}")

            if data['status'] == '1':
                self.routes = data['route']['transits']
                self.display_route()
                self.status_label.setText('状态：导航成功')
            else:
                self.status_label.setText(f"状态：导航失败 - {data['info']}")
        except Exception as e:
            print(f"路线规划过程中出现错误: {e}")
            self.status_label.setText(f'状态：出现错误 - {str(e)}')

    def display_route(self):
        transit = self.routes[0]
        segments = transit['segments']
        coords = []
        for segment in segments:
            for step in segment['walking']['steps']:
                coords.append(step['polyline'])
            if 'bus' in segment:
                for step in segment['bus']['buslines'][0]['polyline'].split(';'):
                    coords.append(step)
        coords = ';'.join(coords)

        map_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>高德地图</title>
            <style type="text/css">
                body, html {{width: 100%; height: 100%; margin: 0; font-family: "微软雅黑";}}
                #container {{width: 100%; height: 100%;}}
            </style>
            <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={self.api_key}"></script>
        </head>
        <body>
            <div id="container"></div>
            <script type="text/javascript">
                var map = new AMap.Map('container', {{
                    resizeEnable: true,
                    zoom: 10
                }});

                var path = '{coords}'.split(';').map(function(item) {{
                    var parts = item.split(',');
                    return [parseFloat(parts[0]), parseFloat(parts[1])];
                }});

                var polyline = new AMap.Polyline({{
                    path: path,
                    borderWeight: 5,
                    strokeColor: 'blue',
                    lineJoin: 'round'
                }});
                map.add(polyline);
                map.setFitView([polyline]);

                var trafficLayer = new AMap.TileLayer.Traffic({{
                    zIndex: 10,
                    autoRefresh: true,
                    interval: 180
                }});
                map.add(trafficLayer);
            </script>
        </body>
        </html>
        '''
        self.webview.setHtml(map_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())
    
"""

