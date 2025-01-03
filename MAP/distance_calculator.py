import math

class DistanceCalculator:
    def __init__(self, api_key):
        self.api_key = api_key

    def haversine_distance(self, coord1, coord2):
        # 将十进制度数转换为弧度
        lat1, lon1 = map(math.radians, coord1)
        lat2, lon2 = map(math.radians, coord2)

        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # 地球平均半径，单位为公里
        return c * r

    def estimate_fare(self, distance):
        base_fare = 10  # 起步价
        fare_per_km = 2  # 每公里费用
        return (base_fare + (fare_per_km * distance)) * 1.44

    def estimate_time(self, distance,mode='driving'):


        avg_speeds = {
                'driving': 60,  # 汽车，60 公里/小时
                'walking': 5,  # 步行，5 公里/小时
                'bicycling': 15,  # 自行车，15 公里/小时
                'transit': 40  # 公共交通，40 公里/小时
                          }

        if mode not in avg_speeds:
             raise ValueError("无效的出行方式，请选择 'car', 'walking', 'bicycle' 或 'public_transport'")

        avg_speed = avg_speeds[mode]
        time= distance / avg_speed  # 行程时间（小时）
        return time * 60  # 转换为分钟