import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from details_view import DetailsView
from navigator import Navigator
from distance_calculator import DistanceCalculator
from Surrounding import SurroundingInfoWindow  # 导入 SurroundingInfoWindow 类
import requests

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle('地图导航软件')
        self.setGeometry(100, 100, 1600, 600) # 设置窗口尺寸，参数分别为 x、y、宽、高

        # API密钥和各个组件的初始化
        self.api_key_web = 'YOUR_WEB_API_KEY'  # 替换为你的高德地图 API Key
        self.api_key = 'YOUR_JS_API_KEY'  # 替换为你的高德地图 API Key
        self.navigator = Navigator(self.api_key_web)
        self.webview = QWebEngineView()  # 用于显示高德二维地图
        self.amap_3d_view = QWebEngineView()  # 用于显示高德三维地图
        self.details_view = DetailsView()
        self.distance_calculator = DistanceCalculator(self.api_key)
        self.initUI()  # 初始化UI界面

    def initUI(self):
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout()
        # 创建中心布局（垂直布局）
        body_layout = QVBoxLayout()
        # 创建右侧布局（垂直布局）
        right_layout = QVBoxLayout()
        # 创建左侧布局（垂直布局，用于三维地图）
        left_layout = QVBoxLayout()

        # 创建一个容器部件，并设置其布局为主布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 创建起点和终点输入框
        self.start_input = QLineEdit(self)
        self.start_input.setPlaceholderText('输入起点地名')
        self.end_input = QLineEdit(self)
        self.end_input.setPlaceholderText('输入终点地名')

        # 创建交通模式选择框
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItem('驾车')
        self.mode_combo.addItem('步行')
        self.mode_combo.addItem('骑行')
        self.mode_combo.addItem('公共交通')

        # 创建导航按钮，并连接点击事件到导航函数
        self.nav_button = QPushButton('开始导航', self)
        self.nav_button.clicked.connect(self.navigate)

        # 新增按钮,用于查看周边信息
        self.surrounding_info_button = QPushButton('查看周边信息', self)  # 新增按钮
        self.surrounding_info_button.clicked.connect(self.show_surrounding_info)  # 连接槽函数

        # 创建状态标签、时间标签和费用标签
        self.status_label = QLabel('状态：', self)
        self.cost_label = QLabel('费用：', self)
        self.time_label = QLabel('时间：', self)

        # 将输入框、选择框、按钮和标签添加到左侧布局中
        body_layout.addWidget(self.start_input)
        body_layout.addWidget(self.end_input)
        body_layout.addWidget(self.nav_button)
        body_layout.addWidget(self.mode_combo)
        # 新增按钮,用于查看周边信息
        body_layout.addWidget(self.surrounding_info_button)  # 添加按钮到布局

        body_layout.addWidget(self.status_label)
        body_layout.addWidget(self.webview)
        body_layout.addWidget(self.cost_label)
        body_layout.addWidget(self.time_label)

        # 添加三维地图视图
        left_layout.addWidget(QLabel('三维地图：'))
        left_layout.addWidget(self.amap_3d_view)
        self.amap_3d_view.setMinimumHeight(800)  # 设置最小高度，根据需要调整
        #self.amap_3d_view.setMaximumHeight(1800)  # 设置最大高度，根据需要调整
        #self.amap_3d_view.setFixedHeight(990)  # 设置固定高度

        # # 新增按钮,用于查看周边信息
        # body_layout.addWidget(self.surrounding_info_button)  # 添加按钮到布局

        # 将路线详情视图添加到右侧布局中
        right_layout.addWidget(QLabel('路线详情：'))
        right_layout.addWidget(self.details_view)

        # 将左侧布局和右侧布局添加到主布局中
        main_layout.addLayout(left_layout, 1)  # 左侧占 1 份
        main_layout.addLayout(body_layout, 2)
        main_layout.addLayout(right_layout, 1)


        self.surrounding_info_text = QLabel(self)  # 定义 surrounding_info_text

        # 加载地图
        self.load_map()
        self.load_amap_3d_map()  # 调用高德三维地图加载方法
        # 连接模式选择框的索引变化信号到模式切换函数
        self.mode_combo.currentIndexChanged.connect(self.switch_mode)

    # 显示周边信息
    def show_surrounding_info(self):
        if hasattr(self, 'start_coords') and hasattr(self, 'end_coords'):
            start_surroundings = self.navigator.get_surrounding_info(self.start_coords)
            end_surroundings = self.navigator.get_surrounding_info(self.end_coords)
            self.display_surrounding_info(start_surroundings, end_surroundings)

    # 显示周边信息
    def display_surrounding_info(self, start_surroundings, end_surroundings):
        start_info = "起点周边信息:\n"
        for poi in start_surroundings[:5]:  # 只显示前五个POI
            start_info += f"{poi['name']} - {poi['address']}\n"

        end_info = "\n终点周边信息:\n"
        for poi in end_surroundings[:5]:  # 只显示前五个POI
            end_info += f"{poi['name']} - {poi['address']}\n"

            # 打开新的窗口显示周边信息
            info_window = SurroundingInfoWindow(start_info, end_info, self)
            info_window.exec_()

    def load_map(self):
        # 构建地图的HTML内容
        map_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="apple-mobile-web-app-title" content="Your App Name"> <!-- For iOS -->
            <meta name="application-name" content="Your App Name"> <!-- For other platforms -->
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
                // 初始化地图
                var map = new AMap.Map('container', {{
                    resizeEnable: true,
                    zoom: 10
                }});

                // 添加实时交通图层
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
        self.webview.setHtml(map_html)  # 将HTML内容加载到网页视图中

    def load_amap_3d_map(self):
        """
        加载高德三维地图。
        """
        amap_3d_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="apple-mobile-web-app-title" content="Your App Name"> <!-- For iOS -->
            <meta name="application-name" content="Your App Name"> <!-- For other platforms -->
            <title>高德三维地图</title>
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
                    zoom: 17,
                    pitch: 75,
                    viewMode: '3D',  // 使用3D视图
                    buildingAnimation: true,  // 楼块出现是否带动画
                    expandZoomRange: true,
                    zooms: [3, 20]
                }});

                var object3Dlayer = new AMap.Object3DLayer({{zIndex: 1}});
                map.add(object3Dlayer);

                // 创建步行导航对象
                var walking = new AMap.Walking({{ 
                    map: map,
                    panel: "panel"
                }});

                // 路线规划
                function planRoute(start, end) {{
                    walking.search(start, end, function(status, result) {{
                        if (status === 'complete') {{
                            console.log('步行路线规划完成');
                        }} else {{
                            console.log('步行路线规划失败：' + result);
                        }}
                    }});
                }}

                // 模拟实时位置更新
                var marker = new AMap.Marker({{
                    position: [116.397428, 39.90923],
                    map: map
                }});

                function updatePosition(lng, lat) {{
                    marker.setPosition([lng, lat]);
                    map.setCenter([lng, lat]);
                }}

                // 示例：更新位置
                setInterval(function() {{
                    var lng = 116.397428 + (Math.random() - 0.5) * 0.01;
                    var lat = 39.90923 + (Math.random() - 0.5) * 0.01;
                    updatePosition(lng, lat);
                }}, 5000);  // 每5秒更新一次位置
            </script>
        </body>
        
        
        </html>
        '''
        self.amap_3d_view.setHtml(amap_3d_html)

    """
    <body>
            <div id="container"></div>
            <script type="text/javascript">
                // 初始化三维地图
                var map = new AMap.Map('container', {{
                    viewMode: '3D',  // 使用 3D 模式
                    zoom: 10,  // 初始缩放级别
                    center: [116.397428, 39.90923]  // 初始中心点（北京）
                }});
                
                
                
                
                map.plugin(['AMap.ControlBar'], function() {{
                    var controlBar = new AMap.ControlBar({{
                        position: {{
                            right: '10px',
                            top: '10px'
                        }}
                    }});
                    map.addControl(controlBar);
                }});
                
                map.setFeatures(['bg', 'road', 'building', 'point', '3d']);
                
                var loca = new Loca.Container({{
                    map: map
                }});
                var pl = new Loca.PolygonLayer({{
                    zIndex: 120,
                    shininess: 10,
                    hasSide: true,
                    cullface: 'back',
                    depth: true,
                }});
                pl.setCustomCenter([116.397428, 39.90923]);
                pl.setLoca(loca);
                map.on('complete', function() {{
                    loca.animate.start();
                }});

                // 添加实时交通图层
                var trafficLayer = new AMap.TileLayer.Traffic({{
                    zIndex: 10,
                    autoRefresh: true,
                    interval: 180
                }});
                map.add(trafficLayer);
            </script>
        </body>
    """

    def update_amap_3d_map(self, coords):
        """
        更新高德三维地图的路线。

        :param coords: 路线坐标（格式为 "经度,纬度;经度,纬度;..."）
        """
        # 将坐标字符串转换为 JavaScript 数组
        path = []
        for coord in coords.split(';'):
            lon, lat = map(float, coord.split(','))
            path.append([lon, lat])

        # 生成 JavaScript 代码
        amap_3d_script = f'''
        // 清除之前的路线
        map.clearMap();

        // 添加路线
        var polyline = new AMap.Polyline({{
            path: {path},
            isOutline: true,
            outlineColor: 'white',
            borderWeight: 2,
            strokeColor: 'blue',
            strokeOpacity: 1,
            strokeWeight: 5,
            lineJoin: 'round'
        }});
        map.add(polyline);

        // 设置视角
        map.setFitView([polyline], false, [100, 100, 100, 100]);
        '''
        # 在高德三维地图视图中执行 JavaScript 代码
        self.amap_3d_view.page().runJavaScript(amap_3d_script)

    def get_poi_info(self, location, keywords):
        # 获取POI信息
        url = f'https://restapi.amap.com/v3/place/around'
        params = {
            'key': self.api_key,
            'location': location,
            'keywords': keywords,
            'radius': 2000,  # 搜索半径
            'extensions': 'all'
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == '1':
            return data['pois']
        else:
            print(f"Error: {data['info']}")
            return []

    def navigate(self):
        # 导航功能
        self.start_location = self.start_input.text()
        self.end_location = self.end_input.text()
        self.mode = self.mode_combo.currentText()

        # 交通模式字典
        mode_dict = {
            '驾车': 'driving',
            '步行': 'walking',
            '骑行': 'bicycling',
            '公共交通': 'transit'
        }

        if self.start_location and self.end_location and self.mode in mode_dict:
            try:
                # 获取起点和终点的坐标
                self.start_coords = self.navigator.geocode(self.start_location)
                self.end_coords = self.navigator.geocode(self.end_location)
                self.start_coords_1 = tuple(map(float, self.start_coords.split(',')))
                self.end_coords_1 = tuple(map(float, self.end_coords.split(',')))

                if self.start_coords and self.end_coords:
                    # 加载路线
                    self.load_route(mode_dict[self.mode])
                else:
                    self.status_label.setText('状态：地名解析失败')
            except Exception as e:
                self.status_label.setText(f'状态：出现错误 - {str(e)}')
                print(f"Error during navigation: {str(e)}")
        else:
            self.status_label.setText('状态：请输入起点和终点地名')

    """
    def navigate(self):
        # 导航功能
        self.start_location = self.start_input.text()
        self.end_location = self.end_input.text()
        self.mode = self.mode_combo.currentText()

        # 交通模式字典
        mode_dict = {
            '驾车': 'driving',
            '步行': 'walking',
            '骑行': 'bicycling',
            '公共交通': 'transit'
        }

        if self.start_location and self.end_location and self.mode in mode_dict:
            try:
                # 获取起点和终点的坐标
                self.start_coords = self.navigator.geocode(self.start_location)
                self.end_coords = self.navigator.geocode(self.end_location)

                # 检查坐标是否有效
                if self.start_coords is None or self.end_coords is None:
                    self.status_label.setText('状态：地名解析失败')

                # 将坐标字符串转换为元组
                self.start_coords_1 = tuple(map(float, self.start_coords.split(',')))
                self.end_coords_1 = tuple(map(float, self.end_coords.split(',')))

                # 加载路线
                self.load_route(mode_dict[self.mode])
            except Exception as e:
                self.status_label.setText(f'状态：出现错误 - {str(e)}')
                print(f"Error during navigation: {str(e)}")
        else:
            self.status_label.setText('状态：请输入起点和终点地名')
    """
    def load_route(self, mode):
        # 加载路线
        if mode == 'transit':
            # 获取起点和终点的城市代码
            start_city = self.navigator.geocode_city_transit(self.start_location)
            end_city = self.navigator.geocode_city_transit(self.end_location)
            if not start_city or not end_city:
                self.status_label.setText('状态：无法获取城市代码')
                return
            # 获取路线
            routes = self.navigator.get_routes(self.start_coords, self.end_coords, mode, start_city, end_city)
        else:
            # 获取路线
            routes = self.navigator.get_routes(self.start_coords, self.end_coords, mode)

        if routes:
            self.routes = routes
            # 显示路线
            self.display_route(mode)
            self.status_label.setText('状态：路线加载成功')
            # 计算并显示费用
            self.display_cost(int(self.distance_calculator.estimate_fare(
                self.distance_calculator.haversine_distance(self.start_coords_1, self.end_coords_1))))
            # 显示预计时间
            self.display_time(int(self.distance_calculator.estimate_time(
                self.distance_calculator.haversine_distance(self.start_coords_1, self.end_coords_1), mode)))
        else:
            self.status_label.setText('状态：路线加载失败')
    """
    def get_city_code(self, location):
        # 获取城市代码
        city_codes = {
            '北京': '110000',
            '上海': '310000',
            '广州': '440100',
            '深圳': '440300'
        }
        return city_codes.get(location, '')
    """

    """
    def get_city_code(self, address):
        '''
        根据地址获取城市代码。

        :param address: 地址（如 "北京市朝阳区"）
        :return: 城市代码（如 "110000"）
        '''
        url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            if data['status'] == '1' and data['geocodes']:
                return data['geocodes'][0]['citycode']
            else:
                print(f"Failed to get city code for address: {address}. Response: {data}")
                return None
        except Exception as e:
            print(f"Error during city code retrieval: {e}")
            return None
    """

    def switch_mode(self):
        # 切换路线模式
        if hasattr(self, 'start_coords') and hasattr(self, 'end_coords'):
            self.mode = self.mode_combo.currentText()
            mode_dict = {
                '驾车': 'driving',
                '步行': 'walking',
                '骑行': 'bicycling',
                '公共交通': 'transit'
            }
            self.load_route(mode_dict[self.mode])

    def display_cost(self, cost):
        # 显示费用
        self.cost_label.setText(f'费用：{cost}元')

    def display_time(self, time):
        # 显示时间
        self.time_label.setText(f'时间：{time}分钟')

    def display_route(self, mode):
        # 显示路线
        if mode == 'transit':
            # 格式化公共交通路线
            route_details_list = self.navigator.format_transit_routes(self.routes)
            all_coords = []
            for route_details in route_details_list:
                # 将路线详情添加到详情视图中
                self.details_view.append(f"路线详情：\n{route_details}\n")
                coords = self.extract_coords_from_transit_route(route_details)
                all_coords.extend(coords)
            self.details_view.append("\n")
            # 在地图上显示公共交通路线
            self.display_transit_routes_on_map(all_coords)
        else:
            # 格式化驾车、步行等路线
            self.route = self.routes[0]
            route_details, coords = self.navigator.format_route(self.route, mode)
            # 更新详情视图
            self.details_view.update_details(route_details)
            # 在地图上显示路线
            self.display_route_on_map(coords)

        # 同步更新三维地图
        self.update_amap_3d_map(coords)



    """
    def extract_coords_from_transit_route(self, route_details):
        # 提取公共交通路线中的坐标
        coords = []
        for step in route_details.split('\n'):
            if "坐" in step and "从" in step and "到" in step:
                coords.append([116.397428, 39.90923])
        return coords
    """

    """
    def extract_coords_from_transit_route(self, route_details):
        '''
        提取公共交通路线中的坐标。

        :param route_details: 路线详情
        :return: 坐标列表
        '''
        coords = []
        for segment in route_details['segments']:
            if 'bus' in segment:
                for bus in segment['bus']['buslines']:
                    coords.extend(bus['polyline'].split(';'))
            if 'railway' in segment:
                for subway in segment['railway']['subways']:
                    coords.extend(subway['polyline'].split(';'))
            if 'walking' in segment:
                for walking in segment['walking']['steps']:
                    coords.extend(walking['polyline'].split(';'))
        return coords
    """

    def extract_coords_from_transit_route(self, route_details):
        """
        提取公共交通路线中的坐标。

        :param route_details: 路线详情
        :return: 坐标列表
        """
        coords = []
        for segment in route_details['transits']:  # 每个传输（公共交通）
            for step in segment['segments']:
                # 检查是否有公交信息
                if 'bus' in step:
                    for bus in step['bus']['buslines']:
                        coords.extend(bus['polyline'].split(';'))
                # 检查是否有轨道信息
                if 'railway' in step:
                    if 'subways' in step['railway']:
                        for subway in step['railway']['subways']:
                            coords.extend(subway['polyline'].split(';'))
                    else:
                        print("Warning: 'subways' field missing in railway segment")
                # 检查步行部分
                if 'walking' in step:
                    coords.extend(step['walking']['polyline'].split(';'))
        return coords

    def display_transit_routes_on_map(self, all_coords):
        # 在地图上显示公共交通路线
        start_coords = self.start_coords_1
        end_coords = self.end_coords_1

        # 获取POI信息
        poi_info = self.get_poi_info(f"{start_coords[0]},{start_coords[1]}", "旅游景点|道路")

        # 生成新的地图HTML
        map_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
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
                // 初始化地图
                var map = new AMap.Map('container', {{
                    resizeEnable: true,
                    zoom: 10
                }});

                // 添加起点标记
                var startMarker = new AMap.Marker({{
                    position: [{start_coords[0]}, {start_coords[1]}],
                    title: '起点'
                }});
                map.add(startMarker);

                // 添加终点标记
                var endMarker = new AMap.Marker({{
                    position: [{end_coords[0]}, {end_coords[1]}],
                    title: '终点'
                }});
                map.add(endMarker);

                // 显示路线
                var paths = {all_coords};
                paths.forEach(function(path) {{
                    var polyline = new AMap.Polyline({{
                        path: path,
                        borderWeight: 5,
                        strokeColor: 'blue',
                        lineJoin: 'round'
                    }});
                    map.add(polyline);
                }});

                // 添加实时交通图层
                var trafficLayer = new AMap.TileLayer.Traffic({{
                    zIndex: 10,
                    autoRefresh: true,
                    interval: 180
                }});
                map.add(trafficLayer);

                // 显示POI信息
                var poi_info = {poi_info};
                poi_info.forEach(function(poi) {{
                    var marker = new AMap.Marker({{
                        position: poi.location.split(',').map(parseFloat),
                        title: poi.name,
                        content: '<div style="background-color: white; border: 1px solid black; padding: 2px;">' + poi.name + '</div>'
                    }});
                    map.add(marker);
                }});
            </script>
        </body>
        </html>
        '''
        self.webview.setHtml(map_html)

    def display_route_on_map(self, coords):
        # 在地图上显示路线
        poi_info = self.get_poi_info(f"{self.start_coords_1[0]},{self.start_coords_1[1]}", "旅游景点|道路")

        # 生成新的地图HTML
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
                // 初始化地图
                var map = new AMap.Map('container', {{
                    resizeEnable: true,
                    zoom: 10
                }});

                // 添加起点标记
                var startMarker = new AMap.Marker({{
                    position: [{self.start_coords_1[0]}, {self.start_coords_1[1]}],
                    title: '起点'
                }});
                map.add(startMarker);

                // 添加终点标记
                var endMarker = new AMap.Marker({{
                    position: [{self.end_coords_1[0]}, {self.end_coords_1[1]}],
                    title: '终点'
                }});
                map.add(endMarker);

                // 显示路线
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

                // 添加实时交通图层
                var trafficLayer = new AMap.TileLayer.Traffic({{
                    zIndex: 10,
                    autoRefresh: true,
                    interval: 180
                }});
                map.add(trafficLayer);

                // 显示POI信息
                var poi_info = {poi_info};
                poi_info.forEach(function(poi) {{
                    var marker = new AMap.Marker({{
                        position: poi.location.split(',').map(parseFloat),
                        title: poi.name,
                        content: '<div style="background-color: white; border: 1px solid black; padding: 2px;">' + poi.name + '</div>'
                    }});
                    map.add(marker);
                }});
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