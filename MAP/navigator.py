import requests
import time

class Navigator:
    def __init__(self, api_key):
        self.api_key = api_key
        #self.api_key_js = api_key_js

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

    def geocode_city_transit(self, city_name):
        """
            根据地址获取城市代码

            Args:
                address (str): 地址字符串，如 "北京市朝阳区"

            Returns:
                str: 城市代码(如 "110000")，失败返回 None


        """
        # 参数检查
        if not city_name or not isinstance(city_name, str):
            print("Error: Invalid address parameter")
            return None

        # API参数准备
        params = {
            'address': city_name,
            'key': self.api_key,
            'output': 'JSON'
        }

        try:
            # 发送请求
            url = 'https://restapi.amap.com/v3/geocode/geo'
            response = requests.get(
                url,
                params=params,
                timeout=5  # 添加超时设置
            )

            # 检查HTTP状态码
            response.raise_for_status()

            # 解析响应数据
            data = response.json()

            # 验证API响应状态
            if data.get('status') != '1':
                print(f"API Error: {data.get('info', 'Unknown error')}")
                return None

            # 验证返回的地理编码结果
            geocodes = data.get('geocodes', [])
            if not geocodes:
                print(f"No results found for address: {city_name}")
                return None

            # 获取城市代码
            city_code = geocodes[0].get('citycode')
            if not city_code:
                print(f"No city code found for address: {city_name}")
                return None

            return city_code

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        finally:
            time.sleep(1)  # 增加延迟，避免超出限制

    """
    def geocode_city_transit(self, city_name):
        url = f'https://restapi.amap.com/v3/config/district?keywords={city_name}&key={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"Geocode city response for {city_name}: {data}")

            if data['status'] == '1' and data['districts']:
                city_code = data['districts'][0]['adcode']
                return city_code
            else:
                print(f"Failed to geocode city: {city_name}. Response: {data}")
                return None
        except Exception as e:
            print(f"Error during geocode city: {e}")
            return None
    """

    def get_routes(self, start_coords, end_coords, mode, city=None, cityd=None):
        if mode == 'driving':
            url = f'https://restapi.amap.com/v3/direction/driving?origin={start_coords}&destination={end_coords}&key={self.api_key}&extensions=all'
        elif mode == 'walking':
            url = f'https://restapi.amap.com/v3/direction/walking?origin={start_coords}&destination={end_coords}&key={self.api_key}'
        elif mode == 'bicycling':
            url = f'https://restapi.amap.com/v4/direction/bicycling?origin={start_coords}&destination={end_coords}&key={self.api_key}'
        elif mode == 'transit':
            if city is None or cityd is None:
                print("Error: Missing city or cityd parameter for transit mode")
                return None
            url = f'https://restapi.amap.com/v3/direction/transit/integrated?origin={start_coords}&destination={end_coords}&city={city}&cityd={cityd}&key={self.api_key}'
        else:
            return None

        try:
            response = requests.get(url)
            data = response.json()
            print(f"Routes response for {mode}: {data}")

            if mode == 'bicycling':
                if data['errcode'] == 0:
                    return data['data']['paths']
                else:
                    print(f"Failed to get bicycling routes: {data['errmsg']}")
                    return None
            elif mode == 'transit':
                if data['status'] == '1':
                    return data['route']['transits']
                else:
                    print(f"Failed to get transit routes: {data['info']}")
                    return None
            else:
                if data['status'] == '1':
                    return data['route']['paths']
                else:
                    print(f"Failed to get routes: {data['info']}")
                    return None
        except Exception as e:
            print(f"Error during route planning: {e}")
            return None
    """
    def format_transit_routes(self, routes):
        formatted_routes = []
        for route in routes:
            steps = []
            for segment in route['segments']:
                if 'bus' in segment:
                    for bus in segment['bus']['buslines']:
                        steps.append(f"坐 {bus['name']} 从 {bus['departure_stop']['name']} 到 {bus['arrival_stop']['name']}")
                if 'railway' in segment:
                    for subway in segment['railway']['subways']:
                        steps.append(f"坐 {subway['name']} 从 {subway['departure_stop']['name']} 到 {subway['arrival_stop']['name']}")
                if 'walking' in segment:
                    for walking in segment['walking']['steps']:
                        steps.append(f"步行 {walking['instruction']}")
            formatted_routes.append('\n'.join(steps))
        return formatted_routes"""

    def format_transit_routes(self, routes):
        """
        格式化公共交通路线详情。

        :param routes: 公共交通路线列表
        :return: 格式化后的路线详情列表
        """
        formatted_routes = []
        for route in routes:
            steps = []
            for segment in route['segments']:
                if 'bus' in segment:
                    for bus in segment['bus']['buslines']:
                        steps.append(
                            f"乘坐 {bus['name']} 从 {bus['departure_stop']['name']} 到 {bus['arrival_stop']['name']}")
                if 'railway' in segment:
                    for subway in segment['railway']['subways']:
                        steps.append(
                            f"乘坐 {subway['name']} 从 {subway['departure_stop']['name']} 到 {subway['arrival_stop']['name']}")
                if 'walking' in segment:
                    for walking in segment['walking']['steps']:
                        steps.append(f"步行 {walking['instruction']}")
            formatted_routes.append('\n'.join(steps))
        return formatted_routes

    def format_route(self, route, mode):
        if mode == 'transit':
            return self.format_transit_routes([route])[0]
        else:
            steps = route['steps']
            details = []
            coords = []
            for step in steps:
                coords.append(step['polyline'])
                instruction = step['instruction']
                distance = step['distance']
                road = step.get('road', '未知道路')
                details.append(f"沿 {road} 行驶 {distance} 米，{instruction}")
            route_details = '\n'.join(details)
            route_coords = ';'.join(coords)
            return route_details, route_coords

    def get_surrounding_info(self, coords, keywords='餐饮服务', radius=1000):

        print(f"Getting surrounding info for {coords}...")
        url = f'https://restapi.amap.com/v3/place/around?location={coords}&keywords={keywords}&radius={radius}&key={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            print(f"Surrounding info response: {data}")

            if data['status'] == '1' and data['pois']:
                pois = data['pois']
                return pois
            else:
                print(f"Failed to get surrounding info. Response: {data}")
                return None
        except Exception as e:
            print(f"Error during getting surrounding info: {e}")
            return None

